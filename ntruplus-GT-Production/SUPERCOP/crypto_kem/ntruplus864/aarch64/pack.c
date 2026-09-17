#include "pack.h"
#include "pack_asm.h"
int tobytes_compare_asm(const uint8_t*,const int16_t*);
void poly_tobytes(uint8_t*out,const poly*in){
 tobytes_full_asm(out,in->coeffs);
}
int poly_tobytes_compare(const uint8_t*expected,const poly*in){
 return tobytes_compare_asm(expected,in->coeffs);
}
void poly_tobytes_small(uint8_t*out,const poly*in){
 tobytes_small_asm(out,in->coeffs);
}
