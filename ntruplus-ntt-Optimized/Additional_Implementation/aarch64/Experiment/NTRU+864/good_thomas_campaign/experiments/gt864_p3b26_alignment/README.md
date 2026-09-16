# P3B26 / P3B27 frozen candidate alignment

Status: complete; both independent substitutions pass full-KEM correctness and
paired PMU. See results.md. Production unchanged; combined candidate unmeasured.

Baseline: P3B25 frozen GT (P3B23 FromBytes, D1 BaseMul, T0 Forward,
r9_to ToBytes), repository HEAD cf8d3dba459bf9e5fc8e3e67dc84519b50f776f7.
The worktree contains uncommitted campaign files; build/source-hashes.json
identifies the actual sources, not HEAD alone.

P3B26 hypothesis: replacing the complete T0 Forward with the existing A1 T1
wrapper, including its in-place tail layout preparation, saves about 67 cycles
per Forward / 133 cycles per KEM. Category: layout/memory. Same FR0 output,
arithmetic and range contract, original T1 physical register allocation; no new
Slothy scheduling. Falsifier: paired full-KEM or Forward component regression.

P3B27 hypothesis: independently replacing only r9_to with P3B6 input-once
ToBytes saves about 346 cycles per call. Category: layout/memory. Same canonical
wire bytes and normalization; no coefficient scratch or spills expected.
Falsifier: differential bytes mismatch, spills, or full-KEM regression.

The two substitutions are never combined in these measurements. SUPERCOP is
the frozen P3B25 imported aarch64 source snapshot; upstream latest not verified.
Compiler flags, RNG, samples, KEM harness and profiling boundaries are inherited
unchanged from P3B25. Separate DSOs prevent symbol/ABI interposition.

Run `python3 run.py --prepare`, then `python3 run.py --run`. The latter uploads
only build/sync to pi@100.99.191.9 under the named experiment directory.
Each process validates eight valid/tampered KEM cases and instrumented/non-
instrumented equivalence before timing. Three repetitions, both execution
orders, CPU 3. Raw logs and source/object hashes remain under ignored build/.

Run `python3 run.py --forward` for the common-input-reset Forward diagnostic;
then `python3 summarize.py` to check source deltas and target-object calls/spills
and reproduce results.md. The initial build lacked the P3B6 header; it failed
before any timing. The runner now stages that original header explicitly.
