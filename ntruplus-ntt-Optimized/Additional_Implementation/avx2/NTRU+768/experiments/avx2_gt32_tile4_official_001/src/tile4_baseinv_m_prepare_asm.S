/* M-lane symbol instantiation of the reusable BaseInv prepare schedule. */
#define gt_native_lambda gt_m_baseinv_lambda
#define gt_native_lambda_qinv gt_m_baseinv_lambda_qinv
#define gt_baseinv_native_prepare_centered_asm gt32_m_baseinv_prepare_centered_asm
#define gt_baseinv_native_prepare_center_on_load_asm gt32_m_baseinv_prepare_center_on_load_asm
#include "../../gt_ntt/gt_baseinv_native_prepare_asm.S"
