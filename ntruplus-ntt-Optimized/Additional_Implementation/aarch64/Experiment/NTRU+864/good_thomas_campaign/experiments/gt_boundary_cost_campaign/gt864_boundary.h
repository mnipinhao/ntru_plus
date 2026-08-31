#ifndef GT864_BOUNDARY_H
#define GT864_BOUNDARY_H

#include <stdint.h>

#define GT864_BOUNDARY_INPUT_COEFFICIENTS 896
#define GT864_BOUNDARY_OUTPUT_COEFFICIENTS 864
#define GT864_BOUNDARY_MAIN_COEFFICIENTS 768
#define GT864_BOUNDARY_FR_SCRATCH_COEFFICIENTS 864
#define GT864_BOUNDARY_FC_TAIL_COEFFICIENTS 96

/*
 * Common input boundary: the exact P8+tail layout emitted by
 * gt864_top_split_ld3.
 *
 *   main(h,j,c,s<8) = in[(((h*3+j)*16+c)*8)+s]
 *   tail(h,j,c,s=8) = in[768+c*8+h*3+j]
 *
 * h=0 is the alpha top root, h=1 is beta; j is the degree-three
 * coefficient plane; c is the NTT16 output column; s is the NTT9 input row.
 */

/* M4.1 diagnostic: materialize [h][j][block][s][lane=column]. */
void gt864_fr_bridge(int16_t out[GT864_BOUNDARY_FR_SCRATCH_COEFFICIENTS],
                     const int16_t in[GT864_BOUNDARY_INPUT_COEFFICIENTS]);

/* M4.1 diagnostic: only extract the six s=8 streams; no FC main bridge. */
void gt864_fc_tail_extract(
    int16_t out[GT864_BOUNDARY_FC_TAIL_COEFFICIENTS],
    const int16_t in[GT864_BOUNDARY_INPUT_COEFFICIENTS]);

/*
 * M4.2 full equal-boundary candidates.  Both consume P8+tail and produce
 * BaseMul-ready 36-tile SoA buffers.  The byte layouts differ and are decoded
 * by the helpers below; both represent the same logical leaves (h,r,c,j).
 */
void gt864_boundary_fr0(int16_t out[GT864_BOUNDARY_OUTPUT_COEFFICIENTS],
                        const int16_t in[GT864_BOUNDARY_INPUT_COEFFICIENTS]);
void gt864_boundary_fc0(int16_t out[GT864_BOUNDARY_OUTPUT_COEFFICIENTS],
                        const int16_t in[GT864_BOUNDARY_INPUT_COEFFICIENTS]);
void gt864_boundary_fr_lane0(
    int16_t out[GT864_BOUNDARY_OUTPUT_COEFFICIENTS],
    const int16_t in[GT864_BOUNDARY_INPUT_COEFFICIENTS]);

/* Scalar direct-evaluation oracle, stored in the FR-0 tile ABI. */
void gt864_boundary_reference_fr0(
    int16_t out[GT864_BOUNDARY_OUTPUT_COEFFICIENTS],
    const int16_t in[GT864_BOUNDARY_INPUT_COEFFICIENTS]);

int16_t gt864_boundary_fr_get(
    const int16_t in[GT864_BOUNDARY_OUTPUT_COEFFICIENTS],
    int top, int row, int column, int component);
int16_t gt864_boundary_fc_get(
    const int16_t in[GT864_BOUNDARY_OUTPUT_COEFFICIENTS],
    int top, int row, int column, int component);
int16_t gt864_boundary_fr_lane0_get(
    const int16_t in[GT864_BOUNDARY_OUTPUT_COEFFICIENTS],
    int top, int logical_row, int column, int component);

#endif
