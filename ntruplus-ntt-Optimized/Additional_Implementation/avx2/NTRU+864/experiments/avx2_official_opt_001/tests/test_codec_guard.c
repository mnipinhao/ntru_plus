/* Guard-page bounds check for the NTRU+864 codecs.
 *
 * The canary tests in test_codec_fused.c / test_codec_direct.c detect
 * out-of-bounds writes but not out-of-bounds reads (a stray read lands in the
 * canary and does not fault).  Here each operand is placed flush against a
 * PROT_NONE page, once directly before it and once directly after it, so any
 * read or write outside the operand faults:
 *   - the 1296-byte wire array for tobytes (write) and frombytes (read);
 *   - the 1728-byte poly for tobytes (read) and frombytes (write).
 * Codecs checked: Official poly_tobytes/poly_frombytes (control), exp001
 * (layout-fused) and exp002 (direct 12-bit).  Each round trip must also agree
 * with Official byte for byte, and frombytes must return the same fail flag.
 */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#include "params.h"
#include "poly.h"

void ntruplus864_officialopt_tobytes_fused(uint8_t r[NTRUPLUS_POLYBYTES], const poly *a);
int ntruplus864_officialopt_frombytes_fused(poly *r, const uint8_t a[NTRUPLUS_POLYBYTES]);
void ntruplus864_officialopt_tobytes_direct(uint8_t r[NTRUPLUS_POLYBYTES], const poly *a);
int ntruplus864_officialopt_frombytes_direct(poly *r, const uint8_t a[NTRUPLUS_POLYBYTES]);

enum { NB = NTRUPLUS_POLYBYTES, PB = (int)sizeof(poly), ROUNDS = 1000 };

typedef struct {
  const char *name;
  void (*tobytes)(uint8_t *, const poly *);
  int (*frombytes)(poly *, const uint8_t *);
} codec;

static void official_tobytes(uint8_t *r, const poly *a) { poly_tobytes(r, a); }
static int official_frombytes(poly *r, const uint8_t *a) { return poly_frombytes(r, a); }

static const codec CODECS[] = {
  {"official", official_tobytes, official_frombytes},
  {"exp001-fused", ntruplus864_officialopt_tobytes_fused, ntruplus864_officialopt_frombytes_fused},
  {"exp002-direct", ntruplus864_officialopt_tobytes_direct, ntruplus864_officialopt_frombytes_direct},
};

typedef struct {
  uint8_t *map;
  size_t len;
  uint8_t *p;
} guarded;

/* Map `size` bytes flush against a PROT_NONE page: after the leading guard
 * (before=1) or before the trailing guard (before=0).  Both placements keep
 * 32-byte alignment because the page size and both operand sizes are
 * multiples of 32 (1728 = 54*32; the wire array needs no alignment). */
static guarded guard_alloc(size_t size, int before) {
  size_t pg = (size_t)sysconf(_SC_PAGESIZE);
  size_t data = (size + pg - 1) / pg * pg;
  guarded g;
  g.len = data + 2 * pg;
  g.map = mmap(NULL, g.len, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
  if (g.map == MAP_FAILED) { perror("mmap"); exit(2); }
  if (mprotect(g.map, pg, PROT_NONE) || mprotect(g.map + pg + data, pg, PROT_NONE)) {
    perror("mprotect");
    exit(2);
  }
  g.p = before ? g.map + pg : g.map + pg + data - size;
  return g;
}

static uint64_t rng = 0x9e3779b97f4a7c15u;
static uint32_t next(void) {
  rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17;
  return (uint32_t)(rng >> 16);
}

static void fill_poly(poly *a, int kind) {
  for (int i = 0; i < NTRUPLUS_N; i++) {
    switch (kind) {
      case 0: a->coeffs[i] = (int16_t)next(); break;         /* arbitrary int16 */
      case 1: a->coeffs[i] = 0; break;
      case 2: a->coeffs[i] = NTRUPLUS_Q - 1; break;
      case 3: a->coeffs[i] = (int16_t)(i & 1 ? INT16_MAX : INT16_MIN); break;
      default: a->coeffs[i] = (int16_t)(next() % NTRUPLUS_Q); break;
    }
  }
}

static void fill_bytes(uint8_t *b, int kind) {
  for (int i = 0; i < NB; i++) {
    switch (kind) {
      case 0: b[i] = (uint8_t)next(); break;                 /* arbitrary, often invalid */
      case 1: b[i] = 0; break;
      case 2: b[i] = 0xff; break;                            /* every coefficient 4095 */
      default: b[i] = (uint8_t)next(); break;
    }
  }
}

int main(void) {
  poly ref_p, cand_p;
  uint8_t ref_b[NB];
  long checks = 0;

  for (size_t c = 0; c < sizeof CODECS / sizeof CODECS[0]; c++) {
    for (int before = 0; before < 2; before++) {
      guarded wire = guard_alloc(NB, before);
      guarded pl = guard_alloc(PB, before);
      poly *gp = (poly *)pl.p;

      for (int r = 0; r < ROUNDS; r++) {
        int kind = r < 5 ? r : 0;
        /* tobytes: guarded poly in, guarded wire out */
        fill_poly(gp, kind);
        poly_tobytes(ref_b, gp);
        CODECS[c].tobytes(wire.p, gp);
        if (memcmp(ref_b, wire.p, NB)) {
          printf("FAIL %s tobytes mismatch (round %d, %s)\n", CODECS[c].name, r, before ? "leading" : "trailing");
          return 1;
        }
        /* frombytes of that valid encoding: guarded wire in, guarded poly out */
        int ref_fail = poly_frombytes(&ref_p, wire.p);
        int cand_fail = CODECS[c].frombytes(gp, wire.p);
        if (ref_fail != cand_fail || memcmp(&ref_p, gp, PB)) {
          printf("FAIL %s frombytes(valid) mismatch (round %d)\n", CODECS[c].name, r);
          return 1;
        }
        /* frombytes of arbitrary bytes (usually rejected) */
        fill_bytes(wire.p, r < 4 ? r : 0);
        ref_fail = poly_frombytes(&ref_p, wire.p);
        cand_fail = CODECS[c].frombytes(gp, wire.p);
        memcpy(&cand_p, gp, PB);
        if (ref_fail != cand_fail || memcmp(&ref_p, &cand_p, PB)) {
          printf("FAIL %s frombytes(arbitrary) mismatch (round %d)\n", CODECS[c].name, r);
          return 1;
        }
        checks += 3;
      }
      munmap(wire.map, wire.len);
      munmap(pl.map, pl.len);
      printf("%-14s %s guard: %d rounds, no fault, Official-equal\n", CODECS[c].name,
             before ? "leading " : "trailing", ROUNDS);
    }
  }
  printf("codec guard-page bounds PASS (%ld checks)\n", checks);
  return 0;
}
