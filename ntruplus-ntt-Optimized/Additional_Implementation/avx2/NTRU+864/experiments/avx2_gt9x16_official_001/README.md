# NTRU+864 AVX2 GT9x16 experiment 001

The immutable research baseline is `upstream/supercop-avx2`, imported from the
release pinned in `bench/supercop.lock`. Never edit it. Put handwritten C in
`src/`, assembly in `asm/`, reproducible generator output in `generated/`,
correctness checks in `tests/`, and experiment-specific benchmark adapters in
`bench/`.

Use a disposable campaign produced by `scripts/prepare_supercop.py`; candidate
installation refuses to target a pristine tree. Repository-local measurements
are diagnostic only. See the repository workflow document for formal gates.

The first shrunk-P1 packet arbitration is recorded in
`CHECKPOINT-P1-SHRUNK.md`. Reproduce its exact 864-cell packed/plane map with
`make p1-map-check`. The plane-major challenger stops before ASM because it
only relocates the same packet permutation and has no structural credit under
the frozen materialized top-split and coefficient-plane consumer boundaries.

The cross-parameter persistent frequency-domain ABI feasibility gate is
recorded in `CHECKPOINT-P3-NATIVE-COMPONENT-CONSUMER.md` and
`generated/p3-native-component-consumer.json`. Reproduce it with
`make p3-map-check`. It lowers the exact 18-route d=3 packed/plane network and
keeps the `vpmaddwd` path separate until its signed-32 reduction and repacking
cost is executable.

That follow-up is recorded in `CHECKPOINT-D3-VPMADDWD-REDUCTION-GATE.md`. The
exact `R=2^16` dword Montgomery reduction and non-saturating repack pass. The
full direct-packed cubic tile is optimistically 49 static instructions larger
than the selected 18-route conversion plus current BaseMul, but that does not
determine cycles because the execution-port and dependency structures differ.
A namespaced tile ASM and same-ELF paired microbenchmark are therefore the
next gate; full integration remains unauthorized.

`CHECKPOINT-D3-VPMADDWD-ASM0.md` records that machine gate. With both paths
starting from two packed T3 operands, the candidate is 4 cycles/tile slower
in 9/9 fresh launches under both normal and reversed function placement. The
MR32 primitive remains valid, but this cubic realization is not selected for
full BaseMul or Native SUPERCOP integration.
