# GT Production A76 Slothy Rerun Plan

Date: 2026-07-23

Execution status:

- Gate 0 and Wave 1 completed on 2026-07-23.
- All 26 formal A76 outputs solved and cross-assembled without spills.
- No Wave 1 output reduced the A76 modeled schedule span versus the exact
  production source order, so no candidate was integrated or promoted.
- The retained result summary is in
  [`gt-production-a76-slothy-wave1-result-2026-07-23.md`](gt-production-a76-slothy-wave1-result-2026-07-23.md).
  Generated schedules and logs were removed because no result passed the
  modeled performance gate.
- Wave 2 remains a separate future iteration.

This is the execution handoff for rerunning Slothy on the fixed NTRU+768
AArch64 GT production release. The solver may run for several hours. Solver
time is not the acceptance criterion: every selected result must preserve the
exact production contract and improve measured Cortex-A76 performance.

## 1. Scope and source of truth

Use this release directory as the behavior and linkage source of truth:

```text
ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768/
```

The fixed KEM data flow is:

```text
keygen:
  Direct-CQ NTT
  -> hierarchical batch base inversion
  -> CQ pointwise products
  -> CQ canonical pack

encapsulation:
  canonical unpack
  -> block-major NTT
  -> specialized a*b+c and byte endpoint

decapsulation:
  canonical unpack
  -> rminus1 pointwise product
  -> rminus1-aware inverse NTT
  -> centered mod-3 path
  -> block-major NTT
  -> compact verify pointwise
```

Do not optimize an older profile, generic profiler symbol, BPQ experiment, or
rejected F2 decap backend. Confirm the active source in `Makefile`
before extracting a region.

Keep all Slothy inputs and outputs outside this release tree. Suggested
development-repository root:

```text
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/
  experiments/gt_production_a76_slothy/
```

For every candidate preserve:

```text
baseline-contract.yml
kernel-contract.yml
instruction-dag.yml
candidate-contract.yml
kernel.sym.S
run_slothy.py
kernel.a76.alloc.S
kernel.a76.opt.S
kernel.a76.log
result.md
```

Never overwrite a selected `.n1.opt.S` or release `.S` during the search.

## 2. Mandatory preflight

Before running a production window:

1. Record the production revision and `SOURCE-MANIFEST.sha256`.
2. Record the Slothy revision, Python executable, `slothy.__file__`, A76 target
   module path, and hashes of the target and architecture modules.
3. Use the repository venv directly. Do not use an unverified global Slothy.
4. Confirm whether the target is a real Cortex-A76 model. If only N1 exists,
   label the result N1 and do not present its estimate as A76 performance.
5. Audit A76 mappings for the instructions used by the selected window:

```text
mul, sqdmulh, sqrdmulh
smull, smull2, smlal, smlal2
ldr, ldp, ld1, ld3, ld4
str, stp, st1, st3, st4
trn1, trn2, uzp1, uzp2, ext, umov
scalar add, sub, subs, cmp, csel
```

6. Remove driver-local placeholder timing patches when the A76 target already
   models the instruction. Record every remaining local model patch.
7. Run a small known kernel under N1 and A76. Explain any schedule difference
   using resources or latency before trusting the A76 model.
8. Reserve `x18`, `x29`, `x30`, and `sp`. Reserve `x19-x28` unless the baseline
   explicitly saves them or the region contract fixes them as live-ins.
9. Treat `d8-d15` as callee-saved at a C-callable boundary. Internal windows may
   use their existing physical registers only when the enclosing wrapper's ABI
   preservation is unchanged.
10. Set `allow_spills = false` for every primary candidate. Spill-enabled runs
    are diagnostics and must be labeled as such.

## 3. Required optimization workflow

Every item below is `existing_region_replacement`.

```text
repo probe
-> exact baseline extraction
-> baseline contract
-> kernel contract
-> instruction DAG
-> symbolic assembly
-> static checks
-> Slothy allocation/scheduling
-> assemble
-> differential correctness
-> ABI sentinel
-> KAT/full KEM
-> paired Pi5 PMU
-> promotion decision
```

Do not send an entire large function to Slothy. Prefer:

```text
small window:
  combined register allocation and scheduling

medium window:
  functional-only allocation
  -> real-instruction window scheduling

macro/repeated kernel:
  explicit symbolic body
  -> functional-only allocation
  -> unfold to real instructions
  -> window scheduling
```

For destructive instructions such as `mls`, encode tied destination/input
semantics before coloring. Reject undefined values, stale physical-register
uses, same-as interference, hidden macro operands, and output contracts that
exist only as comments.

## 4. Wave 1: highest-value production windows

### W1.1 Inverse NTT Stage123

Production source:

```text
asm/invntt.S
DIRECT_STAGE123_BLOCK_TO_SCRATCH
DIRECT_STAGE123_STRIPE_SCRATCH_ROW0/1/2
```

Status:

```text
Stage123 arithmetic is source-order.
Stage45 is already a Slothy-derived schedule.
Stage123 writes 32 q vectors per row to stripe scratch.
```

First run:

```text
one 8-vector Stage123 block
load branch halves
len=2/4/8 butterflies
one eight-q stripe-scratch store group
```

Then run:

```text
two adjacent blocks as one window
four blocks only if the two-block solve is stable
```

Preserve:

```text
x3/x4 input branch bases
x14 stripe-scratch base
v0 modular constants
twiddle=1 lazy sites
all source offsets
all stripe-scratch offsets
exact signed representative/range contract
```

Do not:

```text
remove scratch
change twiddle arithmetic
change lazy-reduction semantics
combine Stage45 in the first run
```

Suggested solver budget:

```text
single block: 15-45 minutes
two blocks:   1-3 hours
four blocks:  diagnostic; allow overnight
```

### W1.2 Inverse NTT Stage45 row

Production source:

```text
asm/invntt.S
RUN_INVNTT32_STAGE45_SCRATCH_ROW
```

Status:

```text
Current physical allocation/order is Slothy N1-derived.
It consumes eight stripe groups and fuses row-end Barrett reduction.
```

Do not rebuild arithmetic from an old inverse prototype. Extract the exact
cleaned production macro expansion. Build:

```text
A76-fixed:  preserve current physical allocation, scheduling only
A76-rename: symbolic SSA values, renaming enabled, no spills
```

Try windows in this order:

```text
two Stage45 stripes
four Stage45 stripes
complete eight-stripe row
```

The complete-row run may take several hours. Keep the best independently
verified smaller-window candidate even if the complete row times out.

Preserve:

```text
x14 input scratch
x2 row output
x3 twiddle table
v0 q/Barrett constants
len16 twiddle=1 lazy contract
natural row-output offsets
row-end representative bounds
```

### W1.3 Decapsulation verify repeated group

Production source:

```text
asm/internal/decap_verify.S
.Lfused_gather_mul_group
```

Status:

```text
Compact F1 backend.
Generated/hand-unrolled, not Slothy-scheduled.
Repeated gather, transpose, quartic multiplication, reduction, and store.
```

Extract exactly one repeated group and its caller-side live-in/out contract.
Start with fixed allocation, then a rename candidate. If profitable, evaluate a
two-group software-pipeline window.

Preserve canonical byte order and the compact F1 code-size profile. A faster
kernel that restores the old F2 text-size expansion is not an automatic win.

Suggested budget:

```text
one group fixed:   15-45 minutes
one group rename:  30-90 minutes
two-group window:  1-4 hours
```

### W1.4 Keygen base-inversion finish

Production source:

```text
asm/internal/keygen_baseinv_finish.S
24-iteration finish loop
fqmul4 macro
```

Status:

```text
Not Slothy-scheduled.
Macro invocation hides four Montgomery multiplication/reduction chains.
```

Do not feed the macro call directly to Slothy. Expand one exact loop body into
real symbolic instructions. Keep the loop branch and pointer updates outside
the first arithmetic window, then try a two-iteration crossover.

Preserve CQ lane meaning, lambda/denominator order, pointer increments, and
24-iteration count.

### W1.5 Keygen hierarchical base-inversion tree

Production source:

```text
asm/internal/keygen_baseinv_tree.S
form_group_pair
forward product tree
gt_fqinv15_asm call
backward recovery tree
recover_group_pair
```

Status:

```text
Not Slothy-scheduled.
Assembler macros hide the real NEON DAG.
```

Create explicit symbolic windows:

```text
A: one form_group_pair
B: two adjacent form_group_pair calls
C: forward 8-to-1 product tree
D: backward recovery tree
E: one recover_group_pair
F: two adjacent recover_group_pair calls
```

Never optimize across `bl gt_fqinv15_asm`. Treat it as a hard call boundary.
Do not change the hierarchical inversion algorithm or 15-multiplication chain.

Suggested budget:

```text
A/E: 15-60 minutes
B/F: 1-3 hours
C/D: 1-4 hours
```

## 5. Wave 2: frequently called serialization and forward kernels

### W2.1 Direct-CQ keygen pack

Production source:

```text
asm/internal/keygen_pack.S
```

Status:

```text
Generated and explicitly expanded.
Not Slothy-scheduled.
Used only by keygen's Direct-CQ path.
```

Split by one canonical output chunk. Run fixed and rename candidates, then a
two-chunk crossover. Regenerate the complete function only after the chunk
differential passes.

Required acceptance evidence:

```text
canonical byte equality
keypair KAT
ABI sentinel
paired full keygen PMU
text size and L1I events
```

### W2.2 Public canonical pack

Production source:

```text
asm/pack.S
```

Status:

```text
Generated source order.
Used in encapsulation and decapsulation.
Historical cross-chunk schedules reduced direct cycles but could regress L1I.
```

Run:

```text
one chunk fixed
one chunk rename
two-chunk crossover
compact shared-core diagnostic
```

Do not promote from standalone pack cycles. Require same-binary paired encap
and decap measurements plus binary text size and L1I refill events.

### W2.3 Canonical unpack

Production source:

```text
asm/internal/unpack.S
```

Use the same chunk-first process as pack. Preserve canonical decoding,
permutation, bounds, pointer advances, and output layout.

### W2.4 Forward NTT

Production source:

```text
asm/ntt.S
```

Do not send the complete file. Separate:

```text
frontend input/split/twist/DFT3 windows
Stage12 windows
Stage345 block1
Stage345 block2
Stage345 block3
final-store windows
```

The current endpoint contracts differ:

```text
public poly_ntt: block-major output
private keygen endpoint: Direct-CQ final store
```

Arithmetic may be shared, but a schedule is only interchangeable when its final
store contract matches the endpoint. Preserve G1R123 producer/consumer mapping
and S2 high-half `umov+str` semantics where they are active.

Start from existing development contracts when they exactly match release:

```text
experiments/forward_ntt_frontend_dce_slothy/
experiments/forward_ntt_phase123_u01/g1_stage345_reduction_slothy/
```

Reject any stale contract that names an older BPQ, tuple, row-specialized, or
postprocess-only layout.

## 6. Wave 3: lower priority or model-validation work

### W3.1 Encapsulation multiply-add

Production source:

```text
asm/internal/encap_muladd.S
```

It already contains Slothy-derived regions. Rerun the crossover and tail under
A76, first preserving allocation and then allowing renaming. Keep its Q31 byte
endpoint and do not generalize the result to generic `poly_basemul_add`.

### W3.2 Rminus1 pointwise base kernel

Production source:

```text
asm/base.S
```

The selected pair pipeline is already Slothy-derived. Rerun only exact
rminus1 pair windows under A76. Preserve the deliberate omitted Montgomery
correction that is absorbed by `poly_invntt`.

### W3.3 Inverse final branchfold

Production source:

```text
asm/invntt.S
FUSED_POST_STRIPE / POST_STORE_PTR_BRANCHFOLD
```

Run one output, one complete three-output stripe, then at most a two-stripe
crossover. Preserve final Barrett reductions and exact representatives consumed
by `poly_crepmod3`. Historical N1 attempts were flat, so treat this as model
validation.

### W3.4 Support kernels

Production source:

```text
asm/support.S
```

The active loops were already Slothy-scheduled. Rerun only if the A76 model
substantially changes structure-load/store or vector-multiply costs:

```text
poly_sub
poly_triple
poly_crepmod3
qsoa_frombytes
qsoa_tobytes
```

These are independent loop-body windows. Do not schedule across loop branches.

## 7. Files that should not be sent to Slothy

```text
asm/kem_api.S
  ABI save/restore wrapper; no arithmetic scheduling opportunity.

asm/internal/fqinv.S
  15-step exponentiation chain with a strict dependency path. Only revisit if
  the algorithm/addition chain changes.

kem.c and other C orchestration
  Use compiler/LTO/link-order analysis, not Slothy.

complete asm/ntt.S or invntt.S
  Too large; extract exact windows.
```

`cbd.S` is also below the first three waves unless component profiling shows a
meaningful weighted budget and a clear repeatable loop contract.

## 8. Artifact and run policy

Use names that preserve target and iteration:

```text
kernel.i01.a76.alloc.S
kernel.i01.a76.opt.S
kernel.i01.a76.log
kernel.i01.result.md
```

For long runs:

```text
one managed solver process per candidate
preserve stdout/stderr
record start/end time and exit status
poll rather than start duplicate runs
retain timeout/infeasible logs
```

Use:

```text
allow_spills = false
allow_reordering = true
functional_only = false
variable_size = true
```

For medium/large symbolic kernels, run allocation separately:

```text
pass 1:
  functional_only = true
  allow_reordering = false
  allow_spills = false

pass 2:
  physical allocated input
  allow_reordering = true
  allow_spills = false
  split heuristic enabled
```

An overnight timeout is evidence that the window is too broad, not permission
to enable spills or weaken live-out constraints.

## 9. Correctness and promotion gates

Every generated candidate must pass:

```text
assembly/link
exact-region contract comparison
kernel differential with zero mismatches
edge vectors and randomized vectors
ABI sentinel mask = 0
KEM roundtrip
canonical KAT
git diff --check
```

Performance must be measured on Pi 5 Cortex-A76:

```text
same binary where possible
balanced AB/BA order
same deterministic inputs and buffers
core pinned
warmup recorded
NTESTS and NITERATIONS recorded
cycles, instructions, CPI
p10/p50/p90 or MAD
text size
function address mod32/mod64
L1I refill and frontend stalls when available
```

Promotion requires:

```text
direct kernel win
no full-KEM regression
no unacceptable text/L1I regression
all correctness and ABI gates
candidate status = promote
```

Slothy expected cycles alone never justify promotion.

## 10. Recommended execution order

Run in this order:

```text
0. A76 target validation [completed]
1. InvNTT Stage123 one-block and two-block windows [completed]
2. InvNTT Stage45 two-stripe and four-stripe windows [completed]
3. decap_verify one-group and two-group windows [completed]
4. keygen_baseinv_finish one/two iterations [completed]
5. keygen_baseinv_tree independent tree windows [completed]
6. keygen_pack one/two chunks
7. public pack and unpack chunk windows
8. forward NTT exact frontend/Stage345 windows
9. encap_muladd and base rminus1 A76 reruns
10. inverse post and support model-validation windows
```

This order prioritizes unscheduled production arithmetic first, then frequently
called serialization, then already-scheduled kernels that may benefit from the
new A76 model.

## 11. Prompt for the remote Codex

Use the following instruction with the other Codex:

```text
Follow docs/SLOTHY-RERUN-PLAN.md exactly.

Gate 0 and Wave 1 are complete. Continue with Wave 2, starting from keygen_pack
one/two chunks. Use the fixed release directory as the behavior and linkage
source of truth, but keep every Slothy source, driver, log, and generated
artifact outside the release tree.

For each region, use existing_region_replacement mode. Create and validate the
baseline contract, kernel contract, instruction DAG, and exact symbolic source
before running Slothy. Do not schedule complete ntt.S or invntt.S files. Do not
feed assembler macro calls directly to Slothy: expand the exact active body
into explicit symbolic instructions.

Use the verified repository venv and Cortex-A76 model. Preserve the N1 baseline
for comparison. Primary candidates must use allow_spills=false. Long runs of
one to several hours are acceptable; do not weaken contracts merely to make a
solve finish.

After every completed candidate, assemble it and run the differential and ABI
tests. Do not modify production defaults and do not claim a speedup from
Slothy estimates. Return the .alloc.S, .opt.S, log, contract comparison, and a
short result report for Pi5 validation.
```
