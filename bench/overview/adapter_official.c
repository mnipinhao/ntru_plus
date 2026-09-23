/*
 * Component adapter for Official-derived NTRU+ AVX2 trees (Official avx2,
 * Official-opt qualification exports, and the Official-path parts of the
 * 1152 exp017 GT tree).  Compiled inside the implementation's include path.
 *
 *   -DOVB_FORWARD=<sym>    Forward the implementation's KEM calls (default poly_ntt)
 *   -DOVB_TOBYTES=<sym>    poly_tobytes binding (default poly_tobytes)
 *   -DOVB_FROMBYTES=<sym>  poly_frombytes binding (default poly_frombytes)
 *   -DOVB_EXP017           add the exp017 GT Encap blocks (GT Forward,
 *                          Serializer V2 + hash_g, H4 exact egress)
 *
 * Inputs mirror the KEM: Forward consumes a CBD1 polynomial, BaseMul /
 * BaseMulScale consume two Forward outputs, BaseInv a Forward output of
 * 3*CBD1+1, inverse a BaseMulScale output, crepmod3 an inverse output,
 * tobytes a BaseMul output, frombytes a public key.  Diagnostic only.
 */
#include <stdint.h>
#include <string.h>

#include "api.h"
#include "params.h"
#include "poly.h"
#include "symmetric.h"
#include "fips202.h"
#include "ovb.h"

#ifdef OVB_EXP017
#include "wire-monotone-kem.h"
#include "scale1-r-serializer-v2-asm.h"
#include "scale1_r_serializer_v2_hash_g.h"
#endif

#ifndef OVB_FORWARD
#define OVB_FORWARD poly_ntt
#else
void OVB_FORWARD(poly *);
#endif
#ifndef OVB_TOBYTES
#define OVB_TOBYTES poly_tobytes
#else
void OVB_TOBYTES(uint8_t *, const poly *);
#endif
#ifndef OVB_FROMBYTES
#define OVB_FROMBYTES poly_frombytes
#else
int OVB_FROMBYTES(poly *, const uint8_t *);
#endif

int crypto_kem_keypair(unsigned char *, unsigned char *);
int crypto_kem_enc(unsigned char *, unsigned char *, const unsigned char *);
int crypto_kem_dec(unsigned char *, const unsigned char *, const unsigned char *);

#define B OVB_BANKS
static poly small[B], small2[B], fin[B], fhat[B], ghat[B], prod[B], sc[B], inv[B], sotp[B], work[B];
static uint8_t pk[B][NTRUPLUS_PUBLICKEYBYTES], sk[B][NTRUPLUS_SECRETKEYBYTES];
static uint8_t ct[B][NTRUPLUS_CIPHERTEXTBYTES], ss[B][NTRUPLUS_SSBYTES];
static uint8_t pk_o[B][NTRUPLUS_PUBLICKEYBYTES], sk_o[B][NTRUPLUS_SECRETKEYBYTES];
static uint8_t ct_o[B][NTRUPLUS_CIPHERTEXTBYTES], ss_o[B][NTRUPLUS_SSBYTES];
static uint8_t bytes_o[B][NTRUPLUS_POLYBYTES];
static uint8_t msg[B][HASH_H_INBYTES], msg_o[B][HASH_H_INBYTES];
static uint8_t buf[B][NTRUPLUS_N / 4], coins[B][NTRUPLUS_SYMBYTES];
static uint8_t hout[B][HASH_H_OUTBYTES + HASH_G_OUTBYTES];
static volatile int sink;
#ifdef OVB_EXP017
static poly wire_r[B], wire_m[B], wire_o[B];
#endif

static void fill(uint8_t *p, unsigned n, unsigned tag) {
    for (unsigned i = 0; i < n; i++) p[i] = (uint8_t)(i * 131U + tag * 29U + (i >> 3) * 7U);
}

static void setup(void) {
    for (unsigned b = 0; b < B; b++) {
        ovb_rng_seed(100 + b);
        if (crypto_kem_keypair(pk[b], sk[b])) __builtin_trap();
        ovb_rng_seed(200 + b);
        if (crypto_kem_enc(ct[b], ss[b], pk[b])) __builtin_trap();
        fill(buf[b], sizeof buf[b], 300 + b);
        fill(msg[b], sizeof msg[b], 400 + b);
        fill(coins[b], sizeof coins[b], 500 + b);
        poly_cbd1(&small[b], buf[b]);
        fill(buf[b], sizeof buf[b], 600 + b);
        poly_cbd1(&small2[b], buf[b]);
        fin[b] = small[b]; poly_triple(&fin[b]); fin[b].coeffs[0] += 1; OVB_FORWARD(&fin[b]);
        fhat[b] = small[b]; OVB_FORWARD(&fhat[b]);
        ghat[b] = small2[b]; OVB_FORWARD(&ghat[b]);
        poly_basemul(&prod[b], &fhat[b], &ghat[b]);
        poly_basemul_scale(&sc[b], &fhat[b], &ghat[b]);
        inv[b] = sc[b]; poly_invntt_scale(&inv[b]);
        poly_sotp_encode(&sotp[b], msg[b], buf[b]);
#ifdef OVB_EXP017
        ntruplus1152_exp001_top_split_small(wire_r[b].coeffs, small[b].coeffs);
        ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(wire_r[b].coeffs);
        ntruplus1152_exp001_top_split_small(wire_m[b].coeffs, small2[b].coeffs);
        ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(wire_m[b].coeffs);
#endif
    }
}

static void p_small(unsigned b) { work[b] = small[b]; }
static void p_sc(unsigned b) { work[b] = sc[b]; }
static void p_inv(unsigned b) { work[b] = inv[b]; }
static void p_kg(unsigned b) { ovb_rng_seed(1000 + b); }
static void p_enc(unsigned b) { ovb_rng_seed(2000 + b); }

static void r_forward(unsigned b) { OVB_FORWARD(&work[b]); }
static void r_basemul(unsigned b) { poly_basemul(&work[b], &fhat[b], &ghat[b]); }
static void r_basemul_scale(unsigned b) { poly_basemul_scale(&work[b], &fhat[b], &ghat[b]); }
static void r_baseinv(unsigned b) { sink ^= poly_baseinv(&work[b], &fin[b]); }
static void r_inverse(unsigned b) { poly_invntt_scale(&work[b]); }
static void r_frombytes(unsigned b) { sink ^= OVB_FROMBYTES(&work[b], pk[b]); }
static void r_tobytes(unsigned b) { OVB_TOBYTES(bytes_o[b], &prod[b]); }
static void r_hash_f(unsigned b) { hash_f(hout[b], pk[b]); }
static void r_hash_g(unsigned b) { hash_g(hout[b], pk[b]); }
static void r_hash_h(unsigned b) { hash_h(hout[b], msg[b]); }
static void r_shake(unsigned b) { shake256(hout[b], NTRUPLUS_N / 4, coins[b], NTRUPLUS_SYMBYTES); }
static void r_cbd1(unsigned b) { poly_cbd1(&work[b], buf[b]); }
static void r_triple(unsigned b) { poly_triple(&work[b]); }
static void r_crepmod3(unsigned b) { poly_crepmod3(&work[b]); }
static void r_sotp_encode(unsigned b) { poly_sotp_encode(&work[b], msg[b], buf[b]); }
static void r_sotp_decode(unsigned b) { sink ^= poly_sotp_decode(msg_o[b], &sotp[b], buf[b]); }
static void r_add(unsigned b) { poly_add(&work[b], &prod[b], &fhat[b]); }
static void r_sub(unsigned b) { poly_sub(&work[b], &prod[b], &fhat[b]); }
static void r_kg(unsigned b) { sink ^= crypto_kem_keypair(pk_o[b], sk_o[b]); }
static void r_enc(unsigned b) { sink ^= crypto_kem_enc(ct_o[b], ss_o[b], pk[b]); }
static void r_dec(unsigned b) { sink ^= crypto_kem_dec(ss_o[b], ct[b], sk[b]); }
#ifdef OVB_EXP017
static void r_gt_forward(unsigned b) {
    ntruplus1152_exp001_top_split_small(work[b].coeffs, small[b].coeffs);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(work[b].coeffs);
}
static void r_ser(unsigned b) { ntruplus1152_exp001_scale1_r_serializer_v2(bytes_o[b], wire_r[b].coeffs); }
static void r_ser_hash_g(unsigned b) { ntruplus1152_exp001_scale1_r_serializer_v2_hash_g(hout[b], wire_r[b].coeffs); }
static void r_h4(unsigned b) {
    sink ^= ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(bytes_o[b], pk[b], wire_r[b].coeffs,
                                                               wire_m[b].coeffs, wire_o[b].coeffs);
}
#endif

static const ovb_component table[] = {
    {"forward", p_small, r_forward},
    {"basemul", 0, r_basemul},
    {"basemul_scale", 0, r_basemul_scale},
    {"baseinv", 0, r_baseinv},
    {"inverse", p_sc, r_inverse},
    {"frombytes", 0, r_frombytes},
    {"tobytes", 0, r_tobytes},
    {"hash_f", 0, r_hash_f},
    {"hash_g", 0, r_hash_g},
    {"hash_h", 0, r_hash_h},
    {"shake256_coins", 0, r_shake},
    {"cbd1", 0, r_cbd1},
    {"triple", p_small, r_triple},
    {"crepmod3", p_inv, r_crepmod3},
    {"sotp_encode", 0, r_sotp_encode},
    {"sotp_decode", 0, r_sotp_decode},
    {"add", 0, r_add},
    {"sub", 0, r_sub},
#ifdef OVB_EXP017
    {"gt_forward", 0, r_gt_forward},
    {"serializer_v2", 0, r_ser},
    {"serializer_v2_hash_g", 0, r_ser_hash_g},
    {"h4_exact_egress", 0, r_h4},
#endif
    {"kem_keypair", p_kg, r_kg},
    {"kem_enc", p_enc, r_enc},
    {"kem_dec", 0, r_dec},
};

const ovb_impl ovb_impl_desc = {
#ifdef OVB_EXP017
    "exp017",
#else
    "official",
#endif
    setup, crypto_kem_keypair, crypto_kem_enc, crypto_kem_dec, hash_f, hash_g, hash_h,
    sizeof table / sizeof table[0], table};
