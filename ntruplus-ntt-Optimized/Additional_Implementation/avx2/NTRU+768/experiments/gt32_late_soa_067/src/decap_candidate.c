/* The only candidate differences are the two 066-qualified call targets. */
#define ntruplus768_dec_impl ntruplus768_dec_latesoa
#define ntruplus768_basemul_scale_m_avx2 late_soa_full_basemul_i2_fused_asm
#define ntruplus768_invntt_m_avx2 gt32_tile4_attr_inverse_i1_cross3_asm
#include "../../../decap.c"
