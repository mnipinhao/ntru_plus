#include "gt864_tobytes.h"
#include "gt864_p18_tobytes.h"
int gt864_p47_decaps_compare_asm(const uint8_t*,const int16_t*);
void gt864_fr0_tobytes_full(uint8_t*out,const poly*in){
 gt864_p18_tobytes_full_asm(out,in->coeffs);
}
int gt864_fr0_tobytes_full_compare(const uint8_t*expected,const poly*in){
 return gt864_p47_decaps_compare_asm(expected,in->coeffs);
}
void gt864_fr0_tobytes_small(uint8_t*out,const poly*in){
 gt864_p18_tobytes_small_asm(out,in->coeffs);
}
