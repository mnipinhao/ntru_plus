#include "integration/api.h"
#include "poly.h"
#include "gt864_fr0_basemul_tables.h"
#include "scaled_tables.h"
int bench_baseinv(poly*out,const poly*in){return gt864_baseinv_asm(out->coeffs,in->coeffs,&gt864_fr0_zetas_mul[0][0]);}
void fr0_basemul_for_inverse(int16_t*out,const int16_t*a,const int16_t*b){gt864_basemul_rinv_asm(out,a,b,&gt864_fr0_zetas_mul[0][0]);}
void fr0_inverse_scaled(poly*out,const poly*in){gt864_inverse_rinv_asm(out->coeffs,in->coeffs,
 &gt864_inverse9_twist_barrett[0][0][0][0][0],&gt864_inverse16_stage_barrett[0][0],
 &gt864_inverse16_main_scale_barrett[0][0][0],&gt864_inverse16_tail_scale_barrett[0][0][0]);}
