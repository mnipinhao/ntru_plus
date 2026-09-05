#ifndef GT864_P3B1_ROUTE9_H
#define GT864_P3B1_ROUTE9_H
#include <stdint.h>
#define P3B1_N 864
void p3b1_current_f2o(int16_t *out, const int16_t *in);
void p3b1_factor_f2o(int16_t *out, const int16_t *in);
void p3b1_r9a_f2o(int16_t *out, const int16_t *in);
void p3b1_r9b_f2o(int16_t *out, const int16_t *in);
void p3b1_current_o2f(int16_t *out, const int16_t *in);
void p3b1_factor_o2f(int16_t *out, const int16_t *in);
void p3b1_r9a_o2f(int16_t *out, const int16_t *in);
void p3b1_r9b_o2f(int16_t *out, const int16_t *in);
#endif
