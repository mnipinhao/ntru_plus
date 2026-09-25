/* Deterministic randombytes for the cross-build output check (SHAKE-free LCG stream). */
#include <stddef.h>
#include <stdint.h>
static uint64_t st = 0x0123456789abcdefULL;
void rb_seed_det(uint64_t s) { st = s; }
void randombytes(uint8_t *out, size_t n) { for (size_t i = 0; i < n; i++) { st = st * 6364136223846793005ULL + 1442695040888963407ULL; out[i] = (uint8_t)(st >> 56); } }
