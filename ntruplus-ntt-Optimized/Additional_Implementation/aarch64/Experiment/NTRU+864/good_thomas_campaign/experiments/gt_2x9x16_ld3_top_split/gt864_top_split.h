#ifndef GT864_TOP_SPLIT_H
#define GT864_TOP_SPLIT_H

#include <stdint.h>

#define GT864_TOP_SPLIT_INPUT_COEFFICIENTS 864
#define GT864_TOP_SPLIT_OUTPUT_COEFFICIENTS 896
#define GT864_TOP_SPLIT_MAIN_COEFFICIENTS 768

/*
 * Split a[3*m+b], m=0..287, into the two roots of z^2-z+1.
 *
 * Main bank, s=0..7:
 *   out[(((top * 3 + branch) * 16 + t) * 8) + s]
 *
 * Tail bank, s=8:
 *   out[768 + t * 8 + top * 3 + branch]
 *
 * Tail lanes 6 and 7 are zero padding.  The 896-coefficient output is an
 * experimental SIMD layout, not the public NTRU+ NTT representation.
 * Input and output must not overlap.
 */
void gt864_top_split_ld3(int16_t out[GT864_TOP_SPLIT_OUTPUT_COEFFICIENTS],
                         const int16_t in[GT864_TOP_SPLIT_INPUT_COEFFICIENTS]);

#endif
