#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <x86intrin.h>

#define WORDS 768
#define DET_WORDS 192
#define TRIALS 1000

extern int gt32_p_j1_attr_direct_avx2(int16_t *, const int16_t *);
extern void gt32_p_j1_attr_prepare(int16_t *, int16_t *, const int16_t *);
extern int gt32_p_j1_attr_batch_inverse(int16_t *);
extern int gt32_p_j1_batch_inverse_asm(int16_t *);
extern int gt32_p_j1_batch_inverse_tree_asm(int16_t *);
extern void gt32_p_j1_attr_finish(int16_t *, const int16_t *);
extern int gt32_p_j1_attr_direct_batch_asm(int16_t *, const int16_t *);
extern int gt32_p_j1_attr_direct_batch_tree_asm(int16_t *, const int16_t *);
extern int gt32_p_j1_attr_direct_split_c(int16_t *, const int16_t *);

static int16_t input[WORDS] __attribute__((aligned(64)));
static int16_t direct[WORDS] __attribute__((aligned(64)));
static int16_t presign_seed[WORDS] __attribute__((aligned(64)));
static int16_t presign_work[WORDS] __attribute__((aligned(64)));
static int16_t determinant_seed[DET_WORDS] __attribute__((aligned(64)));
static int16_t determinant_inverse[DET_WORDS] __attribute__((aligned(64)));
static int16_t determinant_work[DET_WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;
static uint32_t rng = 0x4b334154U;

static uint32_t random32(void)
{
	rng ^= rng << 13;
	rng ^= rng >> 17;
	rng ^= rng << 5;
	return rng;
}

static int center(int value)
{
	value %= 3457;
	if (value < 0)
		value += 3457;
	if (value > 1728)
		value -= 3457;
	return value;
}

static int same_mod_q(const int16_t *a, const int16_t *b)
{
	for (unsigned i = 0; i < WORDS; i++)
		if (center(a[i]) != center(b[i]))
			return 0;
	return 1;
}

static int same_det_mod_q(const int16_t *a, const int16_t *b)
{
	for (unsigned i = 0; i < DET_WORDS; i++)
		if (center(a[i]) != center(b[i]))
			return 0;
	return 1;
}

static int make_state(void)
{
	for (;;) {
		for (unsigned i = 0; i < WORDS; i++)
			input[i] = (int16_t)((int)(random32() % 4359U) - 2179);
		gt32_p_j1_attr_prepare(presign_seed, determinant_seed, input);
		memcpy(determinant_inverse, determinant_seed,
			sizeof determinant_inverse);
		if (gt32_p_j1_attr_batch_inverse(determinant_inverse) == 0)
			return 1;
	}
}

static int differential(void)
{
	int16_t staged[WORDS] __attribute__((aligned(64)));
	int16_t det[DET_WORDS] __attribute__((aligned(64)));
	int16_t det_asm[DET_WORDS] __attribute__((aligned(64)));
	int16_t det_tree[DET_WORDS] __attribute__((aligned(64)));
	int16_t direct_asm[WORDS] __attribute__((aligned(64)));
	int16_t direct_tree[WORDS] __attribute__((aligned(64)));

	memset(input, 0, sizeof input);
	gt32_p_j1_attr_prepare(staged, det, input);
	if (gt32_p_j1_attr_batch_inverse(det) == 0)
		return fprintf(stderr, "zero input accepted\n"), 0;
	memset(det_asm, 0, sizeof det_asm);
	if (gt32_p_j1_batch_inverse_asm(det_asm) == 0)
		return fprintf(stderr, "zero input accepted by asm\n"), 0;
	memset(det_tree, 0, sizeof det_tree);
	if (gt32_p_j1_batch_inverse_tree_asm(det_tree) == 0)
		return fprintf(stderr, "zero input accepted by tree asm\n"), 0;

	for (unsigned trial = 0; trial < TRIALS; trial++) {
		make_state();
		const int status = gt32_p_j1_attr_direct_avx2(direct, input);
		memcpy(staged, presign_seed, sizeof staged);
		memcpy(det, determinant_seed, sizeof det);
		memcpy(det_asm, determinant_seed, sizeof det_asm);
		memcpy(det_tree, determinant_seed, sizeof det_tree);
		const int split_status = gt32_p_j1_attr_batch_inverse(det);
		const int asm_status = gt32_p_j1_batch_inverse_asm(det_asm);
		const int tree_status = gt32_p_j1_batch_inverse_tree_asm(det_tree);
		if (status != split_status)
			return fprintf(stderr, "status mismatch trial=%u\n", trial), 0;
		if (split_status != asm_status)
			return fprintf(stderr, "asm status mismatch trial=%u\n", trial), 0;
		if (split_status != tree_status)
			return fprintf(stderr, "tree status mismatch trial=%u\n", trial), 0;
		if (status != 0)
			continue;
		if (memcmp(det, det_asm, sizeof det) != 0)
			return fprintf(stderr, "asm determinant mismatch trial=%u\n", trial), 0;
		if (!same_det_mod_q(det, det_tree))
			return fprintf(stderr, "tree determinant mismatch trial=%u\n", trial), 0;
		gt32_p_j1_attr_finish(staged, det);
		if (!same_mod_q(direct, staged))
			return fprintf(stderr, "output mismatch trial=%u\n", trial), 0;
		if (gt32_p_j1_attr_direct_batch_asm(direct_asm, input) != 0 ||
			!same_mod_q(direct, direct_asm))
			return fprintf(stderr, "asm full mismatch trial=%u\n", trial), 0;
		if (gt32_p_j1_attr_direct_batch_tree_asm(direct_tree, input) != 0 ||
			!same_mod_q(direct, direct_tree))
			return fprintf(stderr, "tree full mismatch trial=%u\n", trial), 0;
	}
	printf("correctness trials=%u pass\n", TRIALS);
	return 1;
}

__attribute__((noinline)) static void barrier_control(void)
{
	__asm__ volatile("" ::: "memory");
}

__attribute__((noinline)) static void prepare_candidate(void)
{
	gt32_p_j1_attr_prepare(presign_work, determinant_work, input);
}

__attribute__((noinline)) static void batch_control(void)
{
	memcpy(determinant_work, determinant_seed, sizeof determinant_work);
}

__attribute__((noinline)) static void batch_candidate(void)
{
	memcpy(determinant_work, determinant_seed, sizeof determinant_work);
	(void)gt32_p_j1_attr_batch_inverse(determinant_work);
}

__attribute__((noinline)) static void batch_asm(void)
{
	memcpy(determinant_work, determinant_seed, sizeof determinant_work);
	(void)gt32_p_j1_batch_inverse_asm(determinant_work);
}

__attribute__((noinline)) static void batch_tree(void)
{
	memcpy(determinant_work, determinant_seed, sizeof determinant_work);
	(void)gt32_p_j1_batch_inverse_tree_asm(determinant_work);
}

__attribute__((noinline)) static void finish_control(void)
{
	memcpy(presign_work, presign_seed, sizeof presign_work);
}

__attribute__((noinline)) static void finish_candidate(void)
{
	memcpy(presign_work, presign_seed, sizeof presign_work);
	gt32_p_j1_attr_finish(presign_work, determinant_inverse);
}

__attribute__((noinline)) static void full_candidate(void)
{
	(void)gt32_p_j1_attr_direct_avx2(direct, input);
}

__attribute__((noinline)) static void full_asm(void)
{
	(void)gt32_p_j1_attr_direct_batch_asm(direct, input);
}

__attribute__((noinline)) static void full_tree(void)
{
	(void)gt32_p_j1_attr_direct_batch_tree_asm(direct, input);
}

__attribute__((noinline)) static void full_split(void)
{
	(void)gt32_p_j1_attr_direct_split_c(direct, input);
}

typedef void (*region_fn)(void);

static void run(region_fn fn, unsigned iterations)
{
	for (unsigned i = 0; i < iterations; i++)
		fn();
	sink += (uint64_t)(uint16_t)presign_work[iterations % WORDS] +
		(uint64_t)(uint16_t)determinant_work[(iterations + 7U) % DET_WORDS] +
		(uint64_t)(uint16_t)direct[(iterations + 19U) % WORDS];
}

static uint64_t timed(region_fn fn, unsigned iterations)
{
	unsigned aux;
	_mm_lfence();
	const uint64_t begin = __rdtsc();
	run(fn, iterations);
	const uint64_t end = __rdtscp(&aux);
	_mm_lfence();
	return end - begin;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1 ?
		(unsigned)strtoul(argv[1], 0, 0) : 10000;
	const char *gate = argc > 2 ? argv[2] : "full";
	const char *backend = argc > 3 ? argv[3] : "candidate";
	const int skip_check = argc > 4 && !strcmp(argv[4], "nocheck");
	cpu_set_t set;
	region_fn fn = 0;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	(void)sched_setaffinity(0, sizeof set, &set);
	if (!skip_check && !differential())
		return 1;
	make_state();

	if (!strcmp(gate, "prepare"))
		fn = !strcmp(backend, "control") ? barrier_control : prepare_candidate;
	else if (!strcmp(gate, "batch"))
		fn = !strcmp(backend, "control") ? batch_control :
			(!strcmp(backend, "asm") ? batch_asm :
			(!strcmp(backend, "tree") ? batch_tree : batch_candidate));
	else if (!strcmp(gate, "finish"))
		fn = !strcmp(backend, "control") ? finish_control : finish_candidate;
	else if (!strcmp(gate, "full"))
		fn = !strcmp(backend, "control") ? barrier_control :
			(!strcmp(backend, "asm") ? full_asm :
			(!strcmp(backend, "tree") ? full_tree :
			(!strcmp(backend, "split") ? full_split : full_candidate)));
	if (fn == 0 || (strcmp(backend, "control") &&
		strcmp(backend, "candidate") && strcmp(backend, "asm") &&
		strcmp(backend, "tree") && strcmp(backend, "split")))
		return 2;

	run(fn, 1000);
	const uint64_t ticks = timed(fn, iterations);
	printf("BASEINV_ATTR,gate=%s,backend=%s,iterations=%u,"
		"tsc_per_call=%.6f,sink=%llu\n", gate, backend, iterations,
		(double)ticks / iterations, (unsigned long long)sink);
	return 0;
}
