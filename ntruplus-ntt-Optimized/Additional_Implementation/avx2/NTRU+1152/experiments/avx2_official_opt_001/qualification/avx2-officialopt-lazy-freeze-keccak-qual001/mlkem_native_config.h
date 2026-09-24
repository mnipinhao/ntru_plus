/*
 * Local mlkem-native configuration for the NTRU+ AVX2 x1 SHAKE256 backend
 * (third_party/mlkem-native-fips202-b3ba7b32, mlkem-native commit
 * b3ba7b32773e657dd37f6f87bce82528459ad8a4).
 *
 * mlkem-native's common.h includes "mlkem_native_config.h" when
 * MLK_CONFIG_FILE is not defined, so this header is picked up from the
 * include path (repo builds) or from the same directory (flat SUPERCOP
 * tree) without any -D flag.  Only the vendored x1 FIPS202 sources
 * (fips202.c, keccakf1600.c) are compiled against it.
 *
 * - MLK_CONFIG_PARAMETER_SET: required by mlkem-native's params.h.  The
 *   FIPS202 code does not depend on it; 768 matches the component
 *   comparison (avx2_keccak_compare_001) that motivated this backend.
 * - MLK_CONFIG_NAMESPACE_PREFIX: every mlkem-native symbol becomes
 *   ntruplus_mlkfips202_<name>, so it cannot clash with Official
 *   fips202avx_* / KeccakP1600_* in one ELF.  Diagnostic builds may
 *   override it (e.g. a second -O2 copy in the same ELF).
 * - MLK_CONFIG_USE_NATIVE_BACKEND_FIPS202 is deliberately NOT defined:
 *   mlkem-native's x86_64 FIPS202 backend is x4-only
 *   (MLK_USE_NATIVE_FIPS202_X4), so the x1 permutation is the portable C
 *   mlk_keccakf1600_permute_c in either configuration and no x4 assembly
 *   is needed.  The x1 instruction streams of both configurations are
 *   compared in results/keccak-phase-a (keccak-config-equivalence.json).
 * - No arithmetic backend, no custom allocation/zeroize/memcpy/memset:
 *   mlkem-native defaults (stack state, memset + asm barrier zeroize).
 */
#ifndef NTRUPLUS_MLKEM_NATIVE_FIPS202_CONFIG_H
#define NTRUPLUS_MLKEM_NATIVE_FIPS202_CONFIG_H

#define MLK_CONFIG_PARAMETER_SET 768

#if !defined(MLK_CONFIG_NAMESPACE_PREFIX)
#define MLK_CONFIG_NAMESPACE_PREFIX ntruplus_mlkfips202
#endif

#endif /* NTRUPLUS_MLKEM_NATIVE_FIPS202_CONFIG_H */
