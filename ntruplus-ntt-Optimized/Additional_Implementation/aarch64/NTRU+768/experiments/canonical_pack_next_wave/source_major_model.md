# GT-source-major canonical pack model

This is a model-only artifact. It does not authorize or emit assembly.

| GT group | groups | output runs | max runs/group | scalar store lower bound | estimated peak vectors |
|---:|---:|---:|---:|---:|---:|
| 6 | 32 | 117 | 4 | 234 | 7 |
| 8 | 24 | 100 | 5 | 200 | 9 |
| 12 | 16 | 85 | 6 | 170 | 12 |
| 16 | 12 | 60 | 6 | 146 | 14 |
| 24 | 8 | 52 | 8 | 121 | 20 |

The current canonical-major baseline uses 24 gather/assembly instructions and
two sequential multi-register stores per 16 blocks. Source-major candidates
replace those gathers with contiguous or structured loads, but they must pay
for stream permutation and fragmented 6-byte-block output runs. The scalar
store column is only a lower bound and intentionally excludes shuffle cost.

Decision gate: build source-major assembly only after an instruction-level
shuffle/store plan fits the available vector registers and has a modeled
advantage over the canonical-major fixed-offset chunk.
