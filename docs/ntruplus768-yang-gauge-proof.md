# NTRU+768 Yang-inspired gauge / inverse-tail proof

Latest pricing: [combined short test](#combined-pair32-short-pricing) recovers
10.39 inverse cycles versus factored (3/3), but still loses 8.63 to Official
GS (0/3), and 29.36 in complete caller-lazy Decap (0/3). No promotion.

Latest machine follow-up: the user-authorized combined two-pair + 32-Barrett
candidate is implemented and passes validation. See
[combined ASM](#combined-two-pair--32-barrett-asm). No timing yet.

Latest follow-up: [222-chain scheduling and reduction audit](#222-chain-scheduling-and-reduction-audit)
finds a two-pair executable schedule and a safe 40→32 Barrett model. These
are separate unpriced candidates, not changes to the tested factored ASM.

Date: 2026-09-22. Branch: `avx2-official-opt`.

Follow-up: the two open model gates below are now closed by the
[caller closure and complete tail schedule](#caller-closure-and-complete-tail-schedule-follow-up).
The earlier sections preserve the original gate's conditional evidence;
new candidate ASM and machine timing remain unverified.

Latest: the factored schedule has now been lowered and tested. See
[ASM and short pricing](#factored-asm-and-short-pricing): correctness passes,
but it is slower than Official and wresident inverse; no serious/Native gate.

## Result and scope

The new algebraic mechanism is **delay radix-3 alpha multiplication and compose
it with the trinomial level-0 map and final scale**. Two realizations reduce the
full inverse model from 238 to 222 vector Montgomery chains, with the fixed
`wresident` CT prefix and its 40 relative-normalization chains retained.
Neither is a performance result or a qualified ASM candidate.

The tail identity and conditional signed range pass. The remaining gates are
the actual BaseMulScale-to-prefix input closure and full instruction-level
lowering/allocation of the new tail. Only a direct-matrix microkernel has an
allocated instruction model; it is not a linked implementation proof.

No new optimization ASM, timing, clean production, or upstream changes were
made. The tool compiles existing control ASM temporarily to anchor its model.

## Source and paper interpretation

The supplied `2026-1546-NTT-Yang.pdf`, §§6, 10 and 14, motivates comparing
twiddle configurations, composing the trinomial split with normalization, and
checking where unreduced additions occur. It does **not** establish our AVX2
chain counts or predict a cycle improvement. The constructions below are
derived from the actual Official constants and `wresident` mapping.

Executable source and results are in
`ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001/`:

- `tools/prove_yang_tail.py`
- `results/yang-tail-proof-20260922.json`

The JSON records source SHA-256, every physical lane's gauges, coefficients,
bounds, Montgomery words/companions, and the microkernel register allocation.

## Exact map, not a generic butterfly substitution

Work modulo q=3457. Gauge means `semantic value = g × stored value`; it is
distinct from the Montgomery exponent. Each encoded multiplier is
`center(f × 65536 mod q)`, so a Montgomery operation realizes multiplication
by semantic f without an extra R exponent.

For cohort i=0..7 and lane 0..15 the actual six source vectors are:

```text
upper triple: i, i+8,  i+16
lower triple: i+24, i+32, i+40
```

Keep the existing relative normalization to a common lane gauge g. Each
triple then computes, before alpha:

```text
T  = omega × (Y-Z)
S0 = Barrett(X+Y+Z)
S1 = X-Y-T
S2 = X-Z+T
```

Alpha factors are `a=(1,867,1520)` for the upper triple and
`b=(1,3091,2590)` for the lower triple. For degree j, the semantic inputs to
the final map are `U=g*a[j]*Su`, `V=g*b[j]*Sv`.

The exact Official final map, with phi=1634 and n=2646, is:

```text
T     = phi × (U-V)
upper = n × (U+V-T)
lower = 2*n × T
```

The subtraction of T in the upper output is essential. Replacing this with
an ordinary sum/difference butterfly would prove the wrong transform.

### Candidate A: direct composed matrix

For j=1,2:

```text
upper = Mont(Su, n*g*(1-phi)*a) + Mont(Sv, n*g*(1+phi)*b)
lower = Mont(Su, 2*n*g*phi*a)   + Mont(Sv, -2*n*g*phi*b)
```

Here `Mont(x,f)` denotes the existing Montgomery primitive with f encoded
as a Montgomery word. Four chains replace two alpha, one phi and two final
chains. There are 16 affected vector pairs: net **−16 chains**. Degree zero
retains its cheaper original three-chain map.

### Candidate B: factored composed map

For j=1,2:

```text
Vhat  = Mont(Sv, b/a)
T     = Mont(Su-Vhat, phi)
upper = Mont(Su+Vhat-T, n*g*a)
lower = Mont(T, 2*n*g*a)
```

This is also four chains, not five: two alpha operations become one relative
ratio, while common alpha is absorbed into final factors. Ratios are constant
within each degree group. It uses fewer constant operands than the direct
matrix, but has a tighter signed-range margin and a different dependency path.

## Comparable arithmetic and constant ledger

All counts below are model counts, not linked census or cycle estimates.
Table sizes refer to added candidate tables under the stated straightforward,
non-deduplicated policy, not all inherited rodata.

| Cost | Existing wresident | Direct matrix | Factored map |
|---|---:|---:|---:|
| CT prefix Montgomery | 78 | 78 | 78 |
| Pre-radix3 relative normalization | 40 | 40 | 40 |
| Complete inverse Montgomery | 238 | 222 | 222 |
| Barrett vectors | 40 | 40 | 40 |
| Modeled added tables, bytes | 11264 | 15360 | 13344 |
| Tail constant operands, excluding q/v | 124 | 244 | 184 |

Existing total = 78+40+16 omega+32 alpha+24 phi+48 final = 238.
The historical **118** count covers only `78+40`; it is not the full inverse
total. This ledger must not be compared with that partial count.

Direct matrix adds 4096 table bytes and 120 constant operands. Factored map
adds 2080 bytes (including an aligned 32-byte ratio block) and 60 operands.
The factored count assumes public degree-group traversal with ratio and phi
resident; full loop allocation/address overhead remains to be lowered.
Neither table estimate is a lower bound; deduplication may trade footprint
against addressing and reloads. A memory operand still performs a load.

The new mechanism does not eliminate the pre-radix3 40-chain gauge repair,
add a routing network, or remove a materialization pass. New loop/address and
register costs must be verified before any machine comparison.

## Proof and machine anchor

The inherited repaired-prefix contract is **input magnitude ≤7644**. It is
conditional: this gate does not prove that every real BaseMulScale output
satisfies it. Prefix bounds are conservatively propagated per vector and
then refined by lane constants at the tail.

- 768 basis columns establish the six-input linear maps modulo q across all
  physical lanes. Exact Montgomery residue semantics connect machine-style
  multiplication to those linear maps.
- 18,048 six-input tests cover signed basis, all 64 sign corners and random
  points per lane. These validate the simulator; tests alone are not range proof.
- Interval propagation checks pre-add/sub signed-i16 bounds, separately from
  intentional Montgomery low-word wrap. Direct-map maximum is 27893 and
  output envelope ±4288; factored-map maximum is 31802.
- 784 full inverse cases (768 basis +16 random) match the unchanged linked
  `wresident` ASM **raw exactly** for the control simulator. Both new model
  variants match its residues and exact subsequent `crepmod3` output.
- Existing linked `crepmod3` is exhaustively checked on all 8577 words of
  the new ±4288 envelope against centered-equivalent inputs.

New variants are not expected to reproduce the control's lazy representatives.
The proof does not insert reductions to force raw equality.

## Decision and remaining work

**Algebraic chain elimination: established. Conditional tail range: passed.
Complete caller range and new linked feasibility: not established. Performance:
unmeasured.**

The factored map is the more economical constant-policy candidate, but is not
declared faster. Before recommending ASM:

1. Close the real BaseMulScale output contract into the fixed CT prefix.
2. Lower the complete radix-3 / level-0 loop, including constants, memory
   ownership and public degree traversal; replay def/use and last-use ≤16 YMM.
3. Reconcile the model constant ledger with that concrete schedule. Keep the
   direct matrix as a proof/control alternative rather than silently combining
   its range margin with the factored map's constant count.

Reproduce from the experiment directory:

```sh
python3 tools/prove_yang_tail.py
sha256sum results/yang-tail-proof-20260922.json
```

The generator has a fixed seed and no timestamp or temporary-path metadata.
It requires Python, an AVX2-capable host, and a C compiler for the unchanged
ASM anchor. This is a correctness run, not a benchmark.

## Caller closure and complete tail schedule follow-up

Reproducer: `tools/close_yang_contract.py`; artifact:
`results/yang-closure-schedule-20260923.json` (campaign identifier).
No optimization ASM is generated or assembled. Existing Official ASM is
compiled as an independent anchor only.

### 1. Real BaseMulScale → CT prefix contract

The actual Decap caller first decodes/validates `c`, `f`, and `hinv`, then
calls `poly_basemul_scale(&m,&c,&f)`. Every stored decoder word is masked to
12 bits; its unsigned max tree includes all eight output vectors per block.
Because values are at most 4095, the signed comparison to 3456 is also a
valid nonnegative comparison. Mismatch accumulates across all six blocks.
Therefore reaching BaseMulScale implies **both operands are in [0,3456]**,
including canonical ciphertexts or secret keys that later fail KEM checks.
Noncanonical encodings return before this arithmetic. No extra validation
pass, delayed validation or altered failure behavior is proposed.

The new tool interprets the actual `poly_basemul_scale` instruction stream,
including both positive/negative-zeta halves and all six loop iterations.
It propagates intervals through every signed high multiply/add/sub; low-word
products explicitly retain modular wrap semantics. No overflowing add/sub is
silently truncated. This is a source-instruction interval proof anchored to
machine differentials, not a theorem about arbitrary unvalidated input.

| Physical degree plane | Proven output interval |
|---|---:|
| c0 | [−3608,3791] |
| c1 | [−5285,5651] |
| c2 | [−6963,7512] |
| c3 | [−6912,7644] |

Consequently the existing **±7644 CT-prefix contract covers all accepted
decoder inputs**; no new repair is necessary. A decoded runtime product has
interval [−1728,1911], and c3 is a sum of four such products. The other three
planes also pass after the actual zeta operations are included.

The older abbreviated caller ledger incorrectly used a two-product zeta
bound for c0; c0 actually wraps **three** products. c1 wraps two, c2 one,
c3 none. That intermediate accounting is corrected here; it does not change
the valid global 7644 cap. This proof does not assert that the cap is tight
or that its extreme is attainable.

Validation:

- 1,152 dynamically expanded arithmetic instruction rows, each with 16-lane
  bounds and intentional-wrap labels.
- 1,003 full BaseMulScale vectors raw-exact against existing ASM and matched
  to independent quartic convolution modulo q with the R^-1 output scale.
- All 4,096 possible 12-bit values checked through existing decoder ASM;
  an additional 2,304 single-position q−1/q/4095 cases cover every wire slot.
- The existing 7644-prefix proof, its fixed repairs and tail proof are reused;
  recorded source hashes are checked to reject a stale tail dependency.

### 2. Complete loop/register/constant schedules

Both designs now have full radix-3 plus level-0 instruction models. The fixed
CT prefix is unchanged. All operations have SSA inputs, assigned physical
YMM destinations, last-use and live-set records. The executable interpreter
checks that physical-register replay agrees with SSA values. These are YMM
word operations; the ratio broadcast reads a duplicated-word **4-byte memory
operand**, not an assumed free XMM/YMM alias.

| Loop | Public trip count | Data ownership | Vector rows/iteration, matrix / factored |
|---|---:|---|---:|
| Upper radix-3 | 8 | (i,i+8,i+16) | 28 / 28 |
| Lower radix-3 | 8 | (i+24,i+32,i+40) | 32 / 32 |
| Level-0 j0 | 8 | (i,i+24) | 19 / 19 |
| Level-0 j1 | 8 | (i+8,i+32) | 22 / 23 |
| Level-0 j2 | 8 | (i+16,i+40) | 22 / 23 |

Each loop has one reusable register assignment: all eight expanded iterations
are checked to have identical opcode/register signatures, data cursor +32 B,
and the specified constant cursor stride (128/192/256 B). Loop constants
remain live through the backedge even if their last arithmetic use is earlier.
This avoids proving an unrolled schedule that cannot implement a compact loop.

GPR plan: copy original data base into caller-clobbered r8; each loop sets
rdi=data-group base, r9=end, r10=constant-group base. Its body ends with two
pointer adds, cmp, and public jb. Five loops total 40 iterations. Including
base capture, three setup instructions per loop and return gives **177 GPR /
control instructions** in this particular tail schedule. No secret-dependent
dispatch, callee-saved GPR or stack scratch is needed by the model.

The two radix-3 passes load their three inputs before any overwrite. The
level-0 passes load the paired upper/lower vectors before storing either
final result. Every memory read checks the expected `prefix → r3 → final`
version; all 48 slots end as final output. The original 1536-byte in-place
buffer is reused, and data loads/stores remain 96/96 across the two tail
passes. No extra array or new routing instruction is introduced.

| Complete modeled tail | Direct matrix | Factored |
|---|---:|---:|
| Peak live YMM, including constants | 10 | 10 |
| Tail / full inverse Montgomery chains | 144 / 222 | 144 / 222 |
| Tail Barrett vectors | 16 | 16 |
| Constant operands, including explicit q/v setup | 246 | 186 |
| Constant operands, excluding q/v | 244 | 184 |
| Modeled tail table storage including common constants | 7872 B | 5856 B |
| Max signed add/sub magnitude | 27891 | 31798 |
| Final output magnitude | 4286 | 2544 |

The full inverse retains 24 prefix Barrett vectors: total remains 40.
The fixed prefix may itself use more than ten YMM; **10 is the new tail peak,
not the entire inverse peak**. The full design stays within 16 using the
existing prefix and this independently allocated materialized tail boundary.

Both schedules explicitly pay six full-vector setup loads (q,v,omega and phi
companions); the factored version additionally pays four `vpbroadcastd` loads
for its two ratios. The four duplicated-word constants fit in one aligned
32-byte block. Other table entries and code labels are planned `.p2align 5`;
the in-place polynomial must be 32-byte aligned, as in the existing caller.
No q/v load is silently credited as reused from the prefix.

The 7872/5856 sizes include common q/v/omega/phi storage (192 B); they are not
the earlier full **added-table** figures. Subtract that common storage and
add the unchanged 7680-byte CT-prefix tables to recover 15360/13344 B.
The two constant accounting taxonomies therefore agree.

Range is replayed on these actual operation schedules. Existing Barrett
correlation is handled by exact local interval enumeration; intentional
Montgomery low-word wrap is distinct from forbidden signed add/sub overflow.
160 full-tail fixtures per variant include all 64 sign patterns of each
six-input cohort and random boundary-domain inputs. Physical-register
execution matches the prior algebraic model **raw exactly** for each variant.
The tighter final envelopes fit inside the preceding exhaustive ±4288
`crepmod3` check. No new reduction is inserted to obtain these proofs.

### Decision

The requested **caller range closure and complete model schedule gates pass**.
The factored map is the recommended first ASM realization because it offers
the same −16-chain algebraic credit with 60 fewer constant operands than the
matrix version. That is a candidate-selection trade-off, not a cycle forecast;
its serial dependency and smaller range margin remain relevant.

Remaining future gates are faithful namespaced ASM lowering, linked
instruction/constant/ABI/alias audits, machine differential and complete Decap
correctness, then component/caller pricing if authorized. No cycle benefit,
Native qualification or production readiness is established by this gate.

## Factored ASM and short pricing

The next authorized step faithfully lowered the factored schedule into
`asm/ntruplus768_officialopt_invntt_yang_factored.s`, generated by
`tools/generate_yang_factored.py`. The source-pinned wresident CT prefix is
unchanged except for symbol/table names. The tail uses precisely the closed
physical-register assignment and five compact public loops; no additional
arithmetic optimization, repair or layout change is introduced.

### Correctness and linked evidence

- 5,003 direct inverse and 1,003 BaseMulScale→inverse cases agree with
  Official residues and exact subsequent `crepmod3` outputs.
- 100 deterministic valid Decap, 100 tampered-CT and 100 invalid-SK cases
  have byte-exact results and matching return behavior against Official.
- 128 signed-corner cases exercise both ends of guard-page-protected buffers
  and check every accessible byte outside the in-place polynomial.
- 160 direct machine-tail cases match the closed factored model raw-exactly.
- C harness ASan/UBSan pass (host-restricted LeakSanitizer disabled). Guard
  pages and linked operands, not ASan, cover the ASM memory accesses.
- Every linked tail vector opcode, register operand, data/constant offset
  and RIP-relative constant target matches lowering; table bytes match exactly.
- No stack spill, call, internal `vzeroupper` or callee-saved GPR clobber.
  Entry and loop alignment are 32 bytes. Tail peak is 10 YMM; the retained
  prefix remains within its existing 16-YMM allocation.
- Generator rerun reproduces identical ASM bytes.

The new symbol is **2300 B**, versus wresident's historical 2290 B. Complete
inverse counts are **222 Montgomery chains and 40 Barrett vectors**. Private
constant storage is **13536 B**, versus wresident's 11264 B: **+2272 B**.
This exceeds the earlier +2080 B estimate by 192 B because faithful standalone
tail lowering also stores local copies of q/v/omega/phi constants. Those
copies and the explicit q/v reloads are counted, not silently treated as free
reuse from the prefix. Tail constant operands are 186 including q/v setup,
or 184 excluding it (the prior comparison taxonomy).

Artifacts: `results/yang-factored-{lowering,linked}.json` and
`results/yang-factored-disassembly.txt`. The numerical bound remains inherited
from the now-closed canonical BaseMulScale contract; none of these tests
authorizes arbitrary general-input inverse use.

### Matched cycle-counter results

CPU 1, performance governor, turbo disabled, normal placement / ASLR-on,
common O3GC, three fresh processes. Actual backend:
**`default-perfevent`**, reported 1.4 GHz; not labeled RDPMC.
The StQ implementation follows the pinned SUPERCOP `stq.h` definition.
Raw observations, source/ELF hashes, compiler recipe and sanitizer/build logs
are preserved per campaign. These are **SUPERCOP-derived diagnostics**, not
Native SUPERCOP KEM measurements.

Both complete-Decap arms use the same frozen caller-lazy Forward and caller
source. Only inverse is replaced. Inverse-only uses identical 16 banks of
canonical-input BaseMulScale outputs, reset outside timing. The two comparisons
have separate same-ELF images; their absolute values/deltas must not be added.

| Candidate − comparator | Inverse | Inverse + crepmod3 | Complete caller-lazy Decap |
|---|---:|---:|---:|
| Factored − Official GS | +17.80 (0/3) | +13.69 (0/3) | +52.25 (0/3) |
| Factored − wresident | +11.58 (0/3) | +3.41 (0/3) | +12.48 (1/3) |

Parentheses count favorable launches. Primary Official-GS StQ2 comparison:
inverse **973.54 → 991.34**; complete Decap **19230.41 → 19282.66**.
The direct wresident comparison is the incremental mechanism check: even
with 16 fewer Montgomery chains, this schedule is slower for inverse in all
three launches. Its complete-Decap deltas are +38.43, −28.34, +12.76, so the
full-caller incremental result is mixed rather than a stable win.

Raw campaigns:

- `results/yang-factored-vs-official-short-buildfix-20260923/`
- `results/yang-factored-vs-wresident-short-20260923/`

The earlier `yang-factored-vs-official-short-20260923/` directory contains
only a pre-timing check: benchmark compilation selected a reference header
before the AVX2 header. Include order was corrected before any cycle samples
were collected. It is not an additional performance campaign.

### Decision

**Algebraic chain elimination and faithful machine feasibility pass;
inverse/caller performance gate fails.** Stop this realization: no serious
campaign, Native installation or clean production change.

Concrete trade-offs are more constant operands, different finalizer reuse,
and the new relative-ratio→phi→final dependency. The short tests do not
isolate how many cycles each costs; they do not prove a cache bottleneck,
nor that CT is intrinsically inferior. The small text-size difference alone
is not an explanation. Any future attempt needs a new controlled mechanism,
not another placement search or a claim based on chain count.

Reproduce from the experiment directory:

```sh
python3 tools/generate_yang_factored.py
make check-yang
python3 tools/audit_yang_factored.py
ASAN_OPTIONS=detect_leaks=0 make BUILD=build_yang_san \
  CFLAGS='-O1 -g -mavx2 -fsanitize=address,undefined -fno-omit-frame-pointer -fwrapv' check-yang
python3 tools/run_yang_short.py --control official --tag NEW_UNIQUE_TAG
python3 tools/run_yang_short.py --control wresident --tag ANOTHER_UNIQUE_TAG
```

Timing runners refuse mismatched host controls and existing result paths.

## 222-chain scheduling and reduction audit

Reproduce with `python3 tools/audit_yang_followup.py` in the experiment.
The deterministic artifact is `results/yang-222-schedule-reduction-audit.json`.
This gate changes only research models/documentation: no new ASM, benchmark,
Native installation or production change. Existing dirty work is preserved.

### Schedule-only control: two independent pairs

Keep all 222 full-inverse Montgomery chains, all 40 Barrett vectors, every
constant byte and every data access. Within each level-0 degree group,
interleave the instruction streams of adjacent cohorts i and i+1. Each stream
retains its original SSA dependencies; the two streams use disjoint slots.
The two radix-3 loops remain unchanged. A compact level-0 body processes two
pairs, advances data by 64 bytes and constants by 256 bytes, and runs four
iterations. All four iterations have identical allocated register signatures.

| Model metric | Tested factored control | Two-pair schedule |
|---|---:|---:|
| Complete inverse Montgomery / Barrett | 222 / 40 | 222 / 40 |
| Tail peak YMM, constants included | 10 | 11 |
| Tail loop iterations | 40 | 28 |
| Four-instruction loop-control work | 160 | 112 |
| Constant operands / data traffic | unchanged | unchanged |

Physical-register execution matches the original factored model raw-exactly
on 160 signed-corner/random full-tail fixtures. Range replay passes at maximum
add/sub magnitude 31768. Unlike the old closure's per-vector-max collapse,
this follow-up retains the prefix's lane-specific bounds. The smaller bound
is a proof refinement, not a reduction-policy change.

This is a concrete independent-work/loop-control mechanism, not proof of
shorter hardware critical path. No linked allocation, encoding, ABI or cycle
claim is made. In particular, memory operands still load constants.

### Constant reuse: no duplicate finalizer vectors

All 96 finalizer constant vectors (word and QINV companion included) have
distinct contents. Simple table deduplication cannot restore the old
wresident three-degree sharing. Factoring alpha into the finalizer makes
the factors degree-dependent; a constant-resident implementation must count
its loading/addressing costs instead of claiming free reuse. This does not
rule out compressed tables or a different constant-generation mechanism,
but neither has an established 222-chain schedule here. The proposed paired
schedule claims zero constant-load savings.

### Reduction-only control: remove eight radix-3 S0 Barrett vectors

The existing inverse is already CT in its five radix-2 stages. Its remaining
40 standalone Barrett vectors consist of 24 prefix repairs and 16 radix-3
S0 reductions. The analysis starts with the previously closed canonical
BaseMulScale caller contract, using its conservative uniform ±7644 cap.
No arbitrary general-input inverse claim is made.

All 24 prefix sites were individually omitted and replayed through the
remaining fixed repairs and tail. None passes this interval certificate.
For example, omitting the first stage-4 A repair gives an add/sub bound of
33683. This is proof insufficiency, **not a reachable overflow witness**.
Further BaseMulScale correlations or tighter caller domains remain possible.

Each of the 16 radix-3 S0 reductions can individually be omitted, but the
16 omissions cannot be combined under this certificate. Level-0 pairs the
upper/lower S0 streams, so single-site success is not compositional. Omitting
both reductions of a pair yields a failing bound (first pair: ±33931).

Test both-removal for all eight independent S0 pairs; retain one reduction
per pair and verify the complete selected cover again. The compact selected
policy is:

```text
upper radix-3 S0: store X+Y+Z without its Barrett (8 removals)
lower radix-3 S0: retain the existing Barrett (8 retained)
CT prefix:        retain all 24 repairs
level-0/finalizer: retain all existing factored Montgomery arithmetic
```

Complete inverse: **222 Montgomery, 32 Barrett**, no replacement multiply,
new routing or scratch. This saves 24 vector arithmetic instructions in the
model. Every signed pre-operation passes; maximum add/sub magnitude is
32189 and final magnitude is 2547, inside the prior exhaustively checked
`crepmod3` ±4288 envelope. Low-word Montgomery wrap remains explicitly modeled
and is not used to mask overflowing add/sub. 160 signed-corner/random fixtures
match the unchanged control modulo q; raw representatives may differ.

The selected cover is maximal only for these independent S0 pairs under this
interval certificate. It is not a global reduction lower bound. No new ASM
differential, guard-page, KAT or performance evidence is claimed.

### Next machine arbitration

Keep the two changes separate initially: (1) 222/40 with two-pair scheduling,
(2) 222/32 with the original single-pair scheduling. Compare each against the
same factored control, then Official GS, with the established correctness and
cycle-counter gates. Do not combine their hypothetical credits or present
the model's smaller instruction count as a speed result.

## Combined two-pair / 32-Barrett ASM

The user explicitly authorized stacking the two changes before machine
pricing. New symbol: `ntruplus768_officialopt_invntt_yang_pair32`, generated by
`tools/generate_yang_pair32.py`. The original factored symbol remains intact.
The combined model is reallocated and range-checked after removing the upper
radix-3's eight S0 Barrett blocks; no separate-candidate performance results
are assumed or added. Prefix arithmetic, factors, layout and output scale
remain unchanged. This is a caller-bounded research inverse, not a general
signed-i16 inverse or a clean implementation.

### Actual machine differences

| Metric | Original factored | Combined pair32 |
|---|---:|---:|
| Full inverse Montgomery chains | 222 | 222 |
| Full inverse Barrett vectors | 40 | 32 |
| Tail peak allocated YMM | 10 | 11 |
| Tail loop iterations | 40 | 28 |
| Function text bytes | 2300 | 2692 |
| Private constant bytes | 13536 | 13536 |

The unchanged CT prefix still has its existing ≤16-YMM allocation. Upper
radix-3 now stores unreduced S0; lower radix-3 retains reduction. Each of the
three level-0 loops processes two independent pairs per iteration, with data
stride 64 and constant stride 256 bytes, for four iterations. The two radix-3
loops still execute eight iterations. There are 24 fewer vector arithmetic
instructions and 48 fewer loop-body GPR/control instructions per inverse;
this is not a cycle estimate. Constant operands and data loads/stores are
unchanged. The +392-byte text cost comes with the wider loop bodies and
alignment; no instruction-cache conclusion follows.

Linked audit expands actual backward loops and counts 444 `vpmulhw` (two per
Montgomery chain) and 32 `vpmulhrsw`. Every tail vector register/memory operand
and constant target matches the allocated instruction model; table bytes
match exactly. Every loop body has a stable register/address signature across
all its iterations. Entry, loop labels and tables are 32-byte aligned.
There are no stack references, calls, `vzeroupper`, or callee-saved GPR writes.
All branches are fixed public loop controls; data/constant addresses depend
only on public cursors. This is a code/def-use audit, not a universal formal
side-channel proof.

### Combined proof and validation

The combined signed add/sub envelope remains ±32189; final output is within
±2547 and the prior exhaustive `crepmod3` contract. Prefix input remains the
closed canonical-BaseMulScale ±7644 envelope. Montgomery low-word wrap and
illegal signed add/sub overflow remain distinct in the executable model.

- 160 combined model fixtures agree with the control modulo q.
- 160 direct machine-tail fixtures match the combined allocated model raw-exactly.
- 5,003 direct inverse and 1,003 BaseMulScale→inverse cases match Official
  residues and exact subsequent `crepmod3` output.
- 100 valid Decap vectors, 100 tampered CT cases and 100 invalid SK cases
  match Official return behavior and output bytes. The research Decap uses
  frozen caller-lazy Forward, with only its inverse changed.
- 128 signed-corner guard-page/canary cases check the in-place polynomial
  at both ends of a protected page. No extra buffer or changed alias API.
- C harness ASan/UBSan pass; host-restricted LeakSanitizer is disabled.
  Assembly memory evidence is the separate guard-page/canary/operand audit.
- Regeneration reproduces identical ASM and lowering JSON hashes.

Reproduce from the experiment directory:

```sh
python3 tools/generate_yang_pair32.py
make check-yang-pair32
python3 tools/audit_yang_pair32.py
python3 tools/validate_yang_pair32.py
```

The final command also runs the sanitizer build and saves command output,
compiler identity, source/ELF hashes and reproducibility evidence. Artifacts:
`results/yang-pair32-{lowering,linked,validation}.json` and
`results/yang-pair32-disassembly.txt`. Lowering includes the full combined
range, instruction, liveness and physical-register records.

Decision: **combined semantic/range and linked feasibility gates pass**.
No cycle benchmark, serious campaign, Native installation or production
promotion was performed. The next performance question is the combined
candidate versus the frozen factored control and Official GS on matched
inverse / inverse+crepmod3 / complete-Decap boundaries.

## Combined pair32 short pricing

The authorized three-region test ran serially in two separate same-ELF
campaigns. CPU 1, performance governor, turbo disabled, normal placement /
ASLR-on were checked before launches; no host controls were changed. Each
comparison used three fresh processes, 16 matched banks, eight balanced
blocks and 64 observations per arm/block/region. Reset and preflight are
outside timing. Counter identity was `default-perfevent`, reporting
1400000000 per second, not RDPMC. StQ follows pinned SUPERCOP `stq.h`.
These are SUPERCOP-derived diagnostics, not Native SUPERCOP results.

Correctness, sanitizer and linked audit were rerun before timing. Both
complete-Decap arms retain frozen caller-lazy Forward and the same caller;
only the inverse differs. Thus "Official GS" identifies the inverse control,
not an unmodified Official full-KEM implementation.

| Region | Factored StQ2 | Pair32 StQ2 | Delta (wins) |
|---|---:|---:|---:|
| Inverse | 991.14 | 980.75 | −10.39 (3/3) |
| Inverse + crepmod3 | 1173.95 | 1168.67 | −5.29 (3/3) |
| Complete caller-lazy Decap | 19338.82 | 19328.43 | −10.39 (2/3) |

Inverse launch deltas: −11.3984, −10.0234, −9.6719. Full-Decap deltas:
−14.5703, −3.2031, +6.1250. The full caller is mixed despite the favorable
pooled StQ2; it is not a stable full-caller win.

| Region | Official GS StQ2 | Pair32 StQ2 | Delta (wins) |
|---|---:|---:|---:|
| Inverse | 973.26 | 981.88 | +8.63 (0/3) |
| Inverse + crepmod3 | 1163.64 | 1167.34 | +3.70 (0/3) |
| Complete caller-lazy Decap | 19166.73 | 19196.09 | +29.36 (0/3) |

Inverse launch deltas: +9.8750, +9.5703, +6.9531. Full-Decap deltas:
+33.8984, +13.8125, +45.9531. Do not combine absolute cycles or deltas across
these two linked images, or subtract historical campaigns to infer a gain.

The +392 B text did **not cancel all local benefit** of the combined change:
pair32 consistently improves on factored inverse in this diagnostic. It does
not prove that code expansion has no cost, or isolate that cost from the
eight removed reductions and interleaving. No code-size-only control was
run, and no instruction-cache bottleneck is asserted. The unchanged 13536 B
private constants and constant operand count remain paid. This combined
realization still does not beat Official GS or pass the full-caller gate.

Decision: preserve the local improvement, but **no serious, Native or clean
promotion**. Any further candidate requires a new mechanism rather than a
placement search. Reproduction (use fresh tags; runner refuses overwrite):

```sh
python3 tools/run_yang_short.py --candidate pair32 --control factored --tag NEW_FACTORED_TAG
python3 tools/run_yang_short.py --candidate pair32 --control official --tag NEW_OFFICIAL_TAG
```

Raw StQ1/2/3, per-launch observations, preflight, source/ELF hashes, compiler
recipes, disassembly and host metadata are retained in
`results/yang-pair32-vs-factored-short-20260923/` and
`results/yang-pair32-vs-official-short-20260923/`.

## Constant reuse and relative-gauge follow-up

This is a source/executable-model investigation, **not a new linked ASM or
cycle measurement**. Reproduce with
`python3 tools/research_yang_constant_reuse.py` from the experiment directory;
the complete ownership, operation, bound and constant census is saved in
`results/yang-constant-reuse-research.json`.

The most local opportunity is in CT stage 5. Its third and fourth butterfly
pairs use byte-identical `(word, qinv)` constant vectors in each of six
packets. The current pair32 source loads both pairs separately into `ymm15`
and `ymm2`, with no intervening write to either register. Reusing the first
pair removes **two constant-vector loads per packet, 12 per inverse**. This
changes neither multiplication count, range, layout nor register count. The
source def/use and constant-byte checks pass; an edited linked object and
cycle result do not yet exist.

Across packets, all four CT-prefix factor vectors at a given stage repeat.
The current prefix table allocates 7,680 bytes, whereas its nonidentity
factor-vector census contains only 11 distinct `(word, qinv)` pairs (704 bytes
in a simple deduplicated table). This is a *table-footprint* opportunity, not
an automatic runtime-load saving: addressing changes and a real linked
schedule must be priced. Keeping all factors resident is also not established
under the 16-YMM limit.

The upper and lower level-0 finalizer constants satisfy
`K_lower = 2 K_upper (mod q)`. An executable alternative computes the same
Montgomery product with `K_upper` and doubles the lower result. It passes 160
residue fixtures, has a proved signed-add/sub envelope of ±32,189 and a final
bound of ±3,586, inside the established `crepmod3` input contract. It could
halve 96 finalizer constant vectors to 48 (1,536 table bytes), but the modeled
tail exchanges 48 constant-memory operands for **48 explicit vector loads
plus 24 adds**; peak YMM rises from 11 to 15. Montgomery remains 222 and
Barrett remains 32 for the full inverse, while modeled tail instruction rows
rise 986→1,058. Thus this is constant *relocation/compression*, not a proven
machine improvement; the longer lower-result dependency and tight register
budget make it a poor first ASM target without measured constant-footprint
pressure. Raw representatives differ, so only residue and downstream wire
contracts would be required of an eventual ASM version.

Finally, under the **fixed current radix-3 formulas** and whole-vector gauge
normalizations, choosing separate upper/lower gauge anchors cannot remove
relative normalization chains. The current allocation is 40 pre-radix-3 plus
16 post-radix-3 chains = 56. Exhaustive anchor enumeration over eight cohorts
finds a minimum of seven per cohort: alternatives trade 5+2 for 4+3, still
56. Each triple has distinct source gauges; at least four pre-normalizations
are needed. The three upper/lower output-gauge ratios are distinct, so at
most one of three post comparisons can be an identity; enumerating all
potential 4- and 5-pre anchors closes the below-seven cases. This is a
restricted-family result, **not a global inverse arithmetic lower bound**.
Actually eliminating these chains requires changing the radix-3 linear map,
normalization placement or terminal scale together, with fresh range and
constant-economics proof.

Decision: the stage-5 12-load reuse is the narrow, low-risk next machine
prototype. Prefix-table deduplication deserves a separate footprint experiment
only if linked constants/frontend evidence warrants it. Do not promote the
shared-finalizer model or claim a cycle gain from it; do not reopen the same
gauge-anchor search expecting fewer chains without a new radix-3 mechanism.

### Stage-5 constant-residency ASM and short pricing

The narrow prototype is now a namespaced function,
`ntruplus768_officialopt_invntt_yang_stage5reuse`, generated from SHA-pinned
`yang_pair32`. It retains the first stage-5 `(word,qinv)` pair in `ymm15/ymm2`
for the next butterfly instead of loading its byte-identical copy. It does
not change arithmetic, twiddle values, range, ownership, output scale or any
other inverse stage.

The linked same-ELF audit verifies **two fewer stage-5 loads × six public
loop iterations = 12 fewer dynamic constant-vector loads per inverse**.
All other vector opcodes and YMM def/use match; the entire stage-5 tables are
byte-identical. Both entries and tables are 32-byte aligned; there are no
stack references, calls, `vzeroupper` or new branches. The inverse function
remains 2,692 bytes because alignment padding absorbs the removed load
encodings. Thus this is a load-reuse candidate, not a code-size gain.

It passes 5,003 raw bit-exact/canary cases against pair32; separately, 5,003
direct inverse and 1,003 BaseMulScale→inverse cases match Official residues
and exact `crepmod3`. One hundred valid Decap, 100 tampered CT and 100 invalid
SK cases are byte-exact, as are 128 guard-page signed-corner cases. C harness
ASan/UBSan passes with host-restricted LeakSanitizer disabled. Regeneration
reproduces the candidate source hash. The source-only constant/liveness
argument is complemented by the linked opcode/table audit; these tests are
not a universal formal side-channel proof.

Three SUPERCOP-derived same-ELF short campaigns used the pinned `cpucycles()`
backend `default-perfevent` (1.4 GHz reported rate), CPU 1, performance
governor and disabled turbo. Normal/ASLR-on was the initial setting, with
three fresh processes and balanced observations; a second independent
normal campaign checked stability. The reversed campaign swaps link order
of the two inverse implementations and consequently changes other symbol
placement as well. It is a placement-sensitivity control, **not** a pure
inverse-placement experiment. Candidate minus pair32 pooled StQ2 cycles:

| Campaign | Inverse | Inverse+crepmod3 | Complete caller-lazy Decap |
|---|---:|---:|---:|
| Normal A | +0.64 (1/3 favorable) | −0.74 (3/3) | −54.02 (3/3) |
| Normal confirmation | −0.97 (2/3) | −1.55 (2/3) | −74.14 (3/3) |
| Reversed | −2.18 (3/3) | −1.42 (3/3) | +98.10 (0/3) |

The isolated inverse result is small and mixed across normal launches; the
large complete-Decap delta reverses with image placement. These observations
**do not show that deleting 12 loads saves 54–74 caller cycles**. They show a
valid structural optimization whose cycle credit is at or near diagnostic
noise in the isolated kernel, plus substantial linked-image sensitivity in
the caller. No nine-process serious, Native SUPERCOP or clean-production
promotion is justified. In particular, pair32 itself still loses to the
Official GS inverse in its earlier same-ELF comparison.

Reproduce from the experiment directory:

```sh
python3 tools/generate_yang_stage5reuse.py
make check-yang-stage5reuse
python3 tools/audit_yang_stage5reuse.py
python3 tools/run_yang_short.py --candidate stage5reuse --control pair32 --tag NEW_NORMAL_TAG
python3 tools/run_yang_short.py --candidate stage5reuse --control pair32 --reversed-placement --tag NEW_REVERSED_TAG
```

The three original campaigns, including raw observations, source manifests,
saved ELFs, sanitizer logs and backend identity, are in
`results/yang-stage5reuse-vs-pair32-{short,confirm,reversed}-20260923/`.
Structural evidence is in `results/yang-stage5reuse-{generation,linked}.json`.

### Batched-cycle method pilot

The new local batch engine follows mlkem-native's 50 warm-ups, 300 consecutive
operations and 20 separately reset tests, using the pinned SUPERCOP
`cpucycles()` backend for this machine. It alternates A/B order by test and
reports the upper median batch total divided by 300. This is a **different
measurement contract** from the earlier per-operation StQ short test.
The inverse region necessarily includes a 1,536-byte input copy on every
iteration, so it is labeled `copy_plus_inverse`.

Three fresh-process pilot comparisons of stage5reuse minus pair32 found a
median launch delta of −2.28 cycles for `copy_plus_inverse` (2/3 favorable)
and −110.94 for complete Decap (3/3) in normal/ASLR-on placement. With
reversed source/link order, the corresponding values were +0.57 (1/3) and
−35.24 (2/3). This is **not** a Native SUPERCOP or serious nine-process
claim, and the large Decap change remains sensitive to image placement.
The independent prior per-operation campaign even reversed its Decap sign
under the reversed image; these unlike estimators must not be merged.

The reusable method, input-reset rule and exact commands are in
`bench/mlkem-batch.md`. Raw totals, ELFs, backend/host metadata and source
hashes are in `results/yang-stage5reuse-mlkem-batch{,-reversed}-20260923/`.

### Same-size, fixed-relative-layout A/B

The earlier placement ambiguity motivated a stricter qualification-only
comparison. Both ASM sources were generated under the **same symbol and table
names** and linked into separate, otherwise identical ELFs. No unreachable
padding had to be added: pair32 and stage5reuse already occupy 2,692 bytes
each after assembler alignment. The linked audit found the inverse at the
same relative address (`0xe700`) in both images; every sized symbol has the
same address and size; `.text` outside the inverse is byte-identical, as is
the complete 18,848-byte `.rodata`. The inverse itself differs in 631 encoded
bytes because removing two loads also changes branch encodings/offsets; the
generated source comparison proves the only *source instruction* difference
is those two stage-5 loads. This controls relative caller and constant
placement, not every microarchitectural condition.

Using the pinned SUPERCOP `cpucycles()` backend `default-perfevent`, the
50/300/20 batch contract and balanced ABBA/BAAB order, each campaign ran
10 blocks = 20 fresh processes per variant. Each block delta is the mean of
its two candidate process medians minus the mean of its two control process
medians; the reported headline is the median across the 10 block deltas.
Negative favors stage5reuse. `copy_plus_inverse` includes the required input
copy, not an isolated destructive inverse invocation.

| Per-process ASLR | copy+inverse delta | favorable blocks | complete Decap delta | favorable blocks |
|---|---:|---:|---:|---:|
| On | −0.56 cycles (bootstrap 95% block-median CI −1.28..+0.97) | 6/10 | −7.66 (−33.79..+42.12) | 6/10 |
| Off (`setarch -R`) | +0.60 (−1.16..+1.21) | 3/10 | +5.11 (−12.99..+21.71) | 4/10 |

The intervals are descriptive bootstrap intervals over only ten blocks, not
a formal hardware-performance guarantee. With ASLR off, the process
personality was verified as `00040000`; CPU 1 remained on `performance` with
turbo disabled. Neither campaign supports a caller-level win. The local
inverse effect is about zero or slightly adverse under these batch contracts.
Thus the previous normal/reversed full-Decap direction should **not** be
promoted as a reliable effect of deleting 12 loads. The structural change is
real, but current evidence favors leaving pair32 as the research control and
not promoting stage5reuse to Native or clean production. This does not prove
the two functions are cycle-identical on every AVX2 CPU.

Reproduce from the experiment directory:

```sh
python3 tools/generate_yang_fixed_layout.py
make build/bench_yang_fixed_control build/bench_yang_fixed_candidate
python3 tools/audit_yang_fixed_layout.py
python3 tools/run_yang_fixed_layout.py --tag NEW_ASLR_ON --blocks 10
python3 tools/run_yang_fixed_layout.py --tag NEW_ASLR_OFF --blocks 10 --aslr off
```

The two campaigns and all 80 process outputs, batch totals, saved ELFs,
source hashes, symbol audit and estimator details are in
`results/yang-fixed-layout-upper{,-aslr-off}-20260923/`. The earlier
`yang-fixed-layout{,-aslr-off}-20260923/` pilot used the mean of the two
middle batch totals in the outer runner, not the batch engine's upper
median; its raw data are retained but its summaries are superseded. This is a
SUPERCOP-derived component/caller diagnostic, not Native SUPERCOP.

## Gauge-aware radix-3 / joint twisted-tower gate (2026-09-23)

This is an **exact modular search gate**, not a new ASM or cycle result.
Reproduce from the experiment directory with:

```sh
python3 tools/research_yang_tower_gate.py
python3 tools/research_yang_joint_gauge.py
python3 tools/prove_yang_gauge_consumer.py
python3 tools/probe_yang_full_tower.py
```

The machine-readable artifacts are `results/yang-joint-tower-gate-20260923.json`,
`results/yang-joint-gauge-ancestry-20260923.json`, and
`results/yang-gauge-consumer-contract-20260923.json`, plus the linked Official
`results/yang-official-full-tower-basis-20260923.json`; they include source
SHA-256s. The fixed Yang PDF SHA-256 is
`cd89fef7848f172a1cb2e72fdfb6f8e0bf12959f6519e93fce4aaf281ac2f42f`.

### A. What the fixed CT prefix permits

Each radix-3 triple has gauges `(g, gc, gc²)`: all 256 physical
cohort/half/lane triples satisfy the geometric relation. Yet only 8/256
have `c³ = 1`. The actual three-output map is the 3-point DFT with
`ω = 2734 mod 3457`; its exact matrix and the subsequent trinomial
level-0/final scale were independently reconstructed from basis columns and
checked with random vectors for all 128 lanes of eight cohorts.

For a fixed prefix, moving the twist solely to the three radix-3 outputs
would require `F3·diag(1,c,c²) = D·P·F3`, with `D` diagonal and `P` an output
permutation. Comparing the first output row proves `c` must be a cubic root
of unity. The 248 other triples therefore cannot use that simple GS output
rescaling. This is an exact semantic failure, not a range or register issue.

| Full-inverse tail construction | Vector Montgomery chains after 78-chain prefix | Meaning |
| --- | ---: | --- |
| Existing `stage5reuse` factored tail | 144 | Linked research control; includes 40 pre-radix-3 relative chains and 16 post-radix-3 corrections. |
| Direct six-input/six-output coefficient expansion | 288 | Exact independent matrix oracle; deletes named normalization but doubles tail multiply count. No ASM selection. |

A naive direct three-output DFT expansion already needs 144 coefficient-vector
products before level-0, versus 56 chains for the current pre-normalization
plus `ω` stage. The 288-chain full matrix is a valid construction, **not a
lower bound** on every possible factorization. No new CT/GS factorization
with a better complete dependency/movement budget was established here, so A
has no qualifying ASM prototype or timing result. Changing the CT prefix
itself remains the real open freedom.

### B. Can a materialized input gauge repair the CT prefix?

The linked Official functions establish the current scale anchor:
`poly_invntt_scale(poly_ntt(e_i)) = 3310·e_i = R·e_i (mod 3457)` for all
768 coefficient basis vectors, with 100 additional random `[-1,1]` cases.
The inverse entry is scaled for its real BaseMulScale input; a proposed joint
tower must account for this `R` exponent, not merely match a permutation.

The new ancestry model tracks each of the 48×16 CT-prefix outputs as
`fixed_factor × H[input_ancestor]` for arbitrary nonzero per-position input
gauge `H`. It agrees with 32 independent random-gauge replays of the existing
five-stage model. Equal-gauge constraints across both radix-3 triples are
inconsistent. A short witness uses cohort 0: lane 0 has ancestors
`(0,128,256)` with factors `(1,1,1)`, demanding their `H` values be equal;
lane 4 uses the **same** ancestors with factors `(1100,1282,765)`, demanding
different ratios. No choice of `H` satisfies both. The solver records 496
contradictions across 512 triple-equality constraints. This closes only
"same CT prefix + arbitrary diagonal input reweighting + common triple
gauge". A changed prefix/tower is not covered.

The present CT-prefix gauge is an **inverse-side intermediate**, not a valid
Forward output ABI. As a warning about blindly carrying it into quartic
arithmetic, 744/768 entries are nonidentity, and 0/192 current quartic leaf
groups have one gauge shared by all four degrees. The independent consumer
identity for a materialized diagonal gauge is

```text
stored_c[o] = sum_{i+k mod 4=o}
              stored_a[i] stored_b[k] · Ga[i] Gb[k] / Gc[o]
              · lambda^(i+k>=4)                         (mod q)
```

It was checked for all 192 Official quartic factors and 1,536 deterministic
cases. A uniform per-leaf scalar gauge contributes one common correction;
a general degree-dependent gauge gives separate product coefficients, so a
mere λ-table change is insufficient. Real AVX2 BaseMul additionally applies
its Montgomery `R⁻¹` factor and finalizer. This identity is a consumer
contract, **not** evidence that the current CT-prefix gauge can be exposed
at the Forward boundary.

No B ASM is selected: the searched input-only reweighting is inconsistent,
and a valid paired Forward/inverse tower with complete BaseInv/BaseMul/codec
schedule has not yet been derived. Keygen, Encap, and Decap must all be
accounted for before promoting such an ABI; Encap has no inverse call.
Consequently there is no new short benchmark or Native result from this gate.
The next mathematical search must alter prefix butterfly constants or
orientation together with Forward's tower and then price every materialized
consumer conversion. The findings here do not rule out that wider search.

## Full factor-tree paired-tower screen (2026-09-23)

This is the next, wider **mathematical** gate. It does not turn the preceding
intermediate CT-prefix gauges into a materialized Forward ABI. Reproduce in
order from the experiment directory:

```sh
python3 tools/research_full_twisted_tower.py
python3 tools/research_full_twisted_pairings.py
python3 tools/research_full_twisted_consumers.py
python3 tools/research_yang_true_twist.py
python3 tools/research_yang_true_twist_range_screen.py
```

The first three JSON artifacts are `results/yang-full-twisted-tower-{factor,pairings,consumers}-20260923.json`;
the actual variable-twist model and first range screen are
`results/yang-true-y-twist-{pairings,range-screen}-20260923.json`.
They include source hashes and the complete physical cell→leaf→quartic-degree
map. No source under `upstream/supercop-avx2/`, clean production, or the pinned
SUPERCOP tree was changed.

### Exact factor, scale, and physical ownership

With `y=x⁴`, the ring polynomial is `P(y)=y¹⁹²−y⁹⁶+1`. The two first
`y⁹⁶−c` factors have `c=723,2735` modulo 3457. Each splits into three
`y³²−c` factors and then five binary layers, yielding 192 distinct
`y−λ` leaves / `x⁴−λ` quartics. The artifact records every factor constant
at each level and all 768 physical cells. For Official `poly_ntt`, the value
at the cell owned by `(λ, degree j)` is precisely

```text
sum_{k=0}^{191} a[4k+j] · λ^k  (mod 3457).
```

The materialized Forward scale is **1** at all 768 cells. This was checked
against linked Official ASM on **all 768 coefficient bases** using an
independent direct-remainder oracle. Conversely, every physical input basis
to linked `poly_invntt_scale` agrees with the independent Lagrange/CRT
polynomial, multiplied by `R=65536 mod 3457=3310`. Thus this paired function
contract is `I(F(a))=R·a`, not unscaled identity. One hundred random small
polynomials also pass. This proves the scalar factor map and ownership; it
does **not** prove a new AVX2 orientation, signed range, or timing.

### Rejected fixed-factor gauge-conjugate surrogate

This first executable comparison is **not Yang's true variable-twisted
tower**. It retains the physical factor tree at every intermediate node and
tries to force GS butterflies by diagonal gauge conjugation. We keep it as a
negative control precisely because it exposes a tempting but costly shortcut.
The top trinomial and radix-3 remainder maps stay exact. At a split with child
constants `±a`, plain CT Forward produces

```text
u=A+aB,  v=A−aB.
```

The explicit twisted GS realization first forms `B'=aB`, then emits
`S=A+B'=u`, `D=a(A−B')=a·v`. Its lower child carries gauge `a`.
The paired CT-type inverse consumes `(S,D)` by computing
`A=(S+D/a)/2`, `B=(S−D/a)/(2a)`. Gauge and Montgomery exponent are distinct:
at a materialized leaf here `raw=G_λ·semantic`, while `e=0` stays fixed.

Within this surrogate, both the plain/plain and gauged/gauged scalar towers satisfy `R·Id`
on all 768 bases and 100 random small polynomials. The two crossed pairings
do **not** satisfy the caller contract without a leaf-gauge adapter; with
the exact adapter, both close on the same tests. Of the 192 leaves, 186 have
`G_λ≠1`; each leaf has **one common gauge for all four quartic degrees**.
An unabsorbed full-state adapter therefore touches 744 coefficients. This
is materially different from the earlier degree-dependent inverse-prefix
gauge, which was not a Forward ABI.

| Explicit scalar radix-2 work per transform, four degree columns | Plain | Twisted |
| --- | ---: | ---: |
| Forward fixed multiplications | 1,920 | 3,840 = 1,920 high preweights + 1,920 GS output twiddles |
| Inverse fixed multiplications | 1,920 | 3,840 = 1,920 input untwists + 1,920 high unweights |

These are scalar-model operations, **not AVX2 instruction or cycle counts**.
An optimized radix-3 or earlier-stage constant could in principle absorb
some preweights. This concrete realization has **not** demonstrated that
absorption; counting a moved multiply as eliminated would be wrong.

The first binary stage exposes a more specific obstruction to a *trivial*
radix-3 table edit. Under the two `y⁹⁶` factors, the three radix-3 output
polynomials need high-half preweights `(886,147,1033)` and
`(682,1510,1265)`, respectively. Within each triple they are different.
Scaling those output rows changes the radix-3 matrix's **A-column** from
`(1,1,1)` to those three constants; it cannot be achieved merely by
replacing the existing B/C twiddles while leaving the A contribution free.
The JSON records all six exact rows. This does not prove a lower bound for a
new shared radix-3 algorithm, but it identifies precisely where a joint
schedule must find its credit.

### Surrogate caller-gauge obligations

For one quartic with scalar gauges, the raw product must be corrected by
`G_c/(G_a G_b)` times the ordinary quartic product (with the same `λ`).
The model checks this for all 192 actual leaves and 1,536 deterministic
quartic cases. In Decap's existing plain wire ABI, a twisted state imposes:

| Boundary | Required scalar gauge factor if not absorbed by an existing operation |
| --- | --- |
| decoded `c,f` → BaseMulScale → twisted inverse | `G` on product output |
| message twisted Forward → recovery BaseMul with plain `hinv` → hash bytes | `G⁻¹` on recovery product |
| regenerated-r twisted Forward → equality serialization | `G⁻¹` before wire bytes |

The paired inverse returns ordinary coefficient-domain data, so crepmod3
needs no new gauge in this exact model. Encap could keep `h` plain and both
`r,m,c` twisted through multiplication/addition, but both r-hash and
ciphertext serializers would need `G⁻¹`. Keygen's BaseInv can algebraically
return reciprocal leaf gauge, but its actual scale, range, retry, and SK
serialization remain separate machine contracts. None of these adapters or
consumer helpers has been implemented or priced as AVX2 instructions.

### The actual y-variable twisted tower

Yang §4–§6 and §9 distinguish the above surrogate from a genuine twist:
the variable substitution is performed on the **complete** `y=x⁴` tower,
never on the retained `x` degree. At each `y³²−α` node choose a 32nd root
`ξ` of `α`, substitute `y=ξz`, and work in `z³²−1`. At each binary split,
the upper child is `(A+B)`; the lower `(A−B)` is twisted by powers of a
primitive root of the current node size. At a linear y-leaf, the accumulated
substitution yields exactly the original `λ`. There is **no terminal leaf
gauge** and no codec/consumer adapter. The inverse uses the reciprocal
untwist before its CT merge, with the same total `R` scale as Official.

The executable scalar model independently checked all 768 bases and 100
small random inputs. The twisted Forward equals the direct remainder oracle
at every `(λ,degree)` cell; the twisted inverse composes to `R·Id`.
Plain and true-twisted leaves therefore have the same materialized Official
ABI. All four plain/twisted Forward–inverse pairings are checked without an
adapter. This is **not** true of the fixed-factor surrogate above.

| Fixed scalar multiplications per transform, four quartic degree columns | Plain radix-2 | True y-twisted radix-2 |
| --- | ---: | ---: |
| Forward | 1,920 CT twiddles | 744 initial `y³²` twists + 1,176 GS lower-output twists = 1,920 |
| Inverse | 1,920 GS twiddles | 1,176 CT input untwists + 744 final `y³²` untwists = 1,920 |

So this correct Yang realization **moves 744 fixed multiplications** across
the binary tower but does not eliminate them in the scalar ledger. The
potential gain is instead reduction placement, dependency, vector mapping,
or constant reuse. Unlike the rejected surrogate, it does **not** force
three Decap gauge adapters. The top trinomial and radix-3 remain unchanged
in this first complete-y-tower model; their joint redesign is still open.

The first AVX2 range screen uses the actual BaseMulScale source-level plane
envelopes `(3741,5652,7563,7644)`, not four copies of ±7644, and defers
the five inverse halvings for the existing tail scale contract. In a
**no-repair** CT merge, the first unproved signed-i16 add for degree 1–3 is
already at the size-8 node; degree 3 has bound `30576+30576=61152`.
Degree 0 survives that node but first fails at size 16 with
`29928+29928=59856`. A Barrett at the valid 30,576-bound predecessor would
reduce its conservative bound to 3,107, but that repair and the 32× deferred
scale must be explicitly scheduled and priced. These are interval-proof
failures, **not** demonstrated reachable overflows. Correlated/lane-wise
refinement and the complete radix-3/trinomial tail proof remain open.

### Selection decision and remaining open direction

The true y-twist **passes exact factor, scale, ownership, and consumer ABI
closure**. It does not yet pass the *machine-candidate* gate: there is no
signed-i16 proof on actual BaseMulScale / crepmod3 domains, no schedule with
operands/last-use/≤16 YMM, and no evidence that the relocated reductions or
constants improve the complete inverse+Forward Decap path. A scalar-model
operation-count tie does not decide cycles. Thus this round stops before
namespaced ASM, linked audit, KEM vectors, ASLR-on short timing, and
fixed-layout A/B; none is claimed. The next narrow gate is a real AVX2
range/schedule comparison of this exact no-adapter y-twist against Official
GS and `stage5reuse`, including the six initial `y³²` twists and inverse
untwists. If that gate finds a safe, allocatable machine mechanism, one paired
tower ASM candidate is authorized by the plan. If not, document the exact
overflow or allocation node rather than “fixing” it with unpriced reductions.

### Follow-up: real-cell def/use repair screen

The later [existing-multiply repair gate](ntruplus768-defuse-repair-gate.md)
corrects the old screen's obsolete two-product zeta derivation for its first
three planes. It reads the independently proved 768 BaseMulScale cell bounds
and exact factor ownership. All 24 cohort×degree first unproved true-twist CT
adds have identity twiddles: 18 at size 8 and six at size 16. Thus the local
"move an existing CT twiddle before the first dangerous add" mechanism has no
machine multiply to move. This does not prove reachable overflow or exclude a
correlated proof or a redesigned butterfly. No ASM or cycles were produced by
this selection gate; the v2 JSON supersedes the old plane-bound provenance.

### Correlated-range and butterfly follow-up

The later [correlated-range/butterfly gate](ntruplus768-correlated-range-butterfly.md)
**supersedes the previous “interval failure only” qualification for the
unrepaired CT realization**. A canonical decoded `c,f` witness produces raw
7596 in every degree-3 BaseMulScale leaf; the identity-twiddle size-8 sum is
60768 and signed `vpaddw` corrupts the residue. A modular-half butterfly has
an executable arithmetic proof and a local AVX2 probe, but not a complete
inverse-tail schedule or Decap performance result. Four of five CT levels
must be halved in the tested uniform-stage, no-other-repair family. This is
not a lower bound for every CT or twisted-tower implementation.

The subsequent [mixed-gauge twiddle experiment](ntruplus768-twiddle-half-absorption.md)
demonstrates a partial absorption: pre-halved upper child values allow the
lower child to use modified `w/2` twiddles, eliminating modular-half work at
those merges. Identity twiddles become actual new multiplications, and the
remaining modular-half butterflies still need parity correction. This is a
radix-2 arithmetic/range result, not a linked inverse or cycle win.

The next [mixed-gauge decision gate](ntruplus768-mixed-gauge-decision.md)
closes the factored top tail and actual BaseMulScale→inverse→crepmod3 scalar
contract, but finds additional vector Montgomery chains and mixed-lane
selection. The full 16-YMM linked schedule and Decap pricing remain open;
there is no full inverse ASM or performance promotion.
