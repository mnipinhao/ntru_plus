# BaseInv and paired R^-1 BaseMul/Inverse integration — 2026-09-08

## 2026-09-10 BaseInv arithmetic promotion

Production now uses the 84-instruction fused-wide numerator and 37-instruction
no-centering finish.  The numerator preserves the existing R1 denominator and
adjugate ABI while reducing to seven wide REDC results.  Finish retains one
inverse-denominator R1-to-R0 correction and three product REDCs, but returns raw
R0 representatives bounded by `[-1972,1972]` instead of centered
`[-1728,1728]`.  Keygen-to-D1 consumer closure proves the latter still ends in
`[-1845,1845]`, so small ToBytes remains valid.

The production-linked component test passes 808 cases: 517 successes, 291
failures, all 288 injected zero-leaf positions, exact in-place aliasing,
canaries, AAPCS and the complete 1200-byte scratch wipe.  Pi 5 successful
BaseInv and complete Keygen improvements agree with the prior isolated PMU;
complete current results are in `OPTIMIZATION-ROADMAP.md` and `VALIDATION.md`.

Both requested source integrations are complete in order. Native Mac AArch64
and fresh Linux/Pi5 package tests pass. The subsequent isolated Pi5 campaign
also found a pre-existing noncanonical-ciphertext acceptance difference versus
new Official. See experiments/gt864-native-asm/INTEGRATED-PI-RESULTS.md; the
original pending-gate notes below are retained as integration history.

## Active callers

| Caller | Active path |
| --- | --- |
| Keygen f/g invertibility | gt864_native_poly_baseinv, direct FR0 R0 -> raw FR0 R0 bounded by 1972 |
| Keygen h/hinv products | Unchanged D1 R0 |
| Encaps BaseMulAdd | Unchanged D1 R0 |
| Decaps first c*f product | gt864_native_basemul_for_inverse, FR0 R^-1 output |
| Immediately following Inverse | gt864_native_inverse, natural centered R0 output |
| Decaps second product r2 | Unchanged D1 R0 |
| All ToBytes sites | Unchanged caller-selected full/small entries |

The Makefile aliases Keygen's poly_baseinv calls to the native adapter. kem.c
explicitly selects the paired Decaps functions. The old gt_d1_poly_baseinv and
gt_d1_poly_invntt remain legacy internal helpers, not the active KEM paths.
Only api.h is the supported public KEM API; this does not broaden the package
to arbitrary polynomial multiplication.

## Files and representation

- gt864_native.h / gt864_native.c: typed adapter API and table selection.
- gt864_native_public.S: unchanged measured AAPCS wrappers, failure handling
  and scratch clearing. BaseInv scratch 1200 bytes, Inverse scratch 1792 bytes,
  plus a 160-byte public ABI frame per operation.
- gt864_native_baseinv_{num,prefix,inverse,recover,finish}.S: five scheduled
  BaseInv cores, directly consuming FR0 without Official layout conversion.
- gt864_native_basemul.S: first-Decaps R^-1 product only. Both inputs come from
  FromBytes in [0,4095], including malformed bytes. Output bound is 2497.
  Both early REDCs and all three final REDCs remain; none were deleted here.
- gt864_native_inverse9.S, gt864_native_inverse16_lazy.S,
  gt864_native_inverse_tail_lazy.S, gt864_native_center32.S: consume R^-1,
  compensate it in terminal scale constants, then center the natural output.
- gt864_native_scaled_tables.h: exact experimental scaled table values, with
  a distinct include guard to avoid collision with the legacy R0 table header.

No arithmetic DAG, schedule, root, range or coefficient-memory boundary was
changed during import. audit-production-import.py checks all ten core
instruction streams against their measured candidate.opt.S artifacts, wrapper
byte identity and table identity; it also assembles AArch64 ELF and rejects
stack accesses in leaf cores. Production sources have no experiment-tree build
dependency. Mac symbol aliases and omission of schedule annotation comments do
not change the instructions.

The producer contracts are inherited from the tested source-identical
experiments and the 2026-09-10 consumer closure, not proven by KATs alone:
BaseInv accepts signed-int16 R0 and returns raw R0 bounded by 1972;
first-Decaps BaseMul inputs are [0,4095], its output is
bounded by 2497; inverse I9 terminal bounds and I16 peak 30939 are recorded in
the experimental contracts. The second D1 product is unchanged, so the small
ToBytes proof [-3023,3023] remains applicable. BaseInv's changed representatives
do not invalidate that final D1 output-range proof.

## Sequential validation

The baseline includes the previously integrated dual-entry ToBytes.

| Stage | Objects | KEM test | 100-case KAT |
| --- | ---: | --- | --- |
| Before native integration | 32 | pass | identical |
| BaseInv only | 39 | pass | identical |
| BaseInv + paired BaseMul/Inverse | 44 | pass | identical |

Each stage passes 64 valid KEM round trips and tampered rejection checks.
The full .rsp byte streams compare equal, SHA256:
0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c.

Actual production-built objects, not separately rebuilt experimental objects:

- BaseInv: 808 cases (517 success, 291 failure), every one of 288 injected
  zero-leaf positions, zero output on failure, exact in-place alias, output
  canaries, AAPCS and 1200-byte scratch wipe. Pass at both integration stages.
- Inverse: 256 inputs and 256 BaseMul R^-1 chains; independent cubic product
  identity, output range, exact alias, canaries, AAPCS and 1792-byte wipe. Pass.
- Three-way deterministic transcript comparison: 32 valid cases (exact
  pk/sk/ct/ss), 32 tampered cases and 1024 malformed ciphertext cases. Both
  status and returned shared-secret bytes match across all three builds.
  Transcript SHA256:
  2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67.
- KEM object references native BaseInv and the paired native functions;
  D1 BaseMul/Add, K1 Forward, FromBytes and dual-entry ToBytes remain selected.

## Security review scope

BaseInv scans all 24 terminal prefix lanes, then branches once on the aggregate
noninvertibility result. This is intentionally NOT a blanket no-secret-branch
claim: success/failure timing differs and Keygen retries on this result. The
old implementation also had a failure branch. Retaining this Keygen contract
does not establish a formal timing-leakage proof. No new lane-position early
exit was added. Output is cleared on failure; scratch is wiped on both paths.

BaseMul/Inverse loops and addresses depend on fixed public counters/pointers;
their arithmetic cores contain no data-dependent branch. Exact alias is tested;
partial overlap is unsupported. SIMD temporaries are cleared by the public
wrapper; this is not a claim that every possible secret register or the whole
caller's stack is erased. Canary tests are not guard-page overread proofs.
Security parameters, hash policy and sampling are unchanged.

## Reproduction and pending Linux gate

Use experiments/gt864-native-asm/verify-production-mac.py with a source path and
a fresh build directory. It uses make -Bn libgt864.so for source/flag selection
and links objects directly into Mac test/KAT executables, not a Linux .so.
verify-integrated-components.py <build> --both tests those actual objects.
compare-integrated-kem.py <baseline-build> <baseinv-build> <final-build> compares
the exact transcripts. audit-production-import.py checks source identity/ELF.

Current scratch artifacts: /tmp/gt864-native-integration.qa3hOP, containing
baseline source snapshot, baseinv-stage.tar, and separate baseline-build,
baseinv-build and final-build directories. Persistent identities are in the
source manifest and this report; scratch is disposable.

No new scheduling or benchmark was performed this integration turn. Previous
experimental Pi5 evidence is in experiments/gt864-native-asm/TIMING-RESULTS.md
and TOBYTES-TIMING-RESULTS.md, not a fresh measurement of this final package.
When the current SUPERCOP job is finished, run isolated Linux make check plus
paired package validation. The Official source for subsequent comparison is
/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64, not the 20260627 archive.
