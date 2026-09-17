#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define N 1152
#define BYTES 1728
#define GUARD 32

void ntruplus1152_exp001_top_split_small(int16_t *, const int16_t *);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(int16_t *);
void ntruplus1152_exp001_direct_serializer_wire(uint8_t *, const int16_t *);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_scale1_dual_r(int16_t *, uint8_t *);

static uint64_t rng = UINT64_C(0x4455414c5241534d);
static uint32_t rnd(void) {
  rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17;
  return (uint32_t)(rng >> 16);
}

static int guards_ok(const uint8_t *buffer, size_t payload) {
  for (size_t i = 0; i < GUARD; ++i)
    if (buffer[i] != 0xa5 || buffer[GUARD + payload + i] != 0x5a) return 0;
  return 1;
}

int main(void) {
  _Alignas(32) int16_t coefficient[N], before[N], control[N];
  _Alignas(32) uint8_t state_storage[GUARD + sizeof(int16_t) * N + GUARD];
  _Alignas(32) uint8_t byte_storage[GUARD + BYTES + GUARD];
  _Alignas(32) uint8_t expected[BYTES];
  int16_t *candidate = (int16_t *)(void *)(state_storage + GUARD);
  uint8_t *actual = byte_storage + GUARD;

  for (int trial = 0; trial < 1003; ++trial) {
    for (int i = 0; i < N; ++i) {
      if (trial == 0) coefficient[i] = 0;
      else if (trial == 1) coefficient[i] = (int16_t)((i & 1) ? 1 : -1);
      else coefficient[i] = (int16_t)((int)(rnd() % 3) - 1);
    }
    memcpy(before, coefficient, sizeof before);
    memset(state_storage, 0xa5, GUARD);
    memset(state_storage + GUARD + sizeof(int16_t) * N, 0x5a, GUARD);
    memset(byte_storage, 0xa5, GUARD);
    memset(byte_storage + GUARD + BYTES, 0x5a, GUARD);

    ntruplus1152_exp001_top_split_small(control, coefficient);
    memcpy(candidate, control, sizeof control);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(control);
    ntruplus1152_exp001_direct_serializer_wire(expected, control);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_scale1_dual_r(candidate, actual);

    if (memcmp(control, candidate, sizeof control)) {
      fprintf(stderr, "dual-r state mismatch at trial %d\n", trial); return 1;
    }
    if (memcmp(expected, actual, BYTES)) {
      fprintf(stderr, "dual-r bytes mismatch at trial %d\n", trial); return 1;
    }
    if (memcmp(before, coefficient, sizeof before)) {
      fprintf(stderr, "dual-r input mutation at trial %d\n", trial); return 1;
    }
    if (!guards_ok(state_storage, sizeof(int16_t) * N) ||
        !guards_ok(byte_storage, BYTES)) {
      fprintf(stderr, "dual-r canary failure at trial %d\n", trial); return 1;
    }
  }
  puts("scale-1 r dual-output ASM: ok");
  return 0;
}
