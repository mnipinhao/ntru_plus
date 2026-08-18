# GT32-PLANE-N16-STOCKHAM-STAGES-007

This experiment answers the part left open by architecture audit 006:

> If the post-S1 eight-YMM state becomes persistently plane-major, what is
> the best structured radix-2 AVX2 schedule across N16 stages S2--S5?

Production GT Clean is not modified.  The experiment imports the exact
`GLOBAL-PHYSICAL-001` progressive sequence and the current pair-packed
sequence as controls instead of approximating them.

## Search and proof

The dynamic program searches layouts *between* all four stages.  Its states
cover affine bit permutations, branch complements/sum-difference placement,
and the production-usable AVX2 lane-route primitives.  It retains the full
multi-dimensional Pareto frontier over instructions, shuffle uops, load uops,
peak YMM, estimated bytes, and dependency depth.

The newly executable edge is an unpack-butterfly without reconstruction:

1. route the current butterfly bit to lane bit 2 when required;
2. use four `vpunpckl/h*` pairs to form four full low/high-arm YMM pairs;
3. execute the same four Montgomery chains;
4. retain sum/difference directly in the successor layout.

This costs 8 unpack shuffles instead of the old 16-shuffle local
extract/reconstruct stage.  S2 and S3 still each need an additional 8-shuffle
lane route, so the best persistent path totals 48 shuffles per tile.

All Pareto paths pass an exact 128-basis N16 matrix proof.  The range proof is
unchanged from qualified N5:

| checkpoint | bound |
|---|---:|
| post-S1 | 3456 |
| S2 | 5199 |
| S3 | 7011 |
| S4 | 8855 |
| S5 terminal | 10788 |

The executable allocator uses 13/14/15 YMM for folded/reuse-one/reuse-pair,
including 8 data registers, `q`, four Montgomery temporaries, and zero mask
registers.  No policy spills.

## Fair executable controls

- `progressive`: exact S2--S5 body extracted from
  `GLOBAL-PHYSICAL-001`, including its exact states, twiddles, and final
  transition.
- `pair`: exact current pair-packed S2--S5 plus the required 24-shuffle
  AoS-to-plane deposit.
- `folded`, `reuse_one`, `reuse_pair`: the same persistent-plane arithmetic
  and physical schedule with only the constant policy changed.

All five functions pass 1,000 random differential trials and `out == in`
alias tests against the same scalar N16 oracle.

## Multi-launch result

Environment: Intel Core Ultra 7 155H, CPU 1 affinity, 8 process launches,
20 paired TSC samples per launch, 100,000 calls per sample.  PMU numbers below
are medians over launches.  Counts include the fixed benchmark call/loop
overhead equally for every row.

| candidate | TSC | core cycles | instructions | loads | stores | port 5/11 uops |
|---|---:|---:|---:|---:|---:|---:|
| progressive | **41.254** | **66.697** | **161** | 42 | 9 | **46.424** |
| reuse-pair | 42.999 | 69.702 | 177 | **18** | 9 | 50.428 |
| folded | 43.318 | 70.255 | 169 | 42 | 9 | 50.448 |
| reuse-one | 43.527 | 70.429 | 173 | 30 | 9 | 50.254 |
| pair-packed + plane deposit | 48.660 | 78.378 | 185 | 42 | 9 | 51.042 |

`reuse_pair` is the best persistent-plane policy.  Relative to folded it
retires 24 fewer loads and 8 more instructions, but improves only 0.552 core
cycles.  Relative to progressive it is 3.005 core cycles and 1.744 TSC slower;
progressive wins in all 8 launch medians.

Frontend counters show all bodies are overwhelmingly DSB-delivered.  There is
no spill traffic.  The loss is therefore not a hidden MITE or stack-spill
failure: the persistent path still executes 8 more shuffles and 16 more
retired instructions than progressive after its load reuse is accounted for.

## Decision

Do not promote the persistent plane-major radix-2 schedule.  The answers are:

1. minimum structured persistent permutation cost: **48 shuffles/tile**;
2. 32 folded twiddle operand loads can become 8 explicit pair loads, but the
   realized gain is only **0.552 core cycles**;
3. the combined executable plane-major candidate does **not** beat the exact
   progressive control.

This closes only the structured affine radix-2 persistent-plane N16 family in
this stage library.  It does not close:

- a hybrid terminal chosen jointly with a downstream consumer;
- radix-4 N16 (reserved for 008);
- a new primitive that removes the remaining S2/S3 lane-route layer.

## Reproduction

```sh
make check
make build/bench_stockham
python3 tools/run_benchmark.py \
  --binary ./build/bench_stockham --launches 8 --iterations 100000 --cpu 1 \
  --output generated/plane_n16_stockham_benchmark.json
make report
```

Primary artifacts:

- `generated/plane_n16_stockham_gate.json`: Pareto search and proofs;
- `generated/plane_n16_probe.S`: persistent-plane executable candidates;
- `generated/progressive_control.S`: exact progressive control;
- `generated/pair_control.S`: exact pair-packed control;
- `generated/plane_n16_stockham_benchmark.json`: raw multi-launch samples;
- `generated/plane_n16_stockham_decision.json`: joined decision record.
