#include "byte_boundary.h"
#include "input_once_frombytes.h"
#include "cluster_transpose_frombytes.h"
#include "poly.h"

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
