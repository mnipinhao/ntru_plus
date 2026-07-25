#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "gt_baseinv_native.h"
#include "gt_basemul_soa.h"
#include "gt_invntt_soa.h"
#include "gt_ntt_avx2.h"
#include "gt_ntt_tables.h"

#define QINV 12929
#define RSQ 867
#define ZETA_TOP (-1033)
#define OMEGA3 (-886)

_Static_assert(sizeof(gt_frontend_scratch) == 1536,
	"frontend scratch contract changed");
_Static_assert(sizeof(gt_stage2_scratch) == 1536,
	"stage2 scratch contract changed");

/* Linked from the verified AArch64 portable GT reference. */
void ntt_gt_rowbitrevlayout(int16_t r[GT_NTT_N],
	const int16_t a[GT_NTT_N]);
void invntt_gt_rowbitrevlayout_exact(int16_t r[GT_NTT_N],
	const int16_t a[GT_NTT_N]);
void basemul(int16_t r[4], const int16_t a[4], const int16_t b[4],
	int16_t zeta);
extern const int16_t gt_rowbitrev_lambda[2][96];

#if defined(GT_HAVE_AVX2_ASM)
typedef void (*gt_forward_candidate_fn)(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N]);

struct gt_forward_candidate {
	const char *name;
	gt_forward_candidate_fn run;
	int centered_output;
};

static const struct gt_forward_candidate reducer_forward_candidates[] = {
	{"centered", gt_ntt_avx2_frontend_centered_asm_soa, 1},
	{"centered-queued",
		gt_ntt_avx2_frontend_centered_queued_store_asm_soa, 1},
	{"identity", gt_ntt_avx2_frontend_identity_asm_soa, 0},
	{"identity-centered",
		gt_ntt_avx2_frontend_identity_centered_asm_soa, 1},
	{"identity-centered-queued",
		gt_ntt_avx2_frontend_identity_centered_queued_store_asm_soa, 1},
	{"u2-identity-centered-queued",
		gt_ntt_avx2_frontend_u2_identity_centered_queued_store_asm_soa, 1},
	{"u4-identity-centered-queued",
		gt_ntt_avx2_frontend_u4_identity_centered_queued_store_asm_soa, 1},
};

static const struct gt_forward_candidate native_forward_candidates[] = {
	{"identity-native-centered",
		gt_ntt_avx2_frontend_identity_native_centered_asm, 1},
	{"u2-identity-native-centered",
		gt_ntt_avx2_frontend_u2_identity_native_centered_asm, 1},
	{"u4-identity-native-centered",
		gt_ntt_avx2_frontend_u4_identity_native_centered_asm, 1},
	{"u2-identity-native-centered-fused",
		gt_ntt_avx2_forward_u2_identity_native_centered_fused_asm, 1},
	{"u2-identity-native-centered-pipelined-fused",
		gt_ntt_avx2_forward_u2_identity_native_centered_pipelined_fused_asm,
		1},
	{"u2-fused-split-twist-native-centered-pipelined",
		gt_ntt_avx2_forward_u2_fused_split_twist_native_centered_pipelined_asm,
		1},
	{"u2-high-first-native-centered-pipelined",
		gt_ntt_avx2_forward_u2_high_first_native_centered_pipelined_asm, 1},
	{"fixed-high-first-native-centered-pipelined",
		gt_ntt_avx2_forward_fixed_high_first_native_centered_pipelined_asm,
		1},
	{"wide-high-first-native-centered-pipelined",
		gt_ntt_avx2_forward_wide_high_first_native_centered_pipelined_asm,
		1},
	{"wide-fused-delayed-native-centered-pipelined",
		gt_ntt_avx2_forward_wide_fused_delayed_native_centered_pipelined_asm,
		1},
	{"wide-fused-delayed-row2q2-native-centered-pipelined",
		gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm,
		1},
	{"wide-fused-delayed-row2q2-native-lazy-pipelined",
		gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm,
		0},
	{"wide-fused-delayed-native-centered-contiguous-twiddles-pipelined",
		gt_ntt_avx2_forward_wide_fused_delayed_native_centered_contiguous_twiddles_pipelined_asm,
		1},
	{"wide-fused-partial-n0-native-centered-pipelined",
		gt_ntt_avx2_forward_wide_fused_partial_n0_native_centered_pipelined_asm,
		1},
	{"u4-identity-native-centered-fused",
		gt_ntt_avx2_forward_u4_identity_native_centered_fused_asm, 1},
};

struct guarded_native_output {
	uint64_t before[4];
	int16_t values[GT_NTT_N];
	uint64_t after[4];
} __attribute__((aligned(32)));

static void initialize_native_guards(struct guarded_native_output *guarded)
{
	for (unsigned i = 0; i < 4; i++) {
		guarded->before[i] = UINT64_C(0x243f6a8885a308d3);
		guarded->after[i] = UINT64_C(0x13198a2e03707344);
	}
}

static int native_guards_are_intact(
	const struct guarded_native_output *guarded)
{
	for (unsigned i = 0; i < 4; i++) {
		if (guarded->before[i] != UINT64_C(0x243f6a8885a308d3) ||
		    guarded->after[i] != UINT64_C(0x13198a2e03707344)) {
			return 0;
		}
	}
	return 1;
}
#endif

static uint32_t rng_state = 1;

static uint32_t next_u32(void)
{
	uint32_t x = rng_state;

	x ^= x << 13;
	x ^= x >> 17;
	x ^= x << 5;
	rng_state = x;
	return x;
}

static int16_t montgomery_reduce(int32_t a)
{
	const int16_t t = (int16_t)a * QINV;

	return (int16_t)((a - (int32_t)t * GT_NTT_Q) >> 16);
}

static int16_t fqmul(int16_t a, int16_t b)
{
	return montgomery_reduce((int32_t)a * b);
}

static int16_t centered(int32_t a)
{
	int32_t r = a % GT_NTT_Q;

	if (r > GT_NTT_Q / 2) {
		r -= GT_NTT_Q;
	}
	if (r < -(GT_NTT_Q / 2)) {
		r += GT_NTT_Q;
	}
	return (int16_t)r;
}

static int16_t barrett_reduce(int16_t a)
{
	const int32_t v = ((1 << 26) + GT_NTT_Q / 2) / GT_NTT_Q;
	const int32_t quotient = (v * a + (1 << 25)) >> 26;

	return (int16_t)(a - quotient * GT_NTT_Q);
}

static int congruent(int16_t a, int16_t b)
{
	return centered((int32_t)a - b) == 0;
}

static int16_t centered_i64(int64_t a)
{
	int64_t r = a % GT_NTT_Q;

	if (r > GT_NTT_Q / 2) {
		r -= GT_NTT_Q;
	}
	if (r < -(GT_NTT_Q / 2)) {
		r += GT_NTT_Q;
	}
	return (int16_t)r;
}

static int in_symmetric_bound(int16_t value, int bound)
{
	return (int)value >= -bound && (int)value <= bound;
}

static int floor_divide_32768(int value)
{
	if (value >= 0) {
		return value / 32768;
	}
	return -((-value + 32767) / 32768);
}

static int check_baseinv_center_l8(void)
{
	int16_t input[16];
	int16_t got[16];

	for (int base = -8 * (GT_NTT_Q - 1);
	     base <= 8 * (GT_NTT_Q - 1); base += 16) {
		for (unsigned lane = 0; lane < 16; lane++) {
			const int candidate = base + (int)lane;

			input[lane] = (int16_t)(candidate <=
				8 * (GT_NTT_Q - 1)
				? candidate : 8 * (GT_NTT_Q - 1));
		}
		gt_baseinv_center_l8_test_avx2(got, input);
		for (unsigned lane = 0; lane < 16; lane++) {
			const int quotient = floor_divide_32768(
				(int)input[lane] * 10 + 16384);
			const int16_t want = (int16_t)(
				(int)input[lane] - quotient * GT_NTT_Q);

			if (got[lane] != want ||
			    !congruent(got[lane], input[lane]) ||
			    got[lane] < -3080 || got[lane] > 3079) {
				fprintf(stderr,
					"baseinv center-on-load mismatch input=%d got=%d want=%d\n",
					input[lane], got[lane], want);
				return 1;
			}
		}
	}
	return 0;
}

static int quartic_determinant_nonzero(const int16_t a[4],
	int16_t lambda_montgomery)
{
	const int64_t lambda = centered(fqmul(lambda_montgomery, 1));
	const int64_t t0 = (int64_t)a[0] * a[0] +
		lambda * ((int64_t)a[2] * a[2] -
			2 * (int64_t)a[1] * a[3]);
	const int64_t t1 = 2 * (int64_t)a[0] * a[2] -
		(int64_t)a[1] * a[1] -
		lambda * (int64_t)a[3] * a[3];
	const int16_t t0_mod = centered_i64(t0);
	const int16_t t1_mod = centered_i64(t1);
	const int16_t determinant = centered_i64(
		(int64_t)t0_mod * t0_mod -
		lambda * (int64_t)t1_mod * t1_mod);

	return determinant != 0;
}

static int check_native_baseinv_identity(
	const int16_t input[GT_NTT_N],
	const int16_t inverse[GT_NTT_N], const char *label)
{
	int16_t product[GT_NTT_N] __attribute__((aligned(32)));

	gt_basemul_native_avx2(product, input, inverse);
	for (unsigned batch = 0; batch < GT_SOA_BATCHES; batch++) {
		for (unsigned coefficient = 0; coefficient < 4; coefficient++) {
			for (unsigned lane = 0; lane < GT_SOA_LANES; lane++) {
				const unsigned index = 64U * batch +
					16U * coefficient + lane;
				const int16_t want = coefficient == 0 ? 1 : 0;

				if (!congruent(product[index], want)) {
					fprintf(stderr,
						"native baseinv identity failure case=%s batch=%u coefficient=%u lane=%u got=%d want=%d\n",
						label, batch, coefficient, lane,
						product[index], want);
					return 1;
				}
			}
		}
	}
	return 0;
}

#if defined(GT_HAVE_AVX2_ASM)
static int check_native_baseinv_asm_pair(
	const int16_t centered_input[GT_NTT_N],
	const int16_t lazy_input[GT_NTT_N],
	const int16_t centered_oracle[GT_NTT_N],
	const int16_t lazy_oracle[GT_NTT_N],
	int oracle_status, const char *label)
{
	int16_t centered_copy[GT_NTT_N] __attribute__((aligned(32)));
	int16_t lazy_copy[GT_NTT_N] __attribute__((aligned(32)));
	int16_t centered_inverse[GT_NTT_N] __attribute__((aligned(32)));
	int16_t lazy_inverse[GT_NTT_N] __attribute__((aligned(32)));
	int16_t centered_inplace[GT_NTT_N] __attribute__((aligned(32)));
	int16_t lazy_inplace[GT_NTT_N] __attribute__((aligned(32)));
	int centered_status;
	int lazy_status;
	int centered_inplace_status;
	int lazy_inplace_status;

	memcpy(centered_copy, centered_input, sizeof(centered_copy));
	memcpy(lazy_copy, lazy_input, sizeof(lazy_copy));
	memcpy(centered_inplace, centered_input, sizeof(centered_inplace));
	memcpy(lazy_inplace, lazy_input, sizeof(lazy_inplace));
	centered_status = gt_baseinv_native_centered_asm_avx2(
		centered_inverse, centered_input);
	lazy_status = gt_baseinv_native_center_on_load_asm_avx2(
		lazy_inverse, lazy_input);
	centered_inplace_status = gt_baseinv_native_centered_asm_avx2(
		centered_inplace, centered_inplace);
	lazy_inplace_status = gt_baseinv_native_center_on_load_asm_avx2(
		lazy_inplace, lazy_inplace);

	if (centered_status != oracle_status || lazy_status != oracle_status ||
	    centered_inplace_status != oracle_status ||
	    lazy_inplace_status != oracle_status ||
	    memcmp(centered_copy, centered_input, sizeof(centered_copy)) != 0 ||
	    memcmp(lazy_copy, lazy_input, sizeof(lazy_copy)) != 0) {
		fprintf(stderr,
			"native baseinv ASM status/alias/input failure case=%s oracle=%d centered=%d lazy=%d centered-inplace=%d lazy-inplace=%d\n",
			label, oracle_status, centered_status, lazy_status,
			centered_inplace_status, lazy_inplace_status);
		return 1;
	}

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (centered_inverse[i] != centered_inplace[i] ||
		    lazy_inverse[i] != lazy_inplace[i]) {
			fprintf(stderr,
				"native baseinv ASM out==in failure case=%s i=%u centered=%d centered-inplace=%d lazy=%d lazy-inplace=%d\n",
				label, i, centered_inverse[i],
				centered_inplace[i], lazy_inverse[i],
				lazy_inplace[i]);
			return 1;
		}
		if (oracle_status != 0) {
			if (centered_inverse[i] != 0 || lazy_inverse[i] != 0) {
				fprintf(stderr,
					"native baseinv ASM failure-zero mismatch case=%s i=%u centered=%d lazy=%d\n",
					label, i, centered_inverse[i],
					lazy_inverse[i]);
				return 1;
			}
		} else if (!congruent(centered_inverse[i],
				centered_oracle[i]) ||
		    !congruent(lazy_inverse[i], lazy_oracle[i]) ||
		    !congruent(centered_inverse[i], lazy_inverse[i]) ||
		    !in_symmetric_bound(centered_inverse[i], GT_NTT_Q - 1) ||
		    !in_symmetric_bound(lazy_inverse[i], GT_NTT_Q - 1)) {
			fprintf(stderr,
				"native baseinv ASM differential/range failure case=%s i=%u centered=%d centered-oracle=%d lazy=%d lazy-oracle=%d\n",
				label, i, centered_inverse[i],
				centered_oracle[i], lazy_inverse[i],
				lazy_oracle[i]);
			return 1;
		}
	}
	if (oracle_status == 0 &&
	    (check_native_baseinv_identity(centered_input,
			centered_inverse, label) != 0 ||
	     check_native_baseinv_identity(lazy_input,
			lazy_inverse, label) != 0)) {
		return 1;
	}
	return 0;
}
#endif

static int check_native_baseinv_pair(
	const int16_t centered_input[GT_NTT_N],
	const int16_t lazy_input[GT_NTT_N], const char *label)
{
	int16_t centered_copy[GT_NTT_N] __attribute__((aligned(32)));
	int16_t lazy_copy[GT_NTT_N] __attribute__((aligned(32)));
	int16_t centered_inverse[GT_NTT_N] __attribute__((aligned(32)));
	int16_t lazy_inverse[GT_NTT_N] __attribute__((aligned(32)));
	int16_t centered_inplace[GT_NTT_N] __attribute__((aligned(32)));
	int16_t lazy_inplace[GT_NTT_N] __attribute__((aligned(32)));
	int centered_status;
	int lazy_status;
	int centered_inplace_status;
	int lazy_inplace_status;

	memcpy(centered_copy, centered_input, sizeof(centered_copy));
	memcpy(lazy_copy, lazy_input, sizeof(lazy_copy));
	memcpy(centered_inplace, centered_input, sizeof(centered_inplace));
	memcpy(lazy_inplace, lazy_input, sizeof(lazy_inplace));
	centered_status = gt_baseinv_native_centered_avx2(
		centered_inverse, centered_input);
	lazy_status = gt_baseinv_native_center_on_load_avx2(
		lazy_inverse, lazy_input);
	centered_inplace_status = gt_baseinv_native_centered_avx2(
		centered_inplace, centered_inplace);
	lazy_inplace_status = gt_baseinv_native_center_on_load_avx2(
		lazy_inplace, lazy_inplace);

	if (centered_status != lazy_status ||
	    centered_inplace_status != centered_status ||
	    lazy_inplace_status != lazy_status ||
	    memcmp(centered_copy, centered_input, sizeof(centered_copy)) != 0 ||
	    memcmp(lazy_copy, lazy_input, sizeof(lazy_copy)) != 0) {
		fprintf(stderr,
			"native baseinv status/alias/input failure case=%s centered=%d lazy=%d centered-inplace=%d lazy-inplace=%d\n",
			label, centered_status, lazy_status,
			centered_inplace_status, lazy_inplace_status);
		return 1;
	}

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (centered_inverse[i] != centered_inplace[i] ||
		    lazy_inverse[i] != lazy_inplace[i]) {
			fprintf(stderr,
				"native baseinv out==in failure case=%s i=%u centered=%d centered-inplace=%d lazy=%d lazy-inplace=%d\n",
				label, i, centered_inverse[i],
				centered_inplace[i], lazy_inverse[i],
				lazy_inplace[i]);
			return 1;
		}
		if (centered_status != 0) {
			if (centered_inverse[i] != 0 || lazy_inverse[i] != 0) {
				fprintf(stderr,
					"native baseinv failure-zero mismatch case=%s i=%u centered=%d lazy=%d\n",
					label, i, centered_inverse[i],
					lazy_inverse[i]);
				return 1;
			}
		} else if (!congruent(centered_inverse[i], lazy_inverse[i]) ||
		    !in_symmetric_bound(centered_inverse[i], GT_NTT_Q - 1) ||
		    !in_symmetric_bound(lazy_inverse[i], GT_NTT_Q - 1)) {
			fprintf(stderr,
				"native baseinv differential/range failure case=%s i=%u centered=%d lazy=%d\n",
				label, i, centered_inverse[i], lazy_inverse[i]);
			return 1;
		}
	}

	if (centered_status == 0 &&
	    (check_native_baseinv_identity(centered_input,
			centered_inverse, label) != 0 ||
	     check_native_baseinv_identity(lazy_input,
			lazy_inverse, label) != 0)) {
		return 1;
	}
#if defined(GT_HAVE_AVX2_ASM)
	if (check_native_baseinv_asm_pair(centered_input, lazy_input,
		centered_inverse, lazy_inverse, centered_status, label) != 0) {
		return 1;
	}
#endif
	return 0;
}

static int check_native_baseinv_l3_input(
	const int16_t input[GT_NTT_N], const char *label)
{
	int16_t input_copy[GT_NTT_N] __attribute__((aligned(32)));
	int16_t normalized_inverse[GT_NTT_N] __attribute__((aligned(32)));
	int16_t direct_inverse[GT_NTT_N] __attribute__((aligned(32)));
	int16_t direct_inplace[GT_NTT_N] __attribute__((aligned(32)));
#if defined(GT_HAVE_AVX2_ASM)
	int16_t direct_asm_inverse[GT_NTT_N] __attribute__((aligned(32)));
	int16_t direct_asm_inplace[GT_NTT_N] __attribute__((aligned(32)));
#endif
	int normalized_status;
	int direct_status;
	int direct_inplace_status;
#if defined(GT_HAVE_AVX2_ASM)
	int direct_asm_status;
	int direct_asm_inplace_status;
#endif

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (!in_symmetric_bound(input[i],
			GT_FORWARD_LAZY_L3_BOUND)) {
			fprintf(stderr,
				"GTN-L3 input range failure case=%s i=%u value=%d bound=%d\n",
				label, i, input[i], GT_FORWARD_LAZY_L3_BOUND);
			return 1;
		}
	}

	memcpy(input_copy, input, sizeof(input_copy));
	memcpy(direct_inplace, input, sizeof(direct_inplace));
	normalized_status = gt_baseinv_native_center_on_load_avx2(
		normalized_inverse, input);
	direct_status = gt_baseinv_native_l3_avx2(direct_inverse, input);
	direct_inplace_status = gt_baseinv_native_l3_avx2(
		direct_inplace, direct_inplace);
#if defined(GT_HAVE_AVX2_ASM)
	memcpy(direct_asm_inplace, input, sizeof(direct_asm_inplace));
	direct_asm_status = gt_baseinv_native_l3_asm_avx2(
		direct_asm_inverse, input);
	direct_asm_inplace_status = gt_baseinv_native_l3_asm_avx2(
		direct_asm_inplace, direct_asm_inplace);
#endif

	if (normalized_status != direct_status ||
	    direct_inplace_status != direct_status ||
	    memcmp(input_copy, input, sizeof(input_copy)) != 0
#if defined(GT_HAVE_AVX2_ASM)
	    || direct_asm_status != direct_status ||
	    direct_asm_inplace_status != direct_status
#endif
	    ) {
		fprintf(stderr,
			"GTN-L3 baseinv status/alias/input failure case=%s normalized=%d direct=%d inplace=%d"
#if defined(GT_HAVE_AVX2_ASM)
			" asm=%d asm-inplace=%d"
#endif
			"\n",
			label, normalized_status, direct_status,
			direct_inplace_status
#if defined(GT_HAVE_AVX2_ASM)
			, direct_asm_status, direct_asm_inplace_status
#endif
			);
		return 1;
	}

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (direct_inverse[i] != direct_inplace[i]
#if defined(GT_HAVE_AVX2_ASM)
		    || direct_asm_inverse[i] != direct_asm_inplace[i]
#endif
		    ) {
			fprintf(stderr,
				"GTN-L3 baseinv out==in failure case=%s i=%u direct=%d inplace=%d"
#if defined(GT_HAVE_AVX2_ASM)
				" asm=%d asm-inplace=%d"
#endif
				"\n",
				label, i, direct_inverse[i], direct_inplace[i]
#if defined(GT_HAVE_AVX2_ASM)
				, direct_asm_inverse[i], direct_asm_inplace[i]
#endif
				);
			return 1;
		}
		if (direct_status != 0) {
			if (normalized_inverse[i] != 0 || direct_inverse[i] != 0
#if defined(GT_HAVE_AVX2_ASM)
			    || direct_asm_inverse[i] != 0
#endif
			    ) {
				fprintf(stderr,
					"GTN-L3 baseinv failure-zero mismatch case=%s i=%u\n",
					label, i);
				return 1;
			}
		} else if (!congruent(direct_inverse[i],
				normalized_inverse[i]) ||
		    !in_symmetric_bound(direct_inverse[i], GT_NTT_Q - 1)
#if defined(GT_HAVE_AVX2_ASM)
		    || !congruent(direct_asm_inverse[i],
				normalized_inverse[i]) ||
		    !in_symmetric_bound(direct_asm_inverse[i], GT_NTT_Q - 1)
#endif
		    ) {
			fprintf(stderr,
				"GTN-L3 baseinv differential/range failure case=%s i=%u normalized=%d direct=%d"
#if defined(GT_HAVE_AVX2_ASM)
				" asm=%d"
#endif
				"\n",
				label, i, normalized_inverse[i], direct_inverse[i]
#if defined(GT_HAVE_AVX2_ASM)
				, direct_asm_inverse[i]
#endif
				);
			return 1;
		}
	}

	if (direct_status == 0 &&
	    check_native_baseinv_identity(input, direct_inverse, label) != 0) {
		return 1;
	}
	return 0;
}

static int check_native_baseinv_l3_boundaries(void)
{
	int16_t input[GT_NTT_N] __attribute__((aligned(32)));

	memset(input, 0, sizeof(input));
	for (unsigned batch = 0; batch < GT_SOA_BATCHES; batch++) {
		const int bound = GT_FORWARD_LAZY_BATCH_BOUND(batch);

		for (unsigned lane = 0; lane < GT_SOA_LANES; lane++) {
			input[64U * batch + lane] =
				(int16_t)(((batch + lane) & 1U) != 0
					? bound : -bound);
		}
	}
	if (check_native_baseinv_l3_input(input,
		"l3-forward-vector-endpoints") != 0) {
		return 1;
	}

	memset(input, 0, sizeof(input));
	for (unsigned batch = 0; batch < GT_SOA_BATCHES; batch++) {
		for (unsigned lane = 0; lane < GT_SOA_LANES; lane++) {
			input[64U * batch + lane] =
				(int16_t)(((batch + lane) & 1U) != 0
					? GT_FORWARD_LAZY_L3_BOUND
					: -GT_FORWARD_LAZY_L3_BOUND);
		}
	}
	if (check_native_baseinv_l3_input(input,
		"l3-generic-endpoints") != 0) {
		return 1;
	}

	memset(input, 0, sizeof(input));
	for (unsigned batch = 0; batch < GT_SOA_BATCHES; batch++) {
		for (unsigned lane = 0; lane < GT_SOA_LANES; lane++) {
			input[64U * batch + lane] = 1;
		}
	}
	input[0] = 0;
	if (check_native_baseinv_l3_input(input,
		"l3-one-zero-determinant") != 0) {
		return 1;
	}

	memset(input, 0, sizeof(input));
	return check_native_baseinv_l3_input(input, "l3-all-zero");
}

static int check_native_baseinv_boundaries(void)
{
	int16_t centered_input[GT_NTT_N] __attribute__((aligned(32)));
	int16_t lazy_input[GT_NTT_N] __attribute__((aligned(32)));

	/* Exact GTN-L8 endpoints, all representing nonzero scalar quartics. */
	memset(centered_input, 0, sizeof(centered_input));
	for (unsigned batch = 0; batch < GT_SOA_BATCHES; batch++) {
		for (unsigned lane = 0; lane < GT_SOA_LANES; lane++) {
			const unsigned base = 64U * batch;

			centered_input[base + lane] =
				((batch + lane) & 1U) != 0 ? 8 : -8;
			for (unsigned coefficient = 1; coefficient < 4;
			     coefficient++) {
				centered_input[base + 16U * coefficient + lane] = 0;
			}
		}
	}
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		const unsigned coefficient = (i % 64U) / 16U;

		if (coefficient == 0) {
			lazy_input[i] = centered_input[i] > 0
				? (int16_t)(-8 * (GT_NTT_Q - 1))
				: (int16_t)(8 * (GT_NTT_Q - 1));
		} else {
			const int multiple = (int)((i % 15U)) - 7;

			lazy_input[i] = (int16_t)(multiple * GT_NTT_Q);
		}
	}
	if (check_native_baseinv_pair(centered_input, lazy_input,
		"lazy-endpoints") != 0) {
		return 1;
	}

	/* One zero quartic lane must fail the shared batch and zero all output. */
	memset(centered_input, 0, sizeof(centered_input));
	for (unsigned batch = 0; batch < GT_SOA_BATCHES; batch++) {
		for (unsigned lane = 0; lane < GT_SOA_LANES; lane++) {
			centered_input[64U * batch + lane] = 1;
		}
	}
	memcpy(lazy_input, centered_input, sizeof(lazy_input));
	centered_input[0] = 0;
	lazy_input[0] = 0;
	if (check_native_baseinv_pair(centered_input, lazy_input,
		"one-zero-determinant") != 0) {
		return 1;
	}

	memset(centered_input, 0, sizeof(centered_input));
	memset(lazy_input, 0, sizeof(lazy_input));
	return check_native_baseinv_pair(centered_input, lazy_input,
		"all-zero");
}

static int check_native_baseinv_random(void)
{
	int16_t centered_input[GT_NTT_N] __attribute__((aligned(32)));
	int16_t lazy_input[GT_NTT_N] __attribute__((aligned(32)));
	int16_t l3_input[GT_NTT_N] __attribute__((aligned(32)));

	for (unsigned round = 0; round < 100; round++) {
		char label[40];

		for (unsigned batch = 0; batch < GT_SOA_BATCHES; batch++) {
			for (unsigned lane = 0; lane < GT_SOA_LANES; lane++) {
				int16_t quartic[4];

				do {
					for (unsigned coefficient = 0;
					     coefficient < 4; coefficient++) {
						quartic[coefficient] = (int16_t)(
							(int)(next_u32() % GT_NTT_Q) -
							GT_NTT_Q / 2);
					}
				} while (!quartic_determinant_nonzero(quartic,
					gt_native_lambda[batch][lane]));

				for (unsigned coefficient = 0; coefficient < 4;
				     coefficient++) {
					const unsigned index = 64U * batch +
						16U * coefficient + lane;
					const int multiple =
						(int)(next_u32() % 15U) - 7;
					const int l3_multiple =
						(int)(next_u32() % 5U) - 2;

					centered_input[index] =
						quartic[coefficient];
					lazy_input[index] = (int16_t)(
						(int)quartic[coefficient] +
						multiple * GT_NTT_Q);
					l3_input[index] = (int16_t)(
						(int)quartic[coefficient] +
						l3_multiple * GT_NTT_Q);
				}
			}
		}
		(void)snprintf(label, sizeof(label),
			"native-baseinv-random-%u", round);
		if (check_native_baseinv_pair(centered_input, lazy_input,
			label) != 0) {
			return 1;
		}
		if (check_native_baseinv_l3_input(l3_input, label) != 0) {
			return 1;
		}
	}
	return 0;
}

static unsigned bitreverse_limited(unsigned x, unsigned bits)
{
	unsigned result = 0;

	for (unsigned i = 0; i < bits; i++) {
		result = (result << 1) | (x & 1U);
		x >>= 1;
	}
	return result;
}

static unsigned twiddle_power(unsigned stage, unsigned lo)
{
	if (stage == 1) {
		return 0;
	}
	return bitreverse_limited(lo >> (6 - stage), stage - 1)
		<< (5 - stage);
}

static unsigned input_index(unsigned n3, unsigned n32)
{
	return (64U * n3 + 33U * n32) % 96U;
}

static void scalar_frontend(int16_t rows[3][32][8],
	const int16_t in[GT_NTT_N])
{
	for (unsigned q = 0; q < 32; q++) {
		for (unsigned stream = 0; stream < 8; stream++) {
			const unsigned branch = stream >> 2;
			const unsigned lane = stream & 3U;
			int16_t x[3];

			for (unsigned n3 = 0; n3 < 3; n3++) {
				const unsigned n = input_index(n3, q);
				const int16_t low = in[4U * n + lane];
				const int16_t high = in[384U + 4U * n + lane];
				const int16_t split = fqmul(high, ZETA_TOP);
				const int16_t value = branch == 0
					? (int16_t)(low + split)
					: (int16_t)(low + high - split);

				x[n3] = fqmul(value, gt_twist[branch][n]);
			}

			{
				const int16_t t = fqmul(centered(x[1] - x[2]), OMEGA3);

				rows[0][q][stream] = centered(x[0] + x[1] + x[2]);
				rows[1][q][stream] = centered(x[0] - x[2] + t);
				rows[2][q][stream] = centered(x[0] - x[1] - t);
			}
		}
	}
}

static void scalar_stages12(int16_t rows[3][32][8])
{
	for (unsigned row = 0; row < 3; row++) {
		for (unsigned stage = 1; stage <= 2; stage++) {
			const unsigned distance = 1U << (5 - stage);

			for (unsigned lo = 0; lo < 32; lo++) {
				if ((lo & distance) != 0) {
					continue;
				}
				for (unsigned stream = 0; stream < 8; stream++) {
					const unsigned hi = lo + distance;
					const int16_t u = rows[row][lo][stream];
					const int16_t t = fqmul(rows[row][hi][stream],
						gt_omega32[twiddle_power(stage, lo)]);

					rows[row][lo][stream] = centered(u + t);
					rows[row][hi][stream] = centered(u - t);
				}
			}
		}
	}
}

static int check_montgomery(void)
{
	int16_t a[16];
	int16_t b[16];
	int16_t got[16];

	for (unsigned round = 0; round < 1000; round++) {
		for (unsigned lane = 0; lane < 16; lane++) {
			a[lane] = (int16_t)((int)(next_u32() % 55297U) - 27648);
			b[lane] = (int16_t)((int)(next_u32() % 3457U) - 1728);
		}
		gt_ntt_avx2_montgomery_test(got, a, b);
		for (unsigned lane = 0; lane < 16; lane++) {
			const int16_t want = fqmul(a[lane], b[lane]);

			if (got[lane] != want) {
				fprintf(stderr,
					"Montgomery mismatch round=%u lane=%u got=%d want=%d\n",
					round, lane, got[lane], want);
				return 1;
			}
		}
	}
	return 0;
}

static int check_barrett(void)
{
	int16_t input[16];
	int16_t got[16];

	for (int base = -27648; base <= 27648; base += 16) {
		for (unsigned lane = 0; lane < 16; lane++) {
			int value = base + (int)lane;

			if (value > 27648) {
				value = 27648;
			}
			input[lane] = (int16_t)value;
		}
		gt_ntt_avx2_barrett_test(got, input);
		for (unsigned lane = 0; lane < 16; lane++) {
			const int16_t want = barrett_reduce(input[lane]);

			if (got[lane] != want) {
				fprintf(stderr,
					"Barrett mismatch input=%d got=%d want=%d\n",
					input[lane], got[lane], want);
				return 1;
			}
		}
	}
	return 0;
}

#if defined(GT_HAVE_AVX2_ASM)
static int check_native_forward_baseinv(
	const int16_t input[GT_NTT_N], const char *label)
{
	int16_t centered_native[GT_NTT_N] __attribute__((aligned(32)));
	int16_t lazy_native[GT_NTT_N] __attribute__((aligned(32)));

	gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm(
		centered_native, input);
	gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm(
		lazy_native, input);
	if (check_native_baseinv_pair(centered_native, lazy_native, label) != 0) {
		return 1;
	}
	return check_native_baseinv_l3_input(lazy_native, label);
}

static int check_packed_barrett_asm(void)
{
	int16_t input[16];
	int16_t got[16];

	for (int base = -8 * (GT_NTT_Q - 1);
	     base <= 8 * (GT_NTT_Q - 1); base += 16) {
		for (unsigned lane = 0; lane < 16; lane++) {
			const int value = base + (int)lane;

			input[lane] = (int16_t)(value <= 8 * (GT_NTT_Q - 1)
				? value : 8 * (GT_NTT_Q - 1));
		}
		gt_ntt_avx2_barrett_packed_asm(got, input);
		for (unsigned lane = 0; lane < 16; lane++) {
			const int value = base + (int)lane;

			if (value > 8 * (GT_NTT_Q - 1)) {
				continue;
			}
			if (!congruent(got[lane], input[lane]) || got[lane] < 0 ||
			    got[lane] > GT_NTT_Q) {
				fprintf(stderr,
					"packed ASM Barrett failure input=%d output=%d\n",
					value, got[lane]);
				return 1;
			}
		}
	}
	return 0;
}

static int check_packed_centered_asm(void)
{
	int16_t input[16];
	int16_t got[16];

	for (int base = -8 * (GT_NTT_Q - 1);
	     base <= 8 * (GT_NTT_Q - 1); base += 16) {
		for (unsigned lane = 0; lane < 16; lane++) {
			const int value = base + (int)lane;

			input[lane] = (int16_t)(value <= 8 * (GT_NTT_Q - 1)
				? value : 8 * (GT_NTT_Q - 1));
		}
		gt_ntt_avx2_centered_packed_asm(got, input);
		for (unsigned lane = 0; lane < 16; lane++) {
			const int value = base + (int)lane;

			if (value > 8 * (GT_NTT_Q - 1)) {
				continue;
			}
			if (!congruent(got[lane], input[lane]) ||
			    got[lane] < -3080 || got[lane] > 3079) {
				fprintf(stderr,
					"packed ASM centered failure input=%d output=%d\n",
					value, got[lane]);
				return 1;
			}
		}
	}
	return 0;
}
#endif

static int check_frontend(const int16_t input[GT_NTT_N])
{
	gt_frontend_scratch got;
#if defined(GT_HAVE_AVX2_ASM)
	gt_frontend_scratch asm_got;
#endif
	int16_t want[3][32][8];

	gt_ntt_avx2_frontend(&got, input);
#if defined(GT_HAVE_AVX2_ASM)
	gt_ntt_avx2_frontend_asm(&asm_got, input);
#endif
	scalar_frontend(want, input);
	for (unsigned q = 0; q < 32; q++) {
		for (unsigned stream = 0; stream < 8; stream++) {
#if defined(GT_HAVE_AVX2_ASM)
			if (asm_got.row01[q][stream] != got.row01[q][stream] ||
			    asm_got.row01[q][8 + stream] !=
				got.row01[q][8 + stream] ||
			    asm_got.row2[q][stream] != got.row2[q][stream]) {
				fprintf(stderr,
					"frontend ASM exact mismatch Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
#endif
			if (!in_symmetric_bound(got.row01[q][stream], 3 * 3456) ||
			    !in_symmetric_bound(got.row01[q][8 + stream], 3 * 3456) ||
			    !in_symmetric_bound(got.row2[q][stream], 3 * 3456)) {
				fprintf(stderr, "frontend range failure Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
			if (!congruent(got.row01[q][stream], want[0][q][stream]) ||
			    !congruent(got.row01[q][8 + stream], want[1][q][stream]) ||
			    !congruent(got.row2[q][stream], want[2][q][stream])) {
				fprintf(stderr, "frontend mismatch Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
		}
	}
	return 0;
}

static int check_stage2(const int16_t input[GT_NTT_N])
{
	gt_frontend_scratch frontend;
	gt_stage2_scratch got;
#if defined(GT_HAVE_AVX2_ASM)
	gt_stage2_scratch asm_got;
	gt_stage2_scratch fused_got;
	gt_stage2_scratch fused_inplace;
	gt_stage2_scratch identity_got;
	gt_stage2_scratch identity_row2q2_got;
	gt_stage2_scratch fused_identity_got;
	gt_stage2_scratch fused_identity_inplace;
	gt_stage2_scratch u2_got;
	gt_stage2_scratch u4_got;
	gt_stage2_scratch u2_inplace;
	gt_stage2_scratch u4_inplace;
	gt_stage2_scratch u2_identity_got;
	gt_stage2_scratch u4_identity_got;
	gt_stage2_scratch u2_identity_inplace;
	gt_stage2_scratch u4_identity_inplace;
	gt_stage2_scratch direct_got;
	gt_stage2_scratch half_got;
#endif
	int16_t want[3][32][8];

	gt_ntt_avx2_frontend(&frontend, input);
	gt_ntt_avx2_stage12(&got, &frontend);
#if defined(GT_HAVE_AVX2_ASM)
	gt_ntt_avx2_stage12_asm(&asm_got, &frontend);
	gt_ntt_avx2_frontend_stage12_asm(&fused_got, input);
	memcpy(&fused_inplace, input, sizeof(fused_inplace));
	gt_ntt_avx2_frontend_stage12_asm(&fused_inplace,
		(const int16_t *)(const void *)&fused_inplace);
	gt_ntt_avx2_stage12_identity_asm(&identity_got, &frontend);
	gt_ntt_avx2_stage12_identity_row2q2_asm(&identity_row2q2_got,
		&frontend);
	gt_ntt_avx2_frontend_stage12_identity_asm(&fused_identity_got, input);
	memcpy(&fused_identity_inplace, input, sizeof(fused_identity_inplace));
	gt_ntt_avx2_frontend_stage12_identity_asm(&fused_identity_inplace,
		(const int16_t *)(const void *)&fused_identity_inplace);
	gt_ntt_avx2_frontend_stage12_u2_asm(&u2_got, input);
	gt_ntt_avx2_frontend_stage12_u4_asm(&u4_got, input);
	gt_ntt_avx2_frontend_stage12_u2_identity_asm(&u2_identity_got, input);
	gt_ntt_avx2_frontend_stage12_u4_identity_asm(&u4_identity_got, input);
	memcpy(&u2_inplace, input, sizeof(u2_inplace));
	memcpy(&u4_inplace, input, sizeof(u4_inplace));
	memcpy(&u2_identity_inplace, input, sizeof(u2_identity_inplace));
	memcpy(&u4_identity_inplace, input, sizeof(u4_identity_inplace));
	gt_ntt_avx2_frontend_stage12_u2_asm(&u2_inplace,
		(const int16_t *)(const void *)&u2_inplace);
	gt_ntt_avx2_frontend_stage12_u4_asm(&u4_inplace,
		(const int16_t *)(const void *)&u4_inplace);
	gt_ntt_avx2_frontend_stage12_u2_identity_asm(&u2_identity_inplace,
		(const int16_t *)(const void *)&u2_identity_inplace);
	gt_ntt_avx2_frontend_stage12_u4_identity_asm(&u4_identity_inplace,
		(const int16_t *)(const void *)&u4_identity_inplace);
	gt_ntt_avx2_frontend_stage12_direct_asm(&direct_got, input);
	gt_ntt_avx2_frontend_stage12_half_asm(&half_got, input);
	if (memcmp(&got, &u2_got, sizeof(got)) != 0 ||
	    memcmp(&got, &u4_got, sizeof(got)) != 0 ||
	    memcmp(&got, &u2_inplace, sizeof(got)) != 0 ||
	    memcmp(&got, &u4_inplace, sizeof(got)) != 0 ||
	    memcmp(&identity_got, &u2_identity_got, sizeof(identity_got)) != 0 ||
	    memcmp(&identity_got, &u4_identity_got, sizeof(identity_got)) != 0 ||
	    memcmp(&identity_got, &u2_identity_inplace,
		sizeof(identity_got)) != 0 ||
	    memcmp(&identity_got, &u4_identity_inplace,
		sizeof(identity_got)) != 0) {
		fputs("frontend u2/u4 stage2 exact or in-place mismatch\n", stderr);
		return 1;
	}
#endif
	scalar_frontend(want, input);
	scalar_stages12(want);
	for (unsigned q = 0; q < 32; q++) {
		for (unsigned stream = 0; stream < 8; stream++) {
#if defined(GT_HAVE_AVX2_ASM)
			if (asm_got.row01[q][stream] != got.row01[q][stream] ||
			    asm_got.row01[q][8 + stream] !=
				got.row01[q][8 + stream] ||
			    fused_got.row01[q][stream] != got.row01[q][stream] ||
			    fused_got.row01[q][8 + stream] !=
				got.row01[q][8 + stream] ||
			    fused_inplace.row01[q][stream] != got.row01[q][stream] ||
			    fused_inplace.row01[q][8 + stream] !=
				got.row01[q][8 + stream] ||
			    direct_got.row01[q][stream] != got.row01[q][stream] ||
			    direct_got.row01[q][8 + stream] !=
				got.row01[q][8 + stream] ||
			    half_got.row01[q][stream] != got.row01[q][stream] ||
			    half_got.row01[q][8 + stream] !=
				got.row01[q][8 + stream]) {
				fprintf(stderr,
					"stage12 ASM exact mismatch Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
#endif
			if (!in_symmetric_bound(got.row01[q][stream], 5 * 3456) ||
			    !in_symmetric_bound(got.row01[q][8 + stream], 5 * 3456)) {
				fprintf(stderr, "row01 stage2 range failure Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
			if (!congruent(got.row01[q][stream], want[0][q][stream]) ||
			    !congruent(got.row01[q][8 + stream], want[1][q][stream])) {
				fprintf(stderr, "row01 stage2 mismatch Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
#if defined(GT_HAVE_AVX2_ASM)
			if (!congruent(identity_got.row01[q][stream],
					got.row01[q][stream]) ||
			    !congruent(identity_got.row01[q][8 + stream],
					got.row01[q][8 + stream]) ||
			    identity_got.row01[q][stream] !=
					fused_identity_got.row01[q][stream] ||
			    identity_got.row01[q][8 + stream] !=
					fused_identity_got.row01[q][8 + stream] ||
			    identity_got.row01[q][stream] !=
					fused_identity_inplace.row01[q][stream] ||
			    identity_got.row01[q][8 + stream] !=
					fused_identity_inplace.row01[q][8 + stream] ||
			    identity_row2q2_got.row01[q][stream] !=
					identity_got.row01[q][stream] ||
			    identity_row2q2_got.row01[q][8 + stream] !=
					identity_got.row01[q][8 + stream] ||
			    !in_symmetric_bound(identity_got.row01[q][stream],
					5 * 3456) ||
			    !in_symmetric_bound(identity_got.row01[q][8 + stream],
					5 * 3456)) {
				fprintf(stderr,
					"row01 identity stage2 failure Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
#endif
		}
	}
	for (unsigned q = 0; q < 16; q++) {
		for (unsigned stream = 0; stream < 8; stream++) {
#if defined(GT_HAVE_AVX2_ASM)
			if (asm_got.row2_packed[q][stream] !=
				got.row2_packed[q][stream] ||
			    asm_got.row2_packed[q][8 + stream] !=
				got.row2_packed[q][8 + stream] ||
			    fused_got.row2_packed[q][stream] !=
				got.row2_packed[q][stream] ||
			    fused_got.row2_packed[q][8 + stream] !=
				got.row2_packed[q][8 + stream] ||
			    fused_inplace.row2_packed[q][stream] !=
				got.row2_packed[q][stream] ||
			    fused_inplace.row2_packed[q][8 + stream] !=
				got.row2_packed[q][8 + stream] ||
			    direct_got.row2_packed[q][stream] !=
				got.row2_packed[q][stream] ||
			    direct_got.row2_packed[q][8 + stream] !=
				got.row2_packed[q][8 + stream] ||
			    half_got.row2_packed[q][stream] !=
				got.row2_packed[q][stream] ||
			    half_got.row2_packed[q][8 + stream] !=
				got.row2_packed[q][8 + stream]) {
				fprintf(stderr,
					"row2 stage12 ASM exact mismatch Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
#endif
			if (!in_symmetric_bound(got.row2_packed[q][stream], 5 * 3456) ||
			    !in_symmetric_bound(got.row2_packed[q][8 + stream], 5 * 3456)) {
				fprintf(stderr, "row2 stage2 range failure Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
			if (!congruent(got.row2_packed[q][stream],
					want[2][q][stream]) ||
			    !congruent(got.row2_packed[q][8 + stream],
					want[2][q + 16][stream])) {
				fprintf(stderr, "row2 stage2 mismatch Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
#if defined(GT_HAVE_AVX2_ASM)
			if (!congruent(identity_got.row2_packed[q][stream],
					got.row2_packed[q][stream]) ||
			    !congruent(identity_got.row2_packed[q][8 + stream],
					got.row2_packed[q][8 + stream]) ||
			    identity_got.row2_packed[q][stream] !=
					fused_identity_got.row2_packed[q][stream] ||
			    identity_got.row2_packed[q][8 + stream] !=
					fused_identity_got.row2_packed[q][8 + stream] ||
			    identity_got.row2_packed[q][stream] !=
					fused_identity_inplace.row2_packed[q][stream] ||
			    identity_got.row2_packed[q][8 + stream] !=
					fused_identity_inplace.row2_packed[q][8 + stream] ||
			    !congruent(identity_row2q2_got.row2_packed[q][stream],
					identity_got.row2_packed[q][stream]) ||
			    !congruent(identity_row2q2_got.row2_packed[q][8 + stream],
					identity_got.row2_packed[q][8 + stream]) ||
			    !in_symmetric_bound(
					identity_row2q2_got.row2_packed[q][stream],
					5 * 3456) ||
			    !in_symmetric_bound(
					identity_row2q2_got.row2_packed[q][8 + stream],
					5 * 3456) ||
			    !in_symmetric_bound(identity_got.row2_packed[q][stream],
					5 * 3456) ||
			    !in_symmetric_bound(identity_got.row2_packed[q][8 + stream],
					5 * 3456)) {
				fprintf(stderr,
					"row2 identity stage2 failure Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
#endif
		}
	}
	return 0;
}

static int check_stage5_range(const int16_t input[GT_NTT_N])
{
	gt_frontend_scratch frontend;
	gt_stage2_scratch scratch;

	gt_ntt_avx2_frontend(&frontend, input);
	gt_ntt_avx2_stage12(&scratch, &frontend);
	gt_ntt_avx2_stage345(&scratch);
	for (unsigned q = 0; q < 32; q++) {
		for (unsigned lane = 0; lane < 16; lane++) {
			if (!in_symmetric_bound(scratch.row01[q][lane], 8 * 3456)) {
				fprintf(stderr, "row01 stage5 range failure Q=%u lane=%u\n",
					q, lane);
				return 1;
			}
		}
	}
	for (unsigned q = 0; q < 16; q++) {
		for (unsigned lane = 0; lane < 16; lane++) {
			if (!in_symmetric_bound(scratch.row2_packed[q][lane], 8 * 3456)) {
				fprintf(stderr, "row2 stage5 range failure Q=%u lane=%u\n",
					q, lane);
				return 1;
			}
		}
	}
	return 0;
}

#if defined(GT_HAVE_AVX2_ASM)
static void native_centered_to_soa(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N])
{
	for (unsigned group = 0; group < 4; group++) {
		for (unsigned branch = 0; branch < 2; branch++) {
			for (unsigned coefficient = 0; coefficient < 4; coefficient++) {
				for (unsigned lane = 0; lane < 16; lane++) {
					const unsigned k3 = lane / 8;
					const unsigned q_lane = lane % 8;
					const unsigned native_batch = 2 * group + branch;
					const unsigned soa_batch = 4 * k3 + group;

					out[64 * soa_batch + 16 * coefficient +
						8 * branch + q_lane] =
						in[64 * native_batch +
							16 * coefficient + lane];
				}
			}
		}
	}

	for (unsigned group = 0; group < 2; group++) {
		for (unsigned branch = 0; branch < 2; branch++) {
			for (unsigned coefficient = 0; coefficient < 4; coefficient++) {
				for (unsigned lane = 0; lane < 16; lane++) {
					const unsigned q_half = lane / 8;
					const unsigned q_lane = lane % 8;
					const unsigned native_batch =
						8 + 2 * group + branch;
					const unsigned soa_batch =
						8 + group + 2 * q_half;

					out[64 * soa_batch + 16 * coefficient +
						8 * branch + q_lane] =
						in[64 * native_batch +
							16 * coefficient + lane];
				}
			}
		}
	}
}

static int check_stage345_candidate_scratch(
	const gt_stage2_scratch *input, const char *label)
{
	gt_stage2_scratch oracle_scratch;
	int16_t oracle_rowbitrev[GT_NTT_N];
	int16_t oracle_soa[GT_NTT_N];
	int16_t got[7][GT_NTT_N] __attribute__((aligned(32)));
	int16_t native[GT_NTT_N] __attribute__((aligned(32)));
	int16_t native_soa[GT_NTT_N] __attribute__((aligned(32)));
	static const char *const names[7] = {
		"serial", "interleaved", "remapped", "resident", "queued-store",
		"centered", "centered-queued"
	};

	memcpy(&oracle_scratch, input, sizeof(oracle_scratch));
	gt_ntt_avx2_stage345(&oracle_scratch);
	gt_ntt_avx2_scatter(oracle_rowbitrev, &oracle_scratch);
	gt_ntt_rowbitrev_to_soa(oracle_soa, oracle_rowbitrev);

	gt_ntt_avx2_stage345_soa_asm(got[0], input);
	gt_ntt_avx2_stage345_soa_interleaved_asm(got[1], input);
	gt_ntt_avx2_stage345_soa_remapped_asm(got[2], input);
	gt_ntt_avx2_stage345_soa_resident_asm(got[3], input);
	gt_ntt_avx2_stage345_soa_queued_store_asm(got[4], input);
	gt_ntt_avx2_stage345_soa_centered_asm(got[5], input);
	gt_ntt_avx2_stage345_soa_centered_queued_store_asm(got[6], input);
	gt_ntt_avx2_stage345_native_centered_asm(native, input);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		native_soa[i] = INT16_MIN;
	}
	native_centered_to_soa(native_soa, native);

	for (unsigned candidate = 0; candidate < 7; candidate++) {
		for (unsigned i = 0; i < GT_NTT_N; i++) {
			if (!congruent(got[candidate][i], oracle_soa[i])) {
				fprintf(stderr,
					"stage345 boundary mismatch case=%s candidate=%s i=%u got=%d want=%d\n",
					label, names[candidate], i, got[candidate][i],
					oracle_soa[i]);
				return 1;
			}
			if (candidate < 5 &&
			    (got[candidate][i] < 0 || got[candidate][i] > GT_NTT_Q)) {
				fprintf(stderr,
					"stage345 boundary range failure case=%s candidate=%s i=%u value=%d\n",
					label, names[candidate], i, got[candidate][i]);
				return 1;
			}
			if (candidate >= 5 &&
			    (got[candidate][i] < -3080 || got[candidate][i] > 3079)) {
				fprintf(stderr,
					"stage345 centered range failure case=%s candidate=%s i=%u value=%d\n",
					label, names[candidate], i, got[candidate][i]);
				return 1;
			}
			if (candidate > 0 && candidate < 5 &&
			    got[candidate][i] != got[0][i]) {
				fprintf(stderr,
					"stage345 candidate exact mismatch case=%s candidate=%s i=%u got=%d serial=%d\n",
					label, names[candidate], i, got[candidate][i], got[0][i]);
				return 1;
			}
			if (candidate == 6 && got[candidate][i] != got[5][i]) {
				fprintf(stderr,
					"stage345 centered schedule mismatch case=%s i=%u serial=%d queued=%d\n",
					label, i, got[5][i], got[6][i]);
				return 1;
			}
		}
	}
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (native_soa[i] == INT16_MIN ||
		    native_soa[i] != got[5][i] ||
		    !congruent(native_soa[i], oracle_soa[i]) ||
		    native_soa[i] < -3080 || native_soa[i] > 3079) {
			fprintf(stderr,
				"stage345 native mapping failure case=%s i=%u native=%d centered=%d oracle=%d\n",
				label, i, native_soa[i], got[5][i], oracle_soa[i]);
			return 1;
		}
	}
	return 0;
}

static int check_stage345_candidate_boundaries(void)
{
	gt_stage2_scratch scratch;
	const int bound = 5 * (GT_NTT_Q - 1);
	const uint32_t saved_rng_state = rng_state;

	rng_state = UINT32_C(0x6a09e667);

	for (unsigned q = 0; q < 32; q++) {
		for (unsigned lane = 0; lane < 16; lane++) {
			const unsigned index = 16U * q + lane;

			scratch.row01[q][lane] =
				(int16_t)((index & 1U) != 0 ? bound : -bound);
		}
	}
	for (unsigned q = 0; q < 16; q++) {
		for (unsigned lane = 0; lane < 16; lane++) {
			const unsigned index = 512U + 16U * q + lane;

			scratch.row2_packed[q][lane] =
				(int16_t)((index & 1U) != 0 ? bound : -bound);
		}
	}
	if (check_stage345_candidate_scratch(&scratch,
		"alternating-stage2-bound") != 0) {
		rng_state = saved_rng_state;
		return 1;
	}

	for (unsigned round = 0; round < 100; round++) {
		char label[40];

		for (unsigned q = 0; q < 32; q++) {
			for (unsigned lane = 0; lane < 16; lane++) {
				scratch.row01[q][lane] = (int16_t)(
					(int)(next_u32() % (unsigned)(2 * bound + 1)) - bound);
			}
		}
		for (unsigned q = 0; q < 16; q++) {
			for (unsigned lane = 0; lane < 16; lane++) {
				scratch.row2_packed[q][lane] = (int16_t)(
					(int)(next_u32() % (unsigned)(2 * bound + 1)) - bound);
			}
		}
		(void)snprintf(label, sizeof(label),
			"random-stage2-bound-%u", round);
		if (check_stage345_candidate_scratch(&scratch, label) != 0) {
			rng_state = saved_rng_state;
			return 1;
		}
	}
	rng_state = saved_rng_state;
	return 0;
}
#endif

static int check_soa_mapping(void)
{
	int16_t input[GT_NTT_N];
	int16_t soa[GT_NTT_N];
	int16_t roundtrip[GT_NTT_N];

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		input[i] = (int16_t)((int)i - GT_NTT_N / 2);
	}
	gt_ntt_rowbitrev_to_soa(soa, input);
	gt_ntt_soa_to_rowbitrev(roundtrip, soa);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (roundtrip[i] != input[i]) {
			fprintf(stderr, "SoA mapping round-trip mismatch i=%u\n", i);
			return 1;
		}
	}
	return 0;
}

static int16_t factor_qinv_ref(int16_t factor)
{
	return (int16_t)(uint16_t)((uint32_t)(uint16_t)factor * QINV);
}

static int check_soa_lambda_table(void)
{
	for (unsigned k3 = 0; k3 < 3; k3++) {
		for (unsigned q = 0; q < 32; q++) {
			const unsigned block = (32U * k3 + 3U * q) % 96U;
			const unsigned batch = 4U * k3 + q / 8U;

			for (unsigned branch = 0; branch < 2; branch++) {
				const unsigned lane = 8U * branch + q % 8U;
				const unsigned native_batch = k3 < 2
					? 2U * (q / 8U) + branch
					: 8U + 2U * ((q % 16U) / 8U) + branch;
				const unsigned native_lane = k3 < 2
					? 8U * k3 + q % 8U
					: 8U * (q / 16U) + q % 8U;
				const int16_t want =
					gt_rowbitrev_lambda[branch][block];

				if (gt_soa_lambda[batch][lane] != want ||
				    gt_soa_lambda_qinv[batch][lane] !=
					factor_qinv_ref(want) ||
				    gt_native_lambda[native_batch][native_lane] != want ||
				    gt_native_lambda_qinv[native_batch][native_lane] !=
					factor_qinv_ref(want)) {
					fprintf(stderr,
						"SoA/native lambda mismatch k3=%u Q=%u branch=%u\n",
						k3, q, branch);
					return 1;
				}
			}
		}
	}
	return 0;
}

static void basemul_rowbitrev_reference(int16_t out[GT_NTT_N],
	const int16_t a[GT_NTT_N], const int16_t b[GT_NTT_N])
{
	for (unsigned branch = 0; branch < 2; branch++) {
		for (unsigned block = 0; block < 96; block++) {
			const unsigned offset = 384U * branch + 4U * block;

			basemul(out + offset, a + offset, b + offset,
				gt_rowbitrev_lambda[branch][block]);
		}
	}
}

static void forward_soa(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N])
{
#if defined(GT_HAVE_AVX2_ASM)
	gt_ntt_avx2_asm_soa(out, in);
#else
	int16_t rowbitrev[GT_NTT_N];

	gt_ntt_avx2(rowbitrev, in);
	gt_ntt_rowbitrev_to_soa(out, rowbitrev);
#endif
}

static void schoolbook_mul(int16_t out[GT_NTT_N],
	const int16_t a[GT_NTT_N], const int16_t b[GT_NTT_N])
{
	int64_t temporary[2 * GT_NTT_N - 1] = {0};

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		for (unsigned j = 0; j < GT_NTT_N; j++) {
			temporary[i + j] += (int64_t)a[i] * b[j];
		}
	}
	/* X^768 = X^384 - 1. */
	for (int i = 2 * GT_NTT_N - 2; i >= GT_NTT_N; i--) {
		const int64_t value = temporary[i];

		temporary[i - GT_NTT_N / 2] += value;
		temporary[i - GT_NTT_N] -= value;
	}
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		out[i] = centered_i64(temporary[i]);
	}
}

#if defined(GT_HAVE_AVX2_ASM)
static int check_invntt_ntt32_asm_case(const int16_t input[GT_NTT_N],
	const char *label)
{
	int16_t want[GT_NTT_N] __attribute__((aligned(32)));
	int16_t got[GT_NTT_N] __attribute__((aligned(32)));

	gt_invntt_soa_ntt32_intrinsic(want, input);
	gt_invntt_soa_ntt32_asm(got, input);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (got[i] != want[i]) {
			fprintf(stderr,
				"inverse NTT32 ASM boundary mismatch case=%s i=%u got=%d want=%d\n",
				label, i, got[i], want[i]);
			return 1;
		}
		if (got[i] < 0 || got[i] > GT_NTT_Q) {
			fprintf(stderr,
				"inverse NTT32 ASM range failure case=%s i=%u value=%d\n",
				label, i, got[i]);
			return 1;
		}
	}
	return 0;
}

static int check_invntt_dft3_asm_rows(const int16_t rows[GT_NTT_N],
	const char *label)
{
	int16_t want[GT_NTT_N] __attribute__((aligned(32)));
	int16_t got[GT_NTT_N] __attribute__((aligned(32)));

	memcpy(want, rows, sizeof(want));
	memcpy(got, rows, sizeof(got));
	gt_invntt_soa_dft3_intrinsic(want);
	gt_invntt_soa_dft3_asm(got);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (got[i] != want[i]) {
			fprintf(stderr,
				"inverse DFT3 ASM boundary mismatch case=%s i=%u got=%d want=%d\n",
				label, i, got[i], want[i]);
			return 1;
		}
		if (got[i] < 0 || got[i] > GT_NTT_Q) {
			fprintf(stderr,
				"inverse DFT3 ASM range failure case=%s i=%u value=%d\n",
				label, i, got[i]);
			return 1;
		}
	}
	return 0;
}

static int check_invntt_dft3_asm_case(const int16_t input[GT_NTT_N],
	const char *label)
{
	int16_t rows[GT_NTT_N] __attribute__((aligned(32)));

	/* Build a valid [0,q] inverse-NTT32 scratch boundary first. */
	gt_invntt_soa_ntt32_intrinsic(rows, input);
	return check_invntt_dft3_asm_rows(rows, label);
}

static int check_invntt_postprocess_asm_rows(
	const int16_t rows[GT_NTT_N], const char *label)
{
	int16_t want[GT_NTT_N];
	int16_t got[GT_NTT_N];

	gt_invntt_soa_postprocess_intrinsic(want, rows);
	gt_invntt_soa_postprocess_asm(got, rows);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (got[i] != want[i]) {
			fprintf(stderr,
				"inverse postprocess ASM mismatch case=%s i=%u got=%d want=%d\n",
				label, i, got[i], want[i]);
			return 1;
		}
		if (!in_symmetric_bound(got[i], GT_NTT_Q - 1)) {
			fprintf(stderr,
				"inverse postprocess ASM range failure case=%s i=%u value=%d\n",
				label, i, got[i]);
			return 1;
		}
	}
	return 0;
}

static int check_invntt_postprocess_asm_case(
	const int16_t input[GT_NTT_N], const char *label)
{
	int16_t rows[GT_NTT_N] __attribute__((aligned(32)));

	gt_invntt_soa_ntt32_intrinsic(rows, input);
	gt_invntt_soa_dft3_intrinsic(rows);
	return check_invntt_postprocess_asm_rows(rows, label);
}
#endif

static int check_inverse_soa_case(const int16_t input[GT_NTT_N],
	const char *label)
{
	int16_t rowbitrev[GT_NTT_N];
	int16_t want[GT_NTT_N];
	int16_t got[GT_NTT_N];
	int16_t inplace[GT_NTT_N];
#if defined(GT_HAVE_AVX2_ASM)
	int16_t hybrid[GT_NTT_N];
	int16_t hybrid_inplace[GT_NTT_N];
	int16_t dft3_hybrid[GT_NTT_N];
	int16_t dft3_hybrid_inplace[GT_NTT_N];
	int16_t postprocess_hybrid[GT_NTT_N];
	int16_t postprocess_hybrid_inplace[GT_NTT_N];
	int16_t fused[GT_NTT_N];
	int16_t fused_inplace[GT_NTT_N];
#endif

	gt_ntt_soa_to_rowbitrev(rowbitrev, input);
	invntt_gt_rowbitrevlayout_exact(want, rowbitrev);
	gt_invntt_soa_avx2(got, input);
	memcpy(inplace, input, sizeof(inplace));
	gt_invntt_soa_avx2(inplace, inplace);
#if defined(GT_HAVE_AVX2_ASM)
	gt_invntt_soa_avx2_hybrid(hybrid, input);
	memcpy(hybrid_inplace, input, sizeof(hybrid_inplace));
	gt_invntt_soa_avx2_hybrid(hybrid_inplace, hybrid_inplace);
	gt_invntt_soa_avx2_dft3_hybrid(dft3_hybrid, input);
	memcpy(dft3_hybrid_inplace, input, sizeof(dft3_hybrid_inplace));
	gt_invntt_soa_avx2_dft3_hybrid(dft3_hybrid_inplace,
		dft3_hybrid_inplace);
	gt_invntt_soa_avx2_postprocess_hybrid(postprocess_hybrid, input);
	memcpy(postprocess_hybrid_inplace, input,
		sizeof(postprocess_hybrid_inplace));
	gt_invntt_soa_avx2_postprocess_hybrid(postprocess_hybrid_inplace,
		postprocess_hybrid_inplace);
	gt_invntt_soa_avx2_fused_asm(fused, input);
	memcpy(fused_inplace, input, sizeof(fused_inplace));
	gt_invntt_soa_avx2_fused_asm(fused_inplace, fused_inplace);
#endif
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (!congruent(got[i], want[i]) || got[i] != inplace[i]) {
			fprintf(stderr,
				"SoA inverse mismatch case=%s i=%u got=%d want=%d inplace=%d\n",
				label, i, got[i], want[i], inplace[i]);
			return 1;
		}
		if (!in_symmetric_bound(got[i], GT_NTT_Q - 1)) {
			fprintf(stderr,
				"SoA inverse range failure case=%s i=%u value=%d\n",
				label, i, got[i]);
			return 1;
		}
#if defined(GT_HAVE_AVX2_ASM)
		if (hybrid[i] != got[i] || hybrid[i] != hybrid_inplace[i]) {
			fprintf(stderr,
				"hybrid inverse mismatch case=%s i=%u hybrid=%d intrinsic=%d inplace=%d\n",
				label, i, hybrid[i], got[i], hybrid_inplace[i]);
			return 1;
		}
		if (dft3_hybrid[i] != got[i] ||
		    dft3_hybrid[i] != dft3_hybrid_inplace[i]) {
			fprintf(stderr,
				"DFT3 hybrid inverse mismatch case=%s i=%u hybrid=%d intrinsic=%d inplace=%d\n",
				label, i, dft3_hybrid[i], got[i],
				dft3_hybrid_inplace[i]);
			return 1;
		}
		if (postprocess_hybrid[i] != got[i] ||
		    postprocess_hybrid[i] != postprocess_hybrid_inplace[i]) {
			fprintf(stderr,
				"postprocess hybrid inverse mismatch case=%s i=%u hybrid=%d intrinsic=%d inplace=%d\n",
				label, i, postprocess_hybrid[i], got[i],
				postprocess_hybrid_inplace[i]);
			return 1;
		}
		if (fused[i] != got[i] || fused[i] != fused_inplace[i]) {
			fprintf(stderr,
				"fused ASM inverse mismatch case=%s i=%u fused=%d intrinsic=%d inplace=%d\n",
				label, i, fused[i], got[i], fused_inplace[i]);
			return 1;
		}
#endif
	}
	return 0;
}

static int check_polymul_soa_case(const int16_t a[GT_NTT_N],
	const int16_t b[GT_NTT_N], const char *label)
{
	int16_t a_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t b_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t product_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t got[GT_NTT_N];
	int16_t want[GT_NTT_N];
#if defined(GT_HAVE_AVX2_ASM)
	int16_t hybrid[GT_NTT_N];
	int16_t dft3_hybrid[GT_NTT_N];
	int16_t postprocess_hybrid[GT_NTT_N];
	int16_t fused[GT_NTT_N];
#endif

	forward_soa(a_soa, a);
	forward_soa(b_soa, b);
	gt_basemul_soa_avx2(product_soa, a_soa, b_soa);
	gt_invntt_soa_avx2(got, product_soa);
#if defined(GT_HAVE_AVX2_ASM)
	gt_invntt_soa_avx2_hybrid(hybrid, product_soa);
	gt_invntt_soa_avx2_dft3_hybrid(dft3_hybrid, product_soa);
	gt_invntt_soa_avx2_postprocess_hybrid(postprocess_hybrid, product_soa);
	gt_invntt_soa_avx2_fused_asm(fused, product_soa);
#endif
	schoolbook_mul(want, a, b);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (!congruent(got[i], want[i])) {
			fprintf(stderr,
				"SoA polynomial multiplication mismatch case=%s i=%u got=%d want=%d\n",
				label, i, got[i], want[i]);
			return 1;
		}
#if defined(GT_HAVE_AVX2_ASM)
		if (hybrid[i] != got[i]) {
			fprintf(stderr,
				"hybrid polynomial multiplication mismatch case=%s i=%u hybrid=%d intrinsic=%d\n",
				label, i, hybrid[i], got[i]);
			return 1;
		}
		if (dft3_hybrid[i] != got[i]) {
			fprintf(stderr,
				"DFT3 hybrid polynomial multiplication mismatch case=%s i=%u hybrid=%d intrinsic=%d\n",
				label, i, dft3_hybrid[i], got[i]);
			return 1;
		}
		if (postprocess_hybrid[i] != got[i]) {
			fprintf(stderr,
				"postprocess hybrid polynomial multiplication mismatch case=%s i=%u hybrid=%d intrinsic=%d\n",
				label, i, postprocess_hybrid[i], got[i]);
			return 1;
		}
		if (fused[i] != got[i]) {
			fprintf(stderr,
				"fused ASM polynomial multiplication mismatch case=%s i=%u fused=%d intrinsic=%d\n",
				label, i, fused[i], got[i]);
			return 1;
		}
#endif
	}
	return 0;
}

static int check_basemul_soa_case(const int16_t a[GT_NTT_N],
	const int16_t b[GT_NTT_N], const char *label)
{
	int16_t a_rowbitrev[GT_NTT_N];
	int16_t b_rowbitrev[GT_NTT_N];
	int16_t want_rowbitrev[GT_NTT_N];
	int16_t want[GT_NTT_N];
	int16_t got[GT_NTT_N];
#if defined(GT_HAVE_AVX2_ASM)
	int16_t got_asm[GT_NTT_N];
#endif

	gt_ntt_soa_to_rowbitrev(a_rowbitrev, a);
	gt_ntt_soa_to_rowbitrev(b_rowbitrev, b);
	basemul_rowbitrev_reference(want_rowbitrev, a_rowbitrev, b_rowbitrev);
	gt_ntt_rowbitrev_to_soa(want, want_rowbitrev);
	gt_basemul_soa_avx2(got, a, b);
#if defined(GT_HAVE_AVX2_ASM)
	gt_basemul_soa_asm_avx2(got_asm, a, b);
#endif
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (!congruent(got[i], want[i])) {
			fprintf(stderr,
				"SoA basemul mismatch case=%s i=%u got=%d want=%d\n",
				label, i, got[i], want[i]);
			return 1;
		}
		if (!in_symmetric_bound(got[i], GT_NTT_Q - 1)) {
			fprintf(stderr,
				"SoA basemul range failure case=%s i=%u value=%d\n",
				label, i, got[i]);
			return 1;
		}
#if defined(GT_HAVE_AVX2_ASM)
		if (got_asm[i] != got[i]) {
			fprintf(stderr,
				"SoA basemul ASM mismatch case=%s i=%u asm=%d intrinsic=%d\n",
				label, i, got_asm[i], got[i]);
			return 1;
		}
#endif
	}
	return 0;
}

#if defined(GT_HAVE_AVX2_ASM)
static int check_basemul_rminus1_case(const int16_t a[GT_NTT_N],
	const int16_t b[GT_NTT_N], const char *label)
{
	int16_t normal[GT_NTT_N] __attribute__((aligned(32)));
	int16_t rminus1[GT_NTT_N] __attribute__((aligned(32)));
	int16_t c0lazy[GT_NTT_N] __attribute__((aligned(32)));

	gt_basemul_soa_asm_avx2(normal, a, b);
	gt_basemul_soa_rminus1_asm_avx2(rminus1, a, b);
	gt_basemul_soa_rminus1_c0lazy_asm_avx2(c0lazy, a, b);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		/* Mont(product*R^-1, R^2) is the normal-domain product. */
		const int16_t converted = fqmul(rminus1[i], RSQ);
		const int16_t c0lazy_converted = fqmul(c0lazy[i], RSQ);
		const unsigned coefficient = (i % 64U) / 16U;
		const int c0lazy_bound = coefficient == 0 ? 2 * (GT_NTT_Q - 1) : 2359;

		if (!in_symmetric_bound(rminus1[i], 2359) ||
		    !congruent(converted, normal[i]) ||
		    !in_symmetric_bound(c0lazy[i], c0lazy_bound) ||
		    !congruent(c0lazy_converted, normal[i])) {
			fprintf(stderr,
				"SoA R^-1 basemul failure case=%s i=%u rminus1=%d converted=%d c0lazy=%d c0lazy-converted=%d normal=%d\n",
				label, i, rminus1[i], converted, c0lazy[i],
				c0lazy_converted, normal[i]);
			return 1;
		}
	}
	return 0;
}

static int check_rminus1_polymul_case(const int16_t a[GT_NTT_N],
	const int16_t b[GT_NTT_N], const char *label)
{
	int16_t a_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t b_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t product[GT_NTT_N] __attribute__((aligned(32)));
	int16_t got[GT_NTT_N] __attribute__((aligned(32)));
	int16_t want[GT_NTT_N];

	gt_ntt_avx2_asm_soa(a_soa, a);
	gt_ntt_avx2_asm_soa(b_soa, b);
	gt_basemul_soa_rminus1_asm_avx2(product, a_soa, b_soa);
	gt_invntt_soa_avx2_rminus1_postprocess_hybrid(got, product);
	schoolbook_mul(want, a, b);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (!in_symmetric_bound(product[i], 2359) ||
		    !congruent(got[i], want[i])) {
			fprintf(stderr,
				"R^-1 polymul failure case=%s i=%u product=%d got=%d want=%d\n",
				label, i, product[i], got[i], want[i]);
			return 1;
		}
	}
	gt_basemul_soa_rminus1_c0lazy_asm_avx2(product, a_soa, b_soa);
	gt_invntt_soa_avx2_rminus1_postprocess_hybrid(got, product);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		const unsigned coefficient = (i % 64U) / 16U;
		const int bound = coefficient == 0 ? 2 * (GT_NTT_Q - 1) : 2359;

		if (!in_symmetric_bound(product[i], bound) ||
		    !congruent(got[i], want[i])) {
			fprintf(stderr,
				"R^-1 c0-lazy polymul failure case=%s i=%u product=%d got=%d want=%d\n",
				label, i, product[i], got[i], want[i]);
			return 1;
		}
	}
	return 0;
}
#endif

static int check_forward_basemul_case(const int16_t a[GT_NTT_N],
	const int16_t b[GT_NTT_N], const char *label)
{
	int16_t a_rowbitrev[GT_NTT_N];
	int16_t b_rowbitrev[GT_NTT_N];
	int16_t want_rowbitrev[GT_NTT_N];
	int16_t want[GT_NTT_N];
	int16_t a_soa[GT_NTT_N];
	int16_t b_soa[GT_NTT_N];
	int16_t got[GT_NTT_N];

	ntt_gt_rowbitrevlayout(a_rowbitrev, a);
	ntt_gt_rowbitrevlayout(b_rowbitrev, b);
	basemul_rowbitrev_reference(want_rowbitrev, a_rowbitrev, b_rowbitrev);
	gt_ntt_rowbitrev_to_soa(want, want_rowbitrev);
#if defined(GT_HAVE_AVX2_ASM)
	gt_ntt_avx2_asm_soa(a_soa, a);
	gt_ntt_avx2_asm_soa(b_soa, b);
#else
	gt_ntt_avx2(a_rowbitrev, a);
	gt_ntt_avx2(b_rowbitrev, b);
	gt_ntt_rowbitrev_to_soa(a_soa, a_rowbitrev);
	gt_ntt_rowbitrev_to_soa(b_soa, b_rowbitrev);
#endif
	gt_basemul_soa_avx2(got, a_soa, b_soa);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (!congruent(got[i], want[i])) {
			fprintf(stderr,
				"forward+SoA basemul mismatch case=%s i=%u got=%d want=%d\n",
				label, i, got[i], want[i]);
			return 1;
		}
	}
	return 0;
}

static int check_full(const int16_t input[GT_NTT_N], const char *label)
{
	int16_t want[GT_NTT_N];
	int16_t got[GT_NTT_N];
	int16_t inplace[GT_NTT_N];
#if defined(GT_HAVE_AVX2_ASM)
	int16_t want_soa[GT_NTT_N];
	int16_t got_soa[GT_NTT_N];
	int16_t inplace_soa[GT_NTT_N];
	int16_t frontend_asm_soa[GT_NTT_N];
	int16_t frontend_asm_inplace_soa[GT_NTT_N];
	int16_t direct_asm_soa[GT_NTT_N];
	int16_t direct_asm_inplace_soa[GT_NTT_N];
	int16_t direct_interleaved_asm_soa[GT_NTT_N];
	int16_t direct_interleaved_asm_inplace_soa[GT_NTT_N];
	int16_t direct_queued_asm_soa[GT_NTT_N];
	int16_t direct_queued_asm_inplace_soa[GT_NTT_N];
	int16_t half_asm_soa[GT_NTT_N];
	int16_t half_asm_inplace_soa[GT_NTT_N];
	int16_t remapped_asm_soa[GT_NTT_N];
	int16_t remapped_asm_inplace_soa[GT_NTT_N];
	int16_t half_remapped_asm_soa[GT_NTT_N];
	int16_t half_remapped_asm_inplace_soa[GT_NTT_N];
	int16_t resident_asm_soa[GT_NTT_N];
	int16_t resident_asm_inplace_soa[GT_NTT_N];
	int16_t queued_store_asm_soa[GT_NTT_N];
	int16_t queued_store_asm_inplace_soa[GT_NTT_N];
#endif
	int16_t inverse_input[GT_NTT_N] __attribute__((aligned(32)));
	int16_t inverse_output[GT_NTT_N];
#if defined(GT_HAVE_AVX2_ASM)
	int16_t hybrid_inverse_output[GT_NTT_N];
	int16_t dft3_hybrid_inverse_output[GT_NTT_N];
	int16_t postprocess_hybrid_inverse_output[GT_NTT_N];
	int16_t fused_inverse_output[GT_NTT_N];
#endif

	ntt_gt_rowbitrevlayout(want, input);
	gt_ntt_avx2(got, input);
	memcpy(inplace, input, sizeof(inplace));
	gt_ntt_avx2(inplace, inplace);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (!congruent(got[i], want[i]) || got[i] != inplace[i]) {
			fprintf(stderr,
				"full mismatch case=%s i=%u got=%d want=%d inplace=%d\n",
				label, i, got[i], want[i], inplace[i]);
			return 1;
		}
		if (got[i] < -1729 || got[i] > 1729) {
			fprintf(stderr, "non-centered output case=%s i=%u value=%d\n",
				label, i, got[i]);
			return 1;
		}
	}

#if defined(GT_HAVE_AVX2_ASM)
	gt_ntt_rowbitrev_to_soa(want_soa, want);
	gt_ntt_avx2_asm_soa(got_soa, input);
	memcpy(inplace_soa, input, sizeof(inplace_soa));
	gt_ntt_avx2_asm_soa(inplace_soa, inplace_soa);
	gt_ntt_avx2_frontend_asm_soa(frontend_asm_soa, input);
	memcpy(frontend_asm_inplace_soa, input,
		sizeof(frontend_asm_inplace_soa));
	gt_ntt_avx2_frontend_asm_soa(frontend_asm_inplace_soa,
		frontend_asm_inplace_soa);
	gt_ntt_avx2_frontend_direct_asm_soa(direct_asm_soa, input);
	memcpy(direct_asm_inplace_soa, input,
		sizeof(direct_asm_inplace_soa));
	gt_ntt_avx2_frontend_direct_asm_soa(direct_asm_inplace_soa,
		direct_asm_inplace_soa);
	gt_ntt_avx2_frontend_direct_interleaved_asm_soa(
		direct_interleaved_asm_soa, input);
	memcpy(direct_interleaved_asm_inplace_soa, input,
		sizeof(direct_interleaved_asm_inplace_soa));
	gt_ntt_avx2_frontend_direct_interleaved_asm_soa(
		direct_interleaved_asm_inplace_soa,
		direct_interleaved_asm_inplace_soa);
	gt_ntt_avx2_frontend_direct_queued_store_asm_soa(
		direct_queued_asm_soa, input);
	memcpy(direct_queued_asm_inplace_soa, input,
		sizeof(direct_queued_asm_inplace_soa));
	gt_ntt_avx2_frontend_direct_queued_store_asm_soa(
		direct_queued_asm_inplace_soa, direct_queued_asm_inplace_soa);
	gt_ntt_avx2_frontend_half_asm_soa(half_asm_soa, input);
	memcpy(half_asm_inplace_soa, input, sizeof(half_asm_inplace_soa));
	gt_ntt_avx2_frontend_half_asm_soa(half_asm_inplace_soa,
		half_asm_inplace_soa);
	gt_ntt_avx2_frontend_remapped_asm_soa(remapped_asm_soa, input);
	memcpy(remapped_asm_inplace_soa, input,
		sizeof(remapped_asm_inplace_soa));
	gt_ntt_avx2_frontend_remapped_asm_soa(remapped_asm_inplace_soa,
		remapped_asm_inplace_soa);
	gt_ntt_avx2_frontend_half_remapped_asm_soa(half_remapped_asm_soa,
		input);
	memcpy(half_remapped_asm_inplace_soa, input,
		sizeof(half_remapped_asm_inplace_soa));
	gt_ntt_avx2_frontend_half_remapped_asm_soa(
		half_remapped_asm_inplace_soa, half_remapped_asm_inplace_soa);
	gt_ntt_avx2_frontend_resident_asm_soa(resident_asm_soa, input);
	memcpy(resident_asm_inplace_soa, input,
		sizeof(resident_asm_inplace_soa));
	gt_ntt_avx2_frontend_resident_asm_soa(resident_asm_inplace_soa,
		resident_asm_inplace_soa);
	gt_ntt_avx2_frontend_queued_store_asm_soa(queued_store_asm_soa, input);
	memcpy(queued_store_asm_inplace_soa, input,
		sizeof(queued_store_asm_inplace_soa));
	gt_ntt_avx2_frontend_queued_store_asm_soa(
		queued_store_asm_inplace_soa, queued_store_asm_inplace_soa);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (!congruent(got_soa[i], want_soa[i]) ||
		    got_soa[i] != inplace_soa[i] ||
		    frontend_asm_soa[i] != got_soa[i] ||
		    frontend_asm_inplace_soa[i] != got_soa[i] ||
		    direct_asm_soa[i] != got_soa[i] ||
		    direct_asm_inplace_soa[i] != got_soa[i] ||
		    direct_interleaved_asm_soa[i] != got_soa[i] ||
		    direct_interleaved_asm_inplace_soa[i] != got_soa[i] ||
		    direct_queued_asm_soa[i] != got_soa[i] ||
		    direct_queued_asm_inplace_soa[i] != got_soa[i] ||
		    half_asm_soa[i] != got_soa[i] ||
		    half_asm_inplace_soa[i] != got_soa[i] ||
		    remapped_asm_soa[i] != got_soa[i] ||
		    remapped_asm_inplace_soa[i] != got_soa[i] ||
		    half_remapped_asm_soa[i] != got_soa[i] ||
		    half_remapped_asm_inplace_soa[i] != got_soa[i] ||
		    resident_asm_soa[i] != got_soa[i] ||
		    resident_asm_inplace_soa[i] != got_soa[i] ||
		    queued_store_asm_soa[i] != got_soa[i] ||
		    queued_store_asm_inplace_soa[i] != got_soa[i]) {
			fprintf(stderr,
				"ASM SoA mismatch case=%s i=%u got=%d want=%d inplace=%d frontend-asm=%d frontend-asm-inplace=%d direct=%d direct-inplace=%d direct-interleaved=%d direct-interleaved-inplace=%d direct-queued=%d direct-queued-inplace=%d half=%d half-inplace=%d remapped=%d remapped-inplace=%d half-remapped=%d half-remapped-inplace=%d resident=%d resident-inplace=%d queued-store=%d queued-store-inplace=%d\n",
				label, i, got_soa[i], want_soa[i], inplace_soa[i],
				frontend_asm_soa[i], frontend_asm_inplace_soa[i],
				direct_asm_soa[i], direct_asm_inplace_soa[i],
				direct_interleaved_asm_soa[i],
				direct_interleaved_asm_inplace_soa[i],
				direct_queued_asm_soa[i], direct_queued_asm_inplace_soa[i],
				half_asm_soa[i],
				half_asm_inplace_soa[i], remapped_asm_soa[i],
				remapped_asm_inplace_soa[i], half_remapped_asm_soa[i],
				half_remapped_asm_inplace_soa[i], resident_asm_soa[i],
				resident_asm_inplace_soa[i], queued_store_asm_soa[i],
				queued_store_asm_inplace_soa[i]);
			return 1;
		}
		if (got_soa[i] < 0 || got_soa[i] > GT_NTT_Q) {
			fprintf(stderr,
				"ASM SoA range failure case=%s i=%u value=%d\n",
				label, i, got_soa[i]);
			return 1;
		}
	}
#endif
	forward_soa(inverse_input, input);
	gt_invntt_soa_avx2(inverse_output, inverse_input);
#if defined(GT_HAVE_AVX2_ASM)
	gt_invntt_soa_avx2_hybrid(hybrid_inverse_output, inverse_input);
	gt_invntt_soa_avx2_dft3_hybrid(dft3_hybrid_inverse_output,
		inverse_input);
	gt_invntt_soa_avx2_postprocess_hybrid(
		postprocess_hybrid_inverse_output, inverse_input);
	gt_invntt_soa_avx2_fused_asm(fused_inverse_output, inverse_input);
#endif
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (!congruent(inverse_output[i], input[i])) {
			fprintf(stderr,
				"SoA round-trip mismatch case=%s i=%u got=%d want=%d\n",
				label, i, inverse_output[i], input[i]);
			return 1;
		}
#if defined(GT_HAVE_AVX2_ASM)
		if (hybrid_inverse_output[i] != inverse_output[i]) {
			fprintf(stderr,
				"hybrid SoA round-trip mismatch case=%s i=%u hybrid=%d intrinsic=%d\n",
				label, i, hybrid_inverse_output[i], inverse_output[i]);
			return 1;
		}
		if (dft3_hybrid_inverse_output[i] != inverse_output[i]) {
			fprintf(stderr,
				"DFT3 hybrid SoA round-trip mismatch case=%s i=%u hybrid=%d intrinsic=%d\n",
				label, i, dft3_hybrid_inverse_output[i],
				inverse_output[i]);
			return 1;
		}
		if (postprocess_hybrid_inverse_output[i] != inverse_output[i]) {
			fprintf(stderr,
				"postprocess hybrid SoA round-trip mismatch case=%s i=%u hybrid=%d intrinsic=%d\n",
				label, i, postprocess_hybrid_inverse_output[i],
				inverse_output[i]);
			return 1;
		}
		if (fused_inverse_output[i] != inverse_output[i]) {
			fprintf(stderr,
				"fused ASM SoA round-trip mismatch case=%s i=%u fused=%d intrinsic=%d\n",
				label, i, fused_inverse_output[i], inverse_output[i]);
			return 1;
		}
#endif
	}
	return 0;
}

#if defined(GT_HAVE_AVX2_ASM)
static int check_forward_reducer_variants(
	const int16_t input[GT_NTT_N], const char *label)
{
	int16_t baseline[GT_NTT_N] __attribute__((aligned(32)));
	int16_t got[GT_NTT_N] __attribute__((aligned(32)));
	int16_t inplace[GT_NTT_N] __attribute__((aligned(32)));
	int16_t inverse[GT_NTT_N] __attribute__((aligned(32)));

	gt_ntt_avx2_frontend_asm_soa(baseline, input);
	for (unsigned candidate = 0;
	     candidate < sizeof(reducer_forward_candidates) /
			sizeof(reducer_forward_candidates[0]);
	     candidate++) {
		const struct gt_forward_candidate *variant =
			&reducer_forward_candidates[candidate];

		variant->run(got, input);
		memcpy(inplace, input, sizeof(inplace));
		variant->run(inplace, inplace);
		gt_invntt_soa_avx2_fused_asm(inverse, got);

		for (unsigned i = 0; i < GT_NTT_N; i++) {
			if (!congruent(got[i], baseline[i]) || got[i] != inplace[i]) {
				fprintf(stderr,
					"forward reducer mismatch case=%s candidate=%s i=%u got=%d baseline=%d inplace=%d\n",
					label, variant->name, i, got[i], baseline[i], inplace[i]);
				return 1;
			}
			if (variant->centered_output != 0) {
				if (got[i] < -3080 || got[i] > 3079) {
					fprintf(stderr,
						"forward centered range failure case=%s candidate=%s i=%u value=%d\n",
						label, variant->name, i, got[i]);
					return 1;
				}
			} else if (got[i] < 0 || got[i] > GT_NTT_Q) {
				fprintf(stderr,
					"forward canonical range failure case=%s candidate=%s i=%u value=%d\n",
					label, variant->name, i, got[i]);
				return 1;
			}
			if (!congruent(inverse[i], input[i])) {
				fprintf(stderr,
					"forward reducer round-trip failure case=%s candidate=%s i=%u got=%d want=%d\n",
					label, variant->name, i, inverse[i], input[i]);
				return 1;
			}
		}
	}
	return 0;
}

static int check_reducer_polymul_variants(
	const int16_t a[GT_NTT_N], const int16_t b[GT_NTT_N],
	const char *label)
{
	int16_t a_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t b_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t product[GT_NTT_N] __attribute__((aligned(32)));
	int16_t got[GT_NTT_N] __attribute__((aligned(32)));
	int16_t want[GT_NTT_N];

	schoolbook_mul(want, a, b);
	for (unsigned candidate = 0;
	     candidate < sizeof(reducer_forward_candidates) /
			sizeof(reducer_forward_candidates[0]);
	     candidate++) {
		const struct gt_forward_candidate *variant =
			&reducer_forward_candidates[candidate];

		variant->run(a_soa, a);
		variant->run(b_soa, b);
		gt_basemul_soa_avx2(product, a_soa, b_soa);
		gt_invntt_soa_avx2_fused_asm(got, product);
		for (unsigned i = 0; i < GT_NTT_N; i++) {
			if (!congruent(got[i], want[i])) {
				fprintf(stderr,
					"reducer polymul failure case=%s candidate=%s i=%u got=%d want=%d\n",
					label, variant->name, i, got[i], want[i]);
				return 1;
			}
		}
	}
	return 0;
}

static int check_forward_native_variants(
	const int16_t input[GT_NTT_N], const char *label)
{
	int16_t baseline[GT_NTT_N] __attribute__((aligned(32)));
	struct guarded_native_output native_guard;
	struct guarded_native_output native_inplace_guard;
	int16_t *const native = native_guard.values;
	int16_t *const native_inplace = native_inplace_guard.values;
	int16_t got_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t inplace_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t inverse_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t inverse[GT_NTT_N] __attribute__((aligned(32)));

	gt_ntt_avx2_frontend_identity_centered_queued_store_asm_soa(
		baseline, input);
	for (unsigned candidate = 0;
	     candidate < sizeof(native_forward_candidates) /
			sizeof(native_forward_candidates[0]);
	     candidate++) {
		const struct gt_forward_candidate *variant =
			&native_forward_candidates[candidate];
		const int lazy_output = variant->run ==
			gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm;

		initialize_native_guards(&native_guard);
		initialize_native_guards(&native_inplace_guard);
		variant->run(native, input);
		memcpy(native_inplace, input, sizeof(native_inplace_guard.values));
		variant->run(native_inplace, native_inplace);
		if (!native_guards_are_intact(&native_guard) ||
		    !native_guards_are_intact(&native_inplace_guard)) {
			fprintf(stderr,
				"native forward guard failure case=%s candidate=%s\n",
				label, variant->name);
			return 1;
		}
		native_centered_to_soa(got_soa, native);
		native_centered_to_soa(inplace_soa, native_inplace);
		memcpy(inverse_soa, got_soa, sizeof(inverse_soa));
		if (lazy_output) {
			for (unsigned i = 0; i < GT_NTT_N; i++) {
				inverse_soa[i] = centered(inverse_soa[i]);
			}
		}
		gt_invntt_soa_avx2_fused_asm(inverse, inverse_soa);

		for (unsigned i = 0; i < GT_NTT_N; i++) {
			const int output_mismatch =
				variant->run ==
				gt_ntt_avx2_forward_u2_fused_split_twist_native_centered_pipelined_asm
				|| variant->run ==
				gt_ntt_avx2_forward_wide_fused_delayed_native_centered_pipelined_asm
				|| variant->run ==
				gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm
				|| variant->run ==
				gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm
				|| variant->run ==
				gt_ntt_avx2_forward_wide_fused_delayed_native_centered_contiguous_twiddles_pipelined_asm
				|| variant->run ==
				gt_ntt_avx2_forward_wide_fused_partial_n0_native_centered_pipelined_asm
				? (!congruent(got_soa[i], baseline[i]) ||
				   inplace_soa[i] != got_soa[i])
				: (got_soa[i] != baseline[i] ||
				   inplace_soa[i] != baseline[i]);

			if ((lazy_output
				? !in_symmetric_bound(native[i],
					GT_FORWARD_LAZY_BATCH_BOUND(i / 64U))
				: (native[i] < -3080 || native[i] > 3079)) ||
			    output_mismatch != 0) {
				fprintf(stderr,
					"native forward mismatch case=%s candidate=%s i=%u native=%d soa=%d inplace=%d baseline=%d\n",
					label, variant->name, i, native[i], got_soa[i],
					inplace_soa[i], baseline[i]);
				return 1;
			}
			if (!congruent(inverse[i], input[i])) {
				fprintf(stderr,
					"native forward round-trip failure case=%s candidate=%s i=%u got=%d want=%d\n",
					label, variant->name, i, inverse[i], input[i]);
				return 1;
			}
		}
	}
	return 0;
}

static int check_native_polymul_variants(
	const int16_t a[GT_NTT_N], const int16_t b[GT_NTT_N],
	const char *label)
{
	int16_t a_native[GT_NTT_N] __attribute__((aligned(32)));
	int16_t b_native[GT_NTT_N] __attribute__((aligned(32)));
	int16_t a_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t b_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t product[GT_NTT_N] __attribute__((aligned(32)));
	int16_t got[GT_NTT_N] __attribute__((aligned(32)));
	int16_t want[GT_NTT_N];

	schoolbook_mul(want, a, b);
	for (unsigned candidate = 0;
	     candidate < sizeof(native_forward_candidates) /
			sizeof(native_forward_candidates[0]);
	     candidate++) {
		const struct gt_forward_candidate *variant =
			&native_forward_candidates[candidate];

		/* The lazy forward has an intentionally asymmetric consumer below. */
		if (variant->run ==
		    gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm) {
			continue;
		}

		variant->run(a_native, a);
		variant->run(b_native, b);
		native_centered_to_soa(a_soa, a_native);
		native_centered_to_soa(b_soa, b_native);
		gt_basemul_soa_avx2(product, a_soa, b_soa);
		gt_invntt_soa_avx2_fused_asm(got, product);
		for (unsigned i = 0; i < GT_NTT_N; i++) {
			if (!congruent(got[i], want[i])) {
				fprintf(stderr,
					"native polymul failure case=%s candidate=%s i=%u got=%d want=%d\n",
					label, variant->name, i, got[i], want[i]);
				return 1;
			}
		}
	}
	return 0;
}

static int check_asymmetric_native_polymul(
	const int16_t a[GT_NTT_N], const int16_t b[GT_NTT_N],
	const char *label)
{
	int16_t centered_native[GT_NTT_N] __attribute__((aligned(32)));
	int16_t lazy_native[GT_NTT_N] __attribute__((aligned(32)));
	int16_t product_native[GT_NTT_N] __attribute__((aligned(32)));
#if defined(GT_HAVE_AVX2_ASM)
	int16_t product_native_asm[GT_NTT_N] __attribute__((aligned(32)));
	int16_t product_native_rminus1[GT_NTT_N] __attribute__((aligned(32)));
	int16_t product_native_rminus1_c0lazy[GT_NTT_N]
		__attribute__((aligned(32)));
#endif
	int16_t centered_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t lazy_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t product_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t product_soa_reference[GT_NTT_N] __attribute__((aligned(32)));
#if defined(GT_HAVE_AVX2_ASM)
	int16_t product_soa_rminus1[GT_NTT_N] __attribute__((aligned(32)));
#endif
	int16_t got[GT_NTT_N] __attribute__((aligned(32)));
#if defined(GT_HAVE_AVX2_ASM)
	int16_t got_rminus1[GT_NTT_N] __attribute__((aligned(32)));
	int16_t got_rminus1_c0lazy[GT_NTT_N] __attribute__((aligned(32)));
#endif
	int16_t want[GT_NTT_N];

	schoolbook_mul(want, a, b);
	for (unsigned orientation = 0; orientation < 2; orientation++) {
		const int16_t *const centered_input = orientation == 0 ? a : b;
		const int16_t *const lazy_input = orientation == 0 ? b : a;

		gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm(
			centered_native, centered_input, 1);
		gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm(
			lazy_native, lazy_input, 0);
		gt_basemul_native_avx2(product_native, centered_native, lazy_native);
#if defined(GT_HAVE_AVX2_ASM)
		gt_basemul_native_asm_avx2(
			product_native_asm, centered_native, lazy_native);
		gt_basemul_native_rminus1_asm_avx2(
			product_native_rminus1, centered_native, lazy_native);
		gt_basemul_native_rminus1_c0lazy_asm_avx2(
			product_native_rminus1_c0lazy, centered_native, lazy_native);
#endif

		native_centered_to_soa(centered_soa, centered_native);
		native_centered_to_soa(lazy_soa, lazy_native);
#if defined(GT_HAVE_AVX2_ASM)
		native_centered_to_soa(product_soa, product_native_asm);
#else
		native_centered_to_soa(product_soa, product_native);
#endif
		gt_basemul_soa_avx2(product_soa_reference, centered_soa, lazy_soa);
		gt_invntt_soa_avx2_fused_asm(got, product_soa);
#if defined(GT_HAVE_AVX2_ASM)
		native_centered_to_soa(product_soa_rminus1,
			product_native_rminus1);
		gt_invntt_soa_avx2_rminus1_postprocess_hybrid(
			got_rminus1, product_soa_rminus1);
		native_centered_to_soa(product_soa_rminus1,
			product_native_rminus1_c0lazy);
		gt_invntt_soa_avx2_rminus1_postprocess_hybrid(
			got_rminus1_c0lazy, product_soa_rminus1);
#endif

		for (unsigned i = 0; i < GT_NTT_N; i++) {
			if (!in_symmetric_bound(centered_native[i], 3080) ||
			    !in_symmetric_bound(lazy_native[i],
				GT_FORWARD_LAZY_BATCH_BOUND(i / 64U)) ||
			    !in_symmetric_bound(product_native[i], GT_NTT_Q - 1) ||
#if defined(GT_HAVE_AVX2_ASM)
			    product_native_asm[i] != product_native[i] ||
#endif
			    !congruent(product_soa[i], product_soa_reference[i]) ||
			    !congruent(got[i], want[i]) ||
#if defined(GT_HAVE_AVX2_ASM)
			    !in_symmetric_bound(product_native_rminus1[i], 2359) ||
			    !congruent(got_rminus1[i], want[i]) ||
			    !in_symmetric_bound(product_native_rminus1_c0lazy[i],
				((i % 64U) / 16U) == 0 ?
					2 * (GT_NTT_Q - 1) : 2359) ||
			    !congruent(got_rminus1_c0lazy[i], want[i]) ||
#endif
			    0) {
				fprintf(stderr,
					"asymmetric native polymul failure case=%s orientation=%u i=%u centered=%d lazy=%d product=%d reference=%d got=%d want=%d\n",
					label, orientation, i, centered_native[i],
					lazy_native[i], product_soa[i],
					product_soa_reference[i], got[i], want[i]);
				return 1;
			}
		}
	}
	return 0;
}
#endif

int main(void)
{
	int16_t input[GT_NTT_N];
	int16_t basemul_a[GT_NTT_N];
	int16_t basemul_b[GT_NTT_N];
#if defined(GT_HAVE_AVX2_ASM)
	int16_t dft3_boundary[GT_NTT_N] __attribute__((aligned(32)));
#endif
	static const int16_t basemul_boundaries[] = {
		0, 1, -1, 1728, -1728, 3456, -3456, 3457, -3457
	};

	if (check_montgomery() != 0 || check_barrett() != 0 ||
	    check_soa_mapping() != 0 || check_soa_lambda_table() != 0 ||
	    check_baseinv_center_l8() != 0 ||
	    check_native_baseinv_l3_boundaries() != 0 ||
	    check_native_baseinv_boundaries() != 0 ||
	    check_native_baseinv_random() != 0) {
		return 1;
	}
#if defined(GT_HAVE_AVX2_ASM)
	if (check_packed_barrett_asm() != 0 ||
	    check_packed_centered_asm() != 0 ||
	    check_stage345_candidate_boundaries() != 0) {
		return 1;
	}
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		static const int16_t boundaries[] = {0, 1, GT_NTT_Q - 1, GT_NTT_Q};
		const unsigned row = i / (GT_NTT_N / 3U);

		dft3_boundary[i] = boundaries[(5U * i + row) % 4U];
	}
	if (check_invntt_dft3_asm_rows(dft3_boundary,
		"inverse-dft3-direct-boundary") != 0 ||
	    check_invntt_postprocess_asm_rows(dft3_boundary,
		"inverse-postprocess-direct-boundary") != 0) {
		return 1;
	}
#endif

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		const unsigned count = sizeof(basemul_boundaries) /
			sizeof(basemul_boundaries[0]);

		basemul_a[i] = basemul_boundaries[i % count];
		basemul_b[i] = basemul_boundaries[(3U * i + 1U) % count];
	}
	if (check_basemul_soa_case(basemul_a, basemul_b, "boundary") != 0) {
		return 1;
	}
#if defined(GT_HAVE_AVX2_ASM)
	if (check_basemul_rminus1_case(
		basemul_a, basemul_b, "boundary") != 0) {
		return 1;
	}
#endif
	if (check_inverse_soa_case(basemul_a, "inverse-boundary") != 0) {
		return 1;
	}
#if defined(GT_HAVE_AVX2_ASM)
	if (check_invntt_ntt32_asm_case(basemul_a,
		"inverse-ntt32-boundary") != 0 ||
	    check_invntt_dft3_asm_case(basemul_a,
		"inverse-dft3-boundary") != 0 ||
	    check_invntt_postprocess_asm_case(basemul_a,
		"inverse-postprocess-boundary") != 0) {
		return 1;
	}
#endif
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (basemul_a[i] == GT_NTT_Q || basemul_a[i] == -GT_NTT_Q) {
			basemul_a[i] = 0;
		}
		if (basemul_b[i] == GT_NTT_Q || basemul_b[i] == -GT_NTT_Q) {
			basemul_b[i] = 0;
		}
	}
	if (check_forward_basemul_case(basemul_a, basemul_b,
		"forward-boundary") != 0) {
		return 1;
	}
	for (unsigned round = 0; round < 200; round++) {
		char label[32];

		for (unsigned i = 0; i < GT_NTT_N; i++) {
			basemul_a[i] =
				(int16_t)((int)(next_u32() % 6915U) - 3457);
			basemul_b[i] =
				(int16_t)((int)(next_u32() % 6915U) - 3457);
		}
		(void)snprintf(label, sizeof(label), "basemul-random-%u", round);
		if (check_basemul_soa_case(basemul_a, basemul_b, label) != 0) {
			return 1;
		}
#if defined(GT_HAVE_AVX2_ASM)
		if (check_basemul_rminus1_case(basemul_a, basemul_b, label) != 0) {
			return 1;
		}
#endif
		if (round < 100 && check_inverse_soa_case(basemul_a, label) != 0) {
			return 1;
		}
#if defined(GT_HAVE_AVX2_ASM)
		if (round < 100 &&
		    check_invntt_ntt32_asm_case(basemul_a, label) != 0) {
			return 1;
		}
		if (round < 100 &&
		    check_invntt_dft3_asm_case(basemul_a, label) != 0) {
			return 1;
		}
		if (round < 100 &&
		    check_invntt_postprocess_asm_case(basemul_a, label) != 0) {
			return 1;
		}
#endif
		if (round < 16) {
			for (unsigned i = 0; i < GT_NTT_N; i++) {
				if (basemul_a[i] == GT_NTT_Q ||
				    basemul_a[i] == -GT_NTT_Q) {
					basemul_a[i] = 0;
				}
				if (basemul_b[i] == GT_NTT_Q ||
				    basemul_b[i] == -GT_NTT_Q) {
					basemul_b[i] = 0;
				}
			}
			if (check_forward_basemul_case(
				basemul_a, basemul_b, label) != 0) {
				return 1;
			}
		}
	}

	memset(input, 0, sizeof(input));
	input[0] = 1;
	if (check_frontend(input) != 0 || check_stage2(input) != 0 ||
	    check_stage5_range(input) != 0 || check_full(input, "impulse") != 0
#if defined(GT_HAVE_AVX2_ASM)
	    || check_forward_reducer_variants(input, "impulse") != 0
	    || check_forward_native_variants(input, "impulse") != 0
	    || check_native_forward_baseinv(input, "impulse") != 0
#endif
	    ) {
		return 1;
	}

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		input[i] = (i & 1U) != 0 ? 3456 : -3456;
	}
	if (check_frontend(input) != 0 || check_stage2(input) != 0 ||
	    check_stage5_range(input) != 0 || check_full(input, "boundary") != 0
#if defined(GT_HAVE_AVX2_ASM)
	    || check_forward_reducer_variants(input, "boundary") != 0
	    || check_forward_native_variants(input, "boundary") != 0
	    || check_native_forward_baseinv(input, "boundary") != 0
#endif
	    ) {
		return 1;
	}

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		input[i] = 3456;
	}
	if (check_frontend(input) != 0 || check_stage2(input) != 0 ||
	    check_stage5_range(input) != 0 || check_full(input, "all-max") != 0
#if defined(GT_HAVE_AVX2_ASM)
	    || check_forward_reducer_variants(input, "all-max") != 0
	    || check_forward_native_variants(input, "all-max") != 0
	    || check_native_forward_baseinv(input, "all-max") != 0
#endif
	    ) {
		return 1;
	}

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		input[i] = -3456;
	}
	if (check_frontend(input) != 0 || check_stage2(input) != 0 ||
	    check_stage5_range(input) != 0 || check_full(input, "all-min") != 0
#if defined(GT_HAVE_AVX2_ASM)
	    || check_forward_reducer_variants(input, "all-min") != 0
	    || check_forward_native_variants(input, "all-min") != 0
	    || check_native_forward_baseinv(input, "all-min") != 0
#endif
	    ) {
		return 1;
	}

	for (unsigned round = 0; round < 200; round++) {
		char label[32];

		for (unsigned i = 0; i < GT_NTT_N; i++) {
			input[i] = (int16_t)((int)(next_u32() % 6913U) - 3456);
		}
		(void)snprintf(label, sizeof(label), "random-%u", round);
		if (check_full(input, label) != 0) {
			return 1;
		}
#if defined(GT_HAVE_AVX2_ASM)
		if (round < 16 &&
		    (check_forward_reducer_variants(input, label) != 0 ||
		     check_forward_native_variants(input, label) != 0 ||
		     check_native_forward_baseinv(input, label) != 0)) {
			return 1;
		}
#endif
		if (round < 8 && (check_frontend(input) != 0 ||
		    check_stage2(input) != 0 || check_stage5_range(input) != 0)) {
			return 1;
		}
	}

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		basemul_a[i] = (i & 1U) != 0 ? 3456 : -3456;
		basemul_b[i] = i % 3U == 0 ? 3456 : (i % 3U == 1 ? -3456 : 0);
	}
	if (check_polymul_soa_case(basemul_a, basemul_b,
		"polymul-boundary") != 0
#if defined(GT_HAVE_AVX2_ASM)
	    || check_rminus1_polymul_case(
			basemul_a, basemul_b, "polymul-boundary") != 0
	    || check_reducer_polymul_variants(
			basemul_a, basemul_b, "polymul-boundary") != 0
	    || check_native_polymul_variants(
			basemul_a, basemul_b, "polymul-boundary") != 0
	    || check_asymmetric_native_polymul(
			basemul_a, basemul_b, "polymul-boundary") != 0
#endif
	    ) {
		return 1;
	}

	for (unsigned round = 0; round < 16; round++) {
		char label[32];

		for (unsigned i = 0; i < GT_NTT_N; i++) {
			basemul_a[i] = (int16_t)((int)(next_u32() % 3U) - 1);
			basemul_b[i] = (int16_t)((int)(next_u32() % 3U) - 1);
		}
		(void)snprintf(label, sizeof(label), "polymul-random-%u", round);
		if (check_polymul_soa_case(basemul_a, basemul_b, label) != 0) {
			return 1;
		}
#if defined(GT_HAVE_AVX2_ASM)
		if (check_rminus1_polymul_case(
			basemul_a, basemul_b, label) != 0) {
			return 1;
		}
		if (check_reducer_polymul_variants(
			basemul_a, basemul_b, label) != 0 ||
		    check_native_polymul_variants(
			basemul_a, basemul_b, label) != 0 ||
		    check_asymmetric_native_polymul(
			basemul_a, basemul_b, label) != 0) {
			return 1;
		}
#endif
	}

	puts("GT AVX2 forward/basemul/baseinv/inverse: all differential, layout, failure, and polynomial-product tests passed");
	return 0;
}
