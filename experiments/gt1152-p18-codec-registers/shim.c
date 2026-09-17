/* Maps the harness's poly_* names onto the codec's *_asm entry points. */
#include "pack.h"
#include "pack_asm.h"
void poly_tobytes(uint8_t o[1728], const int16_t i[1152]) { tobytes_full_asm(o, i); }
void poly_tobytes_small(uint8_t o[1728], const int16_t i[1152]) { tobytes_small_asm(o, i); }
int poly_tobytes_compare(const uint8_t e[1728], const int16_t i[1152]) { return tobytes_compare_asm(e, i); }
int poly_frombytes(int16_t o[1152], const uint8_t i[1728]) { return frombytes_asm(o, i); }
