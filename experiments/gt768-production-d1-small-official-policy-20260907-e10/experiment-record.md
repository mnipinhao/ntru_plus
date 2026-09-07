# GT768 Production integration — e10

Experiment ID: `gt768-production-d1-small-official-policy-20260907-e10`.
Decision: **accept**. Integrate readable source; no compiler-lowered package.

## Revisions and scope

- Previous Production/champion: `0bdc5798d848c25c09e308ab4a9de2cda250d0c1`.
- Accepted source/champion: `dcfce09ede48e5276d3a7a7ef908b4734ceb6005`.
- Candidate branch: `codex/gt768-production-d1-small-official-policy-20260907-e10`.
- D1 source: e03 `954832c6acfcbbf1590976bdfe860ee03445694d`.
- Prior integration evidence: e08 `d2f11ff6`, e09 `5e0faa34`.
- Official: `/home/pi/supercop-20260627/crypto_kem/ntruplus768/aarch64`.
  This is a source snapshot, not a claimed Git main revision. Every Official
  file hash is retained in `gate-summary.json:official_sources`.

The production directory is
`ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768`.
Only D1 verification basemul, Encap-small (two Encap Forward calls), and the
explicitly authorized lower-clear policy are integrated. Generic/Keygen/
Decap Forward and Production pack/basemul layout remain in place. No native
P/M consumer overlay, compiler-flattened trim, or loose-pack experiment is
promoted. The release source manifest covers all package files.

## Correctness, ABI and linkage

- Mac Apple Clang and Pi GCC14.2 `make check`: pass.
- 100 KEM round trips; canonical-input rejection gate: pass.
- 4096 signed [-2,2] Forward fixtures, exact generic-vs-small output and
  in-place alias: pass. The shortcut is NOT valid for arbitrary signed16 input.
- NIST KAT req/rsp are byte-exact. Rsp SHA256:
  `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.
- Required AAPCS64 mask = 0, including new Encap-small endpoint. Existing
  custom internal helper mask remains `0x3fc00`; these are not public ABI.
- Candidate and Official public KEM ABI masks = 0.
- Source-derived flattened leaves pass standalone KAT and six-path cleanup.
- Linked disassembly has exactly two BL sites to Encap-small. All linked
  candidate source hashes match the readable local package.
- No Slothy run or arithmetic re-factorization was performed in this gate.

## Cleanup policy

Same Official-style policy, **not identical memory topology or full erasure**.
Retain C secret buffers; reuse Keygen sample/h storage and Encap ciphertext
workspace; omit public h/hash_f-image clearing; use Official inline SHAKE
contexts through the package clear primitive. Remove only P0-B assembly wipe
blocks while preserving ABI restore instructions. Existing short keygen
prepare/fqinv register wipes remain. No full-frame/register-remanence claim.

Seed-123 audited explicit C clear calls/bytes:

| Path | Old Production | Candidate | Official |
|---|---:|---:|---:|
| Keygen | 23 / 16233 | 20 / 13352 | 20 / 11048 |
| Encap | 19 / 10251 | 16 / 6410 | 16 / 6410 |
| Decap valid | 9 / 10930 | 9 / 10930 | 16 / 11154 |
| Decap verification failure | 9 / 10930 | 9 / 10930 | 16 / 11154 |
| Decap noncanonical | 2 / 8608 | 2 / 8608 | 9 / 8832 |
| Encap invalid PK | 4 / 2816 | 2 / 128 | 2 / 128 |

Candidate trace exactly matches the validated e09 same-policy small leaf.
GT-specific inversion scratch accounts for extra Keygen bytes; Decap uses
different storage lifetimes. Invalid-PK ciphertext is zeroed normally, not
counted as an explicit clear. All audited bytes are zero after each clear.

## Complete SUPERCOP benchmark

Physical isolated SUPERCOP tree; never run the original tree's scripts
through symlinks. Three full invocations per leaf, rotated order, core 3.
Each invocation produces three samples per operation; take within-invocation
median, then median of three invocations. This is not the 62x2000 paired loop.

| Implementation | Keygen | Encap | Decap |
|---|---:|---:|---:|
| Old Production | 36914 | 38189 | 33073 |
| Accepted candidate | **36300** | **37309** | **32502** |
| Official | 38417 | 38584 | 33530 |
| Improvement vs old Production | 1.66% | 2.30% | 1.73% |
| Improvement vs Official | 5.51% | 3.30% | 3.07% |

All nine invocations selected GCC14.2:
`-march=native -mtune=native -O3 -fwrapv -fPIC -fPIE -gdwarf-4 -Wall`.
All use the same SUPERCOP `timingleaks` classification; Official goal markers
are omitted only in its staging copy. This classification is not a TIMECOP
or constant-time security claim. Every start/end throttle reading is 0x0;
highest observed benchmark temperature 66.4 C.

The improvement includes cleanup/backend changes and must not be attributed
entirely to D1 or Encap-small arithmetic. Their independent same-policy
attribution was established in e09.

Standalone no-GC KAT ELF `size text` (includes harness/constants): old
Production 135000, candidate 126815, Official 43031 bytes. Candidate remains
substantially larger than Official; this is not a code-size parity claim.

## Dynamic dispatch control

200000 Forward calls, three perf repetitions per mode in the same candidate.
Small saves approximately **95 instructions/call** relative to this candidate's
generic entry. It deletes 96 arithmetic instructions and adds one suffix
branch. The new generic dispatcher itself adds four instructions relative
to the previous generic, explaining the earlier e09 net **91** comparison.
An initial audit incorrectly expected 91 for the same-candidate comparison;
the model was corrected, with no source change, and the check repeated.
This verifies execution of the specialized frontend, not merely its linkage.

## Reproduction and artifacts

Pi: `ssh pi@100.99.191.9`, root
`/home/pi/gt768-production-d1-small-official-policy-20260907-e10`.

1. Stage the committed production directory as `NTRU+768` there.
2. Run `python3 -u run_gate.py` then `python3 -u final_audit.py`.
3. Source package gate is `make check BUILD_DIR=<experiment>/.build/package`.
4. Remote driver reuses e09 `common.py` helpers and e08 frozen Production/
   coverage/shim inputs, plus the established deterministic benchmark RNG.
   These dependencies and paths are explicit in the drivers; they must be
   available to reproduce this exact harness. Official headers and cryptoint
   objects are required for its standalone validation, supplied by SUPERCOP.

Persistent: this record, scoreboard, drivers, summarized results, source and
export hashes, compiler/environment metadata. Ephemeral: `.build/` objects,
executables, disassembly, PMU logs, raw runner output and isolated SUPERCOP.
No redundant permanent candidate source copy; the Git source commit is the
reproducibility identity. `integrate.py` is a one-time patch-construction aid,
not needed to build or benchmark the committed package.
