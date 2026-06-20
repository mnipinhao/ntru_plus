#ifndef GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_H
#define GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_H

#include <stdint.h>

#include "params.h"

#define GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK 0
#define GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT 1
#define GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_DISABLED 2

const char *gt_tmvp_quartic_tmvp_experimental_status_name(int status);

int gt_tmvp_quartic_tmvp_rowpack_index(int branch, int row, int lane,
                                       int k32);
int gt_tmvp_quartic_tmvp_physical_j(int row, int k32);

int gt_tmvp_quartic_tmvp_experimental_c(int16_t r[NTRUPLUS_N],
                                        const int16_t a[NTRUPLUS_N],
                                        const int16_t b[NTRUPLUS_N]);

int gt_tmvp_quartic_tmvp_add_experimental_c(int16_t r[NTRUPLUS_N],
                                            const int16_t a[NTRUPLUS_N],
                                            const int16_t b[NTRUPLUS_N],
                                            const int16_t c[NTRUPLUS_N]);

int gt_tmvp_quartic_tmvp_incomplete_materialized_stage5_adapter_c(
	int16_t r[NTRUPLUS_N],
	const int16_t a_stage4[NTRUPLUS_N],
	const int16_t b_stage4[NTRUPLUS_N]);

int gt_tmvp_quartic_tmvp_add_incomplete_materialized_stage5_adapter_c(
	int16_t r[NTRUPLUS_N],
	const int16_t a_stage4[NTRUPLUS_N],
	const int16_t b_stage4[NTRUPLUS_N],
	const int16_t c_stage4[NTRUPLUS_N]);

int gt_tmvp_quartic_tmvp_experimental_asm(int16_t r[NTRUPLUS_N],
                                          const int16_t a[NTRUPLUS_N],
                                          const int16_t b[NTRUPLUS_N]);

int gt_tmvp_quartic_tmvp_add_experimental_asm(int16_t r[NTRUPLUS_N],
                                              const int16_t a[NTRUPLUS_N],
                                              const int16_t b[NTRUPLUS_N],
                                              const int16_t c[NTRUPLUS_N]);

int gt_tmvp_quartic_tmvp_experimental_asm_fast(int16_t r[NTRUPLUS_N],
                                               const int16_t a[NTRUPLUS_N],
                                               const int16_t b[NTRUPLUS_N]);

int gt_tmvp_quartic_tmvp_add_experimental_asm_fast(int16_t r[NTRUPLUS_N],
                                                   const int16_t a[NTRUPLUS_N],
                                                   const int16_t b[NTRUPLUS_N],
                                                   const int16_t c[NTRUPLUS_N]);

#endif
