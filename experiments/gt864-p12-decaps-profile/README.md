# P12 — residual Decaps profiler

This experiment freezes NTRU+864 GT production at revision `dd8c3146` and
rebuilds it alongside the selected SUPERCOP source at
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`.

Control revision `1c790870` completed P11 but changed only the package roadmap;
it explicitly kept the `dd8c3146` P10/P8 production kernel.  Freezing the last
production revision preserves its source-manifest closure while profiling the
same current linked implementation.

The first P12 hard gate is diagnostic: refresh clean full-KEM PMU and complete
call-site profiles before selecting another Decaps DAG.  Clean full-KEM timing
is authoritative; instrumented component timing is used only to localize the
remaining gap.

The runner refuses an active `do-part`, checks the three pinned Official source
hashes, performs a fresh GT manifest/build/test/KAT, records linked objects and
binary hashes, and runs six balanced processes on Pi 5 core 3.
