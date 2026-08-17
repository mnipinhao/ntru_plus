#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define N 768
#define Q 3457
#define R 3310

int gt32_p_baseinv_direct_avx2(int16_t *, const int16_t *);
int gt32_p_j1_baseinv_direct_avx2(int16_t *, const int16_t *);
void gt_basemul_native_asm_avx2(int16_t *, const int16_t *, const int16_t *);
void gt_basemul_native_f0_j1_e0_asm_avx2(int16_t *, const int16_t *, const int16_t *);
void gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(uint8_t *, const int16_t *);

static uint32_t state = 1;
static uint32_t rng32(void)
{
	state = state * 1664525u + 1013904223u;
	return state;
}

static int modq(int value)
{
	value %= Q;
	return value < 0 ? value + Q : value;
}

int main(void)
{
	_Alignas(32) int16_t input[N], alias[N], standard[N], shifted[N];
	_Alignas(32) int16_t other[N], control[N], candidate[N];
	uint8_t control_bytes[1152], candidate_bytes[1152];
	unsigned successes = 0;

	for (unsigned trial = 0; trial < 1000; trial++) {
		for (unsigned i = 0; i < N; i++) {
			input[i] = (int16_t)((int)(rng32() % 19173) - 9586);
			other[i] = (int16_t)((int)(rng32() % 19173) - 9586);
		}
		const int f0 = gt32_p_baseinv_direct_avx2(standard, input);
		const int f1 = gt32_p_j1_baseinv_direct_avx2(shifted, input);
		if (f0 != f1) return 1;
		if (f0) continue;
		successes++;
		for (unsigned i = 0; i < N; i++)
			if (modq(shifted[i]) != modq((int)standard[i] * R)) return 2;

		memcpy(alias, input, sizeof(alias));
		if (gt32_p_j1_baseinv_direct_avx2(alias, alias) != 0 ||
		    memcmp(alias, shifted, sizeof(alias)) != 0) return 3;

		gt_basemul_native_asm_avx2(control, other, standard);
		gt_basemul_native_f0_j1_e0_asm_avx2(candidate, other, shifted);
		for (unsigned i = 0; i < N; i++)
			if (modq(control[i]) != modq(candidate[i])) return 4;

		gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(control_bytes, control);
		gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(candidate_bytes, candidate);
		if (memcmp(control_bytes, candidate_bytes, sizeof(control_bytes)) != 0)
			return 5;
	}

	memset(input, 0, sizeof(input));
	memset(shifted, 0x55, sizeof(shifted));
	if (gt32_p_j1_baseinv_direct_avx2(shifted, input) != 1) return 6;
	for (unsigned i = 0; i < N; i++) if (shifted[i] != 0) return 7;
	if (successes < 900) return 8;
	printf("P-J1/BM/Q24 differential pass: %u invertible trials\n", successes);
	return 0;
}
