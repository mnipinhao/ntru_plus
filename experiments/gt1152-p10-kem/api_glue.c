#include "poly.h"
#include "base.h"
#include "inverse.h"
#include "inverse_asm.h"
#include "pack_asm.h"
#include "pack.h"
#include "inverse_tables.h"
#include "invntt9_lane_tables.h"
#include "inverse16_tables.h"

/* Thin wrappers, mirroring NTRU+864's ntt_api.c / inverse_api.c / pack.c. */

void ntt_asm(int16_t out[NTRUPLUS_N], const int16_t in[NTRUPLUS_N]);
void invntt_ternary_asm(int16_t *, const int16_t *, const int16_t *,
                        const int16_t *, const int16_t *, const int16_t *);

void poly_ntt(poly *out, const poly *in) { ntt_asm(out->coeffs, in->coeffs); }

void poly_basemul(poly *out, const poly *a, const poly *b)
{ basemul_asm(out->coeffs, a->coeffs, b->coeffs); }

void poly_basemul_add(poly *out, const poly *a, const poly *b, const poly *c)
{ basemul_add_asm(out->coeffs, a->coeffs, b->coeffs, c->coeffs); }

int poly_baseinv(poly *out, const poly *in)
{ return baseinv_asm(out->coeffs, in->coeffs); }

void poly_basemul_rinv(int16_t *out, const int16_t *a, const int16_t *b)
{ basemul_rinv_asm(out, a, b); }

void poly_invntt_ternary(poly *out, const poly *in)
{
    invntt_ternary_asm(out->coeffs, in->coeffs,
                       &invntt9_constants_lane[0][0][0][0],
                       &invntt16_constants[0][0],
                       &invntt16_main_constants[0][0],
                       &invntt16_tail_constants[0][0]);
}

void poly_tobytes(uint8_t r[NTRUPLUS_POLYBYTES], const poly *a)
{ tobytes_full_asm(r, a->coeffs); }

void poly_tobytes_small(uint8_t r[NTRUPLUS_POLYBYTES], const poly *a)
{ tobytes_small_asm(r, a->coeffs); }

int poly_tobytes_compare(const uint8_t expected[NTRUPLUS_POLYBYTES], const poly *a)
{ return tobytes_compare_asm(expected, a->coeffs); }

int poly_frombytes(poly *r, const uint8_t a[NTRUPLUS_POLYBYTES])
{ return frombytes_asm(r->coeffs, a); }
