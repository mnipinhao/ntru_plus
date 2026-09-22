/* Reuse the deterministic invalid-PK/CT test, not its fused implementation. */
#define ntruplus768_exp001_enc_derand_live_b3_pack ntruplus768_exp001_enc_derand_eager
#define CANDIDATE_LABEL "independent eager BaseMul"
#include "test_encap_live_b3_pack_kem.c"
