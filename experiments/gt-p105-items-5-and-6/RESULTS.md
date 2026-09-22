# P105 — items 5 and 6 measured; both are GT wins, and the profiler's record is now complete

## Item 5: NTRU+1152's forward transform

Already in P102's table, once the two call sites are rolled up with the aliasing
`kem.c` uses.  1152 calls `poly_ntt` twice in every operation; in decapsulation
the first is out-of-place for GT and `f = m; poly_ntt(&f)` for Official.

| operation | GT M2 | Off M2 | difference | GT A76 | Off A76 | difference |
|---|---:|---:|---:|---:|---:|---:|
| key generation | 2,218 | 2,136 | +82 (+23.4 ns) | 8,704 | 9,570 | **-866 (-361 ns)** |
| encapsulation | 2,218 | 2,136 | +82 (+23.4 ns) | 8,704 | 9,570 | **-866 (-361 ns)** |
| **decapsulation** | 2,218 | 2,252 | **-34 (-9.7 ns)** | 8,705 | 9,725 | **-1,020 (-425 ns)** |

The roadmap said **+21 / -25 / +47**.  Decapsulation is a **GT win of 10 ns**,
not a 47 ns deficit, for the reason item 4 had: Official pays a `poly` copy
there that GT's out-of-place form avoids.  Encapsulation's sign is wrong too.

What is real is +23 ns on key generation and encapsulation, which is the same
generic in-place forward gap 864 shows (1.04 here, 1.06 there) and P100 already
found to have no concentrated lever.

## Item 6: NTRU+864's baseinv

Both sides are out-of-place `(poly *out, const poly *in)` and key generation
calls it twice, on `f` and on `g`.  Each is given input in **its own** basis --
its own forward transform's output -- and both report the input invertible, so
both take the same path.

| `poly_baseinv`, one call | GT | Official | ratio | key generation, x2 |
|---|---:|---:|---:|---:|
| M2 Pro | 1,334 | 1,349 | **0.99** | **-30 cyc (-8.6 ns)** |
| Cortex-A76 | 3,979 | 4,157 | **0.96** | **-356 cyc (-148 ns)** |

The roadmap said **+33 ns**.  It is **-8.6**.

## The profiler's record, complete

Every roadmap prize that came from the sampling profiler has now been timed
directly:

| item | profiler | measured | |
|---|---:|---:|---|
| 1. 1152 unpack | +157 | **+54** | 3x over |
| 2. 768 encapsulation | +109 | **+18** | 6x over, a fusion accounting error |
| 2. 768 key generation | +69 | **+53** | |
| 4. 864 forward | +61 / +32 / +25 | **+26 uniform** | wrong shape |
| 5. 1152 forward | +21 / -25 / +47 | **+23 / +23 / -10** | two signs wrong |
| 6. 864 baseinv | +33 | **-8.6** | sign wrong |
| 3. 864 inverse | +106 | **+106** | **correct -- and the only one P92 timed directly** |

**Six of seven figures were wrong; the one that was right is the one that was
never sampled.**  P91 had already shown the sampler disagrees with itself by 5%
on a 2,000 ns bucket -- 100 ns, the size of everything on this list.  Two
distinct faults compounded it: sampling error, and comparisons that gave one
side a `poly` copy the real code does not pay (or removed one it does).

What survives on the list is item 2's `poly_tobytes_keygen_cq` (+53 ns on key
generation, 1.32x, three calls, never analysed) and item 3's remaining +68 on
864's inverse.
