#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define N 768

void ntruplus768_ntt_frontend_avx2(int16_t *, const int16_t *);
void ntruplus768_ntt_m_avx2(int16_t *, const int16_t *);
void gt32_qword_ntt_frontend_avx2(int16_t *, const int16_t *);
void gt32_qword_ntt_m_avx2(int16_t *, const int16_t *);

static uint64_t state = UINT64_C(0x9e3779b97f4a7c15);

static uint32_t next_u32(void)
{
	state ^= state << 7;
	state ^= state >> 9;
	return (uint32_t)state;
}

static int modq(int value)
{
	value %= 3457;
	return value < 0 ? value + 3457 : value;
}

int main(void)
{
	_Alignas(32) int16_t input[N], ref_front[N], got_front[N];
	_Alignas(32) int16_t ref[N], got[N], alias[N];

	for (int trial = 0; trial < 1000; trial++) {
		for (int i = 0; i < N; i++)
			input[i] = (int16_t)((next_u32() & 7) - 3);
		ntruplus768_ntt_frontend_avx2(ref_front, input);
		gt32_qword_ntt_frontend_avx2(got_front, input);
		ntruplus768_ntt_m_avx2(ref, ref_front);
		gt32_qword_ntt_m_avx2(got, got_front);
		memcpy(alias, got_front, sizeof alias);
		gt32_qword_ntt_m_avx2(alias, alias);
		for (int i = 0; i < N; i++) {
			if (modq(ref[i]) != modq(got[i]) || got[i] != alias[i]) {
				fprintf(stderr, "trial=%d lane=%d ref=%d got=%d alias=%d\n",
					trial, i, ref[i], got[i], alias[i]);
				return 1;
			}
		}
	}
	puts("qword Forward: 1000 modular differentials + alias PASS");
	return 0;
}
