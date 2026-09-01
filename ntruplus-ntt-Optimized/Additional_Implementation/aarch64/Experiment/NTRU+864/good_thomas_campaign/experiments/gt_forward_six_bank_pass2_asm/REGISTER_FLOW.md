# M5N register-flow view

## Public wrapper state

Entry is `x0=FR0 output`, `x1=P8 input`, and `x30=caller return`.  Four moves
produce `x6=output base`, `x7=P8 base`, `x16=saved return`, and public
`x4=16`.  M5M uses only `x0-x5`, so `x6/x7/x16` remain live across every
internal call.  No stack or callee-saved GPR is needed.

## Bank pointer construction

For public `bank=3*top+component`, the wrapper sets:

- `x0 = x7 + 256*bank` for sixteen contiguous main q-vector loads;
- `x1 = x7 + 1536 + 2*bank` for the first tail halfword;
- `x2 = NTT16[top]`, `x3 = NTT9[top]`, and `x5 = common`.

The `bl` changes `x30`, but the helper `ret` returns to the immediately
following stores.  M5M advances its local pointers but cannot change the
immutable bases.

## One-bank helper

The helper is byte-for-byte the emitted instruction stream of the frozen M5M
optimized artifact, excluding comments and boundary labels.  It reads 144
meaningful coefficients, performs tail and main NTT16 plus both oriented NTT9
blocks, and returns eighteen vectors in the fixed mapping:

`[v26,v30,v7,v25,v19,v21,v3,v24,v22,v23,v2,v0,v31,v28,v18,v5,v29,v20]`.

Scale remains R0.  The inherited maximum magnitude is 28568.

## Direct FR-0 stores

Outputs 0--8 are rows 0--8 for columns 0--7; outputs 9--17 are rows 0--8 for
columns 8--15.  Each is stored at the public top/component/row/block offset.
All eighteen vectors die after their stores, so the next helper call may reuse
every vector register.  Six calls create a bijection over `out[0..863]`.

## Return

After the sixth bank, `mov x30,x16` restores the original link register and
the wrapper returns.  `x6/x7/x16` are caller-saved under AAPCS64, so the public
function has no preservation obligation for them.
