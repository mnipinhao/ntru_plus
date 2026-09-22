/* Only the BaseMul symbol is replaced. All materialized boundaries remain. */
#define ntruplus768_basemul_general_m_avx2 ntruplus768_exp001_basemul_eager_m
#define ntruplus768_enc_derand_impl ntruplus768_exp001_enc_derand_eager
#include "../../../clean/avx2-gt32-clean/encap.c"
