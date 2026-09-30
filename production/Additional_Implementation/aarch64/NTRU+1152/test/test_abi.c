#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "api.h"
#include "poly.h"
#include "inverse.h"

typedef uint64_t (*sentinel)(void *, void *, void *, void *);
#define DECL(name) uint64_t name(void *, void *, void *, void *)
DECL(abi_crypto_kem_keypair); DECL(abi_crypto_kem_enc); DECL(abi_crypto_kem_dec);
DECL(abi_gt_forward); DECL(abi_gt_baseinv); DECL(abi_gt_basemul_inverse);
DECL(abi_gt_inverse_ternary); DECL(abi_gt_frombytes_checked);
DECL(abi_gt_tobytes_full); DECL(abi_gt_tobytes_small);
DECL(abi_gt_hash_f_fixed); DECL(abi_gt_hash_g_fixed);
DECL(abi_keccak_x1);
#if defined(__ARM_FEATURE_SHA3)
DECL(abi_keccak_x1_v84a); DECL(abi_keccak_x2_v84a);
#endif

/* The permutations take the Keccak-f[1600] round constants as an argument. */
static const uint64_t keccak_rc[24] = {
    0x0000000000000001ULL, 0x0000000000008082ULL,
    0x800000000000808aULL, 0x8000000080008000ULL,
    0x000000000000808bULL, 0x0000000080000001ULL,
    0x8000000080008081ULL, 0x8000000000008009ULL,
    0x000000000000008aULL, 0x0000000000000088ULL,
    0x0000000080008009ULL, 0x000000008000000aULL,
    0x000000008000808bULL, 0x800000000000008bULL,
    0x8000000000008089ULL, 0x8000000000008003ULL,
    0x8000000000008002ULL, 0x8000000000000080ULL,
    0x000000000000800aULL, 0x800000008000000aULL,
    0x8000000080008081ULL, 0x8000000000008080ULL,
    0x0000000080000001ULL, 0x8000000080008008ULL,
};

int main(void)
{
    uint8_t pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES];
    uint8_t ct[CRYPTO_CIPHERTEXTBYTES], ss[CRYPTO_BYTES], got[CRYPTO_BYTES];
    uint8_t bytes[NTRUPLUS_POLYBYTES] = {0};
    uint8_t hin[NTRUPLUS_POLYBYTES] = {0}, hout[NTRUPLUS_N / 4] = {0};
    poly a = {{0}}, b = {{0}}, c = {{0}};
    int16_t ntt_scratch[1152] = {0};   /* ntt_asm's caller-owned scratch */
    uint8_t invntt_scratch[POLY_INVNTT_TERNARY_SCRATCHBYTES] = {0};
    uint64_t keccak_state[50] = {0};  /* x2 permutes two states */
    struct item { const char *name; sentinel fn; void *a, *b, *c, *d; } cases[] = {
        {"keypair", abi_crypto_kem_keypair, pk, sk, 0, 0},
        {"enc", abi_crypto_kem_enc, ct, ss, pk, 0},
        {"dec", abi_crypto_kem_dec, got, ct, sk, 0},
        {"forward", abi_gt_forward, &a, &b, ntt_scratch, 0},
        {"baseinv", abi_gt_baseinv, &a, &b, 0, 0},
        {"basemul-inverse", abi_gt_basemul_inverse, &a, &b, &c, 0},
        {"inverse-ternary", abi_gt_inverse_ternary, &a, &b, invntt_scratch, 0},
        {"frombytes", abi_gt_frombytes_checked, &a, bytes, 0, 0},
        {"tobytes-full", abi_gt_tobytes_full, bytes, &a, 0, 0},
        {"tobytes-small", abi_gt_tobytes_small, bytes, &a, 0, 0},
        {"hash-f-fixed", abi_gt_hash_f_fixed, hout, hin, 0, 0},
        {"hash-g-fixed", abi_gt_hash_g_fixed, hout, hin, 0, 0},
        {"keccak-x1", abi_keccak_x1, keccak_state, (void *)keccak_rc, 0, 0},
#if defined(__ARM_FEATURE_SHA3)
        {"keccak-x1-v84a", abi_keccak_x1_v84a, keccak_state, (void *)keccak_rc, 0, 0},
        {"keccak-x2-v84a", abi_keccak_x2_v84a, keccak_state, (void *)keccak_rc, 0, 0},
#endif
    };
    uint64_t failed = 0;
    for (size_t i = 0; i < sizeof cases / sizeof cases[0]; i++) {
        uint64_t mask = cases[i].fn(cases[i].a, cases[i].b, cases[i].c, cases[i].d);
        printf("%-18s mask=0x%05llx\n", cases[i].name, (unsigned long long)mask);
        failed |= mask;
    }
    return failed != 0;
}
