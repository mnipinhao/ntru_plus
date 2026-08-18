#ifndef NTRUPLUS768_OFFICIAL_INVNTT_CT_H
#define NTRUPLUS768_OFFICIAL_INVNTT_CT_H

#include <stdint.h>

/* Default-off experiment.  All objects contain 768 aligned int16_t words. */
void official_ntt_to_f32x3(int16_t out[768], const int16_t in[768]);
void official_invntt_ct_adapter_y2(int16_t out[768], const int16_t in[768]);

#endif
