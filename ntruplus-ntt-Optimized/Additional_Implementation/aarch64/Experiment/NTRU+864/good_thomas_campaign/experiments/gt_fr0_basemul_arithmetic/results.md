# Results

`make check` passes 47 boundary and randomized full-polynomial cases. The Neon
candidate matches an exact scalar mirror using the same `-qinv/add` Montgomery
representatives for both BaseMul and BaseMulAdd. An independent canonical
cubic oracle also reports zero modulo-q mismatches.

All 288 physical leaves map bijectively to official legacy leaf indices, and
each physical zeta equals the mapped official Montgomery zeta. Mapping SHA-256
is `39f9809518d9c8fb63be420e859857fe942e2c87ad78fd8b9229ff27bf93f4f0`;
the zeta-table SHA-256 remains
`1c4d61e3a906acec0c44a3f3e88ef047ec7c0e45ed3e3ed8f3b38030092c4d92`.

Five alias paths per case pass: BaseMul `out==a/b` and BaseMulAdd `out==a/b/c`.
G0 updates the source-closed M5R-D operand bound to 25569. The rerun range
proof establishes int32 safety and R0 output bounds 2148/2205. This gate
makes no BaseInv, inverse-transform, full-KEM, assembly-performance, or
SUPERCOP claim.

During development, reference C's `qinv/subtract` and Neon's
`-qinv/add` conventions produced one representative differing by exactly q.
The exact gate now mirrors Neon semantics; canonical compatibility covers the
reference convention.
