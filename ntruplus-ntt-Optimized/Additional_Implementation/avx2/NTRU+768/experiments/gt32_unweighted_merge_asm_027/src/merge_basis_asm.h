#ifndef GT32_UNWEIGHTED_MERGE_ASM_027_H
#define GT32_UNWEIGHTED_MERGE_ASM_027_H

#include <stdint.h>

typedef void (*merge_inverse_rows_fn)(int16_t out[768], const int16_t in[768]);

/* Diagnostic symbols only.  The two candidate symbols intentionally encode
 * the rejected 026 propagation and must never be linked into production or
 * used for performance claims. */
void qbm_inverse_control_rows_asm(int16_t out[768], const int16_t in[768]);
void qbm_inverse_heterogeneous_rows_asm(int16_t out[768], const int16_t in[768]);
void qbm_inverse_repaired_rows_asm(int16_t out[768], const int16_t in[768]);

#endif
