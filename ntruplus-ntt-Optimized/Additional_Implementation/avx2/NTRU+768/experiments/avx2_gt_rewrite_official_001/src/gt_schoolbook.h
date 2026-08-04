#ifndef GT_SCHOOLBOOK_H
#define GT_SCHOOLBOOK_H

#include <stdint.h>

#define GT_N 768
#define GT_Q 3457

/* Exact int64 oracle for Z_q[x]/(x^768-x^384+1). */
void gt_schoolbook_mul(int16_t r[GT_N], const int16_t a[GT_N],
                       const int16_t b[GT_N]);

int16_t gt_centered_q(int64_t x);
int gt_equal_mod_q(const int16_t a[GT_N], const int16_t b[GT_N]);

#endif
