# 145 — ASLR-off formal benchmark and Encap/Decap profiler

This gate uses only ASLR-disabled processes. It rebuilds the promoted
QL2+direct-r-hash GT and frozen Official images with the explicit NTRU+768
SUPERcop harness, runs a 16-block paired Keypair/Encap/Decap comparison, then
captures balanced LBR profiles of the same ELFs.  The Decap analysis reuses
the same capture corpus, so its comparison has identical binary, process and
ASLR conditions.

```sh
make all
```

LBR leaf intervals are descriptive and non-additive. `hash_g`/`hash_h` are
non-leaf wrappers and are not assigned synthetic component costs.  The
Official Decap byte comparison is inline, so the final-check row explicitly
contains only the visible serializer leaf. Whole-operation claims come only
from the formal SUPERcop-style benchmark.
