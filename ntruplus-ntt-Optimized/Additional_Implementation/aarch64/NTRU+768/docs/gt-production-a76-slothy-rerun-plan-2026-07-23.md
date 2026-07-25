# GT Production Cortex-A76 Slothy Rerun Plan

Date: 2026-07-23

This plan covers the selected AArch64 NTRU+768 GT production KEM. It excludes
generic profiler-only APIs unless they share the exact arithmetic body used by
the KEM.

The release default is:

```text
forward NTT:       shared GT poly_ntt
keygen layout:     mixed BPQ/CQ
encap pointwise:   direct-Q31 basemul_add
decap first pair:  rminus1 basemul + rminus1 InvNTT
decap verify:      compact canonical pointwise F1
serialization:     canonical pack P0 + unpack U1
section GC:        enabled
```

The direct-CQ keygen profile is a formal default-off production profile. It
should be rerun separately after the mixed release default has a stable A76
baseline.

## 1. Why rerun Slothy now

Most selected `.n1.opt` artifacts were generated with
`slothy.targets.aarch64.neoverse_n1_experimental`, then accepted or rejected by
Pi 5 PMU. That process was safe, but N1 was only a scheduling proxy.

The updated A76 model matters most where:

- `mul`, `sqdmulh`, `sqrdmulh`, `smull`, and `smlal` compete for the A76 vector
  multiply resource;
- vector arithmetic can overlap scalar address/control instructions;
- `ldr`/`ldp` and structure loads/stores have different LSU costs;
- `trn`, `uzp`, `ext`, and lane extraction contend with other vector work;
- an old experiment driver locally patched missing instruction models and may
  now override the new A76 model incorrectly.

The goal is not to optimize every assembly file again. The goal is to rerun
small, exact production windows whose old schedule was selected using an
incomplete microarchitecture model.

## 2. Gate 0: validate the A76 target before scheduling production

Before the first production rerun:

1. Confirm the remote module name and checkout, expected to be
   `slothy.targets.aarch64.cortex_a76` or the newly modified equivalent.
2. Record the Slothy commit, Python executable, `slothy.__file__`, target
   module hash, and local driver hash.
3. Audit the target mappings for:
   - `mul`, `sqdmulh`, `sqrdmulh`, `smull`, `smull2`, `smlal`, `smlal2`;
   - `ldr`, `ldp`, `ld1`, `ld3`, `ld4`, `str`, `st1`, `st3`, `st4`;
   - `trn1`, `trn2`, `uzp1`, `uzp2`, `ext`, `umov`;
   - scalar `add/sub/cmp/csel` while Neon instructions are in flight.
4. Run one small known symbolic window under both N1 and A76. Confirm that the
   A76 schedule changes for a defensible resource reason.
5. Disable driver-local instruction-model patches when the A76 target already
   supplies the instruction. A local patch must not silently replace the new
   model.

All new files should use `.a76.alloc.S`, `.a76.opt.S`, and `.a76.log` names.
Do not overwrite the selected `.n1.opt.S` production artifacts during search.

## 3. Wave 1: contracts already exist

These candidates can be rerun without reconstructing their arithmetic
semantics. Their existing baseline contract, kernel contract, symbolic source,
and differential harness should remain the source of truth.

### P0: decap rminus1 basemul pair pipeline

Production:

```text
asm/gt/basemul/poly_basemul_rminus1.n1.opt.S
experiments/rminus1_basemul_pair_pipeline/
```

Current actual KEM result:

```text
1912 cycles, 1900 instructions, once per decapsulation
paired with rminus1 InvNTT: 5467 cycles
```

Why first:

- The previous result explicitly says the N1 estimate did not model A76's
  single vector-multiply resource accurately.
- The kernel is dominated by modular multiply/reduction chains.
- A two-iteration symbolic contract, ABI sentinel, differential test, direct
  PMU, and full-decapsulation replacement harness already exist.
- The selected N1 schedule already saved about 108 cycles over the ABI-safe
  source-order baseline, so scheduling is known to matter.

Rerun:

```text
two-iteration body
fixed allocation
allow_spills = false
then optional renaming search with the same live-in/live-out contract
```

Decision gate:

```text
coefficient differential = 0
ABI mask = 0
KEM count = 0
A76 candidate beats current n1.opt in paired direct PMU
full decapsulation does not regress
```

### P0: encap direct-Q31 basemul_add pair pipeline

Production:

```text
asm/gt/basemul/poly_basemul_add_encap_tobytes_q31.n1.opt.S
experiments/q31_basemul_add_pair_pipeline/
```

Current actual KEM result:

```text
2285 cycles, 2214 instructions, once per encapsulation
basemul_add plus canonical pack: 2902 cycles
```

Why now:

- It overlaps iteration N reduction/store with iteration N+1 loads and
  arithmetic, so LSU/vector resource accuracy directly affects the schedule.
- The old driver patches several vector instructions into a generic V unit.
  Those patches must be reviewed against the updated A76 target.
- Existing 90-instruction crossover and 33-instruction tail windows are small
  enough for controlled reruns.

Rerun:

```text
crossover window
tail window
fixed allocation, no spills
optional renaming only as a separate candidate
```

Do not generalize the result to generic `poly_basemul_add`; this is the
encapsulation-only Q31 byte endpoint.

### P0: forward NTT frontend DCE windows

Production:

```text
asm/gt/ntt/poly_ntt.n1.opt.S
experiments/forward_ntt_frontend_dce_slothy/
```

Current actual KEM result:

```text
2587 cycles per fixed-buffer forward NTT
two calls in encapsulation
two calls in decapsulation
two calls in keygen before layout conversion
```

Why now:

- This is the most frequently used arithmetic kernel in the production KEM.
- The experiment already divides the frontend into eight exact 156-instruction
  iterations and has fixed/rename variants.
- The selected fixed-allocation schedule won on Pi 5; the old rename schedule
  did not. A real A76 target can change that comparison.

Rerun:

```text
each existing frontend iteration class independently
fixed allocation first
rename second
no spills
```

Do not send the complete 4338-line `poly_ntt` to Slothy.

### P1: forward Stage345 reduction windows

Production provenance:

```text
experiments/forward_ntt_phase123_u01/g1_stage345_reduction_slothy/
blocks 1, 2, and 3 of the selected G1R123+S2 schedule
```

Why:

- Blocks 1/2/3 already have frozen schedule-only windows.
- Modular reduction and final-store overlap is sensitive to A76 vector
  multiply and LSU mappings.
- The arithmetic, layout, and S2 high-half store contract must not change.

Rerun blocks 1/2/3 independently with fixed allocation and no spills.

Block0 is not part of the first wave. Its inherited stack-spill/register
pressure previously made the search infeasible. Reopen it only as a separate
diagnostic after the A76 target solves blocks 1/2/3 reliably.

### P1: canonical pack and unpack

Production:

```text
asm/gt/support/poly_canonical_pack.S
asm/gt/support/poly_canonical_unpack_u1.S
experiments/canonical_pack_next_wave/
experiments/canonical_unpack_next_wave/
```

Current actual KEM costs:

```text
canonical pack:   about 613 cycles per call
canonical unpack: about 487-489 cycles per call
```

They are called repeatedly:

```text
encap: pack r, unpack pk, pack ciphertext
decap: two unpacks, pack r1
```

Why:

- These kernels mix structure loads/stores, permutations, shifts, reductions,
  and scalar pointer updates.
- Existing drivers locally add models for `st1 {3 regs}` and `ld1 {3 regs}`.
  The updated A76 target may now model them more accurately.
- The full-KEM weighted serialization overhead is larger than a single
  component row suggests.

Rerun both fixed and rename chunk contracts, then regenerate the complete
function. A chunk-only expected-cycle improvement is not a promotion result.

Required final gate:

```text
canonical byte differential
KAT
ABI sentinel
same-binary encap/decap PMU
text-size and alignment report
```

### P2: inverse post branchfold window

Production context:

```text
asm/gt/invntt/poly_invntt_rminus1.S
experiments/invntt_next_wave/post_branchfold_slothy/
```

The existing 69-instruction, three-output symbolic window is easy to rerun.
The N1 candidate was flat/slightly slower, so this is a model-validation
candidate rather than a high-confidence speedup.

Do not revive previously rejected lane-store/LDP variants in the same run.

## 4. Wave 2: valuable, but rebuild the exact current contract first

These are important production costs, but the current tree does not retain a
clean symbolic source that exactly reproduces the selected production body.
Do not schedule them from an old prototype.

### P0 rebuild: rminus1 InvNTT Stage45 row

Production:

```text
asm/gt/invntt/poly_invntt_rminus1.S
asm/gt/invntt/poly_invntt.n1.opt.inc
```

Current actual cost:

```text
3557 cycles, 4819 instructions, once per decapsulation
```

Build one reusable symbolic row contract for the eight-stripe Stage45 body.
Preserve:

```text
direct Stage123 stripe scratch
Stage45 row-end reduction fusion
lazy twiddle1 through len16
rminus1 factor contract
branchfold post path
```

This is the highest-value contract rebuild for decapsulation. It should be
scheduled row-by-row, not as the complete inverse function.

### P0 rebuild: mixed BPQ/CQ keygen basemul

Production:

```text
asm/gt/keygen_bpq_cq/basemul.S
asm/slothy/production/bpq_cq_keygen/basemul_quad4.n1.opt.inc
```

Current actual cost:

```text
1661 cycles, 2318 instructions, called twice per keygen
```

The selected include has N1 provenance but no current exact symbolic
source/driver was found. Extract the exact quad4 arithmetic and CQ final-store
contract before an A76 rerun.

### P0 rebuild: hierarchical baseinv tree

Production:

```text
asm/gt/keygen_bpq_cq/baseinv_tree.S
```

Current actual cost:

```text
baseinv: 4039 cycles, 4310 instructions, called twice per keygen
baseinv + matching basemul: 5698 cycles, called twice
```

Recommended independent windows:

```text
form_group_pair x4
forward product tree 8 -> 1
backward recovery tree
four recovery groups
```

Do not schedule across the `bl gt_fqinv15_asm` boundary. The 15-step inversion
itself is a strict dependency chain and is not a first-priority Slothy target.

### P1 rebuild: baseinv prepare and CQ finish

Production:

```text
asm/gt/keygen_bpq_cq/baseinv_prepare.S
asm/gt/keygen_bpq_cq/baseinv_finish.S
```

There are older symbolic baseinv experiments, but they do not automatically
prove equivalence to the selected mixed BPQ/CQ production contract. First
extract the current BPQ-to-CQ prepare group and four-lane CQ finish loop.

The finish loop is small and low risk. Prepare is more valuable if the A76
target improves transpose/load overlap.

### P1 rebuild: compact decap verify F1 group

Production:

```text
asm/gt/decap/verify_pointwise_compact.S
```

Current actual cost:

```text
3394 cycles, 4306 instructions, once per decapsulation
```

Schedule one generated repeated group and regenerate the compact function. Do
not replace it with the large F2 speed backend in this experiment; the purpose
is to preserve the selected code-size profile.

### P2 rebuild: inverse Stage123 small windows

Stage123 still has a scratch store/reload boundary. Scheduling may improve
overlap but cannot remove the structural 96 q stores and 96 q reloads.

Start with one or two group windows only. If A76 PMU is flat, stop instead of
expanding to the complete Stage123 body.

## 5. Do not prioritize

Do not spend the first A76 wave on:

- generic `poly_invntt`, generic `poly_basemul`, generic `poly_basemul_add`, or
  generic `poly_baseinv` profiler APIs;
- the full 4338-line forward NTT as one solver problem;
- old all-row rowspec/direct-offset experiments;
- NTT Stage345 block0 until the smaller current-contract windows pass;
- inverse final V0 arithmetic deletion, which already proved 0/192 safe sites;
- twiddle1 arithmetic changes, which already have a separate proof-backed
  production decision;
- the 15-step `fqinv` dependency chain;
- support kernels such as CBD, SOTP, triple, subtraction, or crepmod3;
- direct-CQ-only scheduling before the mixed release-default rerun is stable.

## 6. Recommended execution order

```text
0. A76 target-model audit and N1/A76 smoke comparison
1. rminus1 basemul pair
2. Q31 basemul_add pair
3. forward frontend DCE fixed + rename
4. canonical unpack U1 and pack P0
5. forward Stage345 blocks 1/2/3
6. inverse post branchfold
7. rebuild and schedule inverse Stage45
8. rebuild keygen mixed BPQ/CQ basemul
9. rebuild baseinv tree, prepare, and finish
10. schedule compact decap verify F1 group
11. inverse Stage123 narrow-window diagnostic
12. repeat selected winners for the direct-CQ production profile
```

The first six items reuse existing contracts. Items seven onward require an
exact current-production contract before running Slothy.

## 7. Common acceptance matrix

Every A76 candidate must report:

```text
source and generated artifact hashes
target module and target hash
allow_renaming / allow_spills
solver status and expected cycles
instruction multiset or semantic equivalence
assembly/link result
coefficient or byte differential
KAT / KEM count
AAPCS64 x19-x28 and d8-d15 sentinel
direct paired PMU cycles and instructions
same-binary KEM-context PMU
full keygen/encap/decap replacement result as applicable
symbol size, total .text, address mod32/mod64
```

Promotion requires measured Pi 5 improvement over the current selected
production artifact. A lower Slothy expected-cycle count alone is not a
promotion result.
