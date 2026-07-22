# Canonical pack next wave

This experiment keeps the GT arithmetic layout and production default unchanged.
It studies the fixed GT-to-KPQC serialization boundary in two independent ways:

1. shorten the one-chunk pack dependency path by moving lane-wise
   canonicalization before the 8x8 transpose;
2. model source-major grouping before authoring any source-major assembly.

The existing production chunk is the exact baseline. Candidate assembly may be
generated only after `baseline-contract.yml` and `kernel-contract.yml` pass the
canonical Slothy contract checker.

Status: `investigate`.

## Slothy model scope

The symbolic candidates use the repository's Neoverse-N1 model as the closest
available Cortex-A76 scheduling model. The experiment driver adds two missing
instruction forms without modifying the Slothy checkout:

- fixed-offset `ldr d, [base, #imm]`, inheriting the existing `Ldr_D` LSU model;
- three-register post-increment `st1`, modeled with consecutive vector inputs,
  inverse throughput 3, and pointer-update latency 4.

Runs use a 300-second CP-SAT internal timeout so a `FEASIBLE` best-known
schedule is written out normally. A model cycle count is not a Pi5 PMU result,
and a timed-out feasible result is not claimed to be optimal.

The symbolic lane assembly uses the `mov Vd.d[1], Va.d[0]` alias because this
Slothy version models it directly. It has the same lane-copy encoding semantics
as the original `ins` spelling.

## Local gates

```sh
python3 extract_pack_chunk.py
./run_static_gates.sh
make -B test_gt_canonical_serialization_asm
make -B test_gt_canonical_pack_boundary
make -B test_gt_canonical_pack_chunk_candidates
make -B test_gt_canonical_pack_full_candidates
python3 source_major_model.py
```

`run_static_gates.sh` resolves the installed Codex skill scripts through
`$CODEX_HOME` and checks the contracts and symbolic source when present.

See `results.md` for the frozen Slothy outputs, correctness status, and pending
Pi5 PMU commands. `artifact_hashes.json` records the exact symbolic, driver,
physical-output, and log hashes used by that report.
