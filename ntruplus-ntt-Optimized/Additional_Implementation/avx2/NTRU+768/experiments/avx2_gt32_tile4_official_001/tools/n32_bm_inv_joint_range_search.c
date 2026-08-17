/* Concrete-witness search for the N32 half-native R1-U -> inverse frontier.
 *
 * This is deliberately a bounded search, not a proof of safety.  It models
 * the exact signed-word Montgomery representatives of the row-conjugated
 * NTT32-first producer, the unsigned-low-word R1-U finalizer, typed IDFT3,
 * and the first raw inverse length-2 butterfly.  Every source coefficient is
 * constrained to [-3,4].
 */

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 768
#define Q 3457
#define QINV 12929
#define R_MOD_Q 3310
#define OMEGA96 675
#define OMEGA32 1784
#define INT16_MAX_VALUE 32767

typedef struct {
	int absolute;
	int value;
	int branch;
	int degree;
	int row;
	int q;
	int operation; /* 0=sum, 1=difference */
	int low;
	int high;
} score_t;

static uint64_t rng_state = UINT64_C(0x8a5cd789635d2dff);
static int16_t stage_factor[2][3][5][32];
static int16_t residual_factor[2][3];
static int16_t lambda_factor[2][3][32];

static uint32_t rng32(void)
{
	rng_state ^= rng_state << 7;
	rng_state ^= rng_state >> 9;
	return (uint32_t)rng_state;
}

static int centered_mod(int64_t value)
{
	value %= Q;
	if (value < 0)
		value += Q;
	if (value > Q / 2)
		value -= Q;
	return (int)value;
}

static int pow_mod(int base, unsigned exponent)
{
	int result = 1;
	while (exponent != 0U) {
		if ((exponent & 1U) != 0U)
			result = centered_mod((int64_t)result * base);
		base = centered_mod((int64_t)base * base);
		exponent >>= 1;
	}
	return result < 0 ? result + Q : result;
}

static int inverse_mod(int value)
{
	value %= Q;
	if (value < 0)
		value += Q;
	return pow_mod(value, Q - 2U);
}

static int16_t signed16(int64_t value)
{
	uint16_t word = (uint16_t)value;
	return (int16_t)word;
}

static int16_t factor_qinv(int factor)
{
	return signed16((int64_t)factor * QINV);
}

static int16_t montgomery_fixed(int value, int factor)
{
	const int16_t low = signed16((int64_t)(int16_t)value
		* factor_qinv(factor));
	const int high_factor = ((int32_t)(int16_t)value
		* (int32_t)(int16_t)factor) >> 16;
	const int high_q = ((int32_t)low * Q) >> 16;
	return signed16(high_factor - high_q);
}

static int16_t redc16_unsigned(int32_t value)
{
	const uint16_t m = (uint16_t)((uint32_t)value * (uint32_t)QINV);
	const int high_q = (int)(((uint32_t)m * (uint32_t)Q) >> 16);
	return signed16((value >> 16) - high_q);
}

static int center10(int value)
{
	const int quotient = (value * 10 + (1 << 14)) >> 15;
	return value - quotient * Q;
}

static unsigned bitreverse(unsigned value, unsigned bits)
{
	unsigned result = 0;
	for (unsigned bit = 0; bit < bits; bit++) {
		result = (result << 1) | (value & 1U);
		value >>= 1;
	}
	return result;
}

static unsigned forward_power(unsigned stage, unsigned group)
{
	if (stage == 1U)
		return 0;
	return bitreverse(group >> (6U - stage), stage - 1U)
		<< (5U - stage);
}

static void initialize_tables(void)
{
	const int branch_scale[2] = {2, 22};
	for (int branch = 0; branch < 2; branch++) {
		for (int n3 = 0; n3 < 3; n3++) {
			int residual[32];
			for (int q = 0; q < 32; q++) {
				const unsigned n = (unsigned)((64 * n3 + 33 * q) % 96);
				residual[q] = pow_mod(branch_scale[branch],
					(unsigned)((96 - n) % 96));
			}
			for (unsigned stage = 1; stage <= 5; stage++) {
				const unsigned distance = 32U >> stage;
				int next[32];
				memcpy(next, residual, sizeof(next));
				for (unsigned group = 0; group < 32;
				     group += 2U * distance) {
					const int zeta = pow_mod(OMEGA32,
						forward_power(stage, group));
					for (unsigned lane = 0; lane < distance; lane++) {
						const unsigned low = group + lane;
						const unsigned high = low + distance;
						const int normal = centered_mod((int64_t)zeta
							* residual[high]
							* inverse_mod(residual[low]));
						stage_factor[branch][n3][stage - 1U][low] =
							(int16_t)centered_mod((int64_t)normal * R_MOD_Q);
						next[low] = residual[low];
						next[high] = residual[low];
					}
				}
				memcpy(residual, next, sizeof(residual));
			}
			for (int q = 1; q < 32; q++)
				if (residual[q] != residual[0])
					exit(2);
			residual_factor[branch][n3] = (int16_t)centered_mod(
				(int64_t)residual[0] * R_MOD_Q);
		}
		for (int k3 = 0; k3 < 3; k3++) {
			for (int q = 0; q < 32; q++) {
				const unsigned logical = (unsigned)((32 * k3
					+ 3 * (int)bitreverse((unsigned)q, 5)) % 96);
				const int normal = centered_mod((int64_t)
					pow_mod(OMEGA96, logical)
					* inverse_mod(branch_scale[branch]));
				lambda_factor[branch][k3][q] = (int16_t)
					centered_mod((int64_t)normal * R_MOD_Q);
			}
		}
	}
}

static void n32_forward(int16_t out[2][3][32][4], const int16_t in[N])
{
	for (int branch = 0; branch < 2; branch++) {
		for (int degree = 0; degree < 4; degree++) {
			int16_t rows[3][32];
			for (int n3 = 0; n3 < 3; n3++) {
				for (int q = 0; q < 32; q++) {
					const int n = (64 * n3 + 33 * q) % 96;
					const int low = in[4 * n + degree];
					const int high = in[384 + 4 * n + degree];
					rows[n3][q] = (int16_t)(branch == 0
						? low - 722 * high : low + 723 * high);
				}
				for (unsigned stage = 1; stage <= 5; stage++) {
					const unsigned distance = 32U >> stage;
					for (unsigned group = 0; group < 32;
					     group += 2U * distance) {
						for (unsigned lane = 0; lane < distance; lane++) {
							const unsigned low = group + lane;
							const unsigned high = low + distance;
							const int16_t product = montgomery_fixed(
								rows[n3][high],
								stage_factor[branch][n3][stage - 1U][low]);
							const int value = rows[n3][low];
							rows[n3][low] = (int16_t)(value + product);
							rows[n3][high] = (int16_t)(value - product);
						}
					}
				}
				for (int q = 0; q < 32; q++)
					rows[n3][q] = montgomery_fixed(rows[n3][q],
						residual_factor[branch][n3]);
			}
			for (int q = 0; q < 32; q++) {
				const int x0 = rows[0][q];
				const int x1 = rows[1][q];
				const int x2 = rows[2][q];
				const int t = montgomery_fixed(x1 - x2, -886);
				out[branch][0][q][degree] = (int16_t)(x0 + x1 + x2);
				out[branch][1][q][degree] = (int16_t)(x0 - x2 + t);
				out[branch][2][q][degree] = (int16_t)(x0 - x1 - t);
			}
		}
	}
}

static void quartic_bm(int16_t out[4], const int16_t a[4],
	const int16_t b[4], int lambda)
{
	int16_t lambda_b[4];
	for (int degree = 0; degree < 4; degree++)
		lambda_b[degree] = montgomery_fixed(b[degree], lambda);
	for (int degree = 0; degree < 4; degree++) {
		int32_t accumulator = 0;
		for (int ai = 0; ai < 4; ai++) {
			const int bj = (degree - ai) & 3;
			accumulator += (int32_t)a[ai]
				* (ai <= degree ? b[bj] : lambda_b[bj]);
		}
		out[degree] = redc16_unsigned(accumulator);
	}
}

static score_t evaluate(const int16_t a[N], const int16_t b[N])
{
	int16_t af[2][3][32][4];
	int16_t bf[2][3][32][4];
	int16_t product[2][3][32][4];
	score_t best = {0};
	n32_forward(af, a);
	n32_forward(bf, b);
	for (int branch = 0; branch < 2; branch++)
		for (int k3 = 0; k3 < 3; k3++)
			for (int q = 0; q < 32; q++)
				quartic_bm(product[branch][k3][q],
					af[branch][k3][q], bf[branch][k3][q],
					lambda_factor[branch][k3][q]);

	for (int branch = 0; branch < 2; branch++) {
		for (int degree = 0; degree < 4; degree++) {
			int idft[3][32];
			for (int q = 0; q < 32; q++) {
				const int r0 = product[branch][0][q][degree];
				const int r1 = product[branch][1][q][degree];
				const int r2 = product[branch][2][q][degree];
				const int t = montgomery_fixed(r1 - r2, -886);
				idft[0][q] = r0 + center10(r1 + r2);
				idft[1][q] = r0 - r2 + t;
				idft[2][q] = r0 - r1 - t;
			}
			for (int row = 0; row < 3; row++) {
				for (int q = 0; q < 32; q += 2) {
					const int values[2] = {
						idft[row][q] + idft[row][q + 1],
						idft[row][q] - idft[row][q + 1],
					};
					for (int operation = 0; operation < 2; operation++) {
						const int absolute = values[operation] < 0
							? -values[operation] : values[operation];
						if (absolute > best.absolute) {
							best = (score_t){absolute, values[operation],
								branch, degree, row, q, operation,
								idft[row][q], idft[row][q + 1]};
						}
					}
				}
			}
		}
	}
	return best;
}

static void random_poly(int16_t out[N])
{
	for (int index = 0; index < N; index++)
		out[index] = (int16_t)((int)(rng32() & 7U) - 3);
}

static void copy_best(score_t score, const int16_t a[N], const int16_t b[N],
	score_t *best, int16_t best_a[N], int16_t best_b[N])
{
	if (score.absolute <= best->absolute)
		return;
	*best = score;
	memcpy(best_a, a, N * sizeof(*a));
	memcpy(best_b, b, N * sizeof(*b));
}

static void print_poly(FILE *file, const char *name, const int16_t poly[N])
{
	fprintf(file, "    \"%s\": [", name);
	for (int index = 0; index < N; index++)
		fprintf(file, "%s%d", index == 0 ? "" : ",", poly[index]);
	fputs("]", file);
}

int main(int argc, char **argv)
{
	const unsigned random_trials = argc > 1 ? (unsigned)strtoul(argv[1], NULL, 10) : 100000U;
	const unsigned restarts = argc > 2 ? (unsigned)strtoul(argv[2], NULL, 10) : 12U;
	const unsigned steps = argc > 3 ? (unsigned)strtoul(argv[3], NULL, 10) : 20000U;
	const char *output_path = argc > 4 ? argv[4] : "generated/tile4_n32_bm_inv_joint_range_search.json";
	int16_t a[N], b[N], best_a[N] = {0}, best_b[N] = {0};
	int16_t best_af[2][3][32][4], best_bf[2][3][32][4];
	int forward_abs[2][3] = {{0}};
	score_t best = {0};
	initialize_tables();

	/* Deterministic structured controls. */
	for (int av = -3; av <= 4; av++) {
		for (int bv = -3; bv <= 4; bv++) {
			for (int index = 0; index < N; index++) {
				a[index] = (int16_t)av;
				b[index] = (int16_t)bv;
			}
			copy_best(evaluate(a, b), a, b, &best, best_a, best_b);
		}
	}

	for (unsigned trial = 0; trial < random_trials; trial++) {
		random_poly(a);
		random_poly(b);
		copy_best(evaluate(a, b), a, b, &best, best_a, best_b);
	}

	/* Greedy concrete-witness search.  Each accepted mutation preserves the
	 * exact [-3,4] source contract.  Failure to overflow is not a proof. */
	for (unsigned restart = 0; restart < restarts; restart++) {
		random_poly(a);
		random_poly(b);
		score_t current = evaluate(a, b);
		copy_best(current, a, b, &best, best_a, best_b);
		for (unsigned step = 0; step < steps; step++) {
			int16_t *poly = (rng32() & 1U) != 0U ? a : b;
			const unsigned index = rng32() % N;
			const int16_t old = poly[index];
			int16_t replacement = (int16_t)((int)(rng32() & 7U) - 3);
			if (replacement == old)
				replacement = (int16_t)(replacement == 4 ? -3 : replacement + 1);
			poly[index] = replacement;
			const score_t candidate = evaluate(a, b);
			if (candidate.absolute >= current.absolute) {
				current = candidate;
				copy_best(current, a, b, &best, best_a, best_b);
			} else {
				poly[index] = old;
			}
		}
	}
	n32_forward(best_af, best_a);
	n32_forward(best_bf, best_b);
	for (int branch = 0; branch < 2; branch++)
		for (int k3 = 0; k3 < 3; k3++)
			for (int q = 0; q < 32; q++)
				for (int degree = 0; degree < 4; degree++) {
					const int av = best_af[branch][k3][q][degree] < 0
						? -best_af[branch][k3][q][degree]
						: best_af[branch][k3][q][degree];
					const int bv = best_bf[branch][k3][q][degree] < 0
						? -best_bf[branch][k3][q][degree]
						: best_bf[branch][k3][q][degree];
					if (av > forward_abs[branch][k3])
						forward_abs[branch][k3] = av;
					if (bv > forward_abs[branch][k3])
						forward_abs[branch][k3] = bv;
				}

	FILE *file = fopen(output_path, "w");
	if (file == NULL) {
		perror(output_path);
		return 1;
	}
	fprintf(file,
		"{\n"
		"  \"schema\": \"ntruplus768-n32-bm-inv-joint-range-search-v1\",\n"
		"  \"source_contract\": {\"coefficients\": [-3,4], \"count_per_operand\": 768},\n"
		"  \"producer\": \"bit-exact-row-conjugated-N32-Forward-representative-model\",\n"
		"  \"consumer_frontier\": \"typed-IDFT3-then-raw-inverse-length2\",\n"
		"  \"search\": {\"structured_trials\": 64, \"random_trials\": %u, "
		"\"greedy_restarts\": %u, \"greedy_steps_per_restart\": %u},\n"
		"  \"best_witness_forward_abs_bounds\": [[%d,%d,%d],[%d,%d,%d]],\n"
		"  \"best\": {\"absolute\": %d, \"value\": %d, \"branch\": %d, "
		"\"degree\": %d, \"row\": %d, \"q_pair\": [%d,%d], "
		"\"operation\": \"%s\", \"operands\": [%d,%d]},\n"
		"  \"signed_int16_overflow_witness_found\": %s,\n"
		"  \"bounded_search_is_safety_proof\": false,\n"
		"  \"witness_inputs\": {\n",
		random_trials, restarts, steps,
		forward_abs[0][0], forward_abs[0][1], forward_abs[0][2],
		forward_abs[1][0], forward_abs[1][1], forward_abs[1][2],
		best.absolute, best.value,
		best.branch, best.degree, best.row, best.q, best.q + 1,
		best.operation == 0 ? "sum" : "difference", best.low, best.high,
		best.absolute > INT16_MAX_VALUE ? "true" : "false");
	print_poly(file, "a", best_a);
	fputs(",\n", file);
	print_poly(file, "b", best_b);
	fputs("\n  }\n}\n", file);
	fclose(file);
	printf("best_abs=%d value=%d branch=%d degree=%d row=%d q=%d op=%s\n",
		best.absolute, best.value, best.branch, best.degree, best.row, best.q,
		best.operation == 0 ? "sum" : "difference");
	printf("overflow_witness=%s output=%s\n",
		best.absolute > INT16_MAX_VALUE ? "yes" : "no", output_path);
	return 0;
}
