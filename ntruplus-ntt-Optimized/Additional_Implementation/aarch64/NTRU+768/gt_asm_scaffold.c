#include "poly.h"
#include "ntt.h"
#include "gt_asm.h"

void poly_ntt_gt_ref(poly *r, const poly *a)
{
	ntt_gt_rowbitrevlayout(r->coeffs, a->coeffs);
}

/*
 * Forward GT ASM scaffold.
 *
 * This intentionally calls the C reference for now.  The symbol gives the
 * assembly work a stable ABI target: replace this function with an AArch64
 * implementation once the first kernel is ready, while keeping the same tests.
 */
void poly_ntt_gt_asm(poly *r, const poly *a)
{
	poly_ntt_gt_ref(r, a);
}
