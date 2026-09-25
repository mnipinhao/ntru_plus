/* P139: fully cold KEM operations (P122's method), Cortex-A76.  Before every timed operation the
 * data caches are flushed by reading 32 MiB and the instruction side by executing 96 KiB of distinct
 * nops (icache_thrash.S); the RNG is reseeded so every run of every build sees the same key pair and
 * ciphertext (GT and Official produce identical outputs).  Prints medians of NTESTS per operation.
 * usage: cold TAG */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "api.h"
#include "perf_counter.h"
#ifndef NTESTS
#define NTESTS 61
#endif
void rb_seed(void);
void icache_thrash(void);
static uint8_t pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES], ct[CRYPTO_CIPHERTEXTBYTES], ss[CRYPTO_BYTES], ss2[CRYPTO_BYTES];
static uint8_t *big; static volatile uint64_t sink;
static void flush(void){ uint64_t a = 0; for (size_t i = 0; i < (32u << 20); i += 64) a += big[i]; sink += a; icache_thrash(); }
static int cmp(const void *x, const void *y){ uint64_t a = *(const uint64_t *)x, b = *(const uint64_t *)y; return (a > b) - (a < b); }
int main(int argc, char **argv){
  big = malloc(32u << 20); for (size_t i = 0; i < (32u << 20); i += 64) big[i] = (uint8_t)i;
  if (perf_counter_open()) return 2;
  rb_seed(); if (crypto_kem_keypair(pk, sk)) return 1;
  if (crypto_kem_enc(ct, ss, pk)) return 1;
  if (crypto_kem_dec(ss2, ct, sk) || memcmp(ss, ss2, sizeof ss)) { fprintf(stderr, "selftest failed\n"); return 1; }
  uint64_t t[3][NTESTS];
  for (int i = 0; i < NTESTS; i++) {
    flush(); rb_seed(); perf_counter_start(); crypto_kem_keypair(pk, sk); t[0][i] = perf_counter_stop();
    flush(); rb_seed(); perf_counter_start(); crypto_kem_enc(ct, ss, pk);  t[1][i] = perf_counter_stop();
    flush();            perf_counter_start(); crypto_kem_dec(ss2, ct, sk); t[2][i] = perf_counter_stop();
  }
  for (int k = 0; k < 3; k++) qsort(t[k], NTESTS, sizeof t[k][0], cmp);
  printf("%s cold keygen %llu encaps %llu decaps %llu cycles (medians of %d)\n", argc > 1 ? argv[1] : "?",
         (unsigned long long)t[0][NTESTS / 2], (unsigned long long)t[1][NTESTS / 2], (unsigned long long)t[2][NTESTS / 2], NTESTS);
  return 0; }
