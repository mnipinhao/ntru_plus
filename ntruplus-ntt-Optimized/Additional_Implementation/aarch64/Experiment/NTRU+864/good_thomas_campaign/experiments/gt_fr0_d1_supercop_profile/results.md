# P3B25 — SUPERCOP-source versus frozen GT P3B23

Baseline: `/home/pi/supercop-20260627/crypto_kem/ntruplus864/aarch64`.
**SUPERCOP installed/imported version; upstream latest not verified.**
This checkout was reimported. Its import source directory is `import/ntruplus-20260723`,
whose clean local HEAD is `0c249d5828b90e8dd5de2c8405323d5ee2a0ce41`
(2026-07-25, Clear low-level cryptographic scratch state). The directory name
and SUPERCOP archive date are not an upstream-latest claim. Exact installed
source hashes are saved in `source-hashes.json`; the imported files include
SUPERCOP integration edits and should be identified by those hashes.

Both use SHAKE256 and portable NO_CE Keccak on Pi5 Cortex-A76 core 3,
GCC 14.2.0, `-O3 -march=armv8-a+simd -fPIC`. Each implementation is bound
locally in its own shared object with `-Bsymbolic`; this preserves differing
API signatures and prevents cross-version symbol interposition. RNG is the
same deterministic xorshift benchmark RNG, not system entropy. These are
**PMU measurements of SUPERCOP sources, not native SUPERCOP do-part/stq results**.
GT is frozen P3B24: r9_to ToBytes, P3B23 FromBytes, existing Forward/D1/Inverse.

## Uninstrumented full KEM

| API | SUPERCOP cycles | GT cycles | GT minus SUPERCOP | Relative |
| --- | ---: | ---: | ---: | ---: |
| keygen | 44297.125 | 55757.875 | +11460.750 | +25.87% |
| encaps | 46414.375 | 47718.400 | +1304.025 | +2.81% |
| decaps | 40747.275 | 46048.150 | +5300.875 | +13.01% |

Three repetitions, both execution orders, 41 samples per API/order.
Independent valid/tampered KEM correctness passes eight deterministic cases;
public keys and ciphertexts also match across versions on those cases.
Normal/instrumented outputs are separately checked for equivalence.

## Actual KEM component profiler

Values below are **total cycles per KEM call**, not cycles per primitive.
The profiler redirects only direct calls made by kem.c; it does not count
internal hash/NTT callees a second time. It uses actual valid caller inputs
and a fixed no-retry keygen sample. Full Keygen averages four RNG seeds.
The empty measurement boundary is about 67 cycles and is subtracted per
call. Instrumentation changes code layout/cache state, so components are
diagnostic estimates. They must not be forced to sum to uninstrumented PMU.
Negative residuals below quantify this perturbation, not negative work.
A dash means that version does not call that symbol.

### keygen

| Component | SC calls | SC cycles | GT calls | GT cycles |
| --- | ---: | ---: | ---: | ---: |
| hash_f | 1 | 13301.0 | 1 | 13256.5 |
| poly_baseinv | 2 | 8351.0 | 2 | 17603.0 |
| poly_basemul | 2 | 4876.0 | 2 | 4358.0 |
| poly_cbd1 | 2 | 806.0 | 2 | 772.0 |
| poly_ntt | 2 | 7534.0 | 2 | 8441.0 |
| poly_tobytes | 3 | 3293.0 | 3 | 5665.0 |
| poly_triple | 2 | 484.0 | 2 | 492.0 |
| randombytes | 2 | 280.0 | 2 | 254.0 |
| shake256 | 2 | 5494.0 | 2 | 5607.0 |
| Component sum | | 44418.9 | | 56448.4 |
| Full minus component sum | | -121.8 | | -690.5 |

### encaps

| Component | SC calls | SC cycles | GT calls | GT cycles |
| --- | ---: | ---: | ---: | ---: |
| hash_f | 1 | 13304.5 | 1 | 13260.5 |
| hash_g | 1 | 14593.0 | 1 | 14510.0 |
| hash_h | 1 | 4083.0 | 1 | 4076.0 |
| poly_basemul_add | 1 | 2908.0 | 1 | 2180.0 |
| poly_cbd1 | 1 | 399.0 | 1 | 391.0 |
| poly_frombytes | 1 | 755.0 | 1 | 690.0 |
| poly_ntt | 2 | 7534.0 | 2 | 8443.0 |
| poly_sotp_encode | 1 | 415.0 | 1 | 419.0 |
| poly_tobytes | 2 | 2206.0 | 2 | 3798.0 |
| randombytes | 1 | 381.0 | 1 | 377.0 |
| Component sum | | 46578.4 | | 48144.4 |
| Full minus component sum | | -164.1 | | -426.0 |

### decaps

| Component | SC calls | SC cycles | GT calls | GT cycles |
| --- | ---: | ---: | ---: | ---: |
| hash_g | 1 | 14583.5 | 1 | 14508.0 |
| hash_h | 1 | 4076.5 | 1 | 4079.0 |
| poly_basemul | 1 | 2438.0 | 2 | 4374.0 |
| poly_basemul_scale | 1 | 1755.0 | — | — |
| poly_cbd1 | 1 | 396.0 | 1 | 385.0 |
| poly_crepmod3 | 1 | 488.0 | 1 | 479.0 |
| poly_frombytes | 3 | 2253.0 | 3 | 2042.0 |
| poly_invntt | — | — | 1 | 7718.0 |
| poly_invntt_scale | 1 | 4128.0 | — | — |
| poly_ntt | 2 | 7534.0 | 2 | 8441.0 |
| poly_sotp_decode | 1 | 430.0 | 1 | 395.0 |
| poly_sub | 1 | 214.0 | 1 | 215.0 |
| poly_tobytes | 2 | 2206.0 | 2 | 3796.0 |
| Component sum | | 40501.9 | | 46431.9 |
| Full minus component sum | | +245.4 | | -383.8 |

## Interpretation and contract differences

The installed SUPERCOP version validates canonical encodings in FromBytes;
GT P3B23 preserves all 12-bit representatives without the same rejection
check. Its FromBytes advantage therefore compares different validation work.
Valid ciphertext timing is reported; malformed-input latency/semantics are
not declared equivalent. SUPERCOP Decaps uses one BaseMul and one
BaseMul_scale paired with InvNTT_scale; GT uses two D1 BaseMuls and its
existing Inverse API. Compare the complete pair, not just the normal BaseMul.
GT BaseInv includes the coordinate bridges required by its representation.
ToBytes remains r9_to; the isolated P3B6 ToBytes was not substituted.

Keygen is dominated by the BaseInv gap; Decaps by Inverse and ToBytes.
Forward is now slower than this SUPERCOP baseline, reversing the older
repository-baseline conclusion. Production was not changed.

## Reproduction

1. Fetch the named SUPERCOP aarch64 directory plus cryptoint/crypto_uint64.h
   into build/official-source. Preserve source-hashes.json identity.
2. Run python3 prepare.py using the frozen P3B24 build/sync bundle.
3. Sync build/sync to /home/pi/ntruplus-experiments/gt864-p3b25-supercop-profile.
4. Run make -j4 there; run ./bench --check-only for correctness.
5. Run python3 run_pi5.py and python3 summarize.py locally.
Raw PMU, object audit and environment provenance are under build/raw.
