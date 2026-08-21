# GT32-DECAP-LOAD-TO-COMPUTE-044

Causal decomposition of the 043 exact-image Decap win.

The three independently selected changes are:

- `D`: Decode3's shared Q24 body keeps mask `0123` resident.  Decode3 invokes
  that body three times.
- `S`: only `ntruplus768_basemul_scale_m_avx2` preloads `qinv` once per block.
- `G`: only `ntruplus768_basemul_general_m_avx2` preloads `qinv` once per block.

Eight full Decap measurement images (`A`, `D`, `S`, `G`, `DS`, `DG`, `SG`,
`DSG`) are generated from frozen GT Clean.  Every changed function retains its
control symbol size, so selected symbol addresses and the remainder of the image
must be identical across all eight ELFs.  This is a causal gate, not a padding
or address search.

The decisive images are produced by transplanting the equal-length selected
function ranges from 043 DB into the already frozen 043 Clean measurement ELF.
This preserves 043's exact compiler/link geometry byte-for-byte outside those
ranges.  A source-rebuilt set is retained only as a correctness and alternate-
geometry diagnostic; it must not be used to decompose the 043 result.

The benchmark follows the SUPERcop measurement shape and reports the Decap
StQ2 for each fresh launch.  Keypair and Encap are retained as negative/control
operations.
