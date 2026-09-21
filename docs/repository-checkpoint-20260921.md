# Repository checkpoint inventory — 2026-09-21

Development is paused for repository organization. No production source,
pristine SUPERCOP snapshot, frozen package, or public API is changed by this
cleanup. No files are deleted or relocated; campaign paths remain valid.

## Branch and starting state

- Branch: `avx2-gt-ntt-864-1152`.
- Starting HEAD: `1ed8168` (`docs: track the avx2-gt-ntt-864-1152 branch rename`).
- Starting `git status --short --untracked-files=all`: 116,568 entries.
- Tracked modifications: 19 files, 501 insertions and 42 deletions.
- 113,774 untracked files belong to
  `results/encap-wavefront-native-20260921/supercop/`, a disposable working copy.
- Outside that copy, 53 untracked ELF files were identified by ELF magic:
  49 named `measure`, four named `check-sanitize`.

The status volume is principally a missing artifact-ignore rule, not evidence
of 116,568 source edits or of an incorrect branch.

## Preservation policy

| Content | Treatment |
| --- | --- |
| Experiment source, tests, generators, generated ASM | Keep visible to Git; review and commit by topic |
| Range/mapping contracts, generated proof ledgers | Keep visible; not disposable build output |
| Reports, STATUS, metadata, source hashes, measured source copies | Keep visible and preserve campaign provenance |
| Raw observations and logs newly visible under root results | Preserve; do not blanket-ignore or delete |
| Disposable SUPERCOP working copy | Ignore this exact campaign path; preserve on disk |
| Fixed `measure` and sanitizer ELF files | Ignore scoped basenames; preserve locally for replay |

Ignored does not mean backed up. Before any future disk cleanup, archive the
campaign (including fixed ELFs and raw data), verify archive hashes and recovery,
then obtain explicit deletion approval. Rebuilding an ELF is not a substitute
for retaining the measured ELF. Existing ignore rules are not retroactively
treated as permission to delete evidence.

## Proposed review / commit groups

1. **Repository hygiene**: this inventory and narrow `.gitignore` additions.
2. **Pinned benchmark infrastructure**: lock, source-management scripts,
   benchmark/paired runners, common harness, API/KAT/PMU tools. Verify the
   existing lock change separately; cleanup does not refresh upstream.
3. **Cross-parameter reassessment**: 768/864/1152 report, diagnostic harnesses,
   campaign summaries and provenance. Preserve Native versus derived labels.
4. **768 survey and redesign gates**: survey, priorities, A/B/C gate generator
   and evidence; do not relabel historical scoped failures as global proofs.
5. **768 Encap range closure and wavefront**: generators, two namespaced ASM
   files, def-use/range ledgers, tests/runners, Makefile/STATUS and results.
   Preserve the negative Native result; neither prototype is promoted.
6. **Small independent provenance correction**: the existing 1152 generated
   JSON wording change (`Natural-Q machine wire basis`) needs separate review.

The user authorized topic commits on the existing branch. Checkpoints created:

- `fc08db9`: repository hygiene and proof-refinement proposal.
- `a7e016c`: pinned benchmark infrastructure (including existing scripts).
- `175f23d`: reassessment, surveys and campaign evidence.
- `cf15efe`: 768 range closure, redesign and wavefront evidence.
- `0821e73`: 1152 machine-wire-basis wording correction.

The worktree was clean after these five commits. Existing Python sources passed
syntax parsing and no newly staged file had ELF magic. Native raw output and
Markdown hard-break whitespace were preserved, rather than rewriting historical
evidence to satisfy whitespace warnings. These are preservation checkpoints,
not a fresh correctness/security audit or promotion of every historical result.
Fixed binaries and the disposable snapshot remain local and ignored.

## Where to resume

- Current 768 development narrative: `docs/ntruplus768-forward-redesign.md`.
- Experiment: `ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_gt32_tile4_official_001/`.
- Native wavefront campaign: `results/encap-wavefront-native-20260921/`.
- Future proof refinement: `docs/avx2-range-proof-refinement.md`.

Finish checkpoint review before starting another optimization. In particular,
do not mix a new reduction removal with repository cleanup.
