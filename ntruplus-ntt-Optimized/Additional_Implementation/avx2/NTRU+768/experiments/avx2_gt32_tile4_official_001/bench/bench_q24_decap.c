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
#include <sys/personality.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#include <x86intrin.h>

#include "api.h"
#include "kat/rng.h"

#include "tile4.h"
#include "tile4_kem_candidate.h"

#define SAMPLES 20

typedef int (*decap_fn)(uint8_t *, const uint8_t *, const uint8_t *);
typedef int (*main_fn)(int, char **);
typedef int (*decode_soa_fn)(int16_t *, const uint8_t *);
typedef int (*decode3_soa_fn)(int16_t *, int16_t *, int16_t *,
	const uint8_t *, const uint8_t *);
typedef void (*basemul_fn)(int16_t *, const int16_t *, const int16_t *);
typedef void (*inverse_fn)(int16_t *, const int16_t *);

extern int gt32_q24_decode_soa_body_cage(int16_t *, const uint8_t *);

static uint8_t public_key[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t secret_key[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t ciphertext[CRYPTO_CIPHERTEXTBYTES] __attribute__((aligned(64)));
static uint8_t encapsulated_ss[CRYPTO_BYTES] __attribute__((aligned(64)));
static volatile uint64_t sink;

static int decap_official(uint8_t *, const uint8_t *, const uint8_t *);
static int decap_control(uint8_t *, const uint8_t *, const uint8_t *);
static int decap_unpack_only(uint8_t *, const uint8_t *, const uint8_t *);
static int decap_q24(uint8_t *, const uint8_t *, const uint8_t *);
static int decap_gtpack(uint8_t *, const uint8_t *, const uint8_t *);
static double measure(decap_fn, uint8_t *, unsigned);
#if defined(GT32_GLOBAL_PHYSICAL_KEM)
static int decap_global_inverse(uint8_t *, const uint8_t *, const uint8_t *);
static int decap_native_rcheck(uint8_t *, const uint8_t *, const uint8_t *);
#endif

typedef struct {
	uintptr_t start;
	uintptr_t file_offset;
	uintptr_t load_bias;
} text_mapping_t;

#define MAX_PMU_EVENTS 4

typedef struct {
	const char *name;
	uint32_t type;
	uint64_t config;
	uint64_t config1;
} pmu_event_spec_t;

typedef struct {
	const char *name;
	pmu_event_spec_t events[MAX_PMU_EVENTS];
	int fds[MAX_PMU_EVENTS];
	size_t count;
	uint64_t values[MAX_PMU_EVENTS];
	uint64_t time_enabled;
	uint64_t time_running;
	int error;
} pmu_group_t;

static uintptr_t function_pointer_bits(const void *representation, size_t size)
{
	uintptr_t result = 0;
	const size_t copy_size = size < sizeof result ? size : sizeof result;
	memcpy(&result, representation, copy_size);
	return result;
}

static text_mapping_t executable_text_mapping(void)
{
	char executable[PATH_MAX];
	char line[4096];
	text_mapping_t result = {0, 0, 0};
	const ssize_t length = readlink("/proc/self/exe", executable,
		sizeof executable - 1U);
	FILE *maps;

	if (length < 0)
		return result;
	executable[(size_t)length] = '\0';
	maps = fopen("/proc/self/maps", "r");
	if (maps == NULL)
		return result;
	while (fgets(line, sizeof line, maps) != NULL) {
		unsigned long start;
		unsigned long end;
		unsigned long offset;
		char permissions[5];
		char path[PATH_MAX];
		const int fields = sscanf(line, "%lx-%lx %4s %lx %*s %*s %s",
			&start, &end, permissions, &offset, path);
		(void)end;
		if (fields == 5 && strchr(permissions, 'x') != NULL
			&& strcmp(path, executable) == 0) {
			result.start = (uintptr_t)start;
			result.file_offset = (uintptr_t)offset;
			result.load_bias = (uintptr_t)(start - offset);
			break;
		}
	}
	(void)fclose(maps);
	return result;
}

static void print_virtual_addresses(main_fn main_pointer)
{
	const text_mapping_t mapping = executable_text_mapping();
	const int personality_result = personality(0xffffffffUL);
	const unsigned long process_personality = personality_result < 0
		? ULONG_MAX : (unsigned long)(unsigned int)personality_result;
	decap_fn official_pointer = decap_official;
	decap_fn control_pointer = decap_control;
	decap_fn q24_pointer = decap_q24;
	decap_fn promoted_candidate_pointer = crypto_kem_dec_gt32_candidate;
	decap_fn q24_candidate_pointer = crypto_kem_dec_gt32_q24_decode_candidate;
	decode_soa_fn q24_body_pointer = gt32_q24_decode_soa_body_cage;
	decode3_soa_fn q24_decode3_pointer = gt32_q24_decode3_soa_asm;
	basemul_fn b3_pointer =
		gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm;
	inverse_fn i1_pointer = gt32_tile4_inverse_all_pair_asm;
	inverse_fn t9_pointer =
		gt32_tile4_inverse_tail_t9_isolated_private_asm;

	printf("VA,text_map_start=0x%" PRIxPTR
		",text_map_offset=0x%" PRIxPTR
		",text_load_bias=0x%" PRIxPTR
		",main=0x%" PRIxPTR
		",decap_official=0x%" PRIxPTR
		",decap_control=0x%" PRIxPTR
		",decap_q24=0x%" PRIxPTR
		",decap_promoted_candidate=0x%" PRIxPTR
		",decap_q24_candidate=0x%" PRIxPTR
		",q24_body=0x%" PRIxPTR
		",q24_decode3=0x%" PRIxPTR
		",b3=0x%" PRIxPTR
		",i1=0x%" PRIxPTR
		",t9=0x%" PRIxPTR
		",personality=0x%lx,cpu=%d\n",
		mapping.start, mapping.file_offset, mapping.load_bias,
		function_pointer_bits(&main_pointer, sizeof main_pointer),
		function_pointer_bits(&official_pointer, sizeof official_pointer),
		function_pointer_bits(&control_pointer, sizeof control_pointer),
		function_pointer_bits(&q24_pointer, sizeof q24_pointer),
		function_pointer_bits(&promoted_candidate_pointer,
			sizeof promoted_candidate_pointer),
		function_pointer_bits(&q24_candidate_pointer,
			sizeof q24_candidate_pointer),
		function_pointer_bits(&q24_body_pointer, sizeof q24_body_pointer),
		function_pointer_bits(&q24_decode3_pointer,
			sizeof q24_decode3_pointer),
		function_pointer_bits(&b3_pointer, sizeof b3_pointer),
		function_pointer_bits(&i1_pointer, sizeof i1_pointer),
		function_pointer_bits(&t9_pointer, sizeof t9_pointer),
		process_personality, sched_getcpu());
}

static int read_pmu_type(const char *path, uint32_t *type)
{
	char text[32];
	char *end;
	unsigned long value;
	const int fd = open(path, O_RDONLY);
	ssize_t length;

	if (fd < 0)
		return -1;
	length = read(fd, text, sizeof text - 1U);
	(void)close(fd);
	if (length <= 0)
		return -1;
	text[(size_t)length] = '\0';
	errno = 0;
	value = strtoul(text, &end, 10);
	if (errno != 0 || end == text || value > UINT32_MAX)
		return -1;
	*type = (uint32_t)value;
	return 0;
}

static int perf_event_open_local(struct perf_event_attr *attributes,
	int group_fd)
{
	const long result = syscall(SYS_perf_event_open, attributes, 0, -1,
		group_fd, 0UL);
	return result < 0 || result > INT_MAX ? -1 : (int)result;
}

static int select_pmu_group(pmu_group_t *group)
{
	const char *requested = getenv("Q24_SELF_PMU");
	uint32_t cpu_core_type = 0;

	memset(group, 0, sizeof *group);
	for (size_t i = 0; i < MAX_PMU_EVENTS; i++)
		group->fds[i] = -1;
	if (requested == NULL || requested[0] == '\0') {
		group->name = "disabled";
		return 0;
	}
	group->name = requested;
	if (strcmp(requested, "core") == 0) {
		group->events[0] = (pmu_event_spec_t){"cycles",
			PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, 0};
		group->events[1] = (pmu_event_spec_t){"ref-cycles",
			PERF_TYPE_HARDWARE, PERF_COUNT_HW_REF_CPU_CYCLES, 0};
		group->events[2] = (pmu_event_spec_t){"instructions",
			PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, 0};
		group->count = 3;
		return 0;
	}
	if (strcmp(requested, "branches") == 0) {
		group->events[0] = (pmu_event_spec_t){"branches",
			PERF_TYPE_HARDWARE, PERF_COUNT_HW_BRANCH_INSTRUCTIONS, 0};
		group->events[1] = (pmu_event_spec_t){"branch-misses",
			PERF_TYPE_HARDWARE, PERF_COUNT_HW_BRANCH_MISSES, 0};
		group->count = 2;
		return 0;
	}
	if (read_pmu_type("/sys/bus/event_source/devices/cpu_core/type",
		&cpu_core_type) != 0) {
		group->error = errno != 0 ? errno : ENODEV;
		return -1;
	}
	if (strcmp(requested, "frontend") == 0) {
		/* perf-list names/configs for this CPU, all user-space only. */
		group->events[0] = (pmu_event_spec_t){"idq.dsb_uops",
			cpu_core_type, 0x879, 0};
		group->events[1] = (pmu_event_spec_t){"idq.mite_uops",
			cpu_core_type, 0x479, 0};
		group->events[2] = (pmu_event_spec_t){
			"idq_uops_not_delivered.core", cpu_core_type, 0x19c, 0};
		group->count = 3;
		return 0;
	}
	if (strcmp(requested, "memory") == 0) {
		/* perf-list encodings for this CPU's cpu_core PMU. */
		group->events[0] = (pmu_event_spec_t){"retired-loads",
			cpu_core_type, 0x81d0, 0};
		group->events[1] = (pmu_event_spec_t){"retired-stores",
			cpu_core_type, 0x82d0, 0};
		group->count = 2;
		return 0;
	}
	if (strcmp(requested, "fetch") == 0) {
		group->events[0] = (pmu_event_spec_t){"icache_data.stalls",
			cpu_core_type, 0x480, 0};
		group->events[1] = (pmu_event_spec_t){
			"itlb_misses.walk_completed", cpu_core_type, 0xe11, 0};
		group->count = 2;
		return 0;
	}
	group->error = EINVAL;
	return -1;
}

static int open_pmu_group(pmu_group_t *group)
{
	int leader = -1;

	if (select_pmu_group(group) != 0 || group->count == 0)
		return group->count == 0 ? 0 : -1;
	for (size_t i = 0; i < group->count; i++) {
		struct perf_event_attr attributes;
		memset(&attributes, 0, sizeof attributes);
		attributes.type = group->events[i].type;
		attributes.size = sizeof attributes;
		attributes.config = group->events[i].config;
		attributes.config1 = group->events[i].config1;
		attributes.disabled = i == 0 ? 1U : 0U;
		attributes.exclude_kernel = 1U;
		attributes.exclude_hv = 1U;
		if (i == 0)
			attributes.read_format = PERF_FORMAT_GROUP
				| PERF_FORMAT_TOTAL_TIME_ENABLED
				| PERF_FORMAT_TOTAL_TIME_RUNNING;
		group->fds[i] = perf_event_open_local(&attributes, leader);
		if (group->fds[i] < 0) {
			group->error = errno;
			return -1;
		}
		if (i == 0)
			leader = group->fds[i];
	}
	return 0;
}

static void close_pmu_group(pmu_group_t *group)
{
	for (size_t i = 0; i < group->count; i++) {
		if (group->fds[i] >= 0)
			(void)close(group->fds[i]);
		group->fds[i] = -1;
	}
}

static int start_pmu_group(pmu_group_t *group)
{
	if (group->count == 0 || group->fds[0] < 0)
		return 0;
	if (ioctl(group->fds[0], PERF_EVENT_IOC_RESET,
		PERF_IOC_FLAG_GROUP) != 0
		|| ioctl(group->fds[0], PERF_EVENT_IOC_ENABLE,
			PERF_IOC_FLAG_GROUP) != 0) {
		group->error = errno;
		return -1;
	}
	return 0;
}

static int stop_pmu_group(pmu_group_t *group)
{
	uint64_t data[3 + MAX_PMU_EVENTS];
	ssize_t bytes;

	if (group->count == 0 || group->fds[0] < 0)
		return 0;
	if (ioctl(group->fds[0], PERF_EVENT_IOC_DISABLE,
		PERF_IOC_FLAG_GROUP) != 0) {
		group->error = errno;
		return -1;
	}
	bytes = read(group->fds[0], data,
		(3U + group->count) * sizeof data[0]);
	if (bytes != (ssize_t)((3U + group->count) * sizeof data[0])
		|| data[0] != group->count) {
		group->error = errno != 0 ? errno : EIO;
		return -1;
	}
	group->time_enabled += data[1];
	group->time_running += data[2];
	for (size_t i = 0; i < group->count; i++)
		group->values[i] += data[3U + i];
	return 0;
}

static void print_pmu_counts(const char *variant, const pmu_group_t *pmu)
{
	for (size_t i = 0; i < pmu->count; i++) {
		const double scale = pmu->time_running == 0 ? 0.0
			: (double)pmu->time_enabled / (double)pmu->time_running;
		printf("PMU_COUNT,%s,%s,%" PRIu64 ",%.3f,%" PRIu64 ",%" PRIu64
			"\n", variant, pmu->events[i].name, pmu->values[i],
			(double)pmu->values[i] * scale, pmu->time_enabled,
			pmu->time_running);
	}
}

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

static void reset_rng(void)
{
	uint8_t entropy[48];
	for (size_t i = 0; i < sizeof entropy; i++)
		entropy[i] = (uint8_t)(73U + 19U * i);
	randombytes_init(entropy, NULL, 256);
}

__attribute__((noinline))
static int decap_official(uint8_t *ss, const uint8_t *ct, const uint8_t *sk)
{
	return crypto_kem_dec(ss, ct, sk);
}

__attribute__((noinline))
static int decap_control(uint8_t *ss, const uint8_t *ct, const uint8_t *sk)
{
	return crypto_kem_dec_gt32_soa_domain_candidate(ss, ct, sk);
}

__attribute__((noinline))
static int decap_unpack_only(uint8_t *ss, const uint8_t *ct,
	const uint8_t *sk)
{
	return crypto_kem_dec_gt32_q24_decode_candidate(ss, ct, sk);
}

__attribute__((noinline))
static int decap_q24(uint8_t *ss, const uint8_t *ct, const uint8_t *sk)
{
	return crypto_kem_dec_gt32_candidate(ss, ct, sk);
}

__attribute__((noinline))
static int decap_gtpack(uint8_t *ss, const uint8_t *ct, const uint8_t *sk)
{
	return crypto_kem_dec_gt32_q24_pack_candidate(ss, ct, sk);
}

__attribute__((noinline))
static int decap_lazy_pack(uint8_t *ss, const uint8_t *ct,
	const uint8_t *sk)
{
	return crypto_kem_dec_gt32_q24_lazy_pack_candidate(ss, ct, sk);
}

#if defined(GT32_GLOBAL_PHYSICAL_KEM)
__attribute__((noinline))
static int decap_global_inverse(uint8_t *ss, const uint8_t *ct,
	const uint8_t *sk)
{
	return crypto_kem_dec_gt32_global_inverse_candidate(ss, ct, sk);
}

static int decap_native_rcheck(uint8_t *ss, const uint8_t *ct,
	const uint8_t *sk)
{
	return crypto_kem_dec_gt32_native_rcheck_candidate(ss, ct, sk);
}

static int run_global_inverse_tsc_regions(uint8_t *official_ss,
	uint8_t *control_ss, uint8_t *candidate_ss, unsigned iterations)
{
	double official_samples[SAMPLES];
	double control_samples[SAMPLES];
	double candidate_samples[SAMPLES];

	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(decap_official, official_ss, 100);
		(void)measure(decap_q24, control_ss, 100);
		(void)measure(decap_global_inverse, candidate_ss, 100);
	}
	printf("META,correctness=byte-exact-valid-decap,scope=full-decap-global-inverse,"
		"iterations=%u,samples=%u,order=ABC-CBA\n", iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		if ((sample & 1U) == 0U) {
			official_samples[sample] = measure(decap_official, official_ss,
				iterations);
			control_samples[sample] = measure(decap_q24, control_ss,
				iterations);
			candidate_samples[sample] = measure(decap_global_inverse,
				candidate_ss, iterations);
		} else {
			candidate_samples[sample] = measure(decap_global_inverse,
				candidate_ss, iterations);
			control_samples[sample] = measure(decap_q24, control_ss,
				iterations);
			official_samples[sample] = measure(decap_official, official_ss,
				iterations);
		}
		printf("GLOBAL_SAMPLE,%u,%.6f,%.6f,%.6f,%.6f,%.6f\n", sample,
			official_samples[sample], control_samples[sample],
			candidate_samples[sample],
			candidate_samples[sample] - control_samples[sample],
			candidate_samples[sample] - official_samples[sample]);
	}
	return 0;
}
#endif

static double measure(decap_fn fn, uint8_t *ss, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		sink += (unsigned)fn(ss, ciphertext, secret_key);
	const uint64_t end = stop_tsc();
	sink += ss[iterations % CRYPTO_BYTES];
	return (double)(end - begin) / iterations;
}

static int run_single_pmu_region(const char *name, decap_fn fn, uint8_t *ss,
	unsigned iterations)
{
	double samples[SAMPLES];
	pmu_group_t pmu;
	const int start_cpu = sched_getcpu();
	const int open_status = open_pmu_group(&pmu);
	int start_status;
	int stop_status;

	for (unsigned warm = 0; warm < 2; warm++)
		(void)measure(fn, ss, 100);
	start_status = open_status == 0 ? start_pmu_group(&pmu) : -1;
	for (unsigned sample = 0; sample < SAMPLES; sample++)
		samples[sample] = measure(fn, ss, iterations);
	stop_status = start_status == 0 ? stop_pmu_group(&pmu) : -1;
	printf("META,correctness=byte-exact-valid-decap,scope=decode3-only,"
		"pmu-region=%s,iterations=%u,samples=%u,pmu-group=%s,"
		"pmu-open-status=%d,pmu-start-status=%d,pmu-stop-status=%d,"
		"pmu-error=%d,start-cpu=%d,end-cpu=%d\n",
		name, iterations, SAMPLES, pmu.name, open_status, start_status,
		stop_status, pmu.error, start_cpu, sched_getcpu());
	for (unsigned sample = 0; sample < SAMPLES; sample++)
		printf("PMU_SAMPLE,%u,%.6f\n", sample, samples[sample]);
	print_pmu_counts(name, &pmu);
	printf("SINK,%llu\n", (unsigned long long)sink);
	close_pmu_group(&pmu);
	return 0;
}

static int run_paired_pmu_regions(uint8_t *control_ss, uint8_t *q24_ss,
	unsigned iterations)
{
	double control_samples[SAMPLES];
	double q24_samples[SAMPLES];
	pmu_group_t control_pmu;
	pmu_group_t q24_pmu;
	const int start_cpu = sched_getcpu();
	const int control_open = open_pmu_group(&control_pmu);
	const int q24_open = open_pmu_group(&q24_pmu);

	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(decap_control, control_ss, 100);
		(void)measure(decap_q24, q24_ss, 100);
	}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		if ((sample & 1U) == 0U) {
			(void)start_pmu_group(&control_pmu);
			control_samples[sample] = measure(decap_control, control_ss,
				iterations);
			(void)stop_pmu_group(&control_pmu);
			(void)start_pmu_group(&q24_pmu);
			q24_samples[sample] = measure(decap_q24, q24_ss, iterations);
			(void)stop_pmu_group(&q24_pmu);
		} else {
			(void)start_pmu_group(&q24_pmu);
			q24_samples[sample] = measure(decap_q24, q24_ss, iterations);
			(void)stop_pmu_group(&q24_pmu);
			(void)start_pmu_group(&control_pmu);
			control_samples[sample] = measure(decap_control, control_ss,
				iterations);
			(void)stop_pmu_group(&control_pmu);
		}
	}
	printf("META,correctness=byte-exact-valid-decap,scope=decode3-only,"
		"pmu-region=paired-control-q24,iterations=%u,samples=%u,"
		"pmu-group=%s,control-open=%d,q24-open=%d,control-error=%d,"
		"q24-error=%d,start-cpu=%d,end-cpu=%d,order=AB-BA\n",
		iterations, SAMPLES, control_pmu.name, control_open, q24_open,
		control_pmu.error, q24_pmu.error, start_cpu, sched_getcpu());
	for (unsigned sample = 0; sample < SAMPLES; sample++)
		printf("PMU_PAIR_SAMPLE,%u,%.6f,%.6f,%.6f\n", sample,
			control_samples[sample], q24_samples[sample],
			q24_samples[sample] - control_samples[sample]);
	print_pmu_counts("control", &control_pmu);
	print_pmu_counts("q24", &q24_pmu);
	printf("SINK,%llu\n", (unsigned long long)sink);
	close_pmu_group(&control_pmu);
	close_pmu_group(&q24_pmu);
	return control_open == 0 && q24_open == 0
		&& control_pmu.error == 0 && q24_pmu.error == 0 ? 0 : 3;
}

#if defined(GT32_GLOBAL_PHYSICAL_KEM)
static int run_native_rcheck_pmu_regions(uint8_t *control_ss,
	uint8_t *candidate_ss, unsigned iterations)
{
	double control_samples[SAMPLES];
	double candidate_samples[SAMPLES];
	pmu_group_t control_pmu;
	pmu_group_t candidate_pmu;
	const int start_cpu = sched_getcpu();
	const int control_open = open_pmu_group(&control_pmu);
	const int candidate_open = open_pmu_group(&candidate_pmu);

	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(decap_global_inverse, control_ss, 100);
		(void)measure(decap_native_rcheck, candidate_ss, 100);
	}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		if ((sample & 1U) == 0U) {
			(void)start_pmu_group(&control_pmu);
			control_samples[sample] = measure(decap_global_inverse,
				control_ss, iterations);
			(void)stop_pmu_group(&control_pmu);
			(void)start_pmu_group(&candidate_pmu);
			candidate_samples[sample] = measure(decap_native_rcheck,
				candidate_ss, iterations);
			(void)stop_pmu_group(&candidate_pmu);
		} else {
			(void)start_pmu_group(&candidate_pmu);
			candidate_samples[sample] = measure(decap_native_rcheck,
				candidate_ss, iterations);
			(void)stop_pmu_group(&candidate_pmu);
			(void)start_pmu_group(&control_pmu);
			control_samples[sample] = measure(decap_global_inverse,
				control_ss, iterations);
			(void)stop_pmu_group(&control_pmu);
		}
	}
	printf("META,correctness=byte-exact-valid-decap,scope=native-rcheck-"
		"same-elf-paired-pmu,iterations=%u,samples=%u,pmu-group=%s,"
		"control-open=%d,candidate-open=%d,control-error=%d,"
		"candidate-error=%d,start-cpu=%d,end-cpu=%d,order=AB-BA\n",
		iterations, SAMPLES, control_pmu.name, control_open, candidate_open,
		control_pmu.error, candidate_pmu.error, start_cpu, sched_getcpu());
	for (unsigned sample = 0; sample < SAMPLES; sample++)
		printf("NATIVE_RCHECK_PMU_SAMPLE,%u,%.6f,%.6f,%.6f\n", sample,
			control_samples[sample], candidate_samples[sample],
			candidate_samples[sample] - control_samples[sample]);
	print_pmu_counts("native-rcheck-control", &control_pmu);
	print_pmu_counts("native-rcheck-candidate", &candidate_pmu);
	printf("SINK,%llu\n", (unsigned long long)sink);
	close_pmu_group(&control_pmu);
	close_pmu_group(&candidate_pmu);
	return control_open == 0 && candidate_open == 0
		&& control_pmu.error == 0 && candidate_pmu.error == 0 ? 0 : 3;
}

static int run_global_inverse_pmu_regions(uint8_t *q24_ss,
	uint8_t *candidate_ss, unsigned iterations)
{
	double q24_samples[SAMPLES];
	double candidate_samples[SAMPLES];
	pmu_group_t q24_pmu;
	pmu_group_t candidate_pmu;
	const int start_cpu = sched_getcpu();
	const int q24_open = open_pmu_group(&q24_pmu);
	const int candidate_open = open_pmu_group(&candidate_pmu);

	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(decap_q24, q24_ss, 100);
		(void)measure(decap_global_inverse, candidate_ss, 100);
	}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		if ((sample & 1U) == 0U) {
			(void)start_pmu_group(&q24_pmu);
			q24_samples[sample] = measure(decap_q24, q24_ss,
				iterations);
			(void)stop_pmu_group(&q24_pmu);
			(void)start_pmu_group(&candidate_pmu);
			candidate_samples[sample] = measure(decap_global_inverse,
				candidate_ss, iterations);
			(void)stop_pmu_group(&candidate_pmu);
		} else {
			(void)start_pmu_group(&candidate_pmu);
			candidate_samples[sample] = measure(decap_global_inverse,
				candidate_ss, iterations);
			(void)stop_pmu_group(&candidate_pmu);
			(void)start_pmu_group(&q24_pmu);
			q24_samples[sample] = measure(decap_q24, q24_ss,
				iterations);
			(void)stop_pmu_group(&q24_pmu);
		}
	}
	printf("META,correctness=byte-exact-valid-decap,scope=global-inverse-"
		"paired-pmu,iterations=%u,samples=%u,pmu-group=%s,"
		"q24-open=%d,candidate-open=%d,q24-error=%d,candidate-error=%d,"
		"start-cpu=%d,end-cpu=%d,order=AB-BA\n", iterations, SAMPLES,
		q24_pmu.name, q24_open, candidate_open, q24_pmu.error,
		candidate_pmu.error, start_cpu, sched_getcpu());
	for (unsigned sample = 0; sample < SAMPLES; sample++)
		printf("GLOBAL_PMU_SAMPLE,%u,%.6f,%.6f,%.6f\n", sample,
			q24_samples[sample], candidate_samples[sample],
			candidate_samples[sample] - q24_samples[sample]);
	print_pmu_counts("q24", &q24_pmu);
	print_pmu_counts("global-inverse", &candidate_pmu);
	printf("SINK,%llu\n", (unsigned long long)sink);
	close_pmu_group(&q24_pmu);
	close_pmu_group(&candidate_pmu);
	return q24_open == 0 && candidate_open == 0 && q24_pmu.error == 0
		&& candidate_pmu.error == 0 ? 0 : 3;
}
#endif

static int run_official_q24_pmu_regions(uint8_t *official_ss,
	uint8_t *q24_ss, unsigned iterations)
{
	double official_samples[SAMPLES];
	double q24_samples[SAMPLES];
	pmu_group_t official_pmu;
	pmu_group_t q24_pmu;
	const int start_cpu = sched_getcpu();
	const int official_open = open_pmu_group(&official_pmu);
	const int q24_open = open_pmu_group(&q24_pmu);

	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(decap_official, official_ss, 100);
		(void)measure(decap_q24, q24_ss, 100);
	}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		if ((sample & 1U) == 0U) {
			(void)start_pmu_group(&official_pmu);
			official_samples[sample] = measure(decap_official, official_ss,
				iterations);
			(void)stop_pmu_group(&official_pmu);
			(void)start_pmu_group(&q24_pmu);
			q24_samples[sample] = measure(decap_q24, q24_ss, iterations);
			(void)stop_pmu_group(&q24_pmu);
		} else {
			(void)start_pmu_group(&q24_pmu);
			q24_samples[sample] = measure(decap_q24, q24_ss, iterations);
			(void)stop_pmu_group(&q24_pmu);
			(void)start_pmu_group(&official_pmu);
			official_samples[sample] = measure(decap_official, official_ss,
				iterations);
			(void)stop_pmu_group(&official_pmu);
		}
	}
	printf("META,correctness=byte-exact-valid-decap,scope=production-promoted-"
		"q24-vs-official,pmu-region=paired-official-q24,iterations=%u,"
		"samples=%u,pmu-group=%s,official-open=%d,q24-open=%d,"
		"official-error=%d,q24-error=%d,start-cpu=%d,end-cpu=%d,"
		"order=AB-BA\n", iterations, SAMPLES, official_pmu.name,
		official_open, q24_open, official_pmu.error, q24_pmu.error,
		start_cpu, sched_getcpu());
	for (unsigned sample = 0; sample < SAMPLES; sample++)
		printf("PMU_PAIR_SAMPLE,%u,%.6f,%.6f,%.6f\n", sample,
			official_samples[sample], q24_samples[sample],
			q24_samples[sample] - official_samples[sample]);
	print_pmu_counts("official", &official_pmu);
	print_pmu_counts("q24", &q24_pmu);
	printf("SINK,%llu\n", (unsigned long long)sink);
	close_pmu_group(&official_pmu);
	close_pmu_group(&q24_pmu);
	return official_open == 0 && q24_open == 0
		&& official_pmu.error == 0 && q24_pmu.error == 0 ? 0 : 3;
}

static int run_gtpack_pmu_regions(uint8_t *unpack_only_ss,
	uint8_t *gtpack_ss, unsigned iterations)
{
	double unpack_only_samples[SAMPLES];
	double gtpack_samples[SAMPLES];
	pmu_group_t unpack_only_pmu;
	pmu_group_t gtpack_pmu;
	const int start_cpu = sched_getcpu();
	const int unpack_only_open = open_pmu_group(&unpack_only_pmu);
	const int gtpack_open = open_pmu_group(&gtpack_pmu);

	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(decap_unpack_only, unpack_only_ss, 100);
		(void)measure(decap_gtpack, gtpack_ss, 100);
	}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		if ((sample & 1U) == 0U) {
			(void)start_pmu_group(&unpack_only_pmu);
			unpack_only_samples[sample] = measure(decap_unpack_only,
				unpack_only_ss, iterations);
			(void)stop_pmu_group(&unpack_only_pmu);
			(void)start_pmu_group(&gtpack_pmu);
			gtpack_samples[sample] = measure(decap_gtpack, gtpack_ss,
				iterations);
			(void)stop_pmu_group(&gtpack_pmu);
		} else {
			(void)start_pmu_group(&gtpack_pmu);
			gtpack_samples[sample] = measure(decap_gtpack, gtpack_ss,
				iterations);
			(void)stop_pmu_group(&gtpack_pmu);
			(void)start_pmu_group(&unpack_only_pmu);
			unpack_only_samples[sample] = measure(decap_unpack_only,
				unpack_only_ss, iterations);
			(void)stop_pmu_group(&unpack_only_pmu);
		}
	}
	printf("META,correctness=byte-exact-valid-decap,scope=recovered-r-"
		"centered-soa-q24-gt-pack,pmu-region=paired-unpack-only-gtpack,"
		"iterations=%u,samples=%u,pmu-group=%s,unpack-only-open=%d,"
		"gtpack-open=%d,unpack-only-error=%d,gtpack-error=%d,"
		"start-cpu=%d,end-cpu=%d,order=AB-BA\n", iterations, SAMPLES,
		unpack_only_pmu.name, unpack_only_open, gtpack_open,
		unpack_only_pmu.error, gtpack_pmu.error, start_cpu, sched_getcpu());
	for (unsigned sample = 0; sample < SAMPLES; sample++)
		printf("GTPACK_PMU_PAIR_SAMPLE,%u,%.6f,%.6f,%.6f\n", sample,
			unpack_only_samples[sample], gtpack_samples[sample],
			gtpack_samples[sample] - unpack_only_samples[sample]);
	print_pmu_counts("unpack-only", &unpack_only_pmu);
	print_pmu_counts("gtpack", &gtpack_pmu);
	printf("SINK,%llu\n", (unsigned long long)sink);
	close_pmu_group(&unpack_only_pmu);
	close_pmu_group(&gtpack_pmu);
	return unpack_only_open == 0 && gtpack_open == 0
		&& unpack_only_pmu.error == 0 && gtpack_pmu.error == 0 ? 0 : 3;
}

static int run_lazy_pack_pmu_regions(uint8_t *centered_ss,
	uint8_t *lazy_ss, unsigned iterations)
{
	double centered_samples[SAMPLES];
	double lazy_samples[SAMPLES];
	pmu_group_t centered_pmu;
	pmu_group_t lazy_pmu;
	const int start_cpu = sched_getcpu();
	const int centered_open = open_pmu_group(&centered_pmu);
	const int lazy_open = open_pmu_group(&lazy_pmu);

	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(decap_gtpack, centered_ss, 100);
		(void)measure(decap_lazy_pack, lazy_ss, 100);
	}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		if ((sample & 1U) == 0U) {
			(void)start_pmu_group(&centered_pmu);
			centered_samples[sample] = measure(decap_gtpack, centered_ss,
				iterations);
			(void)stop_pmu_group(&centered_pmu);
			(void)start_pmu_group(&lazy_pmu);
			lazy_samples[sample] = measure(decap_lazy_pack, lazy_ss,
				iterations);
			(void)stop_pmu_group(&lazy_pmu);
		} else {
			(void)start_pmu_group(&lazy_pmu);
			lazy_samples[sample] = measure(decap_lazy_pack, lazy_ss,
				iterations);
			(void)stop_pmu_group(&lazy_pmu);
			(void)start_pmu_group(&centered_pmu);
			centered_samples[sample] = measure(decap_gtpack, centered_ss,
				iterations);
			(void)stop_pmu_group(&centered_pmu);
		}
	}
	printf("META,correctness=byte-exact-valid-decap,scope=final-check-"
		"lazy10788-q24-gt-pack,pmu-region=paired-centered-lazy-pack,"
		"iterations=%u,samples=%u,pmu-group=%s,centered-open=%d,"
		"lazy-open=%d,centered-error=%d,lazy-error=%d,start-cpu=%d,"
		"end-cpu=%d,order=AB-BA\n", iterations, SAMPLES,
		centered_pmu.name, centered_open, lazy_open, centered_pmu.error,
		lazy_pmu.error, start_cpu, sched_getcpu());
	for (unsigned sample = 0; sample < SAMPLES; sample++)
		printf("LAZY_GTPACK_PMU_PAIR_SAMPLE,%u,%.6f,%.6f,%.6f\n", sample,
			centered_samples[sample], lazy_samples[sample],
			lazy_samples[sample] - centered_samples[sample]);
	print_pmu_counts("centered", &centered_pmu);
	print_pmu_counts("lazy", &lazy_pmu);
	printf("SINK,%llu\n", (unsigned long long)sink);
	close_pmu_group(&centered_pmu);
	close_pmu_group(&lazy_pmu);
	return centered_open == 0 && lazy_open == 0
		&& centered_pmu.error == 0 && lazy_pmu.error == 0 ? 0 : 3;
}

static int run_production_tsc_regions(uint8_t *official_ss, uint8_t *q24_ss,
	unsigned iterations)
{
	double official_samples[SAMPLES];
	double q24_samples[SAMPLES];

	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(decap_official, official_ss, 100);
		(void)measure(decap_q24, q24_ss, 100);
	}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		if ((sample & 1U) == 0U) {
			official_samples[sample] = measure(decap_official, official_ss,
				iterations);
			q24_samples[sample] = measure(decap_q24, q24_ss, iterations);
		} else {
			q24_samples[sample] = measure(decap_q24, q24_ss, iterations);
			official_samples[sample] = measure(decap_official, official_ss,
				iterations);
		}
	}
	printf("META,correctness=byte-exact-valid-decap,scope=production-promoted-"
		"q24-vs-official,iterations=%u,samples=%u,order=AB-BA,"
		"unit=TSC-ticks-per-decap\n", iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++)
		printf("PRODUCTION_SAMPLE,%u,%.6f,%.6f,%.6f\n", sample,
			official_samples[sample], q24_samples[sample],
			q24_samples[sample] - official_samples[sample]);
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}

static int run_gtpack_tsc_regions(uint8_t *unpack_only_ss, uint8_t *q24_ss,
	unsigned iterations)
{
	double unpack_only_samples[SAMPLES];
	double q24_samples[SAMPLES];

	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(decap_unpack_only, unpack_only_ss, 100);
		(void)measure(decap_gtpack, q24_ss, 100);
	}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		if ((sample & 1U) == 0U) {
			unpack_only_samples[sample] = measure(decap_unpack_only,
				unpack_only_ss, iterations);
			q24_samples[sample] = measure(decap_gtpack, q24_ss, iterations);
		} else {
			q24_samples[sample] = measure(decap_gtpack, q24_ss, iterations);
			unpack_only_samples[sample] = measure(decap_unpack_only,
				unpack_only_ss, iterations);
		}
	}
	printf("META,correctness=byte-exact-valid-decap,scope=recovered-r-"
		"centered-soa-q24-gt-pack,iterations=%u,samples=%u,order=AB-BA,"
		"unit=TSC-ticks-per-decap\n", iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++)
		printf("GTPACK_SAMPLE,%u,%.6f,%.6f,%.6f\n", sample,
			unpack_only_samples[sample], q24_samples[sample],
			q24_samples[sample] - unpack_only_samples[sample]);
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}

static int run_lazy_pack_tsc_regions(uint8_t *centered_ss, uint8_t *lazy_ss,
	unsigned iterations)
{
	double centered_samples[SAMPLES];
	double lazy_samples[SAMPLES];

	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(decap_gtpack, centered_ss, 100);
		(void)measure(decap_lazy_pack, lazy_ss, 100);
	}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		if ((sample & 1U) == 0U) {
			centered_samples[sample] = measure(decap_gtpack, centered_ss,
				iterations);
			lazy_samples[sample] = measure(decap_lazy_pack, lazy_ss,
				iterations);
		} else {
			lazy_samples[sample] = measure(decap_lazy_pack, lazy_ss,
				iterations);
			centered_samples[sample] = measure(decap_gtpack, centered_ss,
				iterations);
		}
	}
	printf("META,correctness=byte-exact-valid-decap,scope=final-check-"
		"lazy10788-q24-gt-pack,iterations=%u,samples=%u,order=AB-BA,"
		"unit=TSC-ticks-per-decap\n", iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++)
		printf("LAZY_GTPACK_SAMPLE,%u,%.6f,%.6f,%.6f\n", sample,
			centered_samples[sample], lazy_samples[sample],
			lazy_samples[sample] - centered_samples[sample]);
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}

static int run_sidecar_tsc_regions(uint8_t *lazy_ss, uint8_t *sidecar_ss,
	unsigned iterations)
{
	double lazy_samples[SAMPLES];
	double sidecar_samples[SAMPLES];

	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(decap_lazy_pack, lazy_ss, 100);
		(void)measure(decap_q24, sidecar_ss, 100);
	}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		if ((sample & 1U) == 0U) {
			lazy_samples[sample] = measure(decap_lazy_pack, lazy_ss,
				iterations);
			sidecar_samples[sample] = measure(decap_q24, sidecar_ss,
				iterations);
		} else {
			sidecar_samples[sample] = measure(decap_q24, sidecar_ss,
				iterations);
			lazy_samples[sample] = measure(decap_lazy_pack, lazy_ss,
				iterations);
		}
	}
	printf("META,correctness=byte-exact-valid-decap,scope=crepmod3-"
		"sidecar-tap,iterations=%u,samples=%u,order=AB-BA,"
		"full-m-materialized=1,n5-path=unchanged,"
		"unit=TSC-ticks-per-decap\n", iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++)
		printf("SIDECAR_SAMPLE,%u,%.6f,%.6f,%.6f\n", sample,
			lazy_samples[sample], sidecar_samples[sample],
			sidecar_samples[sample] - lazy_samples[sample]);
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	uint8_t official_ss[CRYPTO_BYTES] __attribute__((aligned(64)));
	uint8_t control_ss[CRYPTO_BYTES] __attribute__((aligned(64)));
	uint8_t unpack_only_ss[CRYPTO_BYTES] __attribute__((aligned(64)));
	uint8_t q24_ss[CRYPTO_BYTES] __attribute__((aligned(64)));
	uint8_t gtpack_ss[CRYPTO_BYTES] __attribute__((aligned(64)));
	uint8_t lazy_pack_ss[CRYPTO_BYTES] __attribute__((aligned(64)));
#if defined(GT32_GLOBAL_PHYSICAL_KEM)
	uint8_t global_inverse_ss[CRYPTO_BYTES] __attribute__((aligned(64)));
	uint8_t native_rcheck_ss[CRYPTO_BYTES] __attribute__((aligned(64)));
#endif
	cpu_set_t set;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	print_virtual_addresses(main);
	reset_rng();
	if (crypto_kem_keypair(public_key, secret_key) != 0
		|| crypto_kem_enc(ciphertext, encapsulated_ss, public_key) != 0
		|| decap_official(official_ss, ciphertext, secret_key) != 0
		|| decap_control(control_ss, ciphertext, secret_key) != 0
		|| decap_unpack_only(unpack_only_ss, ciphertext, secret_key) != 0
		|| decap_q24(q24_ss, ciphertext, secret_key) != 0
		|| decap_gtpack(gtpack_ss, ciphertext, secret_key) != 0
		|| decap_lazy_pack(lazy_pack_ss, ciphertext, secret_key) != 0
#if defined(GT32_GLOBAL_PHYSICAL_KEM)
		|| decap_global_inverse(global_inverse_ss, ciphertext, secret_key) != 0
		|| decap_native_rcheck(native_rcheck_ss, ciphertext, secret_key) != 0
#endif
		|| memcmp(official_ss, encapsulated_ss, sizeof official_ss) != 0
		|| memcmp(official_ss, control_ss, sizeof official_ss) != 0
		|| memcmp(official_ss, unpack_only_ss, sizeof official_ss) != 0
		|| memcmp(official_ss, q24_ss, sizeof official_ss) != 0
		|| memcmp(official_ss, gtpack_ss, sizeof official_ss) != 0
		|| memcmp(official_ss, lazy_pack_ss, sizeof official_ss) != 0) {
		fprintf(stderr, "Q24 GT-native full decap correctness failed\n");
		return 1;
	}
#if defined(GT32_GLOBAL_PHYSICAL_KEM)
	if (memcmp(official_ss, global_inverse_ss, sizeof official_ss) != 0) {
		fprintf(stderr, "global inverse full decap correctness failed\n");
		return 1;
	}
	if (memcmp(official_ss, native_rcheck_ss, sizeof official_ss) != 0) {
		fprintf(stderr, "native rcheck full decap correctness failed\n");
		return 1;
	}
#endif
	if (argc > 2) {
#if defined(GT32_GLOBAL_PHYSICAL_KEM)
		if (strcmp(argv[2], "global-inverse") == 0)
			return run_global_inverse_tsc_regions(official_ss, q24_ss,
				global_inverse_ss, iterations);
		if (strcmp(argv[2], "global-inverse-pmu") == 0)
			return run_global_inverse_pmu_regions(q24_ss,
				global_inverse_ss, iterations);
		if (strcmp(argv[2], "native-rcheck-pmu") == 0)
			return run_native_rcheck_pmu_regions(global_inverse_ss,
				native_rcheck_ss, iterations);
#endif
		if (strcmp(argv[2], "production") == 0)
			return run_production_tsc_regions(official_ss, q24_ss,
				iterations);
		if (strcmp(argv[2], "gtpack") == 0)
			return run_gtpack_tsc_regions(unpack_only_ss, gtpack_ss,
				iterations);
		if (strcmp(argv[2], "gtpack-pair") == 0)
			return run_gtpack_pmu_regions(unpack_only_ss, gtpack_ss,
				iterations);
		if (strcmp(argv[2], "lazy-pack") == 0)
			return run_lazy_pack_tsc_regions(gtpack_ss, lazy_pack_ss,
				iterations);
		if (strcmp(argv[2], "sidecar") == 0)
			return run_sidecar_tsc_regions(lazy_pack_ss, q24_ss,
				iterations);
		if (strcmp(argv[2], "lazy-pack-pair") == 0)
			return run_lazy_pack_pmu_regions(gtpack_ss, lazy_pack_ss,
				iterations);
		if (strcmp(argv[2], "official-pair") == 0)
			return run_official_q24_pmu_regions(official_ss, q24_ss,
				iterations);
		if (strcmp(argv[2], "official") == 0)
			return run_single_pmu_region("official", decap_official,
				official_ss, iterations);
		if (strcmp(argv[2], "control") == 0)
			return run_single_pmu_region("control", decap_control,
				control_ss, iterations);
		if (strcmp(argv[2], "q24") == 0)
			return run_single_pmu_region("q24", decap_q24, q24_ss,
				iterations);
		if (strcmp(argv[2], "pair") == 0)
			return run_paired_pmu_regions(control_ss, q24_ss, iterations);
		fprintf(stderr, "unknown PMU region: %s\n", argv[2]);
		return 2;
	}
	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(decap_official, official_ss, 100);
		(void)measure(decap_control, control_ss, 100);
		(void)measure(decap_q24, q24_ss, 100);
	}
	printf("META,correctness=byte-exact-valid-decap,scope=decode3-only,"
		"iterations=%u,samples=%u,order=ABC-CBA\n", iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double official;
		double control;
		double q24;
		if ((sample & 1U) == 0U) {
			official = measure(decap_official, official_ss, iterations);
			control = measure(decap_control, control_ss, iterations);
			q24 = measure(decap_q24, q24_ss, iterations);
		} else {
			q24 = measure(decap_q24, q24_ss, iterations);
			control = measure(decap_control, control_ss, iterations);
			official = measure(decap_official, official_ss, iterations);
		}
		printf("SAMPLE,%u,%.6f,%.6f,%.6f,%.6f,%.6f\n", sample,
			official, control, q24, q24 - control, q24 - official);
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
