# P3B29 — small-input raw-top result

Decision: **accept as the experimental small-input Forward champion**.
Production unchanged. T1 general-input baseline remains available. P3B6
ToBytes is NOT integrated into this candidate; it still uses r9_to.

## Correctness and scope

- P3B28 complete range proof rerun before generation.
- 256 guard cases per Forward process: both allocation edges, disjoint/exact alias.
- 64 Forward cases per process: T1/raw/SUPERCOP serialized bytes match.
- 32 complete raw 2F + D1 BaseMul + Inverse products match schoolbook.
- Full-KEM eight valid/tampered cases and instrumented equivalence pass before timing.
- No claim of bit-exact intermediate representatives or general-input safety.

## Forward paired PMU

Pi 5 Cortex-A76, GCC 14.2.0, CPU 3, three repetitions, both orders.
61 samples/order, 400 calls/sample. Every timed call includes the same
input reset; these are not pure NTT absolute timings.

| Variant | cycles | instructions | branches |
|---|---:|---:|---:|
| t1 | 4233.285 | 4665.148 | 68.032 |
| raw | 4045.347 | 4537.148 | 68.032 |
| sc | 3853.238 | 3736.137 | 57.030 |

Raw saves 187.938 cycles versus T1; remaining SUPERCOP gap is 192.109 cycles.
SUPERCOP is the unchanged P3B25 source snapshot, upstream latest not verified.

## Full-KEM paired PMU

41 samples/API/order; keygen 4 iterations, encaps/decaps 20.

| API | T1 | raw | delta cycles | delta instructions |
|---|---:|---:|---:|---:|
| keygen | 55580.875 | 55234.500 | -346.375 | -256 |
| encaps | 47584.575 | 47167.300 | -417.275 | -256 |
| decaps | 45909.950 | 45521.800 | -388.150 | -256 |

Per-repetition deltas, both orders pooled:

| Repetition | Forward | Keygen | Encaps | Decaps |
|---|---:|---:|---:|---:|
| 1 | -187.938 | -370.625 | -411.525 | -387.100 |
| 2 | -187.934 | -370.250 | -417.225 | -383.425 |
| 3 | -187.938 | -456.500 | -423.900 | -399.125 |

## Object audit and decision

Source delta is exactly top split plus two symbol-reference changes.
Eight static instructions removed; top object 276 -> 244 bytes.
Actual linked wrapper targets small_input. Four MULs remain per loop;
no SQRDMULH or MLS remains in top. Loads/stores, register allocation and
ABI save/restore are unchanged by construction; no spill is introduced.
PMU agrees: -128 instructions/Forward, -256 per KEM, unchanged branches.
No new Slothy run, layout change, or constant-setup cleanup was mixed in.

Reproduce: `python3 run.py --prepare`, `python3 run.py --run`,
`python3 run.py --product`, `python3 summarize.py`.
Exact source hashes, raw logs, object hashes and JSON metrics are in build/.

Next: combine the independently verified P3B6 ToBytes with this small-input
Forward in a separate full-KEM candidate; do not add historical cycle gains
and label the sum a measurement. General GT API and production stay unchanged.
