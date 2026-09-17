#include "inverse.h"
#include "base_tables.h"
#include "inverse_tables.h"
#include "inverse16_tables.h"
void basemul_rinv_asm(int16_t *,const int16_t *,const int16_t *,const int16_t *);
int baseinv_asm(int16_t *,const int16_t *,const int16_t *);
int poly_baseinv(poly *out,const poly *in)
{
    return baseinv_asm(out->coeffs,in->coeffs,&basemul_zetas[0][0]);
}
void poly_basemul_rinv(int16_t *out,const int16_t *a,const int16_t *b)
{
    basemul_rinv_asm(out,a,b,&basemul_zetas[0][0]);
}
void invntt_ternary_asm(int16_t *,const int16_t *,const int16_t *,const int16_t *,const int16_t *,const int16_t *);
void poly_invntt_ternary(poly *out,const poly *in)
{
    invntt_ternary_asm(out->coeffs,in->coeffs,
        &invntt9_constants[0][0][0][0][0],
        &invntt16_constants[0][0],
        &invntt16_main_constants[0][0],
        &invntt16_tail_constants[0][0]);
}
