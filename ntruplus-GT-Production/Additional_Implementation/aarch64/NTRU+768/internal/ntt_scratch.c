/*
 * The forward-transform leaves take their 1536-byte working area as an
 * argument instead of allocating it, so that the transform of f, g, r and the
 * recovered message lies in a buffer the C caller can name and clear.  That is
 * how mlkem-native's kernels are arranged, and it is what lets the runtime
 * zeroization audit see this memory at all: the hook fires inside the C
 * primitive and cannot intercept stores emitted by handwritten assembly.
 *
 * The leaves still clear their own 160-byte frame, which holds the register
 * spills and SLOTHY's spill slot and is not the caller's to reach.
 */
#include "poly.h"
#include "keygen.h"
#include "ntt.h"
#include "decap_verify.h"
#include "secure_clear.h"

#define GT_NTT_SCRATCH_I16 768

void gt_internal_poly_ntt_loose_core(poly *, const poly *, int16_t *);
void gt_keygen_poly_ntt_to_cq_core(gt_cq_poly *, const poly *, int16_t *);
void gt_decap_poly_ntt_core(poly *, const poly *, int16_t *);

void gt_internal_poly_ntt_loose(poly *out, const poly *in)
{
    int16_t scratch[GT_NTT_SCRATCH_I16];
    gt_internal_poly_ntt_loose_core(out, in, scratch);
    gt_secure_clear(scratch, sizeof scratch);
}

void gt_keygen_poly_ntt_to_cq(gt_cq_poly *out_cq, const poly *in)
{
    int16_t scratch[GT_NTT_SCRATCH_I16];
    gt_keygen_poly_ntt_to_cq_core(out_cq, in, scratch);
    gt_secure_clear(scratch, sizeof scratch);
}

void gt_decap_poly_ntt(poly *out, const poly *in)
{
    int16_t scratch[GT_NTT_SCRATCH_I16];
    gt_decap_poly_ntt_core(out, in, scratch);
    gt_secure_clear(scratch, sizeof scratch);
}
