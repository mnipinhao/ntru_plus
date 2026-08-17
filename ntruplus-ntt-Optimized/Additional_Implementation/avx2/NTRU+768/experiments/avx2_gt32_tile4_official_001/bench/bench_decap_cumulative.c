#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <linux/perf_event.h>
#include <limits.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#include <x86intrin.h>

#include "api.h"
#include "kat/rng.h"
#include "poly.h"
#include "symmetric.h"
#include "util.h"

#include "tile4.h"
#include "tile4_kem_candidate.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define SAMPLES 20U
#define PMU_EVENTS 3U

enum checkpoint {
	CHECKPOINT_DECODE = 1,
	CHECKPOINT_FIRST_PRODUCT = 2,
	CHECKPOINT_RECOVERED_R = 3,
	CHECKPOINT_MIDDLE = 4,
	CHECKPOINT_REENCRYPT = 5,
	CHECKPOINT_RETURN = 6
};

static const char *const checkpoint_names[] = {
	"invalid", "C1_decode", "C2_first_product", "C3_recovered_r",
	"C4_middle_sotp", "C5_reencrypt_verify", "C6_return_cleanup"
};

typedef struct {
	int16_t c[WORDS];
	int16_t aux[WORDS];
	int16_t hinv[WORDS];
	int16_t m[WORDS];
	int16_t work[WORDS];
} gt32_scratch_t __attribute__((aligned(64)));

typedef struct {
	poly c;
	poly f;
	poly hinv;
	poly m;
	uint8_t recovered_r[NTRUPLUS_POLYBYTES];
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t hash_g_out[HASH_G_OUTBYTES];
	uint8_t hash_h_out[HASH_H_OUTBYTES];
	uint8_t check[NTRUPLUS_POLYBYTES];
	uint8_t ss[NTRUPLUS_SSBYTES];
	int fail;
} checkpoint_snapshot_t;

typedef int (*prefix_fn)(unsigned, checkpoint_snapshot_t *);

typedef struct {
	const char *name;
	uint64_t config;
	int fd;
} pmu_event_t;

typedef struct {
	pmu_event_t events[PMU_EVENTS];
	int leader;
} pmu_group_t;

typedef struct {
	uint64_t value;
	uint64_t time_enabled;
	uint64_t time_running;
} pmu_read_t;

static uint8_t public_key[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t secret_key[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t ciphertext[CRYPTO_CIPHERTEXTBYTES] __attribute__((aligned(64)));
static uint8_t encapsulated_ss[CRYPTO_BYTES] __attribute__((aligned(64)));
static volatile uint64_t sink;

static uint64_t start_tsc(void)
{
	_mm_lfence();
	return __rdtsc();
}

static uint64_t stop_tsc(void)
{
	unsigned aux;
	const uint64_t result = __rdtscp(&aux);
	_mm_lfence();
	return result;
}

static int verify_bytes_local(const uint8_t *a, const uint8_t *b,
	size_t length)
{
	uint8_t acc = 0;
	for (size_t i = 0; i < length; i++)
		acc |= (uint8_t)(a[i] ^ b[i]);
	return (int)((-(uint64_t)acc) >> 63);
}

static void reset_rng(void)
{
	uint8_t entropy[48];
	for (size_t i = 0; i < sizeof entropy; i++)
		entropy[i] = (uint8_t)(29U + 17U * i);
	randombytes_init(entropy, NULL, 256);
}

static int finish_official_checkpoint(unsigned stop,
	checkpoint_snapshot_t *snapshot, const poly *c, const poly *f,
	const poly *hinv, const poly *m, const uint8_t *buf1,
	const uint8_t *buf2, const uint8_t *buf3, const uint8_t *msg,
	const uint8_t *ss, int fail)
{
	if (snapshot != NULL) {
		snapshot->fail = fail;
		if (stop == CHECKPOINT_DECODE) {
			snapshot->c = *c;
			snapshot->f = *f;
			snapshot->hinv = *hinv;
		} else if (stop == CHECKPOINT_FIRST_PRODUCT) {
			snapshot->m = *m;
		} else if (stop == CHECKPOINT_RECOVERED_R) {
			memcpy(snapshot->recovered_r, buf1, NTRUPLUS_POLYBYTES);
		} else if (stop == CHECKPOINT_MIDDLE) {
			memcpy(snapshot->msg, msg, sizeof snapshot->msg);
			memcpy(snapshot->hash_g_out, buf2,
				sizeof snapshot->hash_g_out);
			memcpy(snapshot->hash_h_out, buf3,
				sizeof snapshot->hash_h_out);
		} else if (stop == CHECKPOINT_REENCRYPT) {
			memcpy(snapshot->check, buf2, sizeof snapshot->check);
		} else if (stop == CHECKPOINT_RETURN) {
			memcpy(snapshot->ss, ss, sizeof snapshot->ss);
		}
	}
	if (stop == CHECKPOINT_DECODE)
		return (int)((uint16_t)c->coeffs[0] ^ (uint16_t)f->coeffs[0]
			^ (uint16_t)hinv->coeffs[0]);
	if (stop == CHECKPOINT_FIRST_PRODUCT)
		return (int)(uint16_t)m->coeffs[0];
	if (stop == CHECKPOINT_RECOVERED_R)
		return (int)buf1[0];
	if (stop == CHECKPOINT_MIDDLE)
		return (int)(msg[0] ^ buf2[0] ^ buf3[0]);
	if (stop == CHECKPOINT_REENCRYPT)
		return fail ^ (int)buf2[0];
	return fail ^ (int)ss[0];
}

__attribute__((noinline, noipa))
static int official_prefix(unsigned stop, checkpoint_snapshot_t *snapshot)
{
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t buf1[NTRUPLUS_POLYBYTES];
	uint8_t buf2[NTRUPLUS_POLYBYTES];
	uint8_t buf3[NTRUPLUS_POLYBYTES + NTRUPLUS_SYMBYTES];
	uint8_t ss[NTRUPLUS_SSBYTES];
	poly c;
	poly f;
	poly hinv;
	poly m;
	int fail = 1;

	if (poly_frombytes(&c, ciphertext) != 0
		|| poly_frombytes(&f, secret_key) != 0
		|| poly_frombytes(&hinv,
			secret_key + NTRUPLUS_POLYBYTES) != 0)
		goto cleanup;
	if (stop == CHECKPOINT_DECODE)
		return finish_official_checkpoint(stop, snapshot, &c, &f, &hinv,
			&m, buf1, buf2, buf3, msg, ss, fail);

	poly_basemul_scale(&m, &c, &f);
	poly_invntt_scale(&m);
	poly_crepmod3(&m);
	if (stop == CHECKPOINT_FIRST_PRODUCT)
		return finish_official_checkpoint(stop, snapshot, &c, &f, &hinv,
			&m, buf1, buf2, buf3, msg, ss, fail);

	f = m;
	poly_ntt(&f);
	poly_sub(&c, &c, &f);
	poly_basemul(&f, &c, &hinv);
	poly_tobytes(buf1, &f);
	if (stop == CHECKPOINT_RECOVERED_R)
		return finish_official_checkpoint(stop, snapshot, &c, &f, &hinv,
			&m, buf1, buf2, buf3, msg, ss, fail);

	hash_g(buf2, buf1);
	fail = poly_sotp_decode(msg, &m, buf2);
	memcpy(msg + NTRUPLUS_N / 8,
		secret_key + 2 * NTRUPLUS_POLYBYTES, NTRUPLUS_SYMBYTES);
	hash_h(buf3, msg);
	if (stop == CHECKPOINT_MIDDLE)
		return finish_official_checkpoint(stop, snapshot, &c, &f, &hinv,
			&m, buf1, buf2, buf3, msg, ss, fail);

	poly_cbd1(&f, buf3 + NTRUPLUS_SSBYTES);
	poly_ntt(&f);
	poly_tobytes(buf2, &f);
	fail |= verify_bytes_local(buf1, buf2, NTRUPLUS_POLYBYTES);
	if (stop == CHECKPOINT_REENCRYPT)
		return finish_official_checkpoint(stop, snapshot, &c, &f, &hinv,
			&m, buf1, buf2, buf3, msg, ss, fail);

	for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
		ss[i] = (uint8_t)(buf3[i] & (uint8_t)~(uint8_t)(-fail));

cleanup:
	secure_clear(msg, sizeof msg);
	secure_clear(buf1, sizeof buf1);
	secure_clear(buf2, sizeof buf2);
	secure_clear(buf3, sizeof buf3);
	secure_clear(&c, sizeof c);
	secure_clear(&f, sizeof f);
	secure_clear(&hinv, sizeof hinv);
	secure_clear(&m, sizeof m);
	return finish_official_checkpoint(CHECKPOINT_RETURN, snapshot, &c, &f,
		&hinv, &m, buf1, buf2, buf3, msg, ss, fail);
}

static int finish_gt_checkpoint(unsigned stop,
	checkpoint_snapshot_t *snapshot, const gt32_scratch_t *scratch,
	const uint8_t *buf1, const uint8_t *buf2, const uint8_t *buf3,
	const uint8_t *msg, const uint8_t *ss, int fail)
{
	if (snapshot != NULL) {
		snapshot->fail = fail;
		if (stop == CHECKPOINT_DECODE) {
			gt32_tile4_soa_to_official_words_grouped_asm(
				snapshot->c.coeffs, scratch->c);
			gt32_tile4_soa_to_official_words_grouped_asm(
				snapshot->f.coeffs, scratch->aux);
			gt32_tile4_soa_to_official_words_grouped_asm(
				snapshot->hinv.coeffs, scratch->hinv);
		} else if (stop == CHECKPOINT_FIRST_PRODUCT) {
			memcpy(snapshot->m.coeffs, scratch->m, sizeof scratch->m);
		} else if (stop == CHECKPOINT_RECOVERED_R) {
			memcpy(snapshot->recovered_r, buf1, NTRUPLUS_POLYBYTES);
		} else if (stop == CHECKPOINT_MIDDLE) {
			memcpy(snapshot->msg, msg, sizeof snapshot->msg);
			memcpy(snapshot->hash_g_out, buf2,
				sizeof snapshot->hash_g_out);
			memcpy(snapshot->hash_h_out, buf3,
				sizeof snapshot->hash_h_out);
		} else if (stop == CHECKPOINT_REENCRYPT) {
			memcpy(snapshot->check, buf2, sizeof snapshot->check);
		} else if (stop == CHECKPOINT_RETURN) {
			memcpy(snapshot->ss, ss, sizeof snapshot->ss);
		}
	}
	if (stop == CHECKPOINT_DECODE)
		return (int)((uint16_t)scratch->c[0] ^ (uint16_t)scratch->aux[0]
			^ (uint16_t)scratch->hinv[0]);
	if (stop == CHECKPOINT_FIRST_PRODUCT)
		return (int)(uint16_t)scratch->m[0];
	if (stop == CHECKPOINT_RECOVERED_R)
		return (int)buf1[0];
	if (stop == CHECKPOINT_MIDDLE)
		return (int)(msg[0] ^ buf2[0] ^ buf3[0]);
	if (stop == CHECKPOINT_REENCRYPT)
		return fail ^ (int)buf2[0];
	return fail ^ (int)ss[0];
}

__attribute__((noinline, noipa))
static int gt32_prefix(unsigned stop, checkpoint_snapshot_t *snapshot)
{
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t buf1[NTRUPLUS_POLYBYTES];
	uint8_t buf2[NTRUPLUS_POLYBYTES];
	uint8_t buf3[NTRUPLUS_POLYBYTES + NTRUPLUS_SYMBYTES];
	uint8_t ss[NTRUPLUS_SSBYTES];
	gt32_scratch_t scratch;
	int fail = 1;

	if (gt32_q24_decode3_soa_asm(scratch.c, scratch.aux, scratch.hinv,
		ciphertext, secret_key) != 0)
		goto cleanup;
	if (stop == CHECKPOINT_DECODE)
		return finish_gt_checkpoint(stop, snapshot, &scratch, buf1, buf2,
			buf3, msg, ss, fail);

	gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(scratch.m,
		scratch.c, scratch.aux);
	gt32_tile4_inverse_all_pair_asm(scratch.work, scratch.m);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(scratch.m,
		scratch.work);
	poly_crepmod3((poly *)(void *)scratch.m);
	if (stop == CHECKPOINT_FIRST_PRODUCT)
		return finish_gt_checkpoint(stop, snapshot, &scratch, buf1, buf2,
			buf3, msg, ss, fail);

	gt32_tile4_frontend_wide_raw_asm(scratch.aux, scratch.m);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch.work, scratch.aux);
	poly_sub((poly *)(void *)scratch.c,
		(const poly *)(const void *)scratch.c,
		(const poly *)(const void *)scratch.work);
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(scratch.aux,
		scratch.c, scratch.hinv);
	gt32_q24_encode_soa_asm(buf1, scratch.aux);
	if (stop == CHECKPOINT_RECOVERED_R)
		return finish_gt_checkpoint(stop, snapshot, &scratch, buf1, buf2,
			buf3, msg, ss, fail);

	hash_g(buf2, buf1);
	fail = poly_sotp_decode(msg, (const poly *)(const void *)scratch.m,
		buf2);
	memcpy(msg + NTRUPLUS_N / 8,
		secret_key + 2 * NTRUPLUS_POLYBYTES, NTRUPLUS_SYMBYTES);
	hash_h(buf3, msg);
	if (stop == CHECKPOINT_MIDDLE)
		return finish_gt_checkpoint(stop, snapshot, &scratch, buf1, buf2,
			buf3, msg, ss, fail);

	poly_cbd1((poly *)(void *)scratch.aux, buf3 + NTRUPLUS_SSBYTES);
	gt32_tile4_frontend_wide_raw_asm(scratch.c, scratch.aux);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch.hinv, scratch.c);
	gt32_q24_encode_soa_lazy10788_asm(buf2, scratch.hinv);
	fail |= verify_bytes_local(buf1, buf2, NTRUPLUS_POLYBYTES);
	if (stop == CHECKPOINT_REENCRYPT)
		return finish_gt_checkpoint(stop, snapshot, &scratch, buf1, buf2,
			buf3, msg, ss, fail);

	for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
		ss[i] = (uint8_t)(buf3[i] & (uint8_t)~(uint8_t)(-fail));

cleanup:
	secure_clear(msg, sizeof msg);
	secure_clear(buf1, sizeof buf1);
	secure_clear(buf2, sizeof buf2);
	secure_clear(buf3, sizeof buf3);
	secure_clear(&scratch, sizeof scratch);
	return finish_gt_checkpoint(CHECKPOINT_RETURN, snapshot, &scratch, buf1,
		buf2, buf3, msg, ss, fail);
}

/*
 * C1--C5 replay one real caller prefix at a time.  C6 deliberately calls the
 * production symbols so the final cumulative point includes the actual
 * selector, cleanup, and code-shape debt instead of pretending that the
 * benchmark copy is an exact full-caller substitute.
 */
__attribute__((noinline, noipa))
static int official_full_caller(unsigned stop, checkpoint_snapshot_t *snapshot)
{
	uint8_t ss[CRYPTO_BYTES];
	const int fail = crypto_kem_dec(ss, ciphertext, secret_key);

	(void)stop;
	(void)snapshot;
	return fail ^ (int)ss[0];
}

__attribute__((noinline, noipa))
static int gt32_full_caller(unsigned stop, checkpoint_snapshot_t *snapshot)
{
	uint8_t ss[CRYPTO_BYTES];
	const int fail = crypto_kem_dec_gt32_candidate(ss, ciphertext, secret_key);

	(void)stop;
	(void)snapshot;
	return fail ^ (int)ss[0];
}

static prefix_fn official_function(unsigned checkpoint)
{
	return checkpoint == CHECKPOINT_RETURN ? official_full_caller
		: official_prefix;
}

static prefix_fn gt32_function(unsigned checkpoint)
{
	return checkpoint == CHECKPOINT_RETURN ? gt32_full_caller : gt32_prefix;
}

static int checkpoint_equal(unsigned checkpoint,
	const checkpoint_snapshot_t *official,
	const checkpoint_snapshot_t *gt32)
{
	if (checkpoint == CHECKPOINT_DECODE)
		return memcmp(&official->c, &gt32->c, sizeof official->c) == 0
			&& memcmp(&official->f, &gt32->f, sizeof official->f) == 0
			&& memcmp(&official->hinv, &gt32->hinv,
				sizeof official->hinv) == 0;
	if (checkpoint == CHECKPOINT_FIRST_PRODUCT)
		return memcmp(&official->m, &gt32->m, sizeof official->m) == 0;
	if (checkpoint == CHECKPOINT_RECOVERED_R)
		return memcmp(official->recovered_r, gt32->recovered_r,
			sizeof official->recovered_r) == 0;
	if (checkpoint == CHECKPOINT_MIDDLE)
		return official->fail == gt32->fail
			&& memcmp(official->msg, gt32->msg,
				sizeof official->msg) == 0
			&& memcmp(official->hash_g_out, gt32->hash_g_out,
				sizeof official->hash_g_out) == 0
			&& memcmp(official->hash_h_out, gt32->hash_h_out,
				sizeof official->hash_h_out) == 0;
	if (checkpoint == CHECKPOINT_REENCRYPT)
		return official->fail == gt32->fail
			&& memcmp(official->check, gt32->check,
				sizeof official->check) == 0;
	return official->fail == gt32->fail
		&& memcmp(official->ss, gt32->ss, sizeof official->ss) == 0;
}

static int prepare_and_check(void)
{
	uint8_t official_ss[NTRUPLUS_SSBYTES];
	uint8_t gt32_ss[NTRUPLUS_SSBYTES];
	checkpoint_snapshot_t official;
	checkpoint_snapshot_t gt32;

	reset_rng();
	if (crypto_kem_keypair(public_key, secret_key) != 0
		|| crypto_kem_enc(ciphertext, encapsulated_ss, public_key) != 0) {
		fprintf(stderr, "deterministic keypair/encapsulation failed\n");
		return 0;
	}
	if (crypto_kem_dec(official_ss, ciphertext, secret_key) != 0
		|| crypto_kem_dec_gt32_candidate(gt32_ss, ciphertext, secret_key) != 0
		|| memcmp(official_ss, gt32_ss, sizeof official_ss) != 0
		|| memcmp(official_ss, encapsulated_ss, sizeof official_ss) != 0) {
		fprintf(stderr, "production decapsulation differential failed\n");
		return 0;
	}
	for (unsigned checkpoint = CHECKPOINT_DECODE;
		checkpoint <= CHECKPOINT_RETURN; checkpoint++) {
		memset(&official, 0, sizeof official);
		memset(&gt32, 0, sizeof gt32);
		(void)official_prefix(checkpoint, &official);
		(void)gt32_prefix(checkpoint, &gt32);
		if (!checkpoint_equal(checkpoint, &official, &gt32)) {
			fprintf(stderr, "checkpoint differential failed at %s\n",
				checkpoint_names[checkpoint]);
			if (checkpoint == CHECKPOINT_MIDDLE) {
				fprintf(stderr, "middle fail=%d/%d msg=%d g=%d h=%d\n",
					official.fail, gt32.fail,
					memcmp(official.msg, gt32.msg, sizeof official.msg),
					memcmp(official.hash_g_out, gt32.hash_g_out,
						sizeof official.hash_g_out),
					memcmp(official.hash_h_out, gt32.hash_h_out,
						sizeof official.hash_h_out));
			}
			return 0;
		}
	}
	return 1;
}

static double measure_tsc(prefix_fn function, unsigned checkpoint,
	unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		sink += (unsigned)function(checkpoint, NULL);
	const uint64_t end = stop_tsc();
	return (double)(end - begin) / iterations;
}

static int perf_event_open_local(struct perf_event_attr *attributes,
	int group_fd)
{
	const long result = syscall(SYS_perf_event_open, attributes, 0, -1,
		group_fd, 0UL);
	return result < 0 || result > INT_MAX ? -1 : (int)result;
}

static int pmu_open(pmu_group_t *group)
{
	static const char *const names[PMU_EVENTS] = {
		"cycles", "ref-cycles", "instructions"
	};
	static const uint64_t configs[PMU_EVENTS] = {
		PERF_COUNT_HW_CPU_CYCLES,
		PERF_COUNT_HW_REF_CPU_CYCLES,
		PERF_COUNT_HW_INSTRUCTIONS
	};

	memset(group, 0, sizeof *group);
	group->leader = -1;
	for (size_t i = 0; i < PMU_EVENTS; i++) {
		struct perf_event_attr attributes;
		memset(&attributes, 0, sizeof attributes);
		attributes.type = PERF_TYPE_HARDWARE;
		attributes.size = sizeof attributes;
		attributes.config = configs[i];
		attributes.disabled = i == 0U ? 1U : 0U;
		attributes.exclude_kernel = 1U;
		attributes.exclude_hv = 1U;
		attributes.read_format = PERF_FORMAT_TOTAL_TIME_ENABLED
			| PERF_FORMAT_TOTAL_TIME_RUNNING;
		group->events[i].name = names[i];
		group->events[i].config = configs[i];
		group->events[i].fd = perf_event_open_local(&attributes,
			group->leader);
		if (group->events[i].fd < 0)
			return 0;
		if (i == 0U)
			group->leader = group->events[i].fd;
	}
	return 1;
}

static void pmu_close(pmu_group_t *group)
{
	for (size_t i = 0; i < PMU_EVENTS; i++) {
		if (group->events[i].fd >= 0)
			(void)close(group->events[i].fd);
	}
}

static int measure_pmu(prefix_fn function, unsigned checkpoint,
	unsigned iterations, pmu_group_t *group, pmu_read_t reads[PMU_EVENTS],
	double *tsc)
{
	const uint64_t begin = start_tsc();
	if (ioctl(group->leader, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP) != 0
		|| ioctl(group->leader, PERF_EVENT_IOC_ENABLE,
			PERF_IOC_FLAG_GROUP) != 0)
		return 0;
	for (unsigned i = 0; i < iterations; i++)
		sink += (unsigned)function(checkpoint, NULL);
	if (ioctl(group->leader, PERF_EVENT_IOC_DISABLE,
		PERF_IOC_FLAG_GROUP) != 0)
		return 0;
	const uint64_t end = stop_tsc();
	*tsc = (double)(end - begin) / iterations;
	for (size_t i = 0; i < PMU_EVENTS; i++) {
		if (read(group->events[i].fd, &reads[i], sizeof reads[i])
			!= (ssize_t)sizeof reads[i])
			return 0;
	}
	return 1;
}

static void run_tsc(unsigned iterations)
{
	for (unsigned checkpoint = CHECKPOINT_DECODE;
		checkpoint <= CHECKPOINT_RETURN; checkpoint++) {
		(void)measure_tsc(official_function(checkpoint), checkpoint, 100U);
		(void)measure_tsc(gt32_function(checkpoint), checkpoint, 100U);
	}
	printf("META,correctness=all-checkpoints-byte-exact,scope=cumulative-"
		"decapsulation,mode=tsc,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		for (unsigned checkpoint = CHECKPOINT_DECODE;
			checkpoint <= CHECKPOINT_RETURN; checkpoint++) {
			double official;
			double gt32;
			if ((sample & 1U) == 0U) {
				official = measure_tsc(official_function(checkpoint),
					checkpoint, iterations);
				gt32 = measure_tsc(gt32_function(checkpoint),
					checkpoint, iterations);
			} else {
				gt32 = measure_tsc(gt32_function(checkpoint),
					checkpoint, iterations);
				official = measure_tsc(official_function(checkpoint),
					checkpoint, iterations);
			}
			printf("CUM_SAMPLE,%s,%u,%.6f,%.6f,%.6f\n",
				checkpoint_names[checkpoint], sample, official, gt32,
				gt32 - official);
		}
	}
}

static void print_pmu_sample(const char *variant, unsigned checkpoint,
	unsigned sample, const pmu_read_t reads[PMU_EVENTS],
	const pmu_group_t *group, unsigned iterations, double tsc)
{
	printf("PMU_TSC,%s,%u,%s,%.6f\n", checkpoint_names[checkpoint],
		sample, variant, tsc);
	for (size_t i = 0; i < PMU_EVENTS; i++) {
		const double scaled = reads[i].time_running == 0U ? 0.0
			: (double)reads[i].value * (double)reads[i].time_enabled
				/ (double)reads[i].time_running / iterations;
		printf("PMU_COUNT,%s,%u,%s,%s,%" PRIu64 ",%.9f,%" PRIu64
			",%" PRIu64 "\n", checkpoint_names[checkpoint], sample,
			variant, group->events[i].name, reads[i].value, scaled,
			reads[i].time_enabled, reads[i].time_running);
	}
}

static int run_pmu(unsigned iterations)
{
	pmu_group_t group;
	if (!pmu_open(&group)) {
		fprintf(stderr, "perf_event_open failed: %s\n", strerror(errno));
		pmu_close(&group);
		return 0;
	}
	printf("META,correctness=all-checkpoints-byte-exact,scope=cumulative-"
		"decapsulation,mode=pmu,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		for (unsigned checkpoint = CHECKPOINT_DECODE;
			checkpoint <= CHECKPOINT_RETURN; checkpoint++) {
			pmu_read_t official[PMU_EVENTS];
			pmu_read_t gt32[PMU_EVENTS];
			double official_tsc;
			double gt32_tsc;
			if ((sample & 1U) == 0U) {
				if (!measure_pmu(official_function(checkpoint), checkpoint,
					iterations,
					&group, official, &official_tsc)
					|| !measure_pmu(gt32_function(checkpoint), checkpoint,
						iterations,
						&group, gt32, &gt32_tsc))
					goto failure;
			} else {
				if (!measure_pmu(gt32_function(checkpoint), checkpoint,
					iterations,
					&group, gt32, &gt32_tsc)
					|| !measure_pmu(official_function(checkpoint), checkpoint,
						iterations,
						&group, official, &official_tsc))
					goto failure;
			}
			print_pmu_sample("official", checkpoint, sample, official,
				&group, iterations, official_tsc);
			print_pmu_sample("gt32", checkpoint, sample, gt32, &group,
				iterations, gt32_tsc);
		}
	}
	pmu_close(&group);
	return 1;

failure:
	fprintf(stderr, "PMU measurement failed: %s\n", strerror(errno));
	pmu_close(&group);
	return 0;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	const int pmu = argc > 2 && strcmp(argv[2], "pmu") == 0;
	cpu_set_t set;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof set, &set) != 0)
		perror("sched_setaffinity");
	if (!prepare_and_check()) {
		fprintf(stderr, "cumulative checkpoint differential failed\n");
		return 1;
	}
	if (iterations == 0U) {
		fprintf(stderr, "iterations must be nonzero\n");
		return 1;
	}
	if (pmu && !run_pmu(iterations))
		return 1;
	if (!pmu)
		run_tsc(iterations);
	printf("SINK,%" PRIu64 "\n", sink);
	return 0;
}
