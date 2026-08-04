#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "api.h"
#include "fips202/fips202.h"
#include "gt_backend.h"
#include "kat/rng.h"
#include "poly.h"
#include "symmetric.h"

typedef struct {
    uint64_t ntt;
    uint64_t basemul;
    uint64_t basemul_scale;
    uint64_t baseinv;
    uint64_t invntt;
    uint64_t tobytes;
    uint64_t frombytes;
    uint64_t add;
    uint64_t sub;
    uint64_t cbd1;
    uint64_t triple;
    uint64_t crepmod3;
    uint64_t sotp_encode;
    uint64_t sotp_decode;
    uint64_t hash_f;
    uint64_t hash_g;
    uint64_t hash_h;
    uint64_t shake256;
    uint64_t randombytes32;
    uint64_t randombytes96;
} counts;

static counts total;

enum profile_phase {
    PHASE_NONE, PHASE_KEYPAIR, PHASE_ENCAP, PHASE_DECAP,
    PHASE_MALFORMED_ENCAP, PHASE_MALFORMED_DECAP
};

typedef struct {
    const char *name;
    uint64_t count;
} edge_count;

static enum profile_phase phase;
static edge_count edges[64];
static size_t edge_length;
static unsigned ordinal_ntt, ordinal_basemul, ordinal_tobytes;
static unsigned ordinal_frombytes;
static unsigned keypair_side;
static uint64_t keypair_f_retries, keypair_g_retries;

static void record_edge(const char *name)
{
    for (size_t i = 0; i < edge_length; ++i) {
        if (strcmp(edges[i].name, name) == 0) {
            ++edges[i].count;
            return;
        }
    }
    if (edge_length >= sizeof edges / sizeof edges[0]) return;
    edges[edge_length].name = name;
    edges[edge_length].count = 1;
    ++edge_length;
}

static void begin_phase(enum profile_phase value)
{
    phase = value;
    ordinal_ntt = 0;
    ordinal_basemul = 0;
    ordinal_tobytes = 0;
    ordinal_frombytes = 0;
    if (value == PHASE_KEYPAIR) keypair_side = 0;
}

void gt_count_poly_ntt(poly *r)
{
    ++total.ntt;
    if (phase == PHASE_KEYPAIR)
        record_edge(keypair_side == 0 ? "keypair.ntt_f" : "keypair.ntt_g");
    else if (phase == PHASE_ENCAP)
        record_edge(ordinal_ntt++ == 0 ? "encap.ntt_r" : "encap.ntt_m");
    else if (phase == PHASE_DECAP)
        record_edge(ordinal_ntt++ == 0 ? "decap.ntt_m" : "decap.ntt_expected_r");
    gt_poly_ntt(r);
}

void gt_count_poly_basemul(poly *r, const poly *a, const poly *b)
{
    ++total.basemul;
    if (phase == PHASE_KEYPAIR)
        record_edge(ordinal_basemul++ == 0 ? "keypair.basemul_h"
                                           : "keypair.basemul_hinv");
    else if (phase == PHASE_ENCAP)
        record_edge("encap.basemul_hr");
    else if (phase == PHASE_DECAP)
        record_edge("decap.basemul_chinv");
    gt_poly_basemul(r, a, b);
}

void gt_count_poly_basemul_scale(poly *r, const poly *a, const poly *b)
{
    ++total.basemul_scale;
    if (phase == PHASE_DECAP) record_edge("decap.basemul_scale_cf");
    gt_poly_basemul_scale(r, a, b);
}

int gt_count_poly_baseinv(poly *r, const poly *a)
{
    ++total.baseinv;
    if (phase == PHASE_KEYPAIR)
        record_edge(keypair_side == 0 ? "keypair.baseinv_f"
                                      : "keypair.baseinv_g");
    const int result = gt_poly_baseinv(r, a);
    if (phase == PHASE_KEYPAIR) {
        if (result != 0) {
            if (keypair_side == 0) ++keypair_f_retries;
            else ++keypair_g_retries;
        } else if (keypair_side == 0) {
            keypair_side = 1;
        }
    }
    return result;
}

void gt_count_poly_invntt_scale(poly *r)
{
    ++total.invntt;
    if (phase == PHASE_DECAP) record_edge("decap.invntt_m");
    gt_poly_invntt_scale(r);
}

void gt_count_poly_tobytes(uint8_t out[NTRUPLUS_POLYBYTES], const poly *a)
{
    ++total.tobytes;
    if (phase == PHASE_KEYPAIR) {
        static const char *const names[] = {
            "keypair.encode_pk", "keypair.encode_sk_f", "keypair.encode_sk_hinv"
        };
        if (ordinal_tobytes < 3) record_edge(names[ordinal_tobytes++]);
    } else if (phase == PHASE_ENCAP) {
        record_edge(ordinal_tobytes++ == 0 ? "encap.encode_r" : "encap.encode_c");
    } else if (phase == PHASE_DECAP) {
        record_edge(ordinal_tobytes++ == 0 ? "decap.encode_recovered_r"
                                           : "decap.encode_expected_r");
    }
    gt_poly_tobytes(out, a);
}

int gt_count_poly_frombytes(poly *r,
                            const uint8_t in[NTRUPLUS_POLYBYTES])
{
    ++total.frombytes;
    if (phase == PHASE_ENCAP) record_edge("encap.decode_pk");
    else if (phase == PHASE_DECAP) {
        static const char *const names[] = {
            "decap.decode_ct", "decap.decode_sk_f", "decap.decode_sk_hinv"
        };
        if (ordinal_frombytes < 3) record_edge(names[ordinal_frombytes++]);
    } else if (phase == PHASE_MALFORMED_ENCAP)
        record_edge("malformed_encap.decode_pk");
    else if (phase == PHASE_MALFORMED_DECAP)
        record_edge("malformed_decap.decode_ct");
    return gt_poly_frombytes(r, in);
}

void gt_count_poly_add(poly *r, const poly *a, const poly *b)
{
    ++total.add;
    if (phase == PHASE_ENCAP) record_edge("encap.add_c");
    poly_add(r, a, b);
}

void gt_count_poly_sub(poly *r, const poly *a, const poly *b)
{
    ++total.sub;
    if (phase == PHASE_DECAP) record_edge("decap.sub_c");
    poly_sub(r, a, b);
}

void gt_count_poly_cbd1(poly *r, const uint8_t buf[NTRUPLUS_N / 4])
{
    ++total.cbd1;
    if (phase == PHASE_KEYPAIR)
        record_edge(keypair_side == 0 ? "keypair.cbd_f" : "keypair.cbd_g");
    else if (phase == PHASE_ENCAP) record_edge("encap.cbd_r");
    else if (phase == PHASE_DECAP) record_edge("decap.cbd_expected_r");
    poly_cbd1(r, buf);
}

void gt_count_poly_triple(poly *r)
{
    ++total.triple;
    if (phase == PHASE_KEYPAIR)
        record_edge(keypair_side == 0 ? "keypair.triple_f" : "keypair.triple_g");
    poly_triple(r);
}

void gt_count_poly_crepmod3(poly *r)
{
    ++total.crepmod3;
    if (phase == PHASE_DECAP) record_edge("decap.crepmod3_m");
    poly_crepmod3(r);
}

void gt_count_poly_sotp_encode(poly *r, const uint8_t msg[NTRUPLUS_N / 8],
                               const uint8_t buf[NTRUPLUS_N / 4])
{
    ++total.sotp_encode;
    if (phase == PHASE_ENCAP) record_edge("encap.sotp_encode_m");
    poly_sotp_encode(r, msg, buf);
}

int gt_count_poly_sotp_decode(uint8_t msg[NTRUPLUS_N / 8], const poly *a,
                              const uint8_t buf[NTRUPLUS_N / 4])
{
    ++total.sotp_decode;
    if (phase == PHASE_DECAP) record_edge("decap.sotp_decode_m");
    return poly_sotp_decode(msg, a, buf);
}

void gt_count_hash_f(uint8_t *buf, const uint8_t *msg)
{
    ++total.hash_f;
    if (phase == PHASE_KEYPAIR) record_edge("keypair.hash_pk");
    else if (phase == PHASE_ENCAP) record_edge("encap.hash_pk");
    hash_f(buf, msg);
}

void gt_count_hash_g(uint8_t *buf, const uint8_t *msg)
{
    ++total.hash_g;
    if (phase == PHASE_ENCAP) record_edge("encap.hash_r");
    else if (phase == PHASE_DECAP) record_edge("decap.hash_recovered_r");
    hash_g(buf, msg);
}

void gt_count_hash_h(uint8_t *buf, const uint8_t *msg)
{
    ++total.hash_h;
    if (phase == PHASE_ENCAP) record_edge("encap.hash_msg");
    else if (phase == PHASE_DECAP) record_edge("decap.hash_msg");
    hash_h(buf, msg);
}

void gt_count_shake256(uint8_t *output, size_t outlen,
                       const uint8_t *input, size_t inlen)
{
    ++total.shake256;
    if (phase == PHASE_KEYPAIR)
        record_edge(keypair_side == 0 ? "keypair.shake_f" : "keypair.shake_g");
    shake256(output, outlen, input, inlen);
}

void gt_count_randombytes(uint8_t *out, size_t outlen)
{
    if (phase == PHASE_KEYPAIR)
        record_edge(keypair_side == 0 ? "keypair.random_f" : "keypair.random_g");
    else if (phase == PHASE_ENCAP) record_edge("encap.random_coins");
    else if (phase == PHASE_MALFORMED_ENCAP)
        record_edge("malformed_encap.random_coins");
    if (outlen == 32U)
        ++total.randombytes32;
    else if (outlen == NTRUPLUS_N / 8U)
        ++total.randombytes96;
    (void)randombytes(out, (unsigned long long)outlen);
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
    SUB(add);
    SUB(sub);
    SUB(cbd1);
    SUB(triple);
    SUB(crepmod3);
    SUB(sotp_encode);
    SUB(sotp_decode);
    SUB(hash_f);
    SUB(hash_g);
    SUB(hash_h);
    SUB(shake256);
    SUB(randombytes32);
    SUB(randombytes96);
#undef SUB
    return after;
}

static void print_counts(const char *name, counts value, int comma)
{
    printf("    \"%s\": {\"ntt\": %llu, \"basemul\": %llu, "
           "\"basemul_scale\": %llu, \"baseinv\": %llu, "
           "\"invntt\": %llu, \"tobytes\": %llu, "
           "\"frombytes\": %llu, \"add\": %llu, \"sub\": %llu, "
           "\"cbd1\": %llu, \"triple\": %llu, \"crepmod3\": %llu, "
           "\"sotp_encode\": %llu, \"sotp_decode\": %llu, "
           "\"hash_f\": %llu, \"hash_g\": %llu, \"hash_h\": %llu, "
           "\"shake256\": %llu, \"randombytes32\": %llu, "
           "\"randombytes96\": %llu}%s\n",
           name,
           (unsigned long long)value.ntt,
           (unsigned long long)value.basemul,
           (unsigned long long)value.basemul_scale,
           (unsigned long long)value.baseinv,
           (unsigned long long)value.invntt,
           (unsigned long long)value.tobytes,
           (unsigned long long)value.frombytes,
           (unsigned long long)value.add,
           (unsigned long long)value.sub,
           (unsigned long long)value.cbd1,
           (unsigned long long)value.triple,
           (unsigned long long)value.crepmod3,
           (unsigned long long)value.sotp_encode,
           (unsigned long long)value.sotp_decode,
           (unsigned long long)value.hash_f,
           (unsigned long long)value.hash_g,
           (unsigned long long)value.hash_h,
           (unsigned long long)value.shake256,
           (unsigned long long)value.randombytes32,
           (unsigned long long)value.randombytes96, comma ? "," : "");
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
    begin_phase(PHASE_KEYPAIR);
    before = total;
    if (gt_count_crypto_kem_keypair(pk, sk) != 0)
        return 1;
    const counts keypair = difference(total, before);

    begin_phase(PHASE_ENCAP);
    before = total;
    if (gt_count_crypto_kem_enc(ct, ss, pk) != 0)
        return 1;
    const counts encap = difference(total, before);

    begin_phase(PHASE_DECAP);
    before = total;
    if (gt_count_crypto_kem_dec(dec, ct, sk) != 0)
        return 1;
    record_edge("decap.verify_r");
    const counts decap = difference(total, before);
    const counts valid_triplet = total;

    unsigned char malformed_pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char malformed_ct[CRYPTO_CIPHERTEXTBYTES];
    memset(malformed_pk, 0xff, sizeof malformed_pk);
    memset(malformed_ct, 0xff, sizeof malformed_ct);
    begin_phase(PHASE_MALFORMED_ENCAP);
    before = total;
    if (gt_count_crypto_kem_enc(ct, ss, malformed_pk) != 1)
        return 1;
    const counts malformed_encap = difference(total, before);
    begin_phase(PHASE_MALFORMED_DECAP);
    before = total;
    if (gt_count_crypto_kem_dec(dec, malformed_ct, sk) != 1)
        return 1;
    const counts malformed_decap = difference(total, before);

    printf("{\n");
    printf("  \"schema_version\": 1,\n");
    printf("  \"deterministic_seed\": \"17+29*i\",\n");
    printf("  \"operations\": {\n");
    print_counts("keypair", keypair, 1);
    print_counts("encap", encap, 1);
    print_counts("decap", decap, 1);
    print_counts("malformed_encap", malformed_encap, 1);
    print_counts("malformed_decap", malformed_decap, 0);
    printf("  },\n");
    printf("  \"caller_edges\": {\n");
    for (size_t i = 0; i < edge_length; ++i)
        printf("    \"%s\": %llu%s\n", edges[i].name,
               (unsigned long long)edges[i].count,
               i + 1 == edge_length ? "" : ",");
    printf("  },\n");
    printf("  \"paths\": {\"keypair.f_retries\": %llu, "
           "\"keypair.g_retries\": %llu, \"encap.invalid_pk\": 1, "
           "\"decap.malformed_encoding\": 1, "
           "\"decap.verify_failure\": 0},\n",
           (unsigned long long)keypair_f_retries,
           (unsigned long long)keypair_g_retries);
    print_counts("triplet", valid_triplet, 0);
    printf("}\n");
    return 0;
}
