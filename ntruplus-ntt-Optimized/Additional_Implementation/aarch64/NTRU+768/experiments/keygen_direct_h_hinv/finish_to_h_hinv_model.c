/*
 * Task B benchmark-only floor model.
 *
 * This keeps the no-ASM rule: it reuses the existing Task 6 v1 direct h/hinv
 * model as the measurable C-level floor for a future finish->h/hinv fused DAG.
 * A real candidate must do more than this wrapper: it must avoid materializing
 * finv/ginv and fuse denominator scaling with the two quartic products.
 */

#include "params.h"
#include "poly.h"

int poly_keygen_compute_h_hinv_direct_model(poly *h, poly *hinv,
                                            const poly *f, const poly *g);
int poly_keygen_finish_to_h_hinv_model(poly *h, poly *hinv, const poly *f,
                                       const poly *g);

int poly_keygen_finish_to_h_hinv_model(poly *h, poly *hinv, const poly *f,
                                       const poly *g)
{
	return poly_keygen_compute_h_hinv_direct_model(h, hinv, f, g);
}
