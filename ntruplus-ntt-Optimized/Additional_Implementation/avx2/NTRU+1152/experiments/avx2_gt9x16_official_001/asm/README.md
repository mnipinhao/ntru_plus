# Candidate assembly

Put handwritten AVX2 experiment assembly here. Keep the public/internal ABI
contracts documented alongside the source.

`g1c_bmscale_inverse_d1.S` contains the namespaced raw diagnostic, exact
materialized M2 control, and selected linked C2-L leaves. The materialized
symbol writes raw BMScale, reloads that boundary, and overwrites it with D1;
the linked symbol stores only post-distance1 vectors.
