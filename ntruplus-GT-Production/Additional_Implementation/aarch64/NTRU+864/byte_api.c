#include "byte_boundary.h"
#include "input_once_frombytes.h"
#include "cluster_transpose_frombytes.h"
#include "poly.h"
#include "gt864_frombytes.h"
#include <arm_neon.h>
#include <stddef.h>

void p3b12_base_tobytes(uint8_t *out, const poly *in);
void p3b12_base_frombytes(poly *out, const uint8_t *in);
void p3b12_candidate_tobytes(uint8_t *out, const poly *in);
void p3b12_candidate_frombytes(poly *out, const uint8_t *in);

void p3b12_base_tobytes(uint8_t *out, const poly *in)
{
    r9_to(out, in->coeffs);
}

void p3b12_base_frombytes(poly *out, const uint8_t *in)
{
    gt864_fr0_input_once_frombytes(out->coeffs, in);
}

void p3b12_candidate_tobytes(uint8_t *out, const poly *in)
{
    r9_to(out, in->coeffs);
}

void p3b12_candidate_frombytes(poly *out, const uint8_t *in)
{
    gt864_fr0_cluster_transpose_frombytes(out->coeffs, in);
}

int gt864_fr0_frombytes_checked(poly *out,const uint8_t *in)
{
    gt864_fr0_cluster_transpose_frombytes(out->coeffs,in);
    /* All unpacked lanes are unsigned 12-bit values. The permutation does not
     * affect the predicate; scan every lane, with no data-dependent early exit. */
    uint16x8_t maximum=vdupq_n_u16(0);
    for (size_t i=0;i<NTRUPLUS_N;i+=8)
        maximum=vmaxq_u16(maximum,vreinterpretq_u16_s16(vld1q_s16(out->coeffs+i)));
    return vmaxvq_u16(maximum)>=NTRUPLUS_Q;
}
