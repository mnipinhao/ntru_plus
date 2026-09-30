# Per-operation margins against the official implementation

This tool produces the performance rows of the package READMEs: "M2 Pro" and
"Cortex-A76" against Official, and the "same Keccak permutation" rows.  It
also produces the sentence that splits the latter into GT's hash layer and its
arithmetic.

## Builds

For each parameter set, `build.sh` links the same harness (`perop.c`) and the
same deterministic `randombytes` against five KEMs:

| binary | KEM | machines |
|---|---|---|
| `offm<set>_noce` | official, main's `NO_CE` build (scalar Keccak) | M2, Pi 5 |
| `offm<set>_ce` | official, main's default build (`CE/`: FEAT_SHA3 Keccak) | M2 |
| `offm<set>_gtk` | official, main's CE sponge calling GT's permutation (FEAT_SHA3 on M2, scalar on the Pi) | M2, Pi 5 |
| `gt<set>_offhash` | GT's arithmetic and KEM flow with that same sponge and permutation | M2, Pi 5 |
| `gt<set>` | the production package, built from its own Makefile's sources and `CFLAGS` | M2, Pi 5 |

The rows against Official compare `gt` with `offm_ce` on M2 and with
`offm_noce` on the Pi.  The "same Keccak permutation" rows compare `gt` with
`offm_gtk`.  `gt_offhash` then splits that lead into GT's hash layer (`gt`
against `gt_offhash`) and the arithmetic (`gt_offhash` against `offm_gtk`).

The official builds come from `../../official/`.  GT's permutation is the
measured package's own `keccakf1600_v84a.S` or `keccakf1600.S`, reached
through a one-instruction `f1600` adapter.  Both machines use the same
compiler for both sides: Apple clang on M2, gcc on the Pi.

## Measurement

`perop.c` times batches of 100 calls of one operation.  Before each batch it
reseeds the deterministic generator, so every build performs the same key
generations, including key generation's retries.  The three operations take
turns within each of 401 rounds.

Each batch is followed by a clock witness, a dependent chain of `add`s whose
time is a direct clock reading.  A batch counts only when its witness is within
2% of the run's fastest.  A run prints, per operation, the fastest accepted
batch in ns per call, the clock ceiling it saw, and how many batches passed.

`run_sessions.sh` runs every build once per session, round robin.
`tables.py` reports the median over the sessions.

On M2 the gate replaces a frequency lock the part does not offer.  It cannot
detect one case: another busy core in the cluster keeps the whole run at
3,408 MHz instead of the single-core 3,504 MHz, and every figure reads about
2.8% high.  Check `clock_ceiling`, or give `tables.py` a minimum ceiling so it
skips those runs.  The Pi 5 runs at a fixed 2.4 GHz; pin the runs to one core.

## Run

```sh
../../official/setup.sh /tmp/official /path/to/supercop-20260831
./check.sh /tmp/official m2 /tmp/perop-check       # every build gives the same outputs
./build.sh /tmp/official m2 /tmp/perop
./run_sessions.sh /tmp/perop 3 > runs_m2.txt
./tables.py runs_m2.txt 3480
```

On the Pi 5, use `pi` instead of `m2`, and run on core 3:

```sh
./run_sessions.sh /tmp/perop 3 taskset -c 3 > runs_pi.txt
./tables.py runs_pi.txt
```

`PRODUCTION=/path/to/aarch64` measures other packages than this repository's
`production/Additional_Implementation/aarch64`.

Three sessions take about three minutes on each machine.  On a busy M2 many
runs fail the 20-batch minimum or the ceiling.  In that case, add sessions to
the same file until every build has three runs.  `tables.py` prints how many
runs each figure used.

## Reproducibility

On 2026-09-28 this tool reproduced every margin in the package READMEs within
0.2 percentage points on the M2 and 0.1 on the Pi 5, and every build's median
within 0.24% and 0.14%.  `check.sh` found every build of a set giving the same
outputs, on both machines, and the M2 and Pi outputs are the same.
