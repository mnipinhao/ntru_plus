# GT-Optimized versus KPQC Final

- Host: `Linux-6.18.33+rpt-rpi-2712-aarch64-with-glibc2.41`
- Compiler: `cc (Debian 14.2.0-19) 14.2.0`
- CPU core: `3`
- Samples per variant: `62`
- Operations per sample: `2000`

| Operation | KPQC p10/p50/p90 | GT p10/p50/p90 | Reduction |
|---|---:|---:|---:|
| keygen | 40111/40134/40142 | 36823/36852/36880 | 8.18% |
| encap | 39308/39311/39317 | 37827/37832/37836 | 3.76% |
| decap | 35157/35179/35198 | 32737/32741/32745 | 6.93% |
