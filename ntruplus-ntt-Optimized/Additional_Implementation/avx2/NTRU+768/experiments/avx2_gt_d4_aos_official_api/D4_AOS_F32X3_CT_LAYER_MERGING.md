# F32X3 CT layer merging

The accepted five-layer inverse NTT32 uses two logical passes.

- Pass A merges L0/L1/L2 in twelve four-YMM tiles and materializes one post-L2 state.
- Pass B merges L3/L4 in twelve tiles and updates that state in place.

For fixed `(row,j1,j2)`, an L3/L4 tile contains blocks `base+{0,4,8,12}`.
L3 pairs `(0,4)` and `(8,12)`; L4 pairs `(0,8)` and `(4,12)`. No semantic
store/reload exists inside either merged region. The physical `b/u/c` lane meaning is
unchanged throughout.
