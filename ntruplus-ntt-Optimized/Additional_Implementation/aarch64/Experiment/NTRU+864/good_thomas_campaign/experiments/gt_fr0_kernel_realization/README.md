# M5A: fused FR-0 kernel realization
Generated binaries, disassembly reports, JSON proofs, and tables live under
ignored `build/`. Production does not include or link this directory.
This closed, default-off experiment answers one question: can M4's fixed-row
P8+tail-to-SoA boundary be realized as readable AArch64 Neon assembly with no
coefficient spill, while preserving exact representatives and giving explicit
range and consumer-map contracts?

The answer is yes. `gt864_boundary_fr0_asm` invokes a stackless leaf block 12
times: `2 top branches * 3 cubic components * 2 eight-column blocks`.  Each
block transposes eight `s=0..7` column vectors into `v0..v7`, constructs `s=8`
in `v16` with eight exact halfword loads, twists `v1..v8`, executes the six
oriented B3 butterflies, and stores nine BaseMul-SoA row vectors.

Run the reproducible gates with:

```sh
make check
make bench                 # diagnostic only, never a SUPERCOP claim
```

Read `REGISTER_BUDGET.md`, `RANGE_PROOF.md`, `results.md`, then `DECISION.md`.
Generated binaries, disassembly reports, JSON proofs, and tables live under
ignored `build/`. Production does not include or link this directory.
