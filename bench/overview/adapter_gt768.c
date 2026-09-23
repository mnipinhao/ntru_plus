/*
 * Component adapter for the NTRU+768 GT32 clean tree (avx2-gt32-clean).
 * GT uses layout-specific stages instead of the Official poly_* primitives:
 *   keygen  forward_p (frontend + P terminal), baseinv_j1, basemul_f0_j1,
 *           pack_p_sp1_lazy (x3)
 *   encap   unpack_m (pk), forward_m (x2), pack_m_lazy (r), basemul_general_m,
 *           pack_m_highrange (ct)
 *   decap   unpack3_m (ct + both sk polys fused), basemul_scale_m,
 *           inverse_m (invntt_m + invntt_tail), forward_m (x2),
 *           basemul_general_m, pack_m_centered (r), equal_m_modq (replaces
 *           the re-encryption tobytes + verify)
 * The shared hash / CBD1 / SOTP / add / sub / crepmod3 / triple primitives
 * are the tree's own copies.  Inputs are produced by the matching GT stages.
 */
#include <stdint.h>
#include <string.h>

#include "api.h"
#include "params.h"
#include "internal.h"
#include "poly.h"
#include "symmetric.h"
#include "fips202.h"
#include "ovb.h"

int crypto_kem_keypair(unsigned char *, unsigned char *);
int crypto_kem_enc(unsigned char *, unsigned char *, const unsigned char *);
int crypto_kem_dec(unsigned char *, const unsigned char *, const unsigned char *);

#define B OVB_BANKS
#define N NTRUPLUS_N
typedef struct { int16_t c[N]; } __attribute__((aligned(64))) vec;
static poly small[B], small2[B], fin_c[B], inv_out[B], sotp[B], work_p[B];
static vec m0[B], m1[B], p_f[B], p_inv[B], p_h[B], sc_m[B], gm[B], gma[B], out[B], tmp[B], tmp2[B];
static uint8_t pk[B][NTRUPLUS_PUBLICKEYBYTES], sk[B][NTRUPLUS_SECRETKEYBYTES];
static uint8_t ct[B][NTRUPLUS_CIPHERTEXTBYTES], ss[B][NTRUPLUS_SSBYTES];
static uint8_t pk_o[B][NTRUPLUS_PUBLICKEYBYTES], sk_o[B][NTRUPLUS_SECRETKEYBYTES];
static uint8_t ct_o[B][NTRUPLUS_CIPHERTEXTBYTES], ss_o[B][NTRUPLUS_SSBYTES];
static uint8_t bytes_o[B][NTRUPLUS_POLYBYTES];
static uint8_t msg[B][HASH_H_INBYTES], msg_o[B][HASH_H_INBYTES];
static uint8_t buf[B][NTRUPLUS_N / 4], coins[B][NTRUPLUS_SYMBYTES];
static uint8_t hout[B][HASH_H_OUTBYTES + HASH_G_OUTBYTES];
static volatile int sink;

static void fill(uint8_t *p, unsigned n, unsigned tag) {
    for (unsigned i = 0; i < n; i++) p[i] = (uint8_t)(i * 131U + tag * 29U + (i >> 3) * 7U);
}
static void fwd_m(int16_t *o, int16_t *scratch, const int16_t *in) {
    ntruplus768_ntt_frontend_avx2(scratch, in);
    ntruplus768_ntt_m_avx2(o, scratch);
}
static void fwd_p(int16_t *o, int16_t *scratch, const int16_t *in) {
    ntruplus768_ntt_frontend_avx2(scratch, in);
    ntruplus768_ntt_p_avx2(o, scratch);
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
        fin_c[b] = small[b]; poly_triple(&fin_c[b]); fin_c[b].coeffs[0] += 1;
        fwd_p(p_f[b].c, tmp[b].c, fin_c[b].coeffs);
        if (ntruplus768_baseinv_j1_avx2(p_inv[b].c, p_f[b].c)) __builtin_trap();
        ntruplus768_basemul_f0_j1_avx2(p_h[b].c, p_f[b].c, p_inv[b].c);
        fwd_m(m0[b].c, tmp[b].c, small[b].coeffs);
        fwd_m(m1[b].c, tmp[b].c, small2[b].coeffs);
        ntruplus768_basemul_scale_m_avx2(sc_m[b].c, m0[b].c, m1[b].c);
        ntruplus768_basemul_general_m_avx2(gm[b].c, m0[b].c, m1[b].c);
        poly_add((poly *)(void *)gma[b].c, (const poly *)(const void *)gm[b].c,
                 (const poly *)(const void *)m0[b].c);
        ntruplus768_invntt_m_avx2(tmp[b].c, sc_m[b].c);
        ntruplus768_invntt_tail_avx2(inv_out[b].coeffs, tmp[b].c);
        poly_sotp_encode(&sotp[b], msg[b], buf[b]);
    }
}

static void p_small(unsigned b) { work_p[b] = small[b]; }
static void p_invout(unsigned b) { work_p[b] = inv_out[b]; }
static void p_kg(unsigned b) { ovb_rng_seed(1000 + b); }
static void p_enc(unsigned b) { ovb_rng_seed(2000 + b); }

static void r_forward_m(unsigned b) { fwd_m(out[b].c, tmp[b].c, small[b].coeffs); }
static void r_forward_p(unsigned b) { fwd_p(out[b].c, tmp[b].c, fin_c[b].coeffs); }
static void r_baseinv(unsigned b) { sink ^= ntruplus768_baseinv_j1_avx2(out[b].c, p_f[b].c); }
static void r_bm_f0_j1(unsigned b) { ntruplus768_basemul_f0_j1_avx2(out[b].c, p_f[b].c, p_inv[b].c); }
static void r_bm_general(unsigned b) { ntruplus768_basemul_general_m_avx2(out[b].c, m0[b].c, m1[b].c); }
static void r_bm_scale(unsigned b) { ntruplus768_basemul_scale_m_avx2(out[b].c, m0[b].c, m1[b].c); }
static void r_inverse(unsigned b) {
    ntruplus768_invntt_m_avx2(tmp2[b].c, sc_m[b].c);
    ntruplus768_invntt_tail_avx2(out[b].c, tmp2[b].c);
}
static void r_unpack(unsigned b) { sink ^= ntruplus768_unpack_m_avx2(out[b].c, pk[b]); }
static void r_unpack3(unsigned b) { sink ^= ntruplus768_unpack3_m_avx2(out[b].c, tmp[b].c, tmp2[b].c, ct[b], sk[b]); }
static void r_pack_p(unsigned b) { ntruplus768_pack_p_sp1_lazy10788_avx2(bytes_o[b], p_h[b].c); }
static void r_pack_lazy(unsigned b) { ntruplus768_pack_m_lazy10788_avx2(bytes_o[b], m0[b].c); }
static void r_pack_high(unsigned b) { ntruplus768_pack_m_highrange12699_avx2(bytes_o[b], gma[b].c); }
static void r_pack_centered(unsigned b) { ntruplus768_pack_m_centered_avx2(bytes_o[b], gm[b].c); }
static void r_equal(unsigned b) { sink ^= ntruplus768_equal_m_modq12699_avx2(m0[b].c, m1[b].c); }
static void r_hash_f(unsigned b) { hash_f(hout[b], pk[b]); }
static void r_hash_g(unsigned b) { hash_g(hout[b], pk[b]); }
static void r_hash_h(unsigned b) { hash_h(hout[b], msg[b]); }
static void r_shake(unsigned b) { shake256(hout[b], NTRUPLUS_N / 4, coins[b], NTRUPLUS_SYMBYTES); }
static void r_cbd1(unsigned b) { poly_cbd1(&work_p[b], buf[b]); }
static void r_triple(unsigned b) { poly_triple(&work_p[b]); }
static void r_crepmod3(unsigned b) { poly_crepmod3(&work_p[b]); }
static void r_sotp_encode(unsigned b) { poly_sotp_encode(&work_p[b], msg[b], buf[b]); }
static void r_sotp_decode(unsigned b) { sink ^= poly_sotp_decode(msg_o[b], &sotp[b], buf[b]); }
static void r_add(unsigned b) { poly_add(&work_p[b], (const poly *)(const void *)gm[b].c, (const poly *)(const void *)m0[b].c); }
static void r_sub(unsigned b) { poly_sub(&work_p[b], (const poly *)(const void *)gm[b].c, (const poly *)(const void *)m0[b].c); }
static void r_kg(unsigned b) { sink ^= crypto_kem_keypair(pk_o[b], sk_o[b]); }
static void r_enc(unsigned b) { sink ^= crypto_kem_enc(ct_o[b], ss_o[b], pk[b]); }
static void r_dec(unsigned b) { sink ^= crypto_kem_dec(ss_o[b], ct[b], sk[b]); }

static const ovb_component table[] = {
    {"forward_m", 0, r_forward_m},
    {"forward_p", 0, r_forward_p},
    {"basemul_general_m", 0, r_bm_general},
    {"basemul_f0_j1", 0, r_bm_f0_j1},
    {"basemul_scale_m", 0, r_bm_scale},
    {"baseinv_j1", 0, r_baseinv},
    {"inverse_m", 0, r_inverse},
    {"unpack_m", 0, r_unpack},
    {"unpack3_m", 0, r_unpack3},
    {"pack_p_sp1_lazy", 0, r_pack_p},
    {"pack_m_lazy", 0, r_pack_lazy},
    {"pack_m_highrange", 0, r_pack_high},
    {"pack_m_centered", 0, r_pack_centered},
    {"equal_m_modq", 0, r_equal},
    {"hash_f", 0, r_hash_f},
    {"hash_g", 0, r_hash_g},
    {"hash_h", 0, r_hash_h},
    {"shake256_coins", 0, r_shake},
    {"cbd1", 0, r_cbd1},
    {"triple", p_small, r_triple},
    {"crepmod3", p_invout, r_crepmod3},
    {"sotp_encode", 0, r_sotp_encode},
    {"sotp_decode", 0, r_sotp_decode},
    {"add", 0, r_add},
    {"sub", 0, r_sub},
    {"kem_keypair", p_kg, r_kg},
    {"kem_enc", p_enc, r_enc},
    {"kem_dec", 0, r_dec},
};

const ovb_impl ovb_impl_desc = {"gt768", setup, crypto_kem_keypair, crypto_kem_enc, crypto_kem_dec,
                                hash_f, hash_g, hash_h, sizeof table / sizeof table[0], table};
