#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "api.h"
#include "poly.h"

typedef uint64_t (*sentinel)(void *, void *, void *, void *);
#define DECL(name) uint64_t name(void *, void *, void *, void *)
DECL(abi_crypto_kem_keypair); DECL(abi_crypto_kem_enc); DECL(abi_crypto_kem_dec);
DECL(abi_gt_forward); DECL(abi_gt_baseinv); DECL(abi_gt_basemul_inverse);
DECL(abi_gt_inverse_ternary); DECL(abi_gt_frombytes_checked);
DECL(abi_gt_tobytes_full); DECL(abi_gt_tobytes_small); DECL(abi_gt_tobytes_compare);
DECL(abi_gt_hash_f_fixed); DECL(abi_gt_hash_g_fixed);

int main(void)
{
    uint8_t pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES];
    uint8_t ct[CRYPTO_CIPHERTEXTBYTES], ss[CRYPTO_BYTES], got[CRYPTO_BYTES];
    uint8_t bytes[NTRUPLUS_POLYBYTES] = {0};
    uint8_t hin[NTRUPLUS_POLYBYTES] = {0}, hout[NTRUPLUS_N / 4] = {0};
    poly a = {{0}}, b = {{0}}, c = {{0}};
    struct item { const char *name; sentinel fn; void *a, *b, *c, *d; } cases[] = {
        {"keypair", abi_crypto_kem_keypair, pk, sk, 0, 0},
        {"enc", abi_crypto_kem_enc, ct, ss, pk, 0},
        {"dec", abi_crypto_kem_dec, got, ct, sk, 0},
        {"forward", abi_gt_forward, &a, &b, 0, 0},
        {"baseinv", abi_gt_baseinv, &a, &b, 0, 0},
        {"basemul-inverse", abi_gt_basemul_inverse, &a, &b, &c, 0},
        {"inverse-ternary", abi_gt_inverse_ternary, &a, &b, 0, 0},
        {"frombytes", abi_gt_frombytes_checked, &a, bytes, 0, 0},
        {"tobytes-full", abi_gt_tobytes_full, bytes, &a, 0, 0},
        {"tobytes-small", abi_gt_tobytes_small, bytes, &a, 0, 0},
        {"tobytes-compare", abi_gt_tobytes_compare, bytes, &a, 0, 0},
        {"hash-f-fixed", abi_gt_hash_f_fixed, hout, hin, 0, 0},
        {"hash-g-fixed", abi_gt_hash_g_fixed, hout, hin, 0, 0},
    };
    uint64_t failed = 0;
    for (size_t i = 0; i < sizeof cases / sizeof cases[0]; i++) {
        uint64_t mask = cases[i].fn(cases[i].a, cases[i].b, cases[i].c, cases[i].d);
        printf("%-18s mask=0x%05llx\n", cases[i].name, (unsigned long long)mask);
        failed |= mask;
    }
    return failed != 0;
}
