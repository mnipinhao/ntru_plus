#ifndef NTT_H
#define NTT_H

#include <stdint.h>
#include "params.h"

extern const int16_t gt_rowbitrev_lambda[2][96];

void ntt(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N]);
void invntt(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N]);
void ntt_gt_rowbitrevlayout(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N]);
void invntt_gt_rowbitrevlayout(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N]);
void invntt_gt_rowbitrevlayout_exact(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N]);

int  baseinv(int16_t r[4], const int16_t a[4], const int16_t zeta);
void basemul(int16_t r[4], const int16_t a[4], const int16_t b[4], const int16_t zeta);
void basemul_add(int16_t r[4], const int16_t a[4], const int16_t b[4], const int16_t c[4], const int16_t zeta);

#endif
