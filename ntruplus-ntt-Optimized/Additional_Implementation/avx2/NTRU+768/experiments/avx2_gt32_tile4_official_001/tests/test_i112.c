#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define N 768

void gt32_tile4_m_to_i112_asm(int16_t *, const int16_t *);
void gt32_tile4_i112_to_m_asm(int16_t *, const int16_t *);
void gt32_tile4_inverse_i112_entry_asm(int16_t *, const int16_t *);
void gt32_tile4_inverse_soa_private_parallel_asm(int16_t *, const int16_t *);
void gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(
	int16_t *, const int16_t *, const int16_t *);
void gt32_tile4_basemul_scale_soa_soa_to_m_private_asm(
	int16_t *, const int16_t *, const int16_t *);
void gt32_tile4_inverse_all_pair_asm(int16_t *, const int16_t *);
void gt32_tile4_m_to_aos_asm(int16_t *, const int16_t *);

static uint32_t state = 1;
static uint32_t random32(void)
{
	state = state * 1664525U + 1013904223U;
	return state;
}

static int16_t centered(int32_t value)
{
	value %= 3457;
	if (value < 0)
		value += 3457;
	if (value > 1728)
		value -= 3457;
	return (int16_t)value;
}

int main(void)
{
	int16_t input[N] __attribute__((aligned(32)));
	int16_t packet[N] __attribute__((aligned(32)));
	int16_t restored[N] __attribute__((aligned(32)));
	int16_t control[N] __attribute__((aligned(32)));
	int16_t native_m[N] __attribute__((aligned(32)));
	int16_t a[N] __attribute__((aligned(32)));
	int16_t b[N] __attribute__((aligned(32)));
	int16_t product_aos[N] __attribute__((aligned(32)));
	int16_t product_m[N] __attribute__((aligned(32)));
	int16_t common[N] __attribute__((aligned(32)));

	for (unsigned trial = 0; trial < 1000; trial++) {
		for (unsigned i = 0; i < N; i++)
			input[i] = (int16_t)((int)(random32() % 5439U) - 2719);
		gt32_tile4_m_to_i112_asm(packet, input);
		gt32_tile4_i112_to_m_asm(restored, packet);
		if (memcmp(input, restored, sizeof(input)) != 0) {
			fprintf(stderr, "I-112 roundtrip failed at trial %u\n", trial);
			return 1;
		}
		gt32_tile4_inverse_soa_private_parallel_asm(control, input);
		gt32_tile4_inverse_i112_entry_asm(native_m, packet);
		if (memcmp(control, native_m, sizeof(control)) != 0) {
			fprintf(stderr, "bounded I-112 entry mismatch at trial %u\n", trial);
			return 1;
		}
		for (unsigned i = 0; i < N; i++) {
			a[i] = (int16_t)((int)(random32() % 2001U) - 1000);
			b[i] = (int16_t)((int)(random32() % 2001U) - 1000);
		}
		gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(
			product_aos, a, b);
		gt32_tile4_inverse_all_pair_asm(control, product_aos);
		gt32_tile4_basemul_scale_soa_soa_to_m_private_asm(product_m, a, b);
		gt32_tile4_m_to_i112_asm(packet, product_m);
		gt32_tile4_inverse_i112_entry_asm(native_m, packet);
		gt32_tile4_m_to_aos_asm(common, native_m);
		for (unsigned i = 0; i < N; i++) {
			if (centered(control[i]) != centered(common[i])) {
				fprintf(stderr, "I-112 BM+inverse mismatch trial=%u word=%u\n",
					trial, i);
				return 1;
			}
		}
	}
	puts("I-112 mapping/bounded inverse entry/BM chain: pass");
	return 0;
}
