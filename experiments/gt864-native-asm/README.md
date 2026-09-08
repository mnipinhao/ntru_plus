# GT864 native arithmetic assembly — experimental integration

**Latest:** local Slothy timing and Pi5 paired benchmark completed.
See [TIMING-RESULTS.md](TIMING-RESULTS.md): Keygen -3.53%, Decaps -1.91%
versus current GT production; Encaps neutral. Production unchanged.
The execution-gate notes below describe the earlier allocation-only milestone.

## Current execution gate (2026-09-08)

User explicitly authorized local Slothy execution from `/Users/chenpinhao/slothy`.
`integration/public.S` now implements BaseInv failure handling, output clearing,
1200-byte scratch wipe, exact alias support and AAPCS preservation. Five Slothy
allocated arithmetic cores passed 808 native ARM64 tests (517 success / 291
failure), including every one of 288 zero-leaf positions. Reproduce:

```
python3 experiments/gt864-native-asm/integration/build_test.py --baseinv-only
```

`--oracle-wrapper` is explicitly a different test mode: it uses C arithmetic
cores and old Inverse assembly adapters to test wrapper control flow only.
The default build fails closed if any new allocated core is missing.

The Inverse public wrapper has 1792-byte wiped scratch. The newly allocated
Inverse and BaseMul arithmetic now pass 256 inputs and 256 BaseMul chains on
native ARM64, including independent cubic R^-1 identity, range, alias, AAPCS
and scratch wipe checks. Reproduce with `python3
experiments/gt864-native-asm/integration/build_test.py` (without oracle mode).
Current I16 sources are 733 / 669 instructions: 43 arithmetic
instructions plus two dead constant loads removed per block.

ToBytes has been redesigned in `tobytes_block` and `tobytes_merge`: immediate
row normalization/packing, full ST3 .8b into a 648-byte byte scratch, then TBL
merge and STR Q/D to wire bytes. All 132 exact model cases pass. There are no
lane ST3 stores and exactly 108 coefficient Q loads. This deliberately adds
2592 bytes of byte-scratch traffic per call; speedup is NOT established.
Both regions have allocated, assembler-checked artifacts, but no native
ToBytes differential test or integrated public wrapper yet.

`redc_deletion_audit.py` and `redc-deletion-results.json` reject all 31 nonempty
naked-deletion masks of BaseMul's two early and three final REDCs. The scope is
the existing zR table, int16 consumer and R^-1 ABI, not all possible new DAGs.

Allocation logs are per-region `slothy-ra.log`. Native tests are mandatory:
Slothy's optional emulator selftest is disabled on this host. The allocator
must reserve `sp` and `xzr`, not merely x18-x30. Symbolic temporaries avoid tN,
which this architecture model treats as HINT registers.

Production remains unchanged. The sections below preserve the original
source-gate rationale; pending-wrapper statements there describe that earlier
state and are superseded by this execution section.

Production unchanged. This is allocated experimental assembly with native
component correctness tests, **not a completed full-KEM integration**. No new
Pi5 measurement is claimed. Canonical `slothy-symbolic-asm-authoring` governs
contracts and static gates; the user authorized agent-run local allocation.

## Correct Slothy checkout

- Updated source: `/Users/chenpinhao/slothy`.
- Interpreter: `/Users/chenpinhao/slothy_and_ra/.venv/bin/python`.
- Set `PYTHONPATH=/Users/chenpinhao/slothy`; assert imported architecture path.
- Model: `cortex_a76`, not the old N1 proxy.
- Git base `c9fea6c179454536c92eaa50f90e0f9d8f8152dd`, with local parser/model
  edits. The Git revision alone does not identify the tested model.
- Six lane tests passed: parser roles/roundtrip, lane bounds/types, pointer
  writeback dependency, consecutive-register constraint, model coverage,
  all lane encoding assembly. A separate Unicorn UMOV execution attempt ended
  with exit 132; execution semantics must not be reported as tested by that run.
- `preflight.py` parses each authored instruction, roundtrips it, and requests
  A76 resource/throughput/uop descriptions. This is not allocation feasibility.

## Assembly source index

| Directory | Role | Region instructions |
| --- | --- | ---: |
| `baseinv_num` | 8 cubic cofactors and denominators, FR0 input directly | 124 |
| `baseinv_prefix` | Three independent prefix products | 34 |
| `baseinv_inverse` | Combine three final prefixes, exponent 3455, recover three inverses | 208 |
| `baseinv_recover` | Three reverse-chain steps | 61 |
| `baseinv_finish` | Shared inverse-denominator precomputation, three products, center | 59 |
| `basemul` | 8 cubic products, final R^-1 output | 61 |
| `inverse16_lazy` | Packed-top I16 main, lazy identity butterflies | 733 |
| `inverse_tail_lazy` | Padded tail I16, same lazy identity policy | 669 |

Each directory has `kernel-contract.yml`, `instruction-dag.yml`,
`candidate-contract.yml`, `candidate.sym.S`, and an iteration record. Names in
angle brackets are logical values, **not physical register assignments**.
BaseInv stage scratch for the proposed orchestration is `[step][chain][8 lanes]`;
the five regions together cover the arithmetic, not the outer public function.
Do not call these raw internal symbols from C before ABI handling is supplied.

## BaseInv reductions removed in this symbolic candidate

The reference is `../gt864-fr0-native-baseinv/baseinv.c`, FR0_LAZY variant.

1. Remove all three input centering sequences before `REDC(input*867)`.
   `867 = R² mod q`, `R=65536`. Full signed-int16 input is legal for this
   **wide** product. Its maximum numerator magnitude is bounded by
   `32768*867 + 32768*3457 < 2^31`; output magnitude is at most 2162.
   Exhausting all 65536 inputs reaches exactly 2162. Later products have both
   operands <=4000 and REDC output <=1972; sums/differences remain <4000.
   This proof is for wide Montgomery, not fixed-twiddle Barrett.
2. Remove the initial SQRDMULH/MLS from each final centering operation.
   Final REDC outputs lie in `(-q,q)`. Conditional add q for negatives then
   subtract q above 1728 yields the required centered representative directly.
   Keep these last correction instructions: the output ABI remains centered R0.

Relative to a literal symbolic transcription, numerator is 152 ->124 and finish
67 ->59 instructions. That is 36 fewer instructions/tile, 1296 across 36 tiles,
including constant setup. **Not a comparison against the compiled object's
instruction count or a cycle prediction.** Compiler CSE and future constant
lifetime choices can change the realized delta.

The implemented three-chain protocol uses: 36 numerator calls;
11 prefix steps; zero detection on final prefix vectors; one inverse3;
11 reverse steps; 36 finishes. Failure must zero all output and return 1, and
success return 0. Scratch erasure and in-place alias behavior pass native
integration tests with allocated assembly, in addition to the arithmetic model.

## Why BaseMul ends with Montgomery reduction

For a signed wide accumulator x, use

`t = signed16(low16(x)*(-12929)); y = (x+t*3457)/65536`.

`y = x*R^-1 (mod q)`. UZP1 extracts low halves; MUL constructs t; SMLAL/SMLAL2
add t*q; UZP2 extracts the exact high halves. This both narrows the accumulator
and changes its scale. It is not an R0-preserving reduction deletion.

The two early reductions also stay: cross products must be narrowed before
multiplication by the FR0 `z*R` table, and their R^-1 cancels that R. The three
final reductions then intentionally leave R^-1 for Inverse. Inputs are only
the first Decaps FromBytes pair in [0,4095], not arbitrary BaseMul callers.
The conservative final output contract is <=2497 (integer envelope <=2496).

Inverse stages preserve R^-1 until existing terminal multiplications use
`b_new = center(b_old*R)`, with regenerated Barrett hats. That restores R0
without a separate scale-conversion memory pass. The old C scale prototype is
the oracle; no new measurement was run as requested.

## Inverse consumer-range closure

Reduction reason ledger following `docs/NeonNTT-(Auto)formalised.md`:

| Site | Reason | This candidate |
| --- | --- | --- |
| BaseInv input center | CONSUMER/RANGE only | Delete under full-i16 *R2 wide proof |
| BaseInv internal Montgomery | REPRESENTATION + RANGE | Keep |
| BaseInv final preliminary Barrett | RANGE reset already supplied by REDC | Delete |
| BaseInv final signed correction | CANONICAL/ABI | Keep |
| BaseMul early REDC x2 | REPRESENTATION + narrowing CONSUMER | Keep |
| BaseMul final REDC x3 | REPRESENTATION R^-1 + narrowing | Keep |
| I9 roots / eta / terminal twist | Mathematical constants + RANGE | Keep |
| I16 b=1 groups | RANGE only | Delete 14; retain final reset, omit its MUL |
| I16 other roots and terminal scales | Mathematical constants / REPRESENTATION | Keep |
| Inverse final centering | CANONICAL/ABI for current wrapper | Keep |

No doubled-Montgomery or SHSUB deletion is introduced.

`inverse_range.py` exhausts all signed-int16 inputs for 266 distinct constant
pairs, verifying hat identities and outputs <q. It propagates the exact I9
register topology with conservative independent bounds:

`BaseMul <=2497 -> I9 peak <=22473 -> terminal twist <=3456 -> I16`.

All 32768 masks of the 15 identity butterflies are tested. A passing maximum
deletion mask drops 14 whole Algorithm-10 groups. Keep the last stage's identity
reset at butterfly 24, but omit its actual multiply-by-one instruction.
The resulting I16 peak is <=30939. Terminal scale resets to <q; top subtraction
and final reconstruction stay <=6912. Final canonicalization remains required.

Main: 778 ->735. Tail: 714 ->671. Across six main blocks and one tail, static
saving is 301 instructions; no additional coefficient boundary. This is separate
from the earlier packed-top routing's net 96-instruction saving.

`generate_inverse.py` checks that source stage constants/quotient operands match
the proof's butterfly numbering before removing instructions. `verify.py`
executes both symbolic versions with exact low-half multiplication semantics:
136 inputs each for main and tail compare after centered reduction, including
write-set equality. This is not physical-assembly execution or KAT evidence.

Use unchanged I9 producer from `../gt864-next-dag/inverse9/candidate.sym.S`.
The terminal tables remain `../gt864-decaps-scale/scaled_tables.h`.
Public caller must use the new packed scratch coordinates documented in
`../gt864-next-dag/README.md`. Reusing the old caller with these kernels is wrong.

## ToBytes: retire lane ST3 default, don't merely substitute mnemonic

The previous pair-local output is `72*row + 9*lane + 3*pair + byte`.
One pair supplies only 3 of every 9 bytes. A full ST3 in that spot would corrupt
the wire layout. The three pair streams must be routed together or retiled.

`tobytes_store_map.py` proves an exact 48-byte chunk convention: 16 consecutive
wire coefficient pairs give three 16-byte byte-channel vectors, suitable for
one full ST3, or three already-interleaved STR Q. All 1296 bytes fit exactly:
27 full ST3 or 81 STR Q, no scalar tail and no lane stores.

However, naive independent wire-chunk gathers require 836 Q loads versus 108
distinct input vectors; a chunk can touch 32 different source vectors. This
naive strategy is rejected as the routing default. The next DAG must retain
source reuse while producing contiguous chunks incrementally. The full-vector
wire map is ready; a no-reload/no-spill routing DAG is **not implemented yet**.
The user's 3.28 vs16.13 cycles/48B motivates this policy; those numbers were not
remeasured in this campaign and are not whole-ToBytes predictions.

## Reproduce local gates / handoff

```sh
python3 experiments/gt864-native-asm/verify.py
python3 experiments/gt864-native-asm/inverse_range.py
python3 experiments/gt864-native-asm/tobytes_store_map.py
PYTHONPATH=/Users/chenpinhao/slothy /Users/chenpinhao/slothy_and_ra/.venv/bin/python experiments/gt864-native-asm/preflight.py
```

After reviewing the symbolic sources, user-run RA then small windows, e.g.:

```sh
PYTHONPATH=/Users/chenpinhao/slothy /Users/chenpinhao/slothy_and_ra/.venv/bin/python experiments/gt864-native-asm/optimize.py basemul
```

Expected files: that region's `candidate.alloc.S`, `candidate.opt.S`, plus retain
the console/solver log. All 32 vector registers are available to these internal
regions. Outer ABI preservation is still required. No spills allowed. For I16,
do not attempt a monolithic timing solve: allocation first, then 16-way split
windows. Skill gate remains `Slothy_run_by_user`; no allocation/no-spill/cycle
success is claimed in this source-only turn. Promotion also requires executable
oracle, complete KEM, ABI, constant-time review, and full-path measurements.
