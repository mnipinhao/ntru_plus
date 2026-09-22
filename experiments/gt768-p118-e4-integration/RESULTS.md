# P118 — E4 integrated into NTRU+768 production: decapsulation −1.0% on M2, −1.8% on A76

P117's E4 inverse replaces Official's `poly_invntt_decap_scale` + `poly_crepmod3`
in the production decapsulation path.  Branch `gt768-e4-inverse-integration`.

## What changed in `ntruplus-GT-Production/.../NTRU+768`

| file | change |
|---|---|
| `ntt.S` | The `decap_ntt` section (Official's inverse and its table, no other users) is replaced by `decap_invntt`, which defines `poly_invntt_ternary_decap`.  Generated from P117's `invntt_e4.S` by `make_prod.py`. |
| `base.S` | `poly_frombytes_basemul_decap_scale` stores its product with `st4` instead of `st1` (two lines), plus a comment giving the layout and the 2,458 bound. |
| `decap_verify.h` | New declaration and `POLY_INVNTT_TERNARY_DECAP_SCRATCHBYTES` (2048); the old declaration is removed. |
| `kem.c` | `buf1/buf2` become a 16-byte-aligned union with the inverse's 2,048 B scratch; one call replaces inverse + crepmod3. |
| `test/abi_sentinel.S`, `test/test_abi.c` | The sentinel targets the new leaf and passes a scratch buffer. |
| `docs/IMPLEMENTATION.md`, `README.md` | Pair contract: `st4` layout, R^-1, range bound, fused mod 3, caller scratch. |
| `SOURCE-MANIFEST.sha256` | Regenerated (same file list). |

**ABI:** `void poly_invntt_ternary_decap(poly *inout, uint8_t scratch[2048])`.

- In place on x0.  The body never writes x0 or x1.
- Three 512 B row buffers and the 512 B stage123 stripe live at x1.  The frame
  keeps only x30 and d8-d15 (80 B), which is Official's convention too: its
  inverse did not clear its d8-d15 spill either.
- The scratch is dead before `buf1/buf2` are first written, and
  `crypto_kem_dec_internal` already clears the whole scratch object on return.
  So the working area costs no extra clear.  The zeroization gate pins exactly
  that clear.

**Proof:** `range_interp.py` (P117) run on the production object with the new
ABI (`--scratch-x1`): **0 overflows for |input| ≤ 2,458**.  That bound is the
analytic one for Official's product, (4·3456² + 32768·q) / 2¹⁶.

## Gates

`make check` passes **on both M2 (clang) and the Pi 5 (gcc)**:

- manifest and release check (58 files);
- 100 KEM round trips;
- ABI: required mask 0x00000, `decap_invntt` 0x00000.  The internal masks are
  identical to the pre-change tree.
- 9,216 canonical-boundary cases;
- small-input differential;
- source and runtime zeroization;
- support tests;
- shake_prefixed;
- **KAT byte-identical**: `.rsp` SHA-256 `22c72039…a67d7ea785c9d4f66253e5d6cc1`, the
  canonical hash.

`scripts/export_supercop.py` succeeds on the Pi.  A full SUPERCOP run of the
exported leaf was not done.

The parent `aarch64/SHA256SUMS` was already stale before this change: it lists
the pre-refactor `asm/...` layout, and nothing checks it.  Left untouched.

## Full KEM, pre-change tree vs this branch

`bench_kem3.c`: each tree built separately with its Makefile's KEM sources and
flags (portable Keccak, as `make` builds), runs alternated old/new three times.

| | M2 ns (witness-gated best) | A76 cycles (median of 61 x 500, core 3) |
|---|---:|---:|
| keygen | 5,771.8 → 5,772.2 | 31,540 → 31,569 (+0.1%) |
| encaps | 5,090.4 → 5,091.2 | 29,371 → 29,363 |
| **decaps** | **3,139.2 → 3,106.7 (−32.5, −1.0%)** | **27,740 → 27,242 (−498, −1.8%)** |

The table shows means of the three runs.  Runs agree within 1.5 ns (M2) and
14 cycles (A76); A76 `throttled=0x0`.

The decapsulation gain matches P117's first-product chain (−28 ns / −482
cycles), plus the removed crepmod3 pass.

## Files

- `make_prod.py` → `decap_invntt.S`: the production section, as spliced into `ntt.S`.
- `bench_kem3.c`, `build_kem3.sh`: the full-KEM comparison
  (`build_kem3.sh TREE OUT [cc args]`).
