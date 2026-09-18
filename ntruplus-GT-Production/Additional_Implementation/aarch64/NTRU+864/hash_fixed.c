#include <stdint.h>
#include <stddef.h>
#include "params.h"
#include "fips202.h"


#if defined(__ARM_FEATURE_SHA3)
/*
 * On targets with FEAT_SHA3 the permutation is about twice as fast, so the
 * scalar fused kernels in keccakf1600.S -- which are tuned for Cortex-A76,
 * where folding rotations into the second operand is free -- lose badly.  Use
 * the portable prefixed sponge over the v8.4-A permutation instead.  It keeps
 * what the fused kernels were written for: the message is never copied, nothing
 * is heap allocated, and the state is wiped before returning.
 */
void ntruplus_hash_f_fixed(uint8_t output[32], const uint8_t input[NTRUPLUS_POLYBYTES])
{
    shake256_prefixed(output, 32, 0x00, input, NTRUPLUS_POLYBYTES);
}

void ntruplus_hash_g_fixed(uint8_t output[NTRUPLUS_N / 4],
                           const uint8_t input[NTRUPLUS_POLYBYTES])
{
    shake256_prefixed(output, NTRUPLUS_N / 4, 0x01, input, NTRUPLUS_POLYBYTES);
}

#else /* portable / Cortex-A76: the scalar fused kernels */

static const uint64_t hash_round_constants[24] = {
    UINT64_C(0x0000000000000001), UINT64_C(0x0000000000008082),
    UINT64_C(0x800000000000808a), UINT64_C(0x8000000080008000),
    UINT64_C(0x000000000000808b), UINT64_C(0x0000000080000001),
    UINT64_C(0x8000000080008081), UINT64_C(0x8000000000008009),
    UINT64_C(0x000000000000008a), UINT64_C(0x0000000000000088),
    UINT64_C(0x0000000080008009), UINT64_C(0x000000008000000a),
    UINT64_C(0x000000008000808b), UINT64_C(0x800000000000008b),
    UINT64_C(0x8000000000008089), UINT64_C(0x8000000000008003),
    UINT64_C(0x8000000000008002), UINT64_C(0x8000000000000080),
    UINT64_C(0x000000000000800a), UINT64_C(0x800000008000000a),
    UINT64_C(0x8000000080008081), UINT64_C(0x8000000000008080),
    UINT64_C(0x0000000080000001), UINT64_C(0x8000000080008008),
};

void ntruplus_hash_g_fused_aarch64(uint8_t *out, const uint8_t *input,
                                    const uint64_t rc[24]);
void ntruplus_hash_f_fused_aarch64(uint8_t *out, const uint8_t *input,
                                    const uint64_t rc[24]);

void ntruplus_hash_f_fixed(uint8_t output[32], const uint8_t input[NTRUPLUS_POLYBYTES])
{
    ntruplus_hash_f_fused_aarch64(output, input, hash_round_constants);
}

void ntruplus_hash_g_fixed(uint8_t output[NTRUPLUS_N / 4],
                           const uint8_t input[NTRUPLUS_POLYBYTES])
{
    ntruplus_hash_g_fused_aarch64(output, input, hash_round_constants);
}

#endif /* __ARM_FEATURE_SHA3 */
