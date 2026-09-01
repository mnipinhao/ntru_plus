# M5K: both NTT9 column blocks live-through hard gate

M5K answers the pressure question left by M5J for one `(top,component)` bank:
can all sixteen NTT16 columns be consumed as two complete eight-column NTT9
blocks without coefficient memory traffic, while the first block's nine
outputs remain live throughout the second block?

The source is generated from the frozen M5J and M5I symbolic regions so the
second core cannot silently drift. `generate_symbolic.py` keeps M5J's first
190 instructions, captures the fixed second-tail register with
`orr hold8,v16,v16`, emits eight second-block Algorithm-10 twists, and appends
a fully SSA-renamed M5I core. Only the second inputs and outputs are remapped;
all internal values receive a `second_` prefix.

The fixed-register detail is essential. `v16` contains row `s=8`, columns
8..15 at entry. Its first occurrence in both returned artifacts is the capture
instruction after the first complete NTT9. Therefore Slothy must preserve that
value across all earlier transpose, twist, and NTT9 instructions. After the
capture, `v16` is dead and may be reused normally. In parallel, `out0..out8`
are never redefined in the 143-instruction second section and remain final
live-outs beside `out9..out17`.

The complete region contains 333 real instructions:

- 48 `trn1`/`trn2` instructions;
- 32 public 16-byte table loads;
- 48 lane-twist arithmetic instructions;
- two 102-instruction complete NTT9 cores;
- one fixed-tail capture.

The exact proof checks 144 coordinates and imports M5G's correlation-aware
ranges: NTT16 maximum 9342, fixed-product maximum 3436, and each NTT9 maximum
28568. It also machine-checks that every one of the eighteen outputs has one
definition and that the first nine have no definition in the second section.

The formal remote run used host `fedora`, Slothy 0.2.2, and checkout
`d636d638d06b370d1acc5774ca31c9572d3d2e6f`. RA-only is OPTIMAL in 31.46
seconds with order fixed and spills forbidden. Real split-window scheduling
ends with `split_heuristic_full:OK!` at 83 expected N1-proxy cycles.

Both returned artifacts use all 24 caller-saved vector registers
`v0-v7,v16-v31`; `v8-v15` remain untouched. The only GPR is public pointer
`x3`. There are 32 public loads and no coefficient memory instruction, store,
stack operation, branch, or spill. Both artifacts assemble locally.

This is not yet a full Forward implementation. The region begins at exact
NTT16 outputs for one `(top,component)` bank; pass-2 coefficient loads, the
actual NTT16 producer assembly, repeated-bank control, FR-0 stores, KEM/KAT,
and SUPERCOP remain outside this gate.
