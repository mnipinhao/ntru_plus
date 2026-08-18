#include "poly.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

extern void official_invntt_ct_lane_native_asm(poly *value);

static int modq(int value)
{
	value %= 3457;
	return value < 0 ? value + 3457 : value;
}

static int invmod(int value)
{
	int result = 1;
	int base = modq(value);
	unsigned exponent = 3455;
	while (exponent != 0) {
		if ((exponent & 1U) != 0) result = modq(result * base);
		base = modq(base * base);
		exponent >>= 1;
	}
	return result;
}

int main(void)
{
	for (unsigned basis = 0; basis < 768; ++basis) {
		poly input, official, candidate;
		memset(&input, 0, sizeof(input));
		input.coeffs[basis] = 1;
		official = input;
		candidate = input;
		poly_invntt_scale(&official);
		official_invntt_ct_lane_native_asm(&candidate);
		unsigned wrong = 0;
		for (unsigned i = 0; i < 768; ++i)
			if (modq(official.coeffs[i]) != modq(candidate.coeffs[i])) ++wrong;
		if (wrong != 0) {
			printf("first-terminal-basis-mismatch=%u wrong=%u\n", basis, wrong);
			break;
		}
	}
	poly constant, y;
	memset(&constant, 0, sizeof(constant));
	memset(&y, 0, sizeof(y));
	constant.coeffs[0] = 1;
	y.coeffs[4] = 1;
	poly_ntt(&constant);
	poly_ntt(&y);
	for (unsigned block = 0; block < 6; ++block) {
		printf("eval-root block=%u:", block);
		for (unsigned offset = 0; offset < 128; ++offset) {
			const unsigned index = 128 * block + offset;
			if (modq(constant.coeffs[index]) != 0) {
				printf(" %u:%d", offset,
				       modq(y.coeffs[index]) * invmod(constant.coeffs[index]) % 3457);
			}
		}
		putchar('\n');
	}
	for (unsigned monomial = 0; monomial < 768; ++monomial) {
		poly a, b, terminal, official, candidate;
		memset(&a, 0, sizeof(a));
		memset(&b, 0, sizeof(b));
		a.coeffs[monomial] = 1;
		b.coeffs[0] = 1;
		poly_ntt(&a);
		poly_ntt(&b);
		poly_basemul_scale(&terminal, &a, &b);
		official = terminal;
		candidate = terminal;
		poly_invntt_scale(&official);
		official_invntt_ct_lane_native_asm(&candidate);
		unsigned nonzero = 0;
		unsigned wrong = 0;
		for (unsigned i = 0; i < 768; ++i) {
			const int value = modq(candidate.coeffs[i]);
			if (value != modq(official.coeffs[i])) ++wrong;
		}
		if (wrong == 0) continue;
		printf("monomial=%u official=%d candidate:", monomial,
		       modq(official.coeffs[monomial]));
		for (unsigned i = 0; i < 768; ++i) {
			const int value = modq(candidate.coeffs[i]);
			if (value != 0) {
				if (nonzero < 12) printf(" %u:%d", i, value);
				++nonzero;
			}
		}
		printf(" nonzero=%u wrong=%u\n", nonzero, wrong);
		if (monomial >= 32) break;
	}
	return 0;
}
