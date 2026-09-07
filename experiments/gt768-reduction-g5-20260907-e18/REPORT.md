# G5 — Maintained-source integration and release-shaped gate

## Status and revisions

**Integration, correctness, namespace/export and performance gates PASS.**
Keep as a reviewed integration candidate; `aarch64-production` is not changed.

- ID/branch: `gt768-reduction-g5-20260907-e18` /
  `codex/gt768-reduction-g5-20260907-e18`.
- Baseline reorganized source: `14daa263b10fbadb6d3765685529a17d18882593`.
- Candidate source commit: `b6b7854347417d012e229f8e23f8b795d0959d63`.
- Previous formal Production reference: `d598969f830090de33ca9cc2462e102b668e437e`.
- Source hashes are sealed in `sealed.json` and package SOURCE-MANIFEST.sha256.
- No Official or KPQC implementation was rebenchmarked in this gate; the
  measurement is old GT versus integrated GT under the real SUPERCOP driver.
- No Slothy or new arithmetic optimization was introduced.

## Changes made

Nine package files change. Unlike G3/G4, the new entry is now maintained in the
package's normal ntt.S and reached directly from kem.c; no generated overlay or
external source dependency is needed to build/use the package.

- New `poly_ntt_encap_small_lazy` entry: signed [-2,2] input, same layout and
  modulo-q scaling, output [-21050,21050], in-place permitted.
- Both Encap Forward calls use that entry. G4's shared frontend/tables/late stages
  and three private Stage12 blocks are preserved.
- Old `poly_ntt_encap_small` remains raw-bit-exact to generic loose NTT. Its test
  remains active. New modular/range/alias/pack tests run alongside it.
- New ABI sentinel and required ABI case cover the maintained symbol.
- ntt_internal.h and README document the separate contracts.
- Release checker requires the actual new KEM consumer; manifest hashes updated.
- Exporter itself is unchanged: it discovers and namespaces the new definition
  automatically. Linux namespaced ABI is compiled and tested separately.

No basemul, pack, randombytes, zeroization, Keygen or Decap arithmetic changes.
The original raw-exact entry's mathematical contract is preserved, though its
shared generic path retains G4's dispatch overhead.

## G4 equivalence and code size

Mac NTT object __text bytes exactly match G4 candidate after symbol rename.
No scheduling or arithmetic changed during integration. The final Linux leaf
was sealed against the measured leaf: the only export difference is an ELF
function-type annotation for the new entry; all other normalized assembly
lines and all other leaf files are identical. Final package and exported-leaf
KAT were rerun after this metadata annotation. See `seal.py` / `sealed.json`.

Linux exported KAT executable text:

| Version | Text bytes |
|---|---:|
| Baseline | 123711 |
| Maintained candidate | 125375 |

Net growth remains **1664 bytes**, not G3's ~16 KiB. G2/G4 numeric proof and
dispatch/liveness evidence remain the basis for the new endpoint's contract;
this integration gate does not claim a separate formal proof of the entire KEM.

## Verification

Mac and final Pi5 package `make check` passed: manifest/release, KEM round trip,
required ABI, 9216 canonical/failure cases, old exact small tests plus 4096 lazy
modular/range/alias/pack cases, zeroization and full KAT req/rsp equality.
The expected KAT response SHA256 remains:
`22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.

Exported Linux baseline/candidate KAT and six-path clear coverage match.
The new leaf's namespaced ABI reports required_abi_mask=0. The pre-existing
non-required internal_custom_mask=0x3fc00 remains, not claimed as all-zero.
Encap clear coverage remains 16 calls / 6410 bytes. Invalid and noncanonical
paths retain identical clear coverage. This is not a no-clear comparison.

## Full SUPERCOP comparison

Pi5 pi@100.99.191.9; core3; Linux 6.18.33+rpt-rpi-2712; GCC 14.2.0.
Isolated SUPERCOP-20260627 driver, four rounds with alternating order.
Each run uses the median of its three SUPERCOP cycle rows; aggregate is median
of four run medians. Raw row values, compiler metadata, environment and result
paths are in `performance.json`. Recorded throttle states are all 0x0.

| Version | Keygen cycles | Encap cycles | Decap cycles |
|---|---:|---:|---:|
| Baseline | 36336 | 37255.5 | 32509.5 |
| Integrated candidate | 36359 | **37115.5** | 32492.5 |

Encap improvement: **140 cycles, 0.376%**. Per-round savings:
**170,141,90,189 cycles**, all positive. This is not a confidence-interval study.
Small Keygen/Decap changes are not algorithmic improvements/regressions claimed
by this experiment; their arithmetic was unchanged.

## Reproduce and handoff

Local package: `make check BUILD_DIR=<experiment>/.build/mac`.
Pi staging root: `/home/pi/gt768-reduction-g5-20260907-e18`.
Run `pi_gate.py` in a fresh experiment staging directory for package, leaf,
namespaced ABI, cleanup and benchmark. The script uses the existing isolated
GT baseline leaf and common SUPERCOP driver at their recorded absolute paths.
`seal.py` verifies final-source equivalence to the measured leaf and repeats
final package/exported KAT gates.

Raw outputs and executables stay under gitignored `.build`; persistent source
is the candidate commit rather than a permanent generated kernel copy.

The remaining administrative step is explicit merge/cherry-pick into the desired
formal branch. No such branch mutation or push was performed. If promotion also
requires refreshed Official/KPQC comparisons, run those before that merge; this
gate should not be presented as a new measurement against either implementation.
