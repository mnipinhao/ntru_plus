# 097 — four-slot Encap data-geometry search

Primary objective: minimize the exact production-shaped SUPERCOP Encap image
on the current target machine with CPU 1 pinned and the host's default ASLR
behavior.  ASLR-off is diagnostic rather than a promotion requirement.

The production arithmetic and topology are frozen at `b2a4bea`.  This gate
enumerates all 24 physical orders of the existing `h`, `r`, `m`, and
`c` (frontend/product) 1536-byte fields.  It does not add padding, remove a
slot, change B3 aliasing, or alter any kernel.

Every caller is placed in the qualified 611-byte reservation. All pre-existing
symbols outside the caller, rodata, and the E0V RX tail must remain identical.

The campaign first screens all 24 orders using standard SUPERCOP-style process
launches, then reruns the best orders with a balanced 16-block fixed-image
campaign. Geometry credit is accepted if the selected build is deterministic,
correct, and reproducibly fastest under this declared target protocol.

## Reproduction

```sh
python3 tools/build.py
python3 tools/correctness.py
python3 tools/run_sweep.py
python3 tools/run_formal.py
```

The benchmark scripts deliberately do not use `setarch -R`.  Each measuring
process is pinned to CPU 1 and starts as an ordinary SUPERCOP process with the
host's default ASLR behavior.

See `RESULTS.md` for the completed decision.  No four-slot permutation was
promoted; production remains `h,r,m,c` at commit `b2a4bea`.
