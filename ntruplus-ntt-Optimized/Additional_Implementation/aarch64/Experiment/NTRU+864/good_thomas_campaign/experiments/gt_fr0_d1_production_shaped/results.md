# D1-P1 results

Status: **PASS as a production-shaped consumer gate; keep experimental.**

The same stock `common/kem.c` was compiled three times into one binary. Eight
deterministic cases produce byte-identical Official, GT-old and GT-D1 public
keys, secret keys, ciphertexts and shared secrets. Valid Decaps succeeds and
tampered ciphertext returns the same failure code and zero secret in all
three variants.

This gate exposed two required GT boundary operations that C2b did not model:

- M5R-D's lazy FR0 output must be reduced before stock BaseInv and
  serialization. A `sqrdmulh`/`mls` Neon reduction plus explicit FR0-to-stock
  permutation now provides centered or nonnegative representatives.
- M5E's lazy natural output must be centered before `crepmod3`; modulo-q
  equality alone is insufficient because changing a representative by q also
  changes it modulo 3.

These operations are common to GT-old and GT-D1 and are included in the KEM
measurements below. Cortex-A76 core 3 remained unthrottled (`0x0`).
The normalization proof exhaustively checks every signed halfword: reciprocal
9 leaves `[-3291,3291]`, the masked correction gives `[0,3456]`, and the
centered form is `[-1728,1728]`, always congruent modulo 3457 and int16-safe.

| Boundary | Official | GT-old | GT-D1 | D1 - old | D1 - Official |
| --- | ---: | ---: | ---: | ---: | ---: |
| BaseMul | 2844.099 | 2673.117 | 2142.106 | **-531.011** | **-701.993** |
| BaseMulAdd | 2846.104 | 2820.384 | 2151.363 | **-669.021** | **-694.741** |
| Keypair | 46894.500 | 57899.500 | 56830.875 | **-1068.625** | +9936.375 |
| Encaps | 47023.375 | 51464.675 | 50799.850 | **-664.825** | +3776.475 |
| Decaps | 43438.900 | 54860.050 | 53835.300 | **-1024.750** | +10396.400 |

D1 retires exactly 755 fewer instructions per BaseMul and 760 fewer per
BaseMulAdd in this linked binary. Consequently Keypair and Decaps each retire
1510 fewer instructions and Encaps retires 760 fewer than GT-old. Every one
of three independent paired repetitions favors D1 at all five boundaries.

The linked-object relocation audit confirms that the candidate KEM object
references only `gt_d1_poly_{ntt,baseinv,basemul,basemul_add,invntt,frombytes,
tobytes}` at the transformed boundaries; the GT-old object references the
parallel `gt_old_*` set. Thus this run did not reuse a stale stock or old-GT
target. The AArch64 feature scan reports no optional-ISA use. The only Neon
pattern prompt is the deliberate `sqrdmulh` boundary reducer covered by the
exhaustive signed-halfword proof; secret-independence prompts occur only in
the deterministic test harness, not the production-shaped wrapper.

D1 therefore survives the actual KEM call graph and remains the active GT
arithmetic baseline. The whole GT implementation is not competitive with
Official yet: GT-D1 is 21.19% slower in Keypair, 8.03% slower in Encaps and
23.93% slower in Decaps. Most of that gap is outside D1 and includes the
current explicit permutation/normalization wrappers, stock-BaseInv bridge and
GT Inverse path. No KAT, SUPERCOP or Production promotion is authorized.
