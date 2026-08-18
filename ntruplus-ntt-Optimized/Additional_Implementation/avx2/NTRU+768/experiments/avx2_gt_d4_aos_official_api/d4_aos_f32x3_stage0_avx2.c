#include "d4_aos_f32x3_ref.h"
#include <immintrin.h>
static __m256i canon(__m256i x){const __m256i q=_mm256_set1_epi16(3457),z=_mm256_setzero_si256();x=_mm256_add_epi16(x,_mm256_and_si256(_mm256_cmpgt_epi16(z,x),q));return _mm256_sub_epi16(x,_mm256_and_si256(_mm256_cmpgt_epi16(x,_mm256_set1_epi16(3456)),q));}
void gt_d4aos_f32x3_invntt32_stage0_avx2(d4aos_f32x3_state *out,const d4aos_f32x3_state *in){for(int n=0;n<48;n++){__m256i x=_mm256_load_si256((const __m256i*)&in->lane[16*n]),y=_mm256_permute4x64_epi64(x,0xb1),s=canon(_mm256_add_epi16(x,y)),d=_mm256_permute4x64_epi64(canon(_mm256_sub_epi16(x,y)),0xb1);_mm256_store_si256((__m256i*)&out->lane[16*n],_mm256_blend_epi32(s,d,0xcc));}}
