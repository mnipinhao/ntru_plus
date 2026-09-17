#include <stdint.h>
#include <stdio.h>

#include "internal.h"
#include "witness.h"

void gt32_130_control_normal(int16_t *, const int16_t *);
void gt32_130_candidate_normal(int16_t *, const int16_t *);

static int modq(int value)
{
	value %= 3457;
	return value < 0 ? value + 3457 : value;
}

int main(void)
{
	static int16_t input[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t frontend[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t control[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t candidate[NTRUPLUS_N] __attribute__((aligned(64)));
	size_t mismatches = 0;
	size_t first = 0;

	for (size_t i = 0; i < gt32_131_witness_count; i++) {
		if (gt32_131_witness[i].index >= NTRUPLUS_N)
			return 2;
		input[gt32_131_witness[i].index] = gt32_131_witness[i].value;
	}
	ntruplus768_ntt_frontend_avx2(frontend, input);
	gt32_130_control_normal(control, frontend);
	gt32_130_candidate_normal(candidate, frontend);
	for (size_t i = 0; i < NTRUPLUS_N; i++) {
		if (modq(control[i]) != modq(candidate[i])) {
			if (mismatches == 0)
				first = i;
			mismatches++;
		}
	}
	if (mismatches == 0) {
		fputs("expected candidate wrap witness, but outputs match\n", stderr);
		return 1;
	}
	printf("PASS reachable ternary witness breaks candidate modulo q: "
	       "%zu mismatches, first word %zu (%d vs %d)\n",
	       mismatches, first, control[first], candidate[first]);
	return 0;
}
