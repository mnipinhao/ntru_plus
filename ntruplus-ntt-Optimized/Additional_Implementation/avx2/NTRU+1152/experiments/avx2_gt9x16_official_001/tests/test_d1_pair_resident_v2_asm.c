#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "d1-pair-resident-v2.h"
#include "params.h"
#include "poly.h"
#include "symmetric.h"

#define N NTRUPLUS_N
#define BYTES NTRUPLUS_POLYBYTES
#define GUARD 32

void ntruplus1152_exp001_top_split_small(int16_t *, const int16_t *);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(int16_t *);
void ntruplus1152_exp001_scale1_r_serializer_v2(uint8_t *, const int16_t *);

static uint64_t rng_state = UINT64_C(0x5032524553494454);

static uint32_t rnd(void) {
  rng_state ^= rng_state << 13;
  rng_state ^= rng_state >> 7;
  rng_state ^= rng_state << 17;
  return (uint32_t)(rng_state >> 16);
}

static int guards_ok(const uint8_t *buffer, size_t payload) {
  for (size_t i = 0; i < GUARD; ++i)
    if (buffer[i] != 0xa5 || buffer[GUARD + payload + i] != 0x5a)
      return 0;
  return 1;
}

static int one(const int16_t coefficient[N], int trial) {
  _Alignas(32) int16_t control[N], before[N];
  _Alignas(32) uint8_t state_storage[GUARD + sizeof(int16_t) * N + GUARD];
  _Alignas(32) uint8_t byte_storage[GUARD + BYTES + GUARD];
  _Alignas(32) uint8_t expected[BYTES], official[BYTES];
  _Alignas(32) uint8_t control_hash[HASH_G_OUTBYTES];
  _Alignas(32) uint8_t candidate_hash[HASH_G_OUTBYTES];
  int16_t *candidate = (int16_t *)(void *)(state_storage + GUARD);
  uint8_t *actual = byte_storage + GUARD;
  poly official_poly;

  memcpy(before, coefficient, sizeof before);
  memset(state_storage, 0xa5, GUARD);
  memset(state_storage + GUARD + sizeof(int16_t) * N, 0x5a, GUARD);
  memset(byte_storage, 0xa5, GUARD);
  memset(byte_storage + GUARD + BYTES, 0x5a, GUARD);

  ntruplus1152_exp001_top_split_small(control, coefficient);
  memcpy(candidate, control, sizeof control);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(control);
  ntruplus1152_exp001_scale1_r_serializer_v2(expected, control);
  ntruplus1152_exp001_gt9x16_d1_pair_resident_v2_r(candidate, actual);

  memcpy(official_poly.coeffs, coefficient, sizeof official_poly.coeffs);
  poly_ntt(&official_poly);
  poly_tobytes(official, &official_poly);
  hash_g(control_hash, expected);
  hash_g(candidate_hash, actual);

  if (memcmp(control, candidate, sizeof control)) {
    int cell = 0;
    while (cell < N && control[cell] == candidate[cell]) ++cell;
    fprintf(stderr, "pair-resident raw state mismatch trial=%d cell=%d control=%d candidate=%d\n",
            trial, cell, cell < N ? control[cell] : 0,
            cell < N ? candidate[cell] : 0);
    for (int tile = 0; tile < 18; ++tile) {
      int differences = 0;
      for (int j = 0; j < 64; ++j)
        differences += control[64 * tile + j] != candidate[64 * tile + j];
      if (differences) fprintf(stderr, " tile %d differences=%d\n", tile, differences);
    }
    return 1;
  }
  if (memcmp(expected, actual, BYTES) || memcmp(actual, official, BYTES)) {
    int byte = 0;
    while (byte < BYTES && expected[byte] == actual[byte]) ++byte;
    fprintf(stderr, "pair-resident byte mismatch trial=%d byte=%d\n", trial, byte);
    for (int i = 0; i < 16; ++i)
      fprintf(stderr, " %02x/%02x", expected[i], actual[i]);
    fputc('\n', stderr);
    return 1;
  }
  if (memcmp(control_hash, candidate_hash, sizeof control_hash)) {
    fprintf(stderr, "pair-resident hash_g mismatch trial=%d\n", trial);
    return 1;
  }
  if (memcmp(before, coefficient, sizeof before)) {
    fprintf(stderr, "pair-resident coefficient mutation trial=%d\n", trial);
    return 1;
  }
  if (!guards_ok(state_storage, sizeof(int16_t) * N) ||
      !guards_ok(byte_storage, BYTES)) {
    fprintf(stderr, "pair-resident canary failure trial=%d\n", trial);
    return 1;
  }
  return 0;
}

int main(void) {
  _Alignas(32) int16_t coefficient[N];
  for (int trial = 0; trial < 1007; ++trial) {
    for (int i = 0; i < N; ++i) {
      if (trial == 0) coefficient[i] = 0;
      else if (trial == 1) coefficient[i] = 1;
      else if (trial == 2) coefficient[i] = -1;
      else if (trial == 3) coefficient[i] = (int16_t)((i & 1) ? 1 : -1);
      else if (trial == 4) coefficient[i] = (int16_t)(i == 0);
      else if (trial == 5) coefficient[i] = (int16_t)-(i == N - 1);
      else coefficient[i] = (int16_t)((int)(rnd() % 3) - 1);
    }
    if (one(coefficient, trial)) return 1;
  }
  puts("D1 pair-resident Serializer V2 ASM: ok");
  return 0;
}
