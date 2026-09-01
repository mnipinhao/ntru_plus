# M5O: full Forward composition hard gate

This Experiment composes the frozen `LD3` top split with the frozen M5N
six-bank pass 2 into one callable natural-input-to-FR0 Forward transform.
`gt864_forward_poly_ntt_experiment(out, in)` uses a fixed 1792-byte stack P8
buffer and requires disjoint 864-halfword input and output arrays.

The candidate deliberately returns FR-0, not Official's physical transform
ABI.  `generate_official_map.py` reconstructs every Official physical leaf
from `asm/base.s::zetas_mul`, cross-checks that table against scalar
`zetas[288]`, identifies its exact `(top,row,column)` coordinate, and emits a
bijection from 864 Official SoA offsets to 864 FR-0 offsets.  This adapter is
test-only; it does not add a runtime permutation to the kernel.

The composition performs two meaningful coefficient reads and two meaningful
coefficient writes: natural input -> P8 -> FR-0.  Top split additionally writes
32 zero padding halfwords so that its tail vectors are full Neon vectors; M5N
does not read those positions.  There is no third coefficient-memory pass.

Run `make check` on arm64.  The gate compares every output modulo q against
Official Neon Forward for all 864 basis inputs, range boundaries, and random
centered/canonical inputs, then audits the fixed stack wrapper and final linked
symbols.  No cycle or Production claim is made here.
