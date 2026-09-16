#include "gt864_native.h"
#include "gt864_fr0_basemul_tables.h"
#include "gt864_native_scaled_tables.h"
#include "gt864_p13b_composite_tables.h"
void gt864_basemul_rinv_asm(int16_t *,const int16_t *,const int16_t *,const int16_t *);
int gt864_baseinv_asm(int16_t *,const int16_t *,const int16_t *);
int gt864_native_poly_baseinv(poly *out,const poly *in)
{
    return gt864_baseinv_asm(out->coeffs,in->coeffs,&gt864_fr0_zetas_mul[0][0]);
}
void gt864_native_basemul_for_inverse(int16_t *out,const int16_t *a,const int16_t *b)
{
    gt864_basemul_rinv_asm(out,a,b,&gt864_fr0_zetas_mul[0][0]);
}
void gt864_inverse_ternary_asm(int16_t *,const int16_t *,const int16_t *,const int16_t *,const int16_t *,const int16_t *);
void gt864_native_inverse_ternary(poly *out,const poly *in)
{
    gt864_inverse_ternary_asm(out->coeffs,in->coeffs,
        &gt864_inverse9_twist_barrett[0][0][0][0][0],
        &gt864_inverse16_stage_barrett[0][0],
        &gt864_p13b_main[0][0],
        &gt864_p13b_tail[0][0]);
}
