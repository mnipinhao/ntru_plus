# GT9X16 Forward OPT V3 priority audit

## Scope and current coordinate

This checkpoint does not change production or benchmark a new candidate.  It
re-audits the current scale-1, lazy-reduction, wire-monotone Forward leaf and
decides which Forward freedoms are real before more ASM is written.

The current linked leaf has:

```text
instructions                2875
.text                       15449 bytes
Montgomery chains             296
Barrett vectors                40
routing vectors               488
  vperm2i128                   72
  vpermq                       72
  vpshufb                      56
  unpack                      288
data loads/stores          144/144
stack/spill/call/branch          0
```

At the formal native-compiler attribution boundary, the complete current
Forward is already slightly faster than Official (`-8.875` cycles median), but
its caller edges remain slower.  Forward work therefore needs structural
credit and Native SUPERCOP validation; instruction-count improvements alone
are not promotion evidence.

## 1. D1 to frozen wire ABI orientation

The v1 search exhausted 4096 three-level unpack networks, output renames and
all `vpermq` immediates only after D1 had produced a fixed `(A+T,A-T)`
orientation.  Its 56-shuffle result was not a complete D1 lower bound.

V2 additionally observes that negating the matching lane of both the D1 zeta
and qinv tables changes `T` to `-T`.  This exchanges `(A+T,A-T)` without a
runtime instruction, while semantic leaf ownership and the frozen wire ABI
remain unchanged.  The exhaustive expanded search has 32 such lane variables.

Result:

```text
v1 memory-form vpshufb       56 / Forward
v2 memory-form vpshufb       48 / Forward
saved                          8 / Forward
new zero-shuffle tiles       p=2 and p=16
```

Each new zero-shuffle tile negates 16 D1 constant lanes.  The other twelve
paid tiles still require four within-128 shuffles each.  Thus this is a valid
low-risk peephole candidate, not an architecture-scale Forward win.  Before an
ASM candidate, the negated machine zeta/qinv pairs require canonical
differential and signed-i16 range replay; raw representatives need not match.

Evidence:

- `tools/generate_d1_wire_orientation_v2.py`
- `generated/d1-wire-orientation-v2.json`

## 2. NTT9 to NTT16 materialization

The full 2304-byte state is 72 YMM vectors.  Current traffic is:

```text
initial top-split loads       72
NTT9 intermediate stores     72  <-- boundary
NTT16 intermediate reloads   72  <-- boundary
final wire stores            72
```

The boundary therefore costs exactly 72 stores plus 72 reloads, or 2304 bytes
written and 2304 bytes read.  These accesses are normally L1-resident; they
must not be converted directly into a 144-cycle estimate.

The existing Pass A has nine live NTT9 data vectors plus seven constants and
temporaries: 16/16 YMM registers.  A naive one-row wavefront would have to keep
three earlier q-block outputs live while executing the next NTT9 q-block; a
two-row wavefront would keep six.  Neither fits the existing schedule.  A
"conservative wavefront" is therefore not a simple deletion of stores: it
requires a new NTT9 microkernel, recomputation, or spills that recreate the
same boundary.

The two GT axes commute algebraically, and the materialized top-split AoS makes
both first steps load-friendly:

```text
NTT9 first:   9 row vectors for one q-block
NTT16 first:  4 q-block vectors for one h-row
```

For Natural-Q, either complete order can in principle retain the same single
72-store/72-reload boundary.  For the current frozen wire ABI, however, the
required terminal permutation depends on final `p`.  If NTT16 runs first, D1
still sees top-split `h`, not final NTT9 frequency `p`; applying different
wire permutations before NTT9 would destroy lane-wise NTT9 compatibility.
Postponing that permutation restores correctness but creates a new terminal
pass.  Therefore the present order is preferred:

```text
top-split AoS -> NTT9 (final p becomes known)
              -> NTT16/D1
              -> p-specific wire materialization
```

Decision: do not write a one/two-row wavefront ASM under the present 16-register
schedule.  First design a register-feasible NTT9 tile and account for any
recomputation or spill.  NTT16-first is only worth reopening for a p-invariant
Natural-Q output, not for the frozen p-dependent wire ABI.

## 3. Remaining 40 Barrett vectors

The earlier 512-mask proof used the scale-4 T0-beta envelope.  This checkpoint
repeats all 512 masks using the actual caller-wide scale-1 alpha ranges.

Result:

```text
valid masks                         16 / 512
unique minimum mask                      79
retained registers          7, 8, 15, 10, 13
retained reductions             40 / Forward
peak absolute interval bound           21469
```

So scale-1 does not make a 40-to-smaller direct deletion safe.  The four
already removed inputs are immediately consumed by existing Montgomery
operations.  The five retained values include all three inputs of the
untwisted second radix-3 group and the unmultiplied `a` input of each twisted
group.

Further reduction requires at least one new freedom:

- change radix-3 input/output role or CT/GS orientation so the large value is
  consumed by a reducing multiply;
- prove correlations that independent interval propagation loses; or
- fuse a retained reduction into another arithmetic operation.

Evidence:

- `tools/generate_scale1_forward_reduction_reaudit.py`
- `generated/gt9x16-forward-scale1-reduction-reaudit.json`

## 4. The 296 Montgomery chains

The exact ledger is:

| owner | chains/Forward | role |
| --- | ---: | --- |
| scale-1 alpha normalization | 72 | one per branch, h-row and q-block |
| NTT9 radix-3 kappa | 48 | six radix-3 butterflies per branch/q-block |
| NTT9 rho/zeta interstage | 32 | four fixed twists per branch/q-block |
| NTT16 D8/D4/D2/D1 | 144 | eight radix-2 chains per final p-row |
| **total** | **296** | |

Official AVX2 also uses Montgomery multiplication for ordinary fixed twiddles:
`vpmullw(qinv)`, `vpmulhw(zeta)`, `vpmulhw(q)`, `vpsubw`.  It uses
`vpmulhrsw` Barrett operations for range reduction, not as a general
replacement for its fixed-twiddle multiplication.  Its level-0 `-722`
multiplication is a special raw `vpmullw` because the documented small input
range proves that reduction unnecessary.

The AArch64/NEON implementation has `sqrdmulh` and integer multiply-accumulate
instructions, so a signed-Barrett fixed-constant multiply/MAC can have a
different instruction geometry.  AVX2 has no equivalent 16-bit lane-wise
integer MLA/MLS.  A direct AVX2 Barrett constant multiply still needs low
product, quotient estimate, `q` product and correction, so replacing a
four-instruction Montgomery chain is not automatically a win.

The next meaningful arithmetic target is therefore not a global
"Montgomery-to-Barrett" conversion.  It is one of:

- prove a special raw multiply like Official level 0 for a specific constant;
- change the NTT9 DAG/gauge to reduce the 48 kappa or 32 interstage chains; or
- absorb an alpha factor into an existing radix operation without increasing
  constant traffic or range debt.

## 5. Straight-line scheduling and footprint

The 15.4 KiB leaf unrolls both branches, four NTT9 q-blocks per branch and nine
NTT16 rows per branch.  This buys constant offsets, no loop branches and no
frame, but consumes instruction-cache/uop-cache capacity.

Both principal kernels already reach 16/16 YMM liveness.  A true two-row
interleave is not free: it duplicates row state and therefore needs a different
microkernel or spills.  Keeping more constants resident has the same problem.

A compact realization remains a valid fifth-priority experiment:

```text
same arithmetic, range, wire ABI and alignment
loop/table-driven row realization
vs current 15.4 KiB straight-line leaf
```

Static size is diagnostic only.  The winner must be selected by native
SUPERCOP `enc_cycles`; repository-local Forward timing cannot promote it.

## Producer and consumer graph

There is no single universally optimal Forward ABI.

| caller producer | Forward input | immediate consumers |
| --- | --- | --- |
| keypair `f` | `3*CBD1 + 1` | base inversion, base multiplication, secret-key serialization |
| keypair `g` | `3*CBD1` | base inversion and base multiplication |
| encapsulation `r` | CBD1 `[-1,1]` | public hash serialization and multiplication by decoded `h` |
| encapsulation `m` | SOTP `[-1,1]` | add into the `h*r` multiplication output |
| decapsulation recovered `f=m` | centered mod-3 result | subtraction, multiplication by `hinv`, serialization |
| decapsulation re-encryption `f` | CBD1 `[-1,1]` | serialization/verification |

Consequently, the current wire-monotone ABI is an Encap-specific shared
presentation.  Keypair needs BaseInv-aware ownership; Decap has two different
fanouts; serializer-only calls may prefer a different terminal layout.  A
Forward optimization that changes scale, representative range, p/q ownership
or terminal order must be priced against every caller it is intended to
replace, not only the Encap MA2 path.

## Decision order

1. A small D1-sign ASM prototype is authorized in principle: expected credit
   is exactly eight removed memory-form `vpshufb` per Forward.
2. Do not start materialization-wavefront ASM until a register-feasible
   microkernel shows real store/reload deletion without recomputation/spill.
3. Freeze 40 Barrett under the current scale-1 paper-R2 DAG.
4. Treat NTT9 DAG/gauge and alpha absorption as research changes with new range
   proofs; do not substitute Barrett globally for Montgomery on AVX2.
5. Defer compact/two-row scheduling until the preceding arithmetic/layout
   candidates are settled, and decide it only with Native SUPERCOP.
