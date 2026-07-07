/*
 * Task A benchmark-only model.
 *
 * This is a semantic pair wrapper for the two keygen public-arithmetic calls.
 * It intentionally does not claim the inner-loop sharing that a real pair ASM
 * kernel would need.  If this wrapper has no PMU movement, the next step would
 * require a real paired base_gt loop rather than more C wrapping.
 */

#include "params.h"
#include "poly.h"

void poly_basemul_scaled_r_input(poly *r, const poly *a,
                                 const poly *b_scaled_r);
void poly_keygen_public_arith_pair_model(poly *h, poly *hinv, const poly *f,
                                         const poly *g, const poly *finv,
                                         const poly *ginv);

void poly_keygen_public_arith_pair_model(poly *h, poly *hinv, const poly *f,
                                         const poly *g, const poly *finv,
                                         const poly *ginv)
{
	poly_basemul_scaled_r_input(h, g, finv);
	poly_basemul_scaled_r_input(hinv, f, ginv);
}
