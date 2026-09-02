#ifndef GT864_FRISO2_INVERSE_H
#define GT864_FRISO2_INVERSE_H

#include <stdint.h>

#include "../gt_fr0_inverse_consumer/gt864_fr0_inverse.h"

/*
 * Direct FR-ISO2 leaf consumer.
 *
 * Input and output use the same physical buffers as the FR-0 inverse.  The
 * basis correction is fused into the inverse-NTT9 arithmetic; there is no
 * 864-halfword FR-ISO2 -> FR-0 conversion pass.
 */
void gt864_friso2_inverse_ntt9_neon(
    int16_t out[GT864_INVERSE_P8_PADDED],
    const int16_t in[GT864_FR0_COEFFICIENTS]);

#endif
