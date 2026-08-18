#include "official_invntt_ct.h"
#include "../avx2_gt_d4_aos_official_api/d4_aos_f32x3_ref.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

static uint32_t rng = 0x1546U;
static uint32_t next_u32(void) { rng = 1664525U * rng + 1013904223U; return rng; }
static int congruent(int a, int b) { int d = (a-b) % 3457; return d == 0; }

int main(void)
{
	d4aos_coeff_poly coeff;
	d4aos_ntt_poly d4;
	poly official;
	int16_t mapped[768] __attribute__((aligned(32)));
	poly a, b, product, expected;
	poly alias;
	int16_t got[768] __attribute__((aligned(32)));

	memset(&product, 0, sizeof(product));
	expected = product;
	poly_invntt_scale(&expected);
	official_invntt_ct_adapter_y2(got, product.coeffs);
	for (unsigned i = 0; i < 768; ++i) if (!congruent(got[i], expected.coeffs[i])) {
		fprintf(stderr, "zero inverse mismatch i=%u got=%d want=%d\n",
			i, got[i], expected.coeffs[i]); return 1;
	}

	for (unsigned round = 0; round < 64; ++round) {
		for (unsigned i = 0; i < 768; ++i) {
			coeff.coeff[i] = (int16_t)((int)(next_u32()%8U)-3);
			official.coeffs[i] = coeff.coeff[i];
		}
		d4aos_f32x3_ref_forward(&d4, &coeff);
		poly_ntt(&official);
		official_ntt_to_f32x3(mapped, official.coeffs);
		for (unsigned i = 0; i < 768; ++i) if (!congruent(mapped[i], d4.lane[i])) {
			fprintf(stderr, "forward map mismatch round=%u i=%u got=%d want=%d\n",
				round, i, mapped[i], d4.lane[i]); return 1;
		}
	}

	for (unsigned round = 0; round < 1000; ++round) {
		for (unsigned i = 0; i < 768; ++i) {
			a.coeffs[i] = (int16_t)((int)(next_u32()%3U)-1);
			b.coeffs[i] = (int16_t)((int)(next_u32()%3U)-1);
		}
		poly_ntt(&a); poly_ntt(&b);
		poly_basemul_scale(&product, &a, &b);
		expected = product; poly_invntt_scale(&expected);
		official_invntt_ct_adapter_y2(got, product.coeffs);
		if (round < 16) {
			alias = product;
			official_invntt_ct_adapter_y2(alias.coeffs, alias.coeffs);
		}
		for (unsigned i = 0; i < 768; ++i) if (!congruent(got[i], expected.coeffs[i])) {
			fprintf(stderr, "inverse mismatch round=%u i=%u got=%d want=%d\n",
				round, i, got[i], expected.coeffs[i]); return 1;
		}
		for (unsigned i = 0; round < 16 && i < 768; ++i)
			if (!congruent(alias.coeffs[i], expected.coeffs[i])) {
				fprintf(stderr, "alias mismatch round=%u i=%u got=%d want=%d\n",
					round, i, alias.coeffs[i], expected.coeffs[i]); return 1;
			}
	}
	puts("official-invntt-ct=passed zero=1 forward-map=64 products=1000 alias=16");
	return 0;
}
