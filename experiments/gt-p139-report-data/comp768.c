/* P139: NTRU+768 arithmetic, GT against SUPERCOP's Official, phase by phase (P136's method for
 * 864/1152).  GT fuses several steps, so rows are phases that do the same work on both sides:
 *   keygen  cbd1 x2, triple + forward NTT x2, baseinv x2, basemul x2, tobytes x3
 *   encaps  frombytes, cbd1, forward NTT x2, tobytes (the r transcript), sotp_encode,
 *           basemul_add + tobytes (the ciphertext)
 *   decaps  decode ct, f, hinv + first product; inverse -> ternary; forward NTT x2 (Official's
 *           kem.c copies once, f = m); sub; basemul; tobytes x2; sotp_decode; cbd1
 * Inputs come from a real key pair and ciphertext (GT's crypto_kem_*; the byte formats are
 * shared), and the baseinv inputs are invertible on both sides, so no call takes a failure exit.
 * Official symbols renamed o_*. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "api.h"
#include "params.h"
#include "poly.h"
#include "keygen.h"
#include "encap.h"
#include "decap.h"
#ifdef __APPLE__
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
static inline uint64_t now(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
#define UNIT "ns"
#define START() uint64_t t0=now()
#define STOP() (double)(now()-t0)
#else
#include "perf_counter.h"
#define UNIT "cyc"
#define START() perf_counter_start()
#define STOP() (double)perf_counter_stop()
#endif
int crypto_kem_keypair(unsigned char *pk, unsigned char *sk);
/* abi_wrap.S: these four clobber d8-d15, so they are called through an AAPCS64 wrapper (as kem.c's
 * callers reach them through kem_api.S); the wrapper's cost, a few instructions, is in the GT rows. */
void w_poly_cbd1(poly *, const uint8_t *); void w_poly_sotp_encode(poly *, const uint8_t *, const uint8_t *);
int w_poly_sotp_decode(uint8_t *, const poly *, const uint8_t *); void w_poly_triple(poly *, const poly *);
int crypto_kem_enc(unsigned char *ct, unsigned char *ss, const unsigned char *pk);
void o_poly_cbd1(poly *, const uint8_t *); void o_poly_triple(poly *); void o_poly_ntt(poly *);
int o_poly_baseinv(poly *, const poly *); void o_poly_basemul(poly *, const poly *, const poly *);
void o_poly_tobytes(uint8_t *, const poly *); int o_poly_frombytes(poly *, const uint8_t *);
void o_poly_sotp_encode(poly *, const uint8_t *, const uint8_t *); int o_poly_sotp_decode(uint8_t *, const poly *, const uint8_t *);
void o_poly_basemul_add(poly *, const poly *, const poly *, const poly *); void o_poly_basemul_scale(poly *, const poly *, const poly *);
void o_poly_invntt_scale(poly *); void o_poly_crepmod3(poly *); void o_poly_sub(poly *, const poly *, const poly *);

static uint8_t pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES], ct[CRYPTO_CIPHERTEXTBYTES], ss[CRYPTO_BYTES];
static uint8_t buf[NTRUPLUS_N / 4], msg[NTRUPLUS_N / 8], out[NTRUPLUS_POLYBYTES], scratch[POLY_INVNTT_TERNARY_DECAP_SCRATCHBYTES];
static poly a, r, t, s1, s2, oh, oc, of, ohinv, om, osmall, gh, gsmall, gm1, gcq_in;
static gt_cq_poly gf, gfinv, gcq, gcq2;
static poly gfp, gdec_ct, gm_r, ofp;          /* decaps: first-product outputs */
static volatile int sink;
/* keygen */
static void g_cbd(void){ w_poly_cbd1(&r, buf); }                     static void o_cbd(void){ o_poly_cbd1(&r, buf); }
static void g_tn(void){ w_poly_triple(&gcq.storage, &a); gcq.storage.coeffs[0] += 1; poly_ntt_keygen_cq(&gcq, &gcq.storage); }
static void o_tn(void){ o_poly_triple(&t); o_poly_ntt(&t); }
static void g_inv(void){ sink += poly_baseinv_keygen_cq_scaled_r(&gcq2, &gf); } static void o_inv(void){ sink += o_poly_baseinv(&t, &of); }
static void g_bm(void){ poly_basemul_keygen_cq_scaled_r(&gcq2, &gf, &gfinv); }  static void o_bm(void){ o_poly_basemul(&t, &of, &a); }
static void g_tb3(void){ poly_tobytes_keygen_cq(out, &gfinv); poly_tobytes_keygen_cq(out, &gfinv); poly_tobytes_keygen_cq(out, &gfinv); }
static void o_tb3(void){ o_poly_tobytes(out, &a); o_poly_tobytes(out, &a); o_poly_tobytes(out, &a); }
/* encaps */
static void g_fb(void){ sink += poly_frombytes_encap(&t, pk); }    static void o_fb(void){ sink += o_poly_frombytes(&t, pk); }
static void g_ntt(void){ poly_ntt_encap_small_lazy(&t, &gsmall); } static void o_ntt(void){ o_poly_ntt(&t); }
static void g_tbr(void){ poly_tobytes_encap_loose(out, &gm1); }    static void o_tbr(void){ o_poly_tobytes(out, &a); }
static void g_se(void){ w_poly_sotp_encode(&t, msg, buf); }          static void o_se(void){ o_poly_sotp_encode(&t, msg, buf); }
static void g_bma(void){ poly_basemul_add_encap(&t, &gh, &gm1, &gm1); poly_tobytes_encap(out, &t); }
static void o_bma(void){ o_poly_basemul_add(&t, &oh, &osmall, &osmall); o_poly_tobytes(out, &t); }
/* the same two steps apart; kem.c's basemul_add writes m in place (exact alias), measured both ways */
static poly gm2;
static void g_bmo(void){ poly_basemul_add_encap(&t, &gh, &gm1, &gm1); }
static void g_bmi(void){ memcpy(&gm2, &gm1, sizeof gm2); poly_basemul_add_encap(&gm2, &gh, &gm1, &gm2); }
static void g_cp2(void){ memcpy(&gm2, &gm1, sizeof gm2); __asm__ volatile("" : : "r"(&gm2) : "memory"); }
static void g_tbe(void){ poly_tobytes_encap(out, &t); }
static void o_bmo(void){ o_poly_basemul_add(&t, &oh, &osmall, &osmall); }
static void o_tbe(void){ o_poly_tobytes(out, &t); }
/* decaps */
static void g_dec(void){ sink += poly_frombytes_basemul_decap_scale(&gm_r, &gdec_ct, ct, sk) + poly_frombytes_decap(&t, sk + NTRUPLUS_POLYBYTES); }
static void o_dec(void){ sink += o_poly_frombytes(&oc, ct) + o_poly_frombytes(&of, sk) + o_poly_frombytes(&ohinv, sk + NTRUPLUS_POLYBYTES); o_poly_basemul_scale(&t, &oc, &of); }
static void g_it(void){ memcpy(&t, &gfp, sizeof t); poly_invntt_ternary_decap(&t, scratch); }
static void o_it(void){ memcpy(&t, &ofp, sizeof t); o_poly_invntt_scale(&t); o_poly_crepmod3(&t); }
static void cpy(void){ memcpy(&t, &gfp, sizeof t); __asm__ volatile("" : : "r"(&t) : "memory"); }
static void g_dn(void){ poly_ntt_decap(&t, &s1); poly_ntt_decap(&t, &s1); }
static void o_dn(void){ memcpy(&t, &s1, sizeof t); __asm__ volatile("" : : "r"(&t) : "memory"); o_poly_ntt(&t); o_poly_ntt(&t); }
static void g_sub(void){ poly_sub(&t, &s1, &s2); }                 static void o_sub(void){ o_poly_sub(&t, &s1, &s2); }
static void g_dbm(void){ poly_basemul_decap(&t, &s1, &s2); }       static void o_dbm(void){ o_poly_basemul(&t, &s1, &s2); }
static void g_tb2(void){ poly_tobytes_decap(out, &a); poly_tobytes_decap(out, &a); } static void o_tb2(void){ o_poly_tobytes(out, &a); o_poly_tobytes(out, &a); }
static void g_sd(void){ sink += w_poly_sotp_decode(msg, &gsmall, buf); } static void o_sd(void){ sink += o_poly_sotp_decode(msg, &gsmall, buf); }

static double best(void (*f)(void)){ double b = 1e30; for (int w = 0; w < 2000; w++) f();
  for (int k = 0; k < 300; k++){ START(); for (int i = 0; i < 100; i++) f(); double d = STOP() / 100; if (d < b) b = d; } return b; }
static uint32_t s = 11; static uint32_t rnd(void){ s ^= s << 13; s ^= s >> 17; s ^= s << 5; return s; }
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
#else
  if (perf_counter_open()) return 2;
#endif
  for (int i = 0; i < NTRUPLUS_N; i++){ a.coeffs[i] = rnd() % 3457; s1.coeffs[i] = rnd() % 3457; s2.coeffs[i] = rnd() % 3457; }
  for (unsigned i = 0; i < sizeof buf; i++) buf[i] = rnd();
  for (unsigned i = 0; i < sizeof msg; i++) msg[i] = rnd();
  crypto_kem_keypair(pk, sk); crypto_kem_enc(ct, ss, pk);
  /* f invertible on both sides, each in its own layout */
  for (;;) { for (unsigned i = 0; i < sizeof buf; i++) buf[i] = rnd();
    w_poly_cbd1(&gf.storage, buf); w_poly_triple(&gf.storage, &gf.storage); gf.storage.coeffs[0] += 1; of = gf.storage;
    poly_ntt_keygen_cq(&gf, &gf.storage); o_poly_ntt(&of);
    if (!poly_baseinv_keygen_cq_scaled_r(&gfinv, &gf) && !o_poly_baseinv(&t, &of)) break; }
  w_poly_cbd1(&gsmall, buf);                                   /* signed [-2,2]: the small NTT's input */
  poly_ntt_encap_small_lazy(&gm1, &gsmall);
  poly_frombytes_encap(&gh, pk); o_poly_frombytes(&oh, pk);
  o_poly_cbd1(&osmall, buf); o_poly_ntt(&osmall);
  poly_frombytes_basemul_decap_scale(&gfp, &gdec_ct, ct, sk);
  o_poly_frombytes(&oc, ct); o_poly_frombytes(&of, sk); o_poly_basemul_scale(&ofp, &oc, &of);
  gsmall = gsmall; t = a;
#ifdef __APPLE__
  { uint64_t t1 = now(); while (now() - t1 < 3000000000ull) { g_dn(); o_dn(); g_it(); o_it(); } }
#endif
  double c = best(cpy);
  struct { const char *op, *n; double k; void (*g)(void), (*o)(void); int sub_copy; } rows[] = {
    {"keygen", "cbd1 (f, g)", 2, g_cbd, o_cbd, 0},
    {"keygen", "triple + forward NTT (f, g)", 2, g_tn, o_tn, 0},
    {"keygen", "baseinv (f, g)", 2, g_inv, o_inv, 0},
    {"keygen", "basemul x2", 2, g_bm, o_bm, 0},
    {"keygen", "tobytes x3", 1, g_tb3, o_tb3, 0},
    {"encaps", "frombytes (pk)", 1, g_fb, o_fb, 0},
    {"encaps", "cbd1", 1, g_cbd, o_cbd, 0},
    {"encaps", "forward NTT x2", 2, g_ntt, o_ntt, 0},
    {"encaps", "tobytes (r transcript)", 1, g_tbr, o_tbr, 0},
    {"encaps", "sotp_encode", 1, g_se, o_se, 0},
    {"encaps", "basemul_add + tobytes (ct)", 1, g_bma, o_bma, 0},
    {"decaps", "decode ct,f,hinv + 1st product", 1, g_dec, o_dec, 0},
    {"decaps", "inverse -> ternary", 1, g_it, o_it, 1},
    {"decaps", "forward NTT x2 (+Official copy)", 1, g_dn, o_dn, 0},
    {"decaps", "sub", 1, g_sub, o_sub, 0},
    {"decaps", "basemul", 1, g_dbm, o_dbm, 0},
    {"decaps", "tobytes x2", 1, g_tb2, o_tb2, 0},
    {"decaps", "sotp_decode", 1, g_sd, o_sd, 0},
    {"decaps", "cbd1", 1, g_cbd, o_cbd, 0} };
  double tg[3] = {0}, to[3] = {0};
  printf("NTRU+768 arithmetic, GT - Official (%s), Official as its kem.c calls it\n", UNIT);
  for (unsigned i = 0; i < sizeof rows / sizeof rows[0]; i++){
    double x = best(rows[i].g), y = best(rows[i].o); if (rows[i].sub_copy) { x -= c; y -= c; }
    int op = rows[i].op[0] == 'k' ? 0 : rows[i].op[0] == 'e' ? 1 : 2;
    printf("%s  %-32s GT %8.1f  Off %8.1f  x%.0f -> %+8.1f\n", rows[i].op, rows[i].n, x, y, rows[i].k, rows[i].k * (x - y));
    tg[op] += rows[i].k * x; to[op] += rows[i].k * y; }
  { poly_basemul_add_encap(&t, &gh, &gm1, &gm1); double c2 = best(g_cp2);
    printf("  (encaps detail) GT basemul_add out-of-place %.1f, in place as kem.c %.1f, tobytes_encap %.1f;"
           " Official basemul_add %.1f, tobytes %.1f %s\n", best(g_bmo), best(g_bmi) - c2, best(g_tbe), best(o_bmo), best(o_tbe), UNIT); }
  const char *nm[3] = {"keygen", "encaps", "decaps"};
  for (int i = 0; i < 3; i++) printf("%s arithmetic  GT %.1f  Off %.1f  %+.1f %s\n", nm[i], tg[i], to[i], tg[i] - to[i], UNIT);
  return 0; }
