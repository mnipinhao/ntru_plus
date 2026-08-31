#ifndef GT864_NTT16_H
#define GT864_NTT16_H

#include <stdint.h>

#define GT864_NTT16_PADDED_COEFFICIENTS 896
#define GT864_NTT16_MAIN_COEFFICIENTS 768

/*
 * In-place length-16 producer on the P8+tail output of gt864_top_split_ld3.
 * The physical layout is unchanged; t on input becomes natural column c on
 * output. Coefficients remain signed int16 normal-R0 representatives.
 */
void gt864_ntt16_p8_neon(
    int16_t io[GT864_NTT16_PADDED_COEFFICIENTS]);

#endif
