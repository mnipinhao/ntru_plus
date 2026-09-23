/* NTRU+864 decapsulation arithmetic, GT against Official, component by component.
 * Official symbols renamed o_*; both sides fed canonical data. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "params.h"
#include "poly.h"
#include "inverse.h"
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
void poly_tobytes_small(uint8_t *out, const poly *in);
void poly_basemul_rinv(int16_t *out, const int16_t *a, const int16_t *b);
void o_poly_tobytes(uint8_t *, const poly *); int o_poly_frombytes(poly *, const uint8_t *);
void o_poly_cbd1(poly *, const uint8_t *); int o_poly_sotp_decode(uint8_t *, const poly *, const uint8_t *);
void o_poly_ntt(poly *); void o_poly_invntt_scale(poly *); void o_poly_basemul(poly *, const poly *, const poly *);
void o_poly_basemul_scale(poly *, const poly *, const poly *); void o_poly_sub(poly *, const poly *, const poly *);
void o_poly_crepmod3(poly *);
static poly a, b, r, m0, t; static uint8_t bytes[NTRUPLUS_POLYBYTES], out[NTRUPLUS_POLYBYTES], msg[NTRUPLUS_N/8], buf[NTRUPLUS_N/4];
static uint8_t scratch[POLY_INVNTT_TERNARY_SCRATCHBYTES]; static volatile int sink;
static void g_from(void){ sink += poly_frombytes(&r, bytes); }       static void o_from(void){ sink += o_poly_frombytes(&r, bytes); }
static void g_bmr(void){ poly_basemul_rinv(r.coeffs, a.coeffs, b.coeffs); } static void o_bms(void){ o_poly_basemul_scale(&r, &a, &b); }
static void g_inv(void){ memcpy(&t, &m0, sizeof t); poly_invntt_ternary(&t, &t, scratch); }
static void o_inv(void){ memcpy(&t, &m0, sizeof t); o_poly_invntt_scale(&t); o_poly_crepmod3(&t); }
static void cpy(void){ memcpy(&t, &m0, sizeof t); }
static void g_ntt(void){ poly_ntt(&r, &a); }                           static void o_ntt(void){ memcpy(&r, &a, sizeof r); o_poly_ntt(&r); }
static void g_sub(void){ poly_sub(&r, &a, &b); }                       static void o_sub(void){ o_poly_sub(&r, &a, &b); }
static void g_bm(void){ poly_basemul(&r, &a, &b); }                    static void o_bm(void){ o_poly_basemul(&r, &a, &b); }
static void g_tob(void){ poly_tobytes(out, &a); }                      static void o_tob(void){ o_poly_tobytes(out, &a); }
static void g_tobs(void){ poly_tobytes_small(out, &a); }
static void g_sotp(void){ sink += poly_sotp_decode(msg, &t, buf); }    static void o_sotp(void){ sink += o_poly_sotp_decode(msg, &t, buf); }
static void g_cbd(void){ poly_cbd1(&r, buf); }                         static void o_cbd(void){ o_poly_cbd1(&r, buf); }
static double best(void (*f)(void)){ double bst = 1e30; for (int w = 0; w < 3000; w++) f();
  for (int k = 0; k < 300; k++){ START(); for (int i = 0; i < 100; i++) f(); double d = STOP() / 100; if (d < bst) bst = d; } return bst; }
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
#else
  if (perf_counter_open()) return 2;
#endif
  uint32_t s = 9; for (int i = 0; i < NTRUPLUS_N; i++){ s^=s<<13; s^=s>>17; s^=s<<5; a.coeffs[i] = s % 3457; s^=s<<13; s^=s>>17; s^=s<<5; b.coeffs[i] = s % 3457; }
  for (int i = 0; i < (int)sizeof buf; i++){ s^=s<<13; s^=s>>17; s^=s<<5; buf[i] = s; }
  o_poly_tobytes(bytes, &a); poly_basemul_rinv(m0.coeffs, a.coeffs, b.coeffs);
  for (int i = 0; i < NTRUPLUS_N; i++) t.coeffs[i] = (int16_t)(i % 3) - 1;
#ifdef __APPLE__
  { uint64_t t1 = now(); while (now() - t1 < 3000000000ull) { g_inv(); o_inv(); g_ntt(); o_ntt(); } }   /* reach a P-core at full clock */
#endif
  double c = best(cpy);
  struct { const char *n; int k; void (*g)(void); void (*o)(void); } rows[] = {
    {"frombytes (x3)", 3, g_from, o_from}, {"first product", 1, g_bmr, o_bms}, {"inverse->ternary", 1, g_inv, o_inv},
    {"forward NTT (x2)", 2, g_ntt, o_ntt}, {"sub", 1, g_sub, o_sub}, {"basemul", 1, g_bm, o_bm},
    {"tobytes (x2)", 2, g_tob, o_tob}, {"sotp_decode", 1, g_sotp, o_sotp}, {"cbd1", 1, g_cbd, o_cbd} };
  double tg = 0, to = 0;
  for (unsigned i = 0; i < sizeof rows / sizeof rows[0]; i++){
    double x = best(rows[i].g), y = best(rows[i].o);
    if (rows[i].g == g_inv) { x -= c; y -= c; }
    if (rows[i].g == g_ntt) y -= 0;   /* Official's copy-in is part of its in-place API */
    printf("%-18s GT %8.1f  Off %8.1f  %s  x%d -> %+8.1f\n", rows[i].n, x, y, UNIT, rows[i].k, rows[i].k * (x - y));
    tg += rows[i].k * x; to += rows[i].k * y; }
  printf("GT tobytes_small %.1f (one of the two GT tobytes is the small one)\n", best(g_tobs));
  printf("total arithmetic  GT %.1f  Off %.1f  %s  (%+.1f)\n", tg, to, UNIT, tg - to);
  return 0; }
