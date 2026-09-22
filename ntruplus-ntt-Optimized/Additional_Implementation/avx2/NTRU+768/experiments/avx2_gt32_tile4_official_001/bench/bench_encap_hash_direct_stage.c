#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#ifndef CORRECTNESS_ONLY
#include "cpucycles.h"
#endif
#include "internal.h"
#include "poly.h"
#include "symmetric.h"
#include "kat/rng.h"

void ntruplus768_hash_stage_research(uint8_t *, const int16_t *);
int ntruplus768_hash_stage_enc_derand(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);
void ntruplus768_pack_m_lazy10788_avx2(uint8_t *, const int16_t *);
void ntruplus768_ntt_frontend_avx2(int16_t *, const int16_t *);
void ntruplus768_ntt_m_avx2(int16_t *, const int16_t *);

enum { BANKS = 16, N = 768, WIRE = 1152, OUT = 192 };
typedef struct __attribute__((aligned(64))) {
    int16_t r[N];
    uint8_t pk[NTRUPLUS_PUBLICKEYBYTES], sk[NTRUPLUS_SECRETKEYBYTES];
    uint8_t coins[N / 8], ct[WIRE], ss[NTRUPLUS_SSBYTES];
} bank;
static bank banks[BANKS];

static __attribute__((noinline)) int control_hash(bank *b) {
    ntruplus768_pack_m_lazy10788_avx2(b->ct, b->r);
    hash_g(b->ct, b->ct);
    return 0;
}
static __attribute__((noinline)) int candidate_hash(bank *b) {
    ntruplus768_hash_stage_research(b->ct, b->r);
    return 0;
}
static __attribute__((noinline)) int control_enc(bank *b) {
    return ntruplus768_enc_derand_impl(b->ct, b->ss, b->pk, b->coins);
}
static __attribute__((noinline)) int candidate_enc(bank *b) {
    return ntruplus768_hash_stage_enc_derand(b->ct, b->ss, b->pk, b->coins);
}
typedef int (*operation)(bank *);
static operation functions[2][2] = {{control_hash, candidate_hash}, {control_enc, candidate_enc}};

static void prepare(void) {
    uint8_t entropy[48], cbd[192];
    _Alignas(64) poly coeff;
    _Alignas(64) int16_t front[N];
    for (unsigned j = 0; j < 48; ++j) entropy[j] = (uint8_t)(23 * j + 19);
    randombytes_init(entropy, NULL, 256);
    for (unsigned b = 0; b < BANKS; ++b) {
        assert(ntruplus768_keypair_impl(banks[b].pk, banks[b].sk) == 0);
        randombytes(cbd, sizeof cbd);
        randombytes(banks[b].coins, sizeof banks[b].coins);
        poly_cbd1(&coeff, cbd);
        ntruplus768_ntt_frontend_avx2(front, (const int16_t *)(const void *)&coeff);
        ntruplus768_ntt_m_avx2(banks[b].r, front);
    }
}

static void preflight(void) {
    uint8_t ct[WIRE], ss[NTRUPLUS_SSBYTES], dec[NTRUPLUS_SSBYTES];
    uint8_t pk[NTRUPLUS_PUBLICKEYBYTES], coins[N / 8];
    _Alignas(64) int16_t r[N];
    for (unsigned trial = 0; trial < 100; ++trial) {
        bank *b = &banks[trial % BANKS];
        for (unsigned i = 0; i < sizeof b->coins; ++i) b->coins[i] = (uint8_t)(trial * 73 + i * 19);
        memcpy(pk, b->pk, sizeof pk);
        memcpy(coins, b->coins, sizeof coins);
        memcpy(r, b->r, sizeof r);
        assert(control_hash(b) == 0);
        memcpy(ct, b->ct, OUT);
        assert(candidate_hash(b) == 0 && memcmp(ct, b->ct, OUT) == 0);
        assert(memcmp(r, b->r, sizeof r) == 0);
        assert(control_enc(b) == 0);
        memcpy(ct, b->ct, sizeof ct);
        memcpy(ss, b->ss, sizeof ss);
        assert(candidate_enc(b) == 0);
        assert(memcmp(ct, b->ct, sizeof ct) == 0 && memcmp(ss, b->ss, sizeof ss) == 0);
        assert(memcmp(pk, b->pk, sizeof pk) == 0 && memcmp(coins, b->coins, sizeof coins) == 0);
        assert(ntruplus768_dec_impl(dec, b->ct, b->sk) == 0 && memcmp(dec, ss, sizeof ss) == 0);
        ct[(trial * 17) % WIRE] ^= (uint8_t)(1u << (trial % 8));
        assert(ntruplus768_dec_impl(dec, ct, b->sk) == 1);
        for (unsigned i = 0; i < sizeof dec; ++i) assert(dec[i] == 0);
    }
    bank *b = &banks[0];
    memcpy(pk, b->pk, sizeof pk);
    for (unsigned packet = 0; packet < 48; ++packet) {
        unsigned invalid = packet % 2 ? 3457 : 4095;
        memcpy(b->pk, pk, sizeof pk);
        b->pk[24 * packet + 22] = (uint8_t)((b->pk[24 * packet + 22] & 15) | ((invalid & 15) << 4));
        b->pk[24 * packet + 23] = (uint8_t)(invalid >> 4);
        for (unsigned variant = 0; variant < 2; ++variant) {
            memset(b->ct, 0xa5, sizeof b->ct);
            memset(b->ss, 0x5a, sizeof b->ss);
            assert(functions[1][variant](b) == 1);
            for (unsigned i = 0; i < sizeof b->ct; ++i) assert(b->ct[i] == 0);
            for (unsigned i = 0; i < sizeof b->ss; ++i) assert(b->ss[i] == 0);
        }
    }
    memcpy(b->pk, pk, sizeof pk);
    fprintf(stderr, "preflight=pass deterministic_encap=100 keys=16 tampered_ct=100 invalid_pk_packets=48 immutability=pass\n");
}

int main(void) {
    prepare();
    preflight();
#ifndef CORRECTNESS_ONLY
    fprintf(stderr, "cpucycles_implementation=%s cpucycles_persecond=%lld\n",
            cpucycles_implementation(), (long long)cpucycles_persecond());
    puts("region,block,slot,observation,bank,cycles");
    for (int region = 0; region < 2; ++region) {
        for (int block = 0; block < 8; ++block) {
            const int abba[4] = {0, 1, 1, 0}, baab[4] = {1, 0, 0, 1};
            const int *order = block % 2 ? baab : abba;
            for (int slot = 0; slot < 4; ++slot) {
                operation fn = functions[region][order[slot]];
                /* Match warmup, bank order and address for both variants.
                 * Mode selection, validation, IO and input setup are untimed. */
                for (int bank_id = 0; bank_id < BANKS; ++bank_id) assert(fn(&banks[bank_id]) == 0);
                long long elapsed[32];
                for (int observation = 0; observation < 32; ++observation) {
                    bank *b = &banks[observation % BANKS];
                    long long begin = cpucycles();
                    int rc = fn(b);
                    long long end = cpucycles();
                    assert(rc == 0);
                    elapsed[observation] = end - begin;
                }
                for (int observation = 0; observation < 32; ++observation)
                    printf("%d,%d,%d,%d,%d,%lld\n", region, block, slot, observation,
                           observation % BANKS, elapsed[observation]);
            }
        }
    }
#endif
    return 0;
}
