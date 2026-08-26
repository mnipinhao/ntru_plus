#ifndef GT864_MONTGOMERY_H
#define GT864_MONTGOMERY_H

#include <stdint.h>

#include "gt864_reference.h"

/*
 * GT-domain layout used by every function below:
 *
 *   leaf_index = row * GT864_COLUMNS + column
 *   coefficient_index = leaf_index * GT864_LEAF_DEGREE + branch
 *
 * where row is in 0..8, column is in 0..31, and branch is the coefficient of
 * 1, X, or X^2 in Z_q[X]/(X^3-y_row_column).
 *
 * Coefficients are normal R^0 values.  Montgomery form is used only for
 * public multiplication constants inside the implementation.
 */

/* Natural coefficient order -> row-major GT cubic leaves. */
void gt864_mont_forward(int16_t out[GT864_N], const int16_t in[GT864_N]);

/* Row-major GT cubic leaves -> centered natural coefficient order. */
void gt864_mont_inverse(int16_t out[GT864_N], const int16_t in[GT864_N]);

/* Leafwise multiplication in Z_q[X]/(X^3-y_row_column). */
void gt864_mont_basemul(int16_t out[GT864_N], const int16_t a[GT864_N],
                        const int16_t b[GT864_N]);

/* Complete quotient-ring product using forward, basemul, and inverse. */
void gt864_mont_mul(int16_t out[GT864_N], const int16_t a[GT864_N],
                    const int16_t b[GT864_N]);

/* Raw int16 layout permutations; neither function reduces or rescales. */
void gt864_grid_to_legacy(int16_t out[GT864_N], const int16_t in[GT864_N]);
void gt864_legacy_to_grid(int16_t out[GT864_N], const int16_t in[GT864_N]);

#endif
