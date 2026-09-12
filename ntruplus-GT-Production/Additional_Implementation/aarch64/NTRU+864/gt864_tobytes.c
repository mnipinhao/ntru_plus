#include "gt864_tobytes.h"
#include "gt864_p18_tobytes.h"
#include "p3b1_tables.h"
#include "byte_merge_tables.h"
void gt864_tobytes_full_asm(uint8_t*,const int16_t*,const void*,const void*,const void*);
void gt864_tobytes_small_asm(uint8_t*,const int16_t*,const void*,const void*,const void*);
void gt864_fr0_tobytes_full(uint8_t*out,const poly*in){
 gt864_p18_tobytes_full_asm(out,in->coeffs);
}
void gt864_fr0_tobytes_small(uint8_t*out,const poly*in){
 gt864_p18_tobytes_small_asm(out,in->coeffs);
}
