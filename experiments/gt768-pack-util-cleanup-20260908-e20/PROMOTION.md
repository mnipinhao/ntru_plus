# e20 checked-unpack-only promotion

User explicitly requested checked unpack in aarch64-production on 2026-09-08.
Previous champion: ce617c87a39412958cddea17f10809fd2e0b3a3f.
Source candidate: 561b6aa50dc0e237c3c884ec7174a208baf869e5.
Full candidate record: d09afbb4, branch codex/gt768-pack-util-cleanup-20260908-e20.
Decision: accept U only; champion is the commit containing this promotion record.

Only package pack.S and its SOURCE-MANIFEST.sha256 entry change. The pack.S
hash is 5da6dc136c5909df966c661213d5d1f236f3d5cc3ab2d8dcaecc3bf0906b5a62,
identical to the measured e20 unpack-only source. All 12 changed regions are
inside poly_frombytes_encap. No loose reducer, mod3, subtraction, util helper,
cleanup policy, legacy removal, NTT, or basemul change is promoted.

The promoted mapping eliminates 96 TRN.2D instructions without changing decode,
global-max checks, output addresses, byte mapping, ABI, arithmetic or stores.
E20 symbolic and differential evidence is retained on its experiment branch.
Single-component Pi result: 549.21 -> 512.98 cycles. Same-contract SUPERCOP
unpack-only Encap result: 37152 -> 37140 cycles, a small/noisy difference, not a
claim of a stable full-KEM improvement. This is an explicit user-requested
mapping promotion, not a claim of completed Slothy optimization.

Fresh unpack-only package make check passed on Mac and Pi: manifest, KEM,
required ABI, canonical/failure, small-NTT, zeroization and exact KAT.
KAT rsp SHA256: 22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8.
Mac BUILD_DIR: /tmp/gt768-e20-unpack-promotion-mac.
Pi source: /home/pi/gt768-pack-util-cleanup-20260908-e20/.build/promoted-unpack-source.
Pi BUILD_DIR: /home/pi/gt768-pack-util-cleanup-20260908-e20/.build/promoted-unpack-check.
Pi log: /home/pi/gt768-pack-util-cleanup-20260908-e20/.build/promoted-unpack-check.log.
No new timing run was necessary: the prior unpack-only leaf is this exact
arithmetic/mapping variant. No push was requested or performed.

## Slothy backlog audit of the full e20 candidate

Audit is read-only; no solver run or candidate generation in this turn.

1. New checked unpack mapping: no Slothy run for its new DAG. Highest priority:
   one exact chunk, decode/global-max -> H/S transpose -> UMOV/D scatter stores.
   Preserve max-chain live state, pointer increments and exact per-chunk store
   offsets. Do not assume all 12 textual mappings are interchangeable. Start
   with one chunk including consumers, not the entire unrolled polynomial.
2. Current production loose reducer + compact consumer: e20 P0/P1 were
   handwritten and not solver-scheduled. They regressed and are rejected as
   implemented. A new schedule-only gate around the original 24-op reducer,
   canonical correction and first consuming bitpack nodes remains possible;
   avoid duplicating twelve full cores. This is not the old S0 DAG.
3. G5 lazy Encap Stage12: the latest deleted-reduction DAG was integrated
   without a fresh Slothy run (G4/G5 records). Older shared frontend/late-stage
   schedules do not certify this changed DAG. Use a bounded stripe/tail with
   exact F012 live-outs; do not reschedule the entire NTT or change its range.
4. New e20 crepmod3: four-vector centered-mod3 loop is handwritten, no Slothy
   result. Lower priority, full candidate only. Preserve [-3456,3456] contract,
   alias safety and the corrected q-centering semantics.
5. Decap D1: NOT an unrun tail. e04 (82b3f5b5) integrated a Mac Slothy
   24-instruction N1-proxy result and measured 1992 -> 2015 cycles: rejected.
   Its documented reopen direction is a new tail + tuple ST1 consumer window.
   Do not claim the rejected isolated tail is pending or promoted.

Old S0 (6ed8d735) also already ran all twelve 64-instruction native-layout
windows on the remote A76 model: correct but 26--28 cycles slower, rejected.
That native-layout P0-A1 contract differs from current scattered-load pack.
Existing base.S and ntt.S retain documented Slothy-scheduled kernels; missing
a new run after integration does not mean none of their history used Slothy.
File renames, util.h and removal of uncalled code have no scheduling task.

Priority recommendation: checked unpack consumer window, original loose
reducer + consumer control, then G5 lazy Stage12. Consider new mod3 and expanded
D1 only with component measurements. Every new run requires its own exact
baseline/kernel contracts, valid solver output and Pi verification; static
model improvements are not performance evidence.
