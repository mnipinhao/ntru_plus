#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { N = 864 };
typedef struct { int16_t c[N]; } poly;
typedef void (*invfn)(poly *, const poly *);

static uint64_t state = 864;
void randombytes(uint8_t *out, size_t n) {
  while (n--) {
    state ^= state << 13; state ^= state >> 7; state ^= state << 17;
    *out++ = (uint8_t)state;
  }
}
static uint16_t next16(void) {
  state ^= state << 13; state ^= state >> 7; state ^= state << 17;
  return (uint16_t)state;
}
static invfn load(const char *path) {
  void *h = dlopen(path, RTLD_NOW | RTLD_LOCAL);
  if (!h) { fprintf(stderr, "%s\n", dlerror()); exit(2); }
  invfn fn = (invfn)dlsym(h, "gt864_native_inverse_ternary");
  if (!fn) { fprintf(stderr, "%s\n", dlerror()); exit(2); }
  return fn;
}
int main(int argc, char **argv) {
  if (argc != 3) return 2;
  invfn baseline = load(argv[1]), candidate = load(argv[2]);
  poly in, a, b;
  for (unsigned trial = 0; trial < 256; trial++) {
    state = 0x864000 + trial;
    for (unsigned i = 0; i < N; i++) in.c[i] = (int16_t)((int)(next16() % 4995) - 2497);
    memset(&a, 0x55, sizeof a); memset(&b, 0xaa, sizeof b);
    baseline(&a, &in); candidate(&b, &in);
    unsigned mismatches = 0;
    for (unsigned i = 0; i < N; i++) if (a.c[i] != b.c[i]) {
      fprintf(stderr, "trial=%u first=%u top=%u t=%u row=%u component=%u got=%d want=%d\n",
              trial, i, i / 864, (i % 864) / 54, ((i % 54) / 6), i % 3,
              b.c[i], a.c[i]);
      if (++mismatches == 64) return 1;
    }
    if (mismatches) return 1;
  }
  puts("inverse exact 256/256");
  return 0;
}
