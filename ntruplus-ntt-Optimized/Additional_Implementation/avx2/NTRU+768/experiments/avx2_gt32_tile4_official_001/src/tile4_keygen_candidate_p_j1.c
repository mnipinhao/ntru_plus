/* SUPERcop wrapper for the typed P-J1/finalizer-free Keypair edge. */
#define gt32_p_baseinv_direct_avx2 gt32_p_j1_baseinv_direct_avx2
#define gt_basemul_native_asm_avx2 gt_basemul_native_f0_j1_e0_asm_avx2
#define gt32_q24_encode_p_soa_halfscatter_lazy10788_asm \
	gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm
#include "tile4_keygen_candidate.inc"
