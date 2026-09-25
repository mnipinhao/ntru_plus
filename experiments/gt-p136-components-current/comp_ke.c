/* Key generation and encapsulation arithmetic, GT against Official, component
 * by component (P128's comp2.c).  P136: Official's poly_triple and poly_ntt are
 * timed in place with no copy, as its kem.c calls them in key generation and
 * encapsulation; these kernels are constant time, so the data they run over
 * does not change their time.  Official symbols renamed o_*.  RETRY_F/RETRY_G are the
 * expected attempts per key generation (1152: 29.6% / 27.4% of candidates are
 * non-invertible, P124); the f/g steps are weighted by them. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "params.h"
#include "poly.h"
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
#if NTRUPLUS_N == 1152
#define RETRY_F 1.42
#define RETRY_G 1.38
#else
#define RETRY_F 1.0
#define RETRY_G 1.0
#endif
void poly_tobytes_small(uint8_t *out, const poly *in);
int poly_frombytes(poly *r, const uint8_t a[NTRUPLUS_POLYBYTES]);
void o_poly_tobytes(uint8_t *, const poly *); int o_poly_frombytes(poly *, const uint8_t *);
void o_poly_cbd1(poly *, const uint8_t *); void o_poly_sotp_encode(poly *, const uint8_t *, const uint8_t *);
void o_poly_ntt(poly *); int o_poly_baseinv(poly *, const poly *); void o_poly_basemul(poly *, const poly *, const poly *);
void o_poly_basemul_add(poly *, const poly *, const poly *, const poly *); void o_poly_triple(poly *);
static poly a, b, c, r, fg, fo; static uint8_t bytes[NTRUPLUS_POLYBYTES], out[NTRUPLUS_POLYBYTES], msg[NTRUPLUS_N/8], buf[NTRUPLUS_N/4];
static volatile int sink;
static void g_cbd(void){ poly_cbd1(&r, buf); }            static void o_cbd(void){ o_poly_cbd1(&r, buf); }
static void g_tri(void){ poly_triple(&r, &a); }           static void o_tri(void){ o_poly_triple(&r); }
static void g_ntt(void){ poly_ntt(&r, &a); }              static void o_ntt(void){ o_poly_ntt(&r); }
static void g_inv(void){ sink += poly_baseinv(&r, &fg); } static void o_inv(void){ sink += o_poly_baseinv(&r, &fo); }
static void g_bm(void){ poly_basemul(&r, &a, &b); }       static void o_bm(void){ o_poly_basemul(&r, &a, &b); }
static void g_tob(void){ poly_tobytes(out, &a); }         static void o_tob(void){ o_poly_tobytes(out, &a); }
static void g_tobs(void){ poly_tobytes_small(out, &c); }
/* key generation serializes f in full and pk, hinv with the small serializer */
static void g_tob3(void){ poly_tobytes(out, &a); poly_tobytes_small(out, &c); poly_tobytes_small(out, &c); }
static void o_tob3(void){ o_poly_tobytes(out, &a); o_poly_tobytes(out, &c); o_poly_tobytes(out, &c); }
static void g_from(void){ sink += poly_frombytes(&r, bytes); } static void o_from(void){ sink += o_poly_frombytes(&r, bytes); }
static void g_sotp(void){ poly_sotp_encode(&r, msg, buf); }    static void o_sotp(void){ o_poly_sotp_encode(&r, msg, buf); }
static void g_bma(void){ poly_basemul_add(&r, &a, &b, &c); }   static void o_bma(void){ o_poly_basemul_add(&r, &a, &b, &c); }
static void cpy(void){ memcpy(&r, &a, sizeof r); }
static double best(void (*f)(void)){ double bst = 1e30; for (int w = 0; w < 2000; w++) f();
  for (int k = 0; k < 300; k++){ START(); for (int i = 0; i < 100; i++) f(); double d = STOP() / 100; if (d < bst) bst = d; } return bst; }
static uint32_t s = 11; static uint32_t rnd(void){ s ^= s << 13; s ^= s >> 17; s ^= s << 5; return s; }
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
#else
  if (perf_counter_open()) return 2;
#endif
  for (int i = 0; i < NTRUPLUS_N; i++){ a.coeffs[i] = rnd() % 3457; b.coeffs[i] = rnd() % 3457; c.coeffs[i] = (int16_t)(rnd() % 1729); }
  for (int i = 0; i < (int)sizeof buf; i++) buf[i] = rnd();
  for (int i = 0; i < (int)sizeof msg; i++) msg[i] = rnd();
  o_poly_tobytes(bytes, &a);
  for (;;) {                                   /* an f both sides can invert, each in its own layout */
    for (int i = 0; i < (int)sizeof buf; i++) buf[i] = rnd();
    poly t; poly_cbd1(&t, buf); poly_triple(&t, &t); t.coeffs[0] += 1; fo = t;
    poly_ntt(&fg, &t); o_poly_ntt(&fo);
    if (!poly_baseinv(&r, &fg) && !o_poly_baseinv(&r, &fo)) break; }
#ifdef __APPLE__
  { uint64_t t1 = now(); while (now() - t1 < 3000000000ull) { g_ntt(); o_ntt(); g_inv(); o_inv(); } }
#endif
  double cp = best(cpy);
  struct { const char *op, *n; double k; void (*g)(void); void (*o)(void); int ocopy; } rows[] = {
    {"keygen", "cbd1 (f,g)",     RETRY_F + RETRY_G, g_cbd, o_cbd, 0},
    {"keygen", "triple (f,g)",   RETRY_F + RETRY_G, g_tri, o_tri, 1},
    {"keygen", "forward NTT (f,g)", RETRY_F + RETRY_G, g_ntt, o_ntt, 1},
    {"keygen", "baseinv (f,g)",  RETRY_F + RETRY_G, g_inv, o_inv, 0},
    {"keygen", "basemul x2",     2, g_bm, o_bm, 0},
    {"keygen", "tobytes (f,pk,hinv)", 1, g_tob3, o_tob3, 0},
    {"encaps", "frombytes",      1, g_from, o_from, 0},
    {"encaps", "cbd1",           1, g_cbd, o_cbd, 0},
    {"encaps", "sotp_encode",    1, g_sotp, o_sotp, 0},
    {"encaps", "forward NTT x2", 2, g_ntt, o_ntt, 1},
    {"encaps", "basemul_add",    1, g_bma, o_bma, 0},
    {"encaps", "tobytes (ct)",   1, g_tobs, o_tob, 0} };
  double tg[2] = {0, 0}, to[2] = {0, 0};
  printf("NTRU+%d   (Official in place, as its kem.c calls it)\n", NTRUPLUS_N); (void)cp;
  for (unsigned i = 0; i < sizeof rows / sizeof rows[0]; i++){
    double x = best(rows[i].g), y = best(rows[i].o); int op = rows[i].op[0] == 'e';
    printf("%s  %-18s GT %8.1f  Off %8.1f  x%.2f -> %+8.1f %s\n", rows[i].op, rows[i].n, x, y, rows[i].k, rows[i].k * (x - y), UNIT);
    tg[op] += rows[i].k * x; to[op] += rows[i].k * y; }
  printf("keygen arithmetic  GT %.1f  Off %.1f  %+.1f %s\n", tg[0], to[0], tg[0] - to[0], UNIT);
  printf("encaps arithmetic  GT %.1f  Off %.1f  %+.1f %s\n", tg[1], to[1], tg[1] - to[1], UNIT);
  return 0; }
