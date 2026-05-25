#include "ntt.h"
#include "poly.h"

/*
 * Test-only shim used to validate gt_test/test_polyntt_asm.c without an ASM
 * kernel.  The real ASM target links asm/my_ntt.s instead of this file.
 */
void poly_ntt(poly *r, const poly *a)
{
	ntt_gt_rowbitrevlayout(r->coeffs, a->coeffs);
}
