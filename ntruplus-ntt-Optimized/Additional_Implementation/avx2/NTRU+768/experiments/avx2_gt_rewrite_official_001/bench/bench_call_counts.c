#include <stdint.h>
#include <stdio.h>

#include "api.h"
#include "gt_backend.h"
#include "kat/rng.h"

typedef struct {
    uint64_t ntt;
    uint64_t basemul;
    uint64_t basemul_scale;
    uint64_t baseinv;
    uint64_t invntt;
    uint64_t tobytes;
    uint64_t frombytes;
} counts;

static counts total;

void gt_count_poly_ntt(poly *r)
{
    ++total.ntt;
    gt_poly_ntt(r);
}

void gt_count_poly_basemul(poly *r, const poly *a, const poly *b)
{
    ++total.basemul;
    gt_poly_basemul(r, a, b);
}

void gt_count_poly_basemul_scale(poly *r, const poly *a, const poly *b)
{
    ++total.basemul_scale;
    gt_poly_basemul_scale(r, a, b);
}

int gt_count_poly_baseinv(poly *r, const poly *a)
{
    ++total.baseinv;
    return gt_poly_baseinv(r, a);
}

void gt_count_poly_invntt_scale(poly *r)
{
    ++total.invntt;
    gt_poly_invntt_scale(r);
}

void gt_count_poly_tobytes(uint8_t out[NTRUPLUS_POLYBYTES], const poly *a)
{
    ++total.tobytes;
    gt_poly_tobytes(out, a);
}

int gt_count_poly_frombytes(poly *r,
                            const uint8_t in[NTRUPLUS_POLYBYTES])
{
    ++total.frombytes;
    return gt_poly_frombytes(r, in);
}

int gt_count_crypto_kem_keypair(unsigned char *pk, unsigned char *sk);
int gt_count_crypto_kem_enc(unsigned char *ct, unsigned char *ss,
                            const unsigned char *pk);
int gt_count_crypto_kem_dec(unsigned char *ss, const unsigned char *ct,
                            const unsigned char *sk);

static void reset_rng(void)
{
    unsigned char entropy[48];
    for (size_t i = 0; i < sizeof entropy; ++i)
        entropy[i] = (unsigned char)(17U + 29U * i);
    randombytes_init(entropy, NULL, 256);
}

static counts difference(counts after, counts before)
{
#define SUB(member) after.member -= before.member
    SUB(ntt);
    SUB(basemul);
    SUB(basemul_scale);
    SUB(baseinv);
    SUB(invntt);
    SUB(tobytes);
    SUB(frombytes);
#undef SUB
    return after;
}

static void print_counts(const char *name, counts value, int comma)
{
    printf("    \"%s\": {\"ntt\": %llu, \"basemul\": %llu, "
           "\"basemul_scale\": %llu, \"baseinv\": %llu, "
           "\"invntt\": %llu, \"tobytes\": %llu, "
           "\"frombytes\": %llu}%s\n", name,
           (unsigned long long)value.ntt,
           (unsigned long long)value.basemul,
           (unsigned long long)value.basemul_scale,
           (unsigned long long)value.baseinv,
           (unsigned long long)value.invntt,
           (unsigned long long)value.tobytes,
           (unsigned long long)value.frombytes, comma ? "," : "");
}

int main(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    unsigned char ct[CRYPTO_CIPHERTEXTBYTES];
    unsigned char ss[CRYPTO_BYTES];
    unsigned char dec[CRYPTO_BYTES];
    counts before;

    reset_rng();
    before = total;
    if (gt_count_crypto_kem_keypair(pk, sk) != 0)
        return 1;
    const counts keypair = difference(total, before);

    before = total;
    if (gt_count_crypto_kem_enc(ct, ss, pk) != 0)
        return 1;
    const counts encap = difference(total, before);

    before = total;
    if (gt_count_crypto_kem_dec(dec, ct, sk) != 0)
        return 1;
    const counts decap = difference(total, before);

    printf("{\n");
    printf("  \"schema_version\": 1,\n");
    printf("  \"deterministic_seed\": \"17+29*i\",\n");
    printf("  \"operations\": {\n");
    print_counts("keypair", keypair, 1);
    print_counts("encap", encap, 1);
    print_counts("decap", decap, 0);
    printf("  },\n");
    print_counts("triplet", total, 0);
    printf("}\n");
    return 0;
}
