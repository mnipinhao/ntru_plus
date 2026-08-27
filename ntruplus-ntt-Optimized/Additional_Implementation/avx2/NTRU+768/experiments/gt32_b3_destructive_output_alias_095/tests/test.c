#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "internal.h"

/* basemul.s also contains an unused P/J1 symbol whose table references must
 * resolve in this deliberately small standalone test image. */
#include "baseinv_tables.inc"

#define GUARD_WORDS 32
#define CASES 1000

typedef struct __attribute__((aligned(64))) {
	uint16_t before[GUARD_WORDS];
	int16_t p[NTRUPLUS_N];
	uint16_t after[GUARD_WORDS];
} guarded_poly;

static uint64_t rng_state = UINT64_C(0x095b3a11a5c0ffee);

static uint32_t next_u32(void)
{
	rng_state ^= rng_state << 13;
	rng_state ^= rng_state >> 7;
	rng_state ^= rng_state << 17;
	return (uint32_t)(rng_state >> 16);
}

static void init_guard(guarded_poly *g, uint16_t tag)
{
	for (size_t i = 0; i < GUARD_WORDS; i++) {
		g->before[i] = (uint16_t)(tag ^ (uint16_t)(0x1234u + i));
		g->after[i] = (uint16_t)(tag ^ (uint16_t)(0xa580u + i));
	}
}

static int check_guard(const guarded_poly *g, uint16_t tag)
{
	for (size_t i = 0; i < GUARD_WORDS; i++) {
		if (g->before[i] != (uint16_t)(tag ^ (uint16_t)(0x1234u + i)) ||
		    g->after[i] != (uint16_t)(tag ^ (uint16_t)(0xa580u + i)))
			return 0;
	}
	return 1;
}

static int16_t centered_modq(void)
{
	return (int16_t)((int32_t)(next_u32() % 3457u) - 1728);
}

static int16_t bounded_m(void)
{
	return (int16_t)((int32_t)(next_u32() % 21577u) - 10788);
}

static void fill_direct(int kind, int16_t a[NTRUPLUS_N],
	int16_t b[NTRUPLUS_N])
{
	for (size_t i = 0; i < NTRUPLUS_N; i++) {
		switch (kind) {
		case 0:
			a[i] = 0;
			b[i] = 0;
			break;
		case 1:
			a[i] = (i & 1u) ? 10788 : -10788;
			b[i] = (i & 2u) ? -10788 : 10788;
			break;
		case 2:
			a[i] = (i & 1u) ? 1728 : -1728;
			b[i] = (i & 2u) ? -1728 : 1728;
			break;
		case 3:
			a[i] = centered_modq();
			b[i] = centered_modq();
			break;
		default:
			a[i] = bounded_m();
			b[i] = bounded_m();
			break;
		}
	}
	if (kind == 0) {
		a[0] = 1;
		b[NTRUPLUS_N - 1] = -1;
	}
}

static void fill_coeff(int case_id, int16_t a[NTRUPLUS_N],
	int16_t b[NTRUPLUS_N], int16_t m[NTRUPLUS_N])
{
	for (size_t i = 0; i < NTRUPLUS_N; i++) {
		if (case_id == 0) {
			a[i] = b[i] = m[i] = 0;
		} else if (case_id == 1) {
			a[i] = (i & 1u) ? 1 : -1;
			b[i] = (i & 2u) ? -1 : 1;
			m[i] = (i & 4u) ? 1 : -1;
		} else {
			a[i] = (int16_t)((int32_t)(next_u32() % 3u) - 1);
			b[i] = (int16_t)((int32_t)(next_u32() % 3u) - 1);
			m[i] = (int16_t)((int32_t)(next_u32() % 3u) - 1);
		}
	}
	if (case_id == 0) {
		a[0] = 1;
		b[1] = -1;
		m[2] = 1;
	}
}

static void forward_m(int16_t out[NTRUPLUS_N],
	int16_t tmp[NTRUPLUS_N], const int16_t in[NTRUPLUS_N])
{
	ntruplus768_ntt_frontend_avx2(tmp, in);
	ntruplus768_ntt_m_avx2(out, tmp);
}

static int check_alias_case(const int16_t a[NTRUPLUS_N],
	const int16_t b[NTRUPLUS_N], const int16_t message[NTRUPLUS_N],
	unsigned long case_id)
{
	guarded_poly ga, gb, gaa, gab, gba, gbb, expected;
	uint8_t wire_expected[NTRUPLUS_POLYBYTES];
	uint8_t wire_alias_a[NTRUPLUS_POLYBYTES];
	uint8_t wire_alias_b[NTRUPLUS_POLYBYTES];
	const uint16_t tags[] = {0x101u, 0x202u, 0x303u, 0x404u,
		0x505u, 0x606u, 0x707u};
	guarded_poly *all[] = {&ga, &gb, &gaa, &gab, &gba, &gbb, &expected};

	for (size_t i = 0; i < sizeof all / sizeof all[0]; i++)
		init_guard(all[i], tags[i]);
	memcpy(ga.p, a, sizeof ga.p);
	memcpy(gb.p, b, sizeof gb.p);
	memcpy(gaa.p, a, sizeof gaa.p);
	memcpy(gab.p, b, sizeof gab.p);
	memcpy(gba.p, a, sizeof gba.p);
	memcpy(gbb.p, b, sizeof gbb.p);

	ntruplus768_basemul_general_m_avx2(expected.p, ga.p, gb.p);
	ntruplus768_basemul_general_m_avx2(gaa.p, gaa.p, gab.p);
	ntruplus768_basemul_general_m_avx2(gbb.p, gba.p, gbb.p);

	if (memcmp(expected.p, gaa.p, sizeof expected.p) != 0 ||
	    memcmp(expected.p, gbb.p, sizeof expected.p) != 0 ||
	    memcmp(ga.p, a, sizeof ga.p) != 0 ||
	    memcmp(gb.p, b, sizeof gb.p) != 0 ||
	    memcmp(gab.p, b, sizeof gab.p) != 0 ||
	    memcmp(gba.p, a, sizeof gba.p) != 0) {
		fprintf(stderr, "alias mismatch at case %lu\n", case_id);
		return 0;
	}
	for (size_t i = 0; i < sizeof all / sizeof all[0]; i++) {
		if (!check_guard(all[i], tags[i])) {
			fprintf(stderr, "canary mismatch at case %lu buffer %zu\n",
				case_id, i);
			return 0;
		}
	}

	ntruplus768_pack_m_sum_highrange12699_avx2(
		wire_expected, expected.p, message);
	ntruplus768_pack_m_sum_highrange12699_avx2(
		wire_alias_a, gaa.p, message);
	ntruplus768_pack_m_sum_highrange12699_avx2(
		wire_alias_b, gbb.p, message);
	if (memcmp(wire_expected, wire_alias_a, sizeof wire_expected) != 0 ||
	    memcmp(wire_expected, wire_alias_b, sizeof wire_expected) != 0) {
		fprintf(stderr, "Q24 suffix mismatch at case %lu\n", case_id);
		return 0;
	}
	return 1;
}

int main(void)
{
	static int16_t ca[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t cb[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t cm[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t ma[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t mb[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t mm[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t tmp[NTRUPLUS_N] __attribute__((aligned(64)));
	unsigned long checked = 0;

	for (int kind = 0; kind < 5; kind++) {
		fill_direct(kind, ma, mb);
		memset(mm, 0, sizeof mm);
		if (!check_alias_case(ma, mb, mm, checked++))
			return 1;
	}
	for (int i = 0; i < CASES; i++) {
		fill_coeff(i, ca, cb, cm);
		forward_m(ma, tmp, ca);
		forward_m(mb, tmp, cb);
		forward_m(mm, tmp, cm);
		if (!check_alias_case(ma, mb, mm, checked++))
			return 1;
	}
	printf("PASS cases=%lu alias_a=exact alias_b=exact suffix=byte-exact\n",
		checked);
	return 0;
}
