#ifndef D4_AOS_AVX2_PROTO_H
#define D4_AOS_AVX2_PROTO_H

#include "d4_aos_ref.h"

/* Default-off AVX2 feasibility prototypes; no Official/SoA domain entry. */
void gt_d4aos_ntt_avx2_proto(d4aos_ntt_poly *out, const d4aos_coeff_poly *in);
void gt_d4aos_basemul_avx2_proto(d4aos_ntt_poly *out,
                                  const d4aos_ntt_poly *a,
                                  const d4aos_ntt_poly *b);
void gt_d4aos_invntt_avx2_proto(d4aos_coeff_poly *out,
                                 const d4aos_ntt_poly *in);

#endif
