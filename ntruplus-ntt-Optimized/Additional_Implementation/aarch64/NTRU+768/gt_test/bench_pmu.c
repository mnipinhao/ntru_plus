#include <dlfcn.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#if defined(__APPLE__)
#include <mach/mach.h>
#include <mach/thread_policy.h>
#include <pthread.h>
#include <sys/qos.h>
#endif

#include "api.h"
#include "params.h"
#include "poly.h"

#ifndef PMU_BENCH_MODE
#define PMU_BENCH_MODE "basemul"
#endif

#ifndef PMU_BENCH_LABEL
#define PMU_BENCH_LABEL PMU_BENCH_MODE
#endif

#ifndef PMU_BENCH_CALLS
#define PMU_BENCH_CALLS 1024
#endif

#ifndef PMU_BENCH_WARMUP
#define PMU_BENCH_WARMUP 16
#endif

#ifndef PMU_SUBTRACT_EMPTY
#define PMU_SUBTRACT_EMPTY 0
#endif

#ifndef PMU_FIXED_ONLY
#define PMU_FIXED_ONLY 0
#endif

#ifndef PMU_SYMBOLS_ONLY
#define PMU_SYMBOLS_ONLY 0
#endif

#ifndef PMU_ROUNDS
#define PMU_ROUNDS 11
#endif

#ifndef PMU_DISCARD_FIRST
#define PMU_DISCARD_FIRST 1
#endif

#ifndef PMU_BASE_COMPARE
#define PMU_BASE_COMPARE 0
#endif

#ifndef PMU_COMPARE_LEFT_LABEL
#define PMU_COMPARE_LEFT_LABEL "stock"
#endif

#ifndef PMU_COMPARE_RIGHT_LABEL
#define PMU_COMPARE_RIGHT_LABEL "gt"
#endif

#define KPC_CLASS_FIXED_MASK (1u << 0)
#define KPC_CLASS_CONFIGURABLE_MASK (1u << 1)

int crypto_kem_keypair(uint8_t *pk, uint8_t *sk);
int crypto_kem_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int crypto_kem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);

typedef void (*target_fn)(uint64_t calls);

enum {
	PMU_EVENT_CYCLES = 0,
	PMU_EVENT_INSTRUCTIONS,
	PMU_EVENT_BRANCHES,
	PMU_EVENT_BRANCH_MISSES,
	PMU_EVENT_COUNT
};

typedef struct {
	uint64_t v[PMU_EVENT_COUNT];
} pmu_counts;

typedef struct {
	pmu_counts counts;
	double cycles_per_call;
	double instructions_per_call;
} pmu_round_result;

typedef struct {
	double median;
	double min;
	double max;
	double iqr;
} pmu_stats;

typedef struct {
	int qos_ok;
	int affinity_ok;
	int qos_err;
	int affinity_err;
} thread_setup_result;

typedef struct {
	void *kperf_handle;
	void *kperfdata_handle;
	const char *kperf_path;
	const char *kperfdata_path;

	int (*kpc_force_all_ctrs_get)(int *);
	int (*kpc_force_all_ctrs_set)(int);
	int (*kpc_set_counting)(uint32_t);
	int (*kpc_set_thread_counting)(uint32_t);
	int (*kpc_set_config)(uint32_t, uint64_t *);
	uint32_t (*kpc_get_counter_count)(uint32_t);
	uint32_t (*kpc_get_config_count)(uint32_t);
	int (*kpc_get_thread_counters)(int, unsigned int, uint64_t *);
	uint32_t (*kpc_pmu_version)(void);

	int (*kpep_db_create)(const char *, void **);
	void (*kpep_db_free)(void *);
	int (*kpep_db_event)(void *, const char *, const void **);
	int (*kpep_config_create)(void *, void **);
	void (*kpep_config_free)(void *);
	int (*kpep_config_add_event)(void *, const void *, uint32_t, void *);
	int (*kpep_config_force_counters)(void *);
	int (*kpep_config_kpc_classes)(void *, uint32_t *);
	int (*kpep_config_kpc)(void *, uint64_t *, size_t);
	int (*kpep_config_kpc_map)(void *, size_t *, size_t);
} pmu_api;

typedef struct {
	pmu_api api;
	void *db;
	void *config;
	uint32_t classes;
	uint32_t counter_count;
	uint32_t config_count;
	size_t event_map[PMU_EVENT_COUNT];
	uint64_t *before;
	uint64_t *after;
	int fixed_only;
	int original_force_all;
	int have_original_force_all;
} pmu_state;

static poly g_a;
static poly g_b;
static poly g_c;
static poly g_freq;
static poly g_out;

static uint8_t g_pk[NTRUPLUS_PUBLICKEYBYTES];
static uint8_t g_sk[NTRUPLUS_SECRETKEYBYTES];
static uint8_t g_ct[NTRUPLUS_CIPHERTEXTBYTES];
static uint8_t g_ss_enc[NTRUPLUS_SSBYTES];
static uint8_t g_ss_dec[NTRUPLUS_SSBYTES];

static volatile uint64_t g_sink;

#if PMU_BASE_COMPARE
void stock_poly_basemul(poly *r, const poly *a, const poly *b);
void stock_poly_basemul_add(poly *r, const poly *a, const poly *b,
                            const poly *c);
void gt_poly_basemul(poly *r, const poly *a, const poly *b);
void gt_poly_basemul_add(poly *r, const poly *a, const poly *b,
                         const poly *c);
#endif

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525u + 1013904223u;
	return *state;
}

static void fill_poly(poly *a, uint32_t seed)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		a->coeffs[i] =
		    (int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) -
		              NTRUPLUS_Q);
	}
}

static uint64_t checksum_bytes(const uint8_t *buf, size_t len)
{
	uint64_t acc = 0x9e3779b97f4a7c15ULL;

	for (size_t i = 0; i < len; i++)
	{
		acc ^= (uint64_t)buf[i] + 0x9e3779b97f4a7c15ULL +
		       (acc << 6) + (acc >> 2);
	}

	return acc;
}

static uint64_t checksum_poly(const poly *a)
{
	uint64_t acc = 0x243f6a8885a308d3ULL;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		acc ^= (uint16_t)a->coeffs[i];
		acc *= 0x100000001b3ULL;
		acc ^= acc >> 32;
	}

	return acc;
}

static int modq(int64_t a)
{
	int r = (int)(a % NTRUPLUS_Q);

	if (r < 0)
	{
		r += NTRUPLUS_Q;
	}

	return r;
}

static int equal_modq(int16_t a, int16_t b)
{
	return modq((int)a - (int)b) == 0;
}

static int check_invntt_roundtrip(void)
{
	poly got;

	poly_invntt(&got, &g_freq);
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!equal_modq(got.coeffs[i], g_a.coeffs[i]))
		{
			fprintf(stderr,
			        "bench_pmu invntt setup mismatch at %d: got=%d want=%d\n",
			        i, got.coeffs[i], g_a.coeffs[i]);
			return 0;
		}
	}

	return 1;
}

static void setup_inputs(void)
{
	fill_poly(&g_a, 0x243f6a88u);
	fill_poly(&g_b, 0x85a308d3u);
	fill_poly(&g_c, 0x13198a2eu);
	poly_ntt(&g_freq, &g_a);
}

static int setup_kem(void)
{
	if (crypto_kem_keypair(g_pk, g_sk) != 0 ||
	    crypto_kem_enc(g_ct, g_ss_enc, g_pk) != 0 ||
	    crypto_kem_dec(g_ss_dec, g_ct, g_sk) != 0)
	{
		fprintf(stderr, "bench_pmu KEM setup failed\n");
		return 0;
	}

	if (memcmp(g_ss_enc, g_ss_dec, sizeof(g_ss_enc)) != 0)
	{
		fprintf(stderr, "bench_pmu KEM setup correctness check failed\n");
		return 0;
	}

	return 1;
}

__attribute__((noinline)) static void target_empty(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		__asm__ volatile("" ::: "memory");
	}
}

__attribute__((noinline)) static void target_basemul(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		poly_basemul(&g_out, &g_a, &g_b);
	}
}

__attribute__((noinline)) static void target_basemul_add(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		poly_basemul_add(&g_out, &g_a, &g_b, &g_c);
	}
}

__attribute__((noinline)) static void target_ntt(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		poly_ntt(&g_out, &g_a);
	}
}

__attribute__((noinline)) static void target_invntt(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		poly_invntt(&g_out, &g_freq);
	}
}

__attribute__((noinline)) static void target_kem_dec(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		crypto_kem_dec(g_ss_dec, g_ct, g_sk);
	}
}

#if PMU_BASE_COMPARE
__attribute__((noinline)) static void target_stock_basemul(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		stock_poly_basemul(&g_out, &g_a, &g_b);
	}
}

__attribute__((noinline)) static void target_stock_basemul_add(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		stock_poly_basemul_add(&g_out, &g_a, &g_b, &g_c);
	}
}

__attribute__((noinline)) static void target_gt_basemul(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		gt_poly_basemul(&g_out, &g_a, &g_b);
	}
}

__attribute__((noinline)) static void target_gt_basemul_add(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		gt_poly_basemul_add(&g_out, &g_a, &g_b, &g_c);
	}
}
#endif

static void consume_output(const char *mode)
{
	uint64_t checksum;

	if (strcmp(mode, "kem_dec") == 0)
	{
		checksum = checksum_bytes(g_ss_dec, sizeof(g_ss_dec));
	}
	else
	{
		checksum = checksum_poly(&g_out);
	}
	g_sink = (g_sink << 7) ^ (g_sink >> 3) ^ checksum ^
	         0x9e3779b97f4a7c15ULL;
}

static thread_setup_result setup_thread_policy(void)
{
	thread_setup_result result;

	memset(&result, 0, sizeof(result));
#if defined(__APPLE__) && defined(__aarch64__)
	result.qos_err = pthread_set_qos_class_self_np(
	    QOS_CLASS_USER_INTERACTIVE, 0);
	result.qos_ok = result.qos_err == 0;

#ifdef THREAD_AFFINITY_POLICY
	{
		thread_affinity_policy_data_t policy;
		thread_t self = mach_thread_self();
		kern_return_t kr;

		policy.affinity_tag = 1;
		kr = thread_policy_set(self,
		                       THREAD_AFFINITY_POLICY,
		                       (thread_policy_t)&policy,
		                       THREAD_AFFINITY_POLICY_COUNT);
		result.affinity_ok = kr == KERN_SUCCESS;
		result.affinity_err = result.affinity_ok ? 0 : (int)kr;
		(void)mach_port_deallocate(mach_task_self(), self);
	}
#else
	result.affinity_err = -1;
#endif
#else
	result.qos_err = -1;
	result.affinity_err = -1;
#endif
	printf("thread_qos=user_interactive:%s",
	       result.qos_ok ? "ok" : "failed");
	if (!result.qos_ok)
	{
		printf("(%d)", result.qos_err);
	}
	printf(" thread_affinity:%s",
	       result.affinity_ok ? "ok" : "failed");
	if (!result.affinity_ok)
	{
		printf("(%d)", result.affinity_err);
	}
	printf("\n");

	return result;
}

static int load_symbol(void *handle, const char *framework_name,
                       const char *name, void *out, size_t out_size,
                       int required)
{
	void *sym = dlsym(handle, name);

	if (sym == NULL)
	{
		if (required)
		{
			fprintf(stderr, "bench_pmu: missing %s symbol %s\n",
			        framework_name, name);
		}
		memset(out, 0, out_size);
		return !required;
	}

	memcpy(out, &sym, out_size);
	return 1;
}

#define LOAD_KPERF_REQUIRED(api, field) \
	do { \
		if (!load_symbol((api)->kperf_handle, "kperf.framework", #field, \
		                 &(api)->field, sizeof((api)->field), 1)) \
		{ \
			return 0; \
		} \
	} while (0)

#define LOAD_KPERF_OPTIONAL(api, field) \
	do { \
		(void)load_symbol((api)->kperf_handle, "kperf.framework", #field, \
		                  &(api)->field, sizeof((api)->field), 0); \
	} while (0)

#define LOAD_KPERFDATA_REQUIRED(api, field) \
	do { \
		if (!load_symbol((api)->kperfdata_handle, "kperfdata.framework", #field, \
		                 &(api)->field, sizeof((api)->field), 1)) \
		{ \
			return 0; \
		} \
	} while (0)

static void *open_framework(const char *framework_name,
                            const char *const paths[],
                            const char **selected_path,
                            int required)
{
	void *handle = NULL;

	*selected_path = NULL;
	for (int i = 0; paths[i] != NULL; i++)
	{
		handle = dlopen(paths[i], RTLD_NOW | RTLD_LOCAL);
		if (handle != NULL)
		{
			*selected_path = paths[i];
			break;
		}
	}

	if (handle == NULL && required)
	{
		fprintf(stderr, "bench_pmu: dlopen(%s) failed: %s\n",
		        framework_name, dlerror());
	}

	return handle;
}

static int pmu_api_load_kperf(pmu_api *api)
{
	static const char *const paths[] = {
		"/System/Library/PrivateFrameworks/kperf.framework/kperf",
		"/System/Library/PrivateFrameworks/kperf.framework",
		NULL,
	};

	api->kperf_handle =
	    open_framework("kperf.framework", paths, &api->kperf_path, 1);
	if (api->kperf_handle == NULL)
	{
		return 0;
	}

	LOAD_KPERF_REQUIRED(api, kpc_force_all_ctrs_get);
	LOAD_KPERF_REQUIRED(api, kpc_force_all_ctrs_set);
	LOAD_KPERF_REQUIRED(api, kpc_set_counting);
	LOAD_KPERF_REQUIRED(api, kpc_set_thread_counting);
	LOAD_KPERF_REQUIRED(api, kpc_get_counter_count);
	LOAD_KPERF_REQUIRED(api, kpc_get_thread_counters);
	LOAD_KPERF_OPTIONAL(api, kpc_get_config_count);
	LOAD_KPERF_OPTIONAL(api, kpc_set_config);
	LOAD_KPERF_OPTIONAL(api, kpc_pmu_version);

	return 1;
}

static int pmu_api_load_kperfdata(pmu_api *api)
{
	static const char *const paths[] = {
		"/System/Library/PrivateFrameworks/kperfdata.framework/kperfdata",
		"/System/Library/PrivateFrameworks/kperfdata.framework",
		NULL,
	};

	api->kperfdata_handle =
	    open_framework("kperfdata.framework", paths, &api->kperfdata_path, 0);
	if (api->kperfdata_handle == NULL)
	{
		fprintf(stderr,
		        "bench_pmu: kperfdata/kpep unavailable on this macOS; "
		        "try PMU_FIXED_ONLY=1\n");
		return 0;
	}

	{
		void *sym = dlsym(api->kperfdata_handle, "kpep_db_create");

		if (sym == NULL)
		{
			fprintf(stderr,
			        "bench_pmu: kperfdata/kpep unavailable on this macOS; "
			        "try PMU_FIXED_ONLY=1\n");
			return 0;
		}
		memcpy(&api->kpep_db_create, &sym, sizeof(api->kpep_db_create));
	}

	LOAD_KPERFDATA_REQUIRED(api, kpep_db_free);
	LOAD_KPERFDATA_REQUIRED(api, kpep_db_event);
	LOAD_KPERFDATA_REQUIRED(api, kpep_config_create);
	LOAD_KPERFDATA_REQUIRED(api, kpep_config_free);
	LOAD_KPERFDATA_REQUIRED(api, kpep_config_add_event);
	LOAD_KPERFDATA_REQUIRED(api, kpep_config_force_counters);
	LOAD_KPERFDATA_REQUIRED(api, kpep_config_kpc_classes);
	LOAD_KPERFDATA_REQUIRED(api, kpep_config_kpc);
	LOAD_KPERFDATA_REQUIRED(api, kpep_config_kpc_map);
	return 1;
}

static void print_pmu_symbol_diagnostics(void)
{
	pmu_api api;
	uint32_t fixed_count = 0;
	uint32_t configurable_count = 0;
	uint32_t pmu_version = 0;
	int have_kpep_db_create = 0;

	memset(&api, 0, sizeof(api));
	printf("bench_pmu symbol diagnostics\n");
	if (!pmu_api_load_kperf(&api))
	{
		printf("kperf path: unavailable\n");
		return;
	}

	printf("kperf path: %s\n",
	       api.kperf_path != NULL ? api.kperf_path : "unavailable");
	if (api.kpc_pmu_version != NULL)
	{
		pmu_version = api.kpc_pmu_version();
		printf("kpc_pmu_version: %u\n", pmu_version);
	}
	else
	{
		printf("kpc_pmu_version: unavailable\n");
	}

	fixed_count = api.kpc_get_counter_count(KPC_CLASS_FIXED_MASK);
	configurable_count = api.kpc_get_counter_count(KPC_CLASS_CONFIGURABLE_MASK);
	printf("kpc fixed counter count: %u\n", fixed_count);
	printf("kpc configurable counter count: %u\n", configurable_count);

	{
		static const char *const paths[] = {
			"/System/Library/PrivateFrameworks/kperfdata.framework/kperfdata",
			"/System/Library/PrivateFrameworks/kperfdata.framework",
			NULL,
		};
		api.kperfdata_handle =
		    open_framework("kperfdata.framework", paths, &api.kperfdata_path, 0);
	}
	printf("kperfdata path: %s\n",
	       api.kperfdata_path != NULL ? api.kperfdata_path : "unavailable");
	if (api.kperfdata_handle != NULL)
	{
		have_kpep_db_create =
		    dlsym(api.kperfdata_handle, "kpep_db_create") != NULL;
	}
	printf("kpep_db_create found: %s\n",
	       have_kpep_db_create ? "yes" : "no");

	if (api.kperfdata_handle != NULL)
	{
		dlclose(api.kperfdata_handle);
	}
	if (api.kperf_handle != NULL)
	{
		dlclose(api.kperf_handle);
	}
}

static int resolve_event_alias(pmu_state *pmu,
                               const char *display_name,
                               const char *const aliases[],
                               const void **event_out)
{
	for (int i = 0; aliases[i] != NULL; i++)
	{
		if (pmu->api.kpep_db_event(pmu->db, aliases[i], event_out) == 0)
		{
			return 1;
		}
	}

	fprintf(stderr, "bench_pmu: could not resolve PMU event '%s'. Tried:",
	        display_name);
	for (int i = 0; aliases[i] != NULL; i++)
	{
		fprintf(stderr, " %s", aliases[i]);
	}
	fprintf(stderr, "\n");
	return 0;
}

static int pmu_allocate_counter_buffers(pmu_state *pmu)
{
	pmu->before = calloc(pmu->counter_count, sizeof(*pmu->before));
	pmu->after = calloc(pmu->counter_count, sizeof(*pmu->after));
	if (pmu->before == NULL || pmu->after == NULL)
	{
		fprintf(stderr, "bench_pmu: allocation failed\n");
		return 0;
	}

	return 1;
}

static int pmu_enable_kpc(pmu_state *pmu)
{
	if (geteuid() != 0)
	{
		fprintf(stderr,
		        "bench_pmu requires sudo/root for Apple kpc/kperf counters. "
		        "Run with: sudo ./build/bench_pmu\n");
		return 0;
	}

	if (pmu->api.kpc_force_all_ctrs_get(&pmu->original_force_all) == 0)
	{
		pmu->have_original_force_all = 1;
	}

	if (pmu->api.kpc_force_all_ctrs_set(1) != 0 ||
	    pmu->api.kpc_set_counting(pmu->classes) != 0 ||
	    pmu->api.kpc_set_thread_counting(pmu->classes) != 0)
	{
		fprintf(stderr,
		        "bench_pmu: kpc permission/setup failed (errno=%d). "
		        "Run as root with sudo and close other PMU users.\n",
		        errno);
		return 0;
	}

	return 1;
}

static int pmu_setup_fixed_only(pmu_state *pmu)
{
	pmu->fixed_only = 1;
	pmu->classes = KPC_CLASS_FIXED_MASK;
	if (geteuid() != 0)
	{
		fprintf(stderr,
		        "bench_pmu requires sudo/root for Apple kpc/kperf counters. "
		        "Run with: sudo ./build/bench_pmu\n");
		return 0;
	}

	pmu->counter_count = pmu->api.kpc_get_counter_count(pmu->classes);
	pmu->config_count = pmu->api.kpc_get_config_count != NULL
	                        ? pmu->api.kpc_get_config_count(pmu->classes)
	                        : 0;
	if (pmu->counter_count == 0)
	{
		fprintf(stderr,
		        "bench_pmu: kpc returned zero fixed counter count "
		        "(classes=0x%x)\n",
		        pmu->classes);
		return 0;
	}
	if (!pmu_allocate_counter_buffers(pmu))
	{
		return 0;
	}
	return pmu_enable_kpc(pmu);
}

static int pmu_setup_full_kpep(pmu_state *pmu)
{
	static const char *const cycles_aliases[] = {
		"FIXED_CYCLES", "CPU_CYCLES", "CYCLES", NULL,
	};
	static const char *const instructions_aliases[] = {
		"FIXED_INSTRUCTIONS", "INST_RETIRED", "INSTRUCTIONS", NULL,
	};
	static const char *const branches_aliases[] = {
		"INST_BRANCH", "BRANCH_INSTRUCTIONS", "BRANCHES", NULL,
	};
	static const char *const branch_misses_aliases[] = {
		"BRANCH_MISPRED_NONSPEC",
		"BRANCH_MISPRED",
		"BRANCH_MISPREDICTIONS",
		"BRANCH_MISSES",
		NULL,
	};
	const void *events[PMU_EVENT_COUNT];
	uint64_t *kpc_config;

	if (pmu->api.kpc_set_config == NULL ||
	    pmu->api.kpc_get_config_count == NULL)
	{
		fprintf(stderr,
		        "bench_pmu: missing kperf.framework configurable-counter "
		        "symbols; falling back to fixed-only counters\n");
		return pmu_setup_fixed_only(pmu);
	}

	if (!pmu_api_load_kperfdata(&pmu->api))
	{
		fprintf(stderr, "bench_pmu: falling back to fixed-only counters\n");
		return pmu_setup_fixed_only(pmu);
	}

	if (geteuid() != 0)
	{
		fprintf(stderr,
		        "bench_pmu requires sudo/root for Apple kpc/kperf counters. "
		        "Run with: sudo ./build/bench_pmu\n");
		return 0;
	}

	if (pmu->api.kpep_db_create(NULL, &pmu->db) != 0 ||
	    pmu->api.kpep_config_create(pmu->db, &pmu->config) != 0)
	{
		fprintf(stderr, "bench_pmu: kpep database/config creation failed\n");
		return 0;
	}

	if (!resolve_event_alias(pmu, "cycles", cycles_aliases,
	                         &events[PMU_EVENT_CYCLES]) ||
	    !resolve_event_alias(pmu, "instructions", instructions_aliases,
	                         &events[PMU_EVENT_INSTRUCTIONS]) ||
	    !resolve_event_alias(pmu, "branches", branches_aliases,
	                         &events[PMU_EVENT_BRANCHES]) ||
	    !resolve_event_alias(pmu, "branch-misses", branch_misses_aliases,
	                         &events[PMU_EVENT_BRANCH_MISSES]))
	{
		return 0;
	}

	for (size_t i = 0; i < PMU_EVENT_COUNT; i++)
	{
		if (pmu->api.kpep_config_add_event(pmu->config, events[i], 0, NULL) != 0)
		{
			fprintf(stderr, "bench_pmu: kpep_config_add_event failed for index %zu\n",
			        i);
			return 0;
		}
	}

	if (pmu->api.kpep_config_force_counters(pmu->config) != 0 ||
	    pmu->api.kpep_config_kpc_classes(pmu->config, &pmu->classes) != 0)
	{
		fprintf(stderr, "bench_pmu: kpep config finalization failed\n");
		return 0;
	}

	pmu->config_count = pmu->api.kpc_get_config_count(pmu->classes);
	pmu->counter_count = pmu->api.kpc_get_counter_count(pmu->classes);
	if (pmu->config_count == 0 || pmu->counter_count == 0)
	{
		fprintf(stderr,
		        "bench_pmu: kpc returned zero config/counter count "
		        "(classes=0x%x config=%u counters=%u)\n",
		        pmu->classes,
		        pmu->config_count,
		        pmu->counter_count);
		return 0;
	}

	kpc_config = calloc(pmu->config_count, sizeof(*kpc_config));
	if (kpc_config == NULL || !pmu_allocate_counter_buffers(pmu))
	{
		fprintf(stderr, "bench_pmu: allocation failed\n");
		free(kpc_config);
		return 0;
	}

	if (pmu->api.kpep_config_kpc(pmu->config, kpc_config, pmu->config_count) != 0 ||
	    pmu->api.kpep_config_kpc_map(pmu->config, pmu->event_map,
	                                 PMU_EVENT_COUNT) != 0)
	{
		fprintf(stderr, "bench_pmu: kpep KPC register/map extraction failed\n");
		free(kpc_config);
		return 0;
	}

	for (size_t i = 0; i < PMU_EVENT_COUNT; i++)
	{
		if (pmu->event_map[i] >= pmu->counter_count)
		{
			fprintf(stderr,
			        "bench_pmu: event map index %zu out of range "
			        "(counter_count=%u)\n",
			        pmu->event_map[i],
			        pmu->counter_count);
			free(kpc_config);
			return 0;
		}
	}

	if (pmu->api.kpc_set_config(pmu->classes, kpc_config) != 0)
	{
		fprintf(stderr,
		        "bench_pmu: kpc_set_config failed (errno=%d). "
		        "Try PMU_FIXED_ONLY=1 if configurable counters are unavailable.\n",
		        errno);
		free(kpc_config);
		return 0;
	}

	free(kpc_config);
	return pmu_enable_kpc(pmu);
}

static int pmu_setup(pmu_state *pmu)
{
	memset(pmu, 0, sizeof(*pmu));
	for (size_t i = 0; i < PMU_EVENT_COUNT; i++)
	{
		pmu->event_map[i] = (size_t)-1;
	}

	if (!pmu_api_load_kperf(&pmu->api))
	{
		return 0;
	}

	if (PMU_FIXED_ONLY)
	{
		return pmu_setup_fixed_only(pmu);
	}

	return pmu_setup_full_kpep(pmu);
}

static void pmu_teardown(pmu_state *pmu)
{
	if (pmu->api.kpc_set_thread_counting != NULL)
	{
		(void)pmu->api.kpc_set_thread_counting(0);
	}
	if (pmu->api.kpc_set_counting != NULL)
	{
		(void)pmu->api.kpc_set_counting(0);
	}
	if (pmu->api.kpc_force_all_ctrs_set != NULL)
	{
		(void)pmu->api.kpc_force_all_ctrs_set(
		    pmu->have_original_force_all ? pmu->original_force_all : 0);
	}
	if (pmu->api.kpep_config_free != NULL && pmu->config != NULL)
	{
		pmu->api.kpep_config_free(pmu->config);
	}
	if (pmu->api.kpep_db_free != NULL && pmu->db != NULL)
	{
		pmu->api.kpep_db_free(pmu->db);
	}
	if (pmu->api.kperfdata_handle != NULL)
	{
		dlclose(pmu->api.kperfdata_handle);
	}
	if (pmu->api.kperf_handle != NULL)
	{
		dlclose(pmu->api.kperf_handle);
	}
	free(pmu->before);
	free(pmu->after);
}

static int pmu_measure(pmu_state *pmu, target_fn target, uint64_t calls,
                       pmu_counts *out)
{
	memset(out, 0, sizeof(*out));
	if (pmu->api.kpc_get_thread_counters(0, pmu->counter_count, pmu->before) != 0)
	{
		fprintf(stderr, "bench_pmu: kpc_get_thread_counters before failed\n");
		return 0;
	}

	target(calls);

	if (pmu->api.kpc_get_thread_counters(0, pmu->counter_count, pmu->after) != 0)
	{
		fprintf(stderr, "bench_pmu: kpc_get_thread_counters after failed\n");
		return 0;
	}

	if (pmu->fixed_only)
	{
		const size_t n = pmu->counter_count < PMU_EVENT_COUNT
		                     ? pmu->counter_count
		                     : PMU_EVENT_COUNT;

		for (size_t i = 0; i < n; i++)
		{
			out->v[i] = pmu->after[i] - pmu->before[i];
		}
	}
	else
	{
		for (size_t i = 0; i < PMU_EVENT_COUNT; i++)
		{
			const size_t idx = pmu->event_map[i];
			out->v[i] = pmu->after[idx] - pmu->before[idx];
		}
	}

	return 1;
}

static void subtract_counts(pmu_counts *x, const pmu_counts *overhead)
{
	for (size_t i = 0; i < PMU_EVENT_COUNT; i++)
	{
		if (x->v[i] > overhead->v[i])
		{
			x->v[i] -= overhead->v[i];
		}
		else
		{
			x->v[i] = 0;
		}
	}
}

static int compare_double(const void *a, const void *b)
{
	const double x = *(const double *)a;
	const double y = *(const double *)b;

	if (x < y)
	{
		return -1;
	}
	if (x > y)
	{
		return 1;
	}
	return 0;
}

static double median_sorted(const double *x, size_t n)
{
	if (n == 0)
	{
		return 0.0;
	}
	if ((n & 1u) != 0)
	{
		return x[n / 2];
	}
	return (x[n / 2 - 1] + x[n / 2]) * 0.5;
}

static pmu_stats compute_stats(const double *values, size_t n)
{
	pmu_stats stats;
	double *sorted;

	memset(&stats, 0, sizeof(stats));
	if (n == 0)
	{
		return stats;
	}

	sorted = malloc(n * sizeof(*sorted));
	if (sorted == NULL)
	{
		fprintf(stderr, "bench_pmu: allocation failed while computing stats\n");
		return stats;
	}
	memcpy(sorted, values, n * sizeof(*sorted));
	qsort(sorted, n, sizeof(*sorted), compare_double);

	stats.min = sorted[0];
	stats.max = sorted[n - 1];
	stats.median = median_sorted(sorted, n);
	if (n >= 4)
	{
		const double q1 = sorted[n / 4];
		const double q3 = sorted[(3 * n) / 4];
		stats.iqr = q3 - q1;
	}
	else
	{
		stats.iqr = 0.0;
	}
	free(sorted);
	return stats;
}

static void fill_round_rates(pmu_round_result *round, uint64_t calls)
{
	round->cycles_per_call =
	    (double)round->counts.v[PMU_EVENT_CYCLES] / (double)calls;
	round->instructions_per_call =
	    (double)round->counts.v[PMU_EVENT_INSTRUCTIONS] / (double)calls;
}

static void print_stat_line(const char *name, const pmu_stats *stats)
{
	printf("%s_median=%.3f %s_min=%.3f %s_max=%.3f %s_iqr=%.3f\n",
	       name,
	       stats->median,
	       name,
	       stats->min,
	       name,
	       stats->max,
	       name,
	       stats->iqr);
}

static int included_round_start(size_t rounds)
{
	return PMU_DISCARD_FIRST && rounds > 1 ? 1 : 0;
}

static int select_target(const char *mode, target_fn *target)
{
	if (strcmp(mode, "empty") == 0)
	{
		*target = target_empty;
	}
	else if (strcmp(mode, "basemul") == 0)
	{
		*target = target_basemul;
	}
	else if (strcmp(mode, "basemul_add") == 0)
	{
		*target = target_basemul_add;
	}
	else if (strcmp(mode, "ntt") == 0)
	{
		*target = target_ntt;
	}
	else if (strcmp(mode, "invntt") == 0)
	{
		*target = target_invntt;
	}
	else if (strcmp(mode, "kem_dec") == 0)
	{
		*target = target_kem_dec;
	}
	else
	{
		fprintf(stderr,
		        "bench_pmu: unknown PMU_BENCH_MODE='%s' "
		        "(use empty, basemul, basemul_add, ntt, invntt, kem_dec)\n",
		        mode);
		return 0;
	}

	return 1;
}

static void print_counts(const char *label, const char *mode,
                         const pmu_state *pmu,
                         const pmu_counts *counts, uint64_t calls)
{
	const double cycles = (double)counts->v[PMU_EVENT_CYCLES];
	const double instructions = (double)counts->v[PMU_EVENT_INSTRUCTIONS];

	printf("bench=%s mode=%s pmu_mode=%s calls=%llu subtract_empty=%d sink=%u\n",
	       label,
	       mode,
	       pmu->fixed_only ? "fixed" : "kpep",
	       (unsigned long long)calls,
	       PMU_SUBTRACT_EMPTY,
	       (unsigned)g_sink);
	if (pmu->fixed_only)
	{
		printf("fixed_counter_count=%u\n", pmu->counter_count);
		for (uint32_t i = 0; i < pmu->counter_count && i < PMU_EVENT_COUNT; i++)
		{
			printf("fixed[%u]_total=%llu\n",
			       i,
			       (unsigned long long)counts->v[i]);
		}
#if defined(__APPLE__) && defined(__aarch64__)
		printf("fixed[0]_likely_cycles_total=%llu\n",
		       (unsigned long long)counts->v[0]);
		if (pmu->counter_count > 1)
		{
			printf("fixed[1]_likely_instructions_total=%llu\n",
			       (unsigned long long)counts->v[1]);
		}
#endif
	}
	printf("cycles_total=%llu\n",
	       (unsigned long long)counts->v[PMU_EVENT_CYCLES]);
	printf("instructions_total=%llu\n",
	       (unsigned long long)counts->v[PMU_EVENT_INSTRUCTIONS]);
	if (pmu->fixed_only)
	{
		printf("branches_total=unavailable_fixed_only\n");
		printf("branch_misses_total=unavailable_fixed_only\n");
	}
	else
	{
		printf("branches_total=%llu\n",
		       (unsigned long long)counts->v[PMU_EVENT_BRANCHES]);
		printf("branch_misses_total=%llu\n",
		       (unsigned long long)counts->v[PMU_EVENT_BRANCH_MISSES]);
	}
	printf("cycles/call=%.3f\n", cycles / (double)calls);
	printf("instructions/call=%.3f\n", instructions / (double)calls);
	printf("IPC=%.6f\n", cycles > 0.0 ? instructions / cycles : 0.0);
	if (pmu->fixed_only)
	{
		printf("branch_misses/call=unavailable_fixed_only\n");
	}
	else
	{
		printf("branch_misses/call=%.6f\n",
	       (double)counts->v[PMU_EVENT_BRANCH_MISSES] / (double)calls);
	}
}

static size_t median_round_index(const pmu_round_result *rounds,
                                 size_t start, size_t end)
{
	size_t best = start;
	double *cycles;
	double median;

	if (start >= end)
	{
		return 0;
	}

	cycles = malloc((end - start) * sizeof(*cycles));
	if (cycles == NULL)
	{
		fprintf(stderr, "bench_pmu: allocation failed while selecting median\n");
		return start;
	}
	for (size_t i = start; i < end; i++)
	{
		cycles[i - start] = rounds[i].cycles_per_call;
	}
	qsort(cycles, end - start, sizeof(*cycles), compare_double);
	median = median_sorted(cycles, end - start);
	free(cycles);

	for (size_t i = start + 1; i < end; i++)
	{
		const double cur =
		    rounds[i].cycles_per_call > median
		        ? rounds[i].cycles_per_call - median
		        : median - rounds[i].cycles_per_call;
		const double old =
		    rounds[best].cycles_per_call > median
		        ? rounds[best].cycles_per_call - median
		        : median - rounds[best].cycles_per_call;
		if (cur < old)
		{
			best = i;
		}
	}

	return best;
}

static int run_single_rounds(pmu_state *pmu, const char *label,
                             const char *mode, target_fn target,
                             uint64_t calls)
{
	const size_t rounds = PMU_ROUNDS > 0 ? PMU_ROUNDS : 1;
	const size_t start = included_round_start(rounds);
	const size_t included = rounds - start;
	pmu_round_result *results;
	double *cycles;
	double *instructions;
	pmu_stats cycles_stats;
	pmu_stats instructions_stats;
	size_t median_index;

	results = calloc(rounds, sizeof(*results));
	cycles = calloc(included, sizeof(*cycles));
	instructions = calloc(included, sizeof(*instructions));
	if (results == NULL || cycles == NULL || instructions == NULL)
	{
		fprintf(stderr, "bench_pmu: allocation failed\n");
		free(results);
		free(cycles);
		free(instructions);
		return 0;
	}

	for (size_t i = 0; i < rounds; i++)
	{
		pmu_counts overhead;

		if (PMU_SUBTRACT_EMPTY && strcmp(mode, "empty") != 0)
		{
			if (!pmu_measure(pmu, target_empty, calls, &overhead))
			{
				free(results);
				free(cycles);
				free(instructions);
				return 0;
			}
		}
		else
		{
			memset(&overhead, 0, sizeof(overhead));
		}

		if (!pmu_measure(pmu, target, calls, &results[i].counts))
		{
			free(results);
			free(cycles);
			free(instructions);
			return 0;
		}
		consume_output(mode);

		if (PMU_SUBTRACT_EMPTY && strcmp(mode, "empty") != 0)
		{
			subtract_counts(&results[i].counts, &overhead);
		}
		fill_round_rates(&results[i], calls);
		printf("round[%zu] cycles/call=%.3f instructions/call=%.3f%s\n",
		       i,
		       results[i].cycles_per_call,
		       results[i].instructions_per_call,
		       i < start ? " discarded" : "");
	}

	for (size_t i = start; i < rounds; i++)
	{
		cycles[i - start] = results[i].cycles_per_call;
		instructions[i - start] = results[i].instructions_per_call;
	}
	cycles_stats = compute_stats(cycles, included);
	instructions_stats = compute_stats(instructions, included);
	median_index = median_round_index(results, start, rounds);

	print_counts(label, mode, pmu, &results[median_index].counts, calls);
	printf("rounds=%zu discarded_first=%d included_rounds=%zu median_round=%zu\n",
	       rounds,
	       start != 0,
	       included,
	       median_index);
	print_stat_line("cycles/call", &cycles_stats);
	print_stat_line("instructions/call", &instructions_stats);

	free(results);
	free(cycles);
	free(instructions);
	return 1;
}

#if PMU_BASE_COMPARE
static void print_prefixed_stat_line(const char *prefix, const char *name,
                                     const pmu_stats *stats)
{
	printf("%s_%s_median=%.3f %s_%s_min=%.3f %s_%s_max=%.3f "
	       "%s_%s_iqr=%.3f\n",
	       prefix,
	       name,
	       stats->median,
	       prefix,
	       name,
	       stats->min,
	       prefix,
	       name,
	       stats->max,
	       prefix,
	       name,
	       stats->iqr);
}

static int select_compare_targets(const char *mode, const char **op_label,
                                  target_fn *stock, target_fn *gt)
{
	if (strcmp(mode, "base_compare") == 0 ||
	    strcmp(mode, "basemul_compare") == 0)
	{
		*op_label = "basemul";
		*stock = target_stock_basemul;
		*gt = target_gt_basemul;
		return 1;
	}
	if (strcmp(mode, "basemul_add_compare") == 0 ||
	    strcmp(mode, "base_add_compare") == 0)
	{
		*op_label = "basemul_add";
		*stock = target_stock_basemul_add;
		*gt = target_gt_basemul_add;
		return 1;
	}

	fprintf(stderr,
	        "bench_pmu: unknown compare mode '%s' "
	        "(use base_compare or basemul_add_compare)\n",
	        mode);
	return 0;
}

static void print_compare_target_summary(const char *prefix,
                                  const pmu_round_result *results,
                                  size_t rounds,
                                  size_t start)
{
	const size_t included = rounds - start;
	double *cycles;
	double *instructions;
	pmu_stats cycles_stats;
	pmu_stats instructions_stats;

	cycles = calloc(included, sizeof(*cycles));
	instructions = calloc(included, sizeof(*instructions));
	if (cycles == NULL || instructions == NULL)
	{
		fprintf(stderr, "bench_pmu: allocation failed\n");
		free(cycles);
		free(instructions);
		return;
	}
	for (size_t i = start; i < rounds; i++)
	{
		cycles[i - start] = results[i].cycles_per_call;
		instructions[i - start] = results[i].instructions_per_call;
	}
	cycles_stats = compute_stats(cycles, included);
	instructions_stats = compute_stats(instructions, included);

	print_prefixed_stat_line(prefix, "cycles/call", &cycles_stats);
	print_prefixed_stat_line(prefix, "instructions/call", &instructions_stats);

	free(cycles);
	free(instructions);
}

static void print_compare_ratio_summary(const char *name, const double *ratios,
                                        size_t included)
{
	pmu_stats stats = compute_stats(ratios, included);

	printf("paired_%s_ratio_right_over_left_median=%.6f "
	       "paired_%s_ratio_right_over_left_min=%.6f "
	       "paired_%s_ratio_right_over_left_max=%.6f "
	       "paired_%s_ratio_right_over_left_iqr=%.6f\n",
	       name,
	       stats.median,
	       name,
	       stats.min,
	       name,
	       stats.max,
	       name,
	       stats.iqr);
}

static int run_base_compare_rounds(pmu_state *pmu, const char *mode,
                                   uint64_t calls)
{
	const size_t rounds = PMU_ROUNDS > 0 ? PMU_ROUNDS : 1;
	const size_t start = included_round_start(rounds);
	const size_t included = rounds - start;
	const char *op_label;
	target_fn stock;
	target_fn gt;
	pmu_round_result *stock_results;
	pmu_round_result *gt_results;
	double *cycles_ratios;
	double *instructions_ratios;

	if (!select_compare_targets(mode, &op_label, &stock, &gt))
	{
		return 0;
	}

	stock_results = calloc(rounds, sizeof(*stock_results));
	gt_results = calloc(rounds, sizeof(*gt_results));
	cycles_ratios = calloc(included, sizeof(*cycles_ratios));
	instructions_ratios = calloc(included, sizeof(*instructions_ratios));
	if (stock_results == NULL || gt_results == NULL ||
	    cycles_ratios == NULL || instructions_ratios == NULL)
	{
		fprintf(stderr, "bench_pmu: allocation failed\n");
		free(stock_results);
		free(gt_results);
		free(cycles_ratios);
		free(instructions_ratios);
		return 0;
	}

	for (size_t i = 0; i < rounds; i++)
	{
		target_fn first = (i & 1u) == 0 ? stock : gt;
		target_fn second = (i & 1u) == 0 ? gt : stock;
		pmu_round_result *first_result =
		    (i & 1u) == 0 ? &stock_results[i] : &gt_results[i];
		pmu_round_result *second_result =
		    (i & 1u) == 0 ? &gt_results[i] : &stock_results[i];

		if (!pmu_measure(pmu, first, calls, &first_result->counts))
		{
			free(stock_results);
			free(gt_results);
			free(cycles_ratios);
			free(instructions_ratios);
			return 0;
		}
		consume_output(op_label);

		if (!pmu_measure(pmu, second, calls, &second_result->counts))
		{
			free(stock_results);
			free(gt_results);
			free(cycles_ratios);
			free(instructions_ratios);
			return 0;
		}
		consume_output(op_label);

		fill_round_rates(&stock_results[i], calls);
		fill_round_rates(&gt_results[i], calls);
		if (i >= start)
		{
			cycles_ratios[i - start] =
			    stock_results[i].cycles_per_call > 0.0
			        ? gt_results[i].cycles_per_call /
			              stock_results[i].cycles_per_call
			        : 0.0;
			instructions_ratios[i - start] =
			    stock_results[i].instructions_per_call > 0.0
			        ? gt_results[i].instructions_per_call /
			              stock_results[i].instructions_per_call
			        : 0.0;
		}
		printf("round[%zu] order=%s-first "
		       "left_cycles/call=%.3f right_cycles/call=%.3f "
		       "left_instructions/call=%.3f right_instructions/call=%.3f "
		       "paired_cycles_ratio_right/left=%.6f "
		       "paired_instructions_ratio_right/left=%.6f%s\n",
		       i,
		       (i & 1u) == 0 ? "left" : "right",
		       stock_results[i].cycles_per_call,
		       gt_results[i].cycles_per_call,
		       stock_results[i].instructions_per_call,
		       gt_results[i].instructions_per_call,
		       stock_results[i].cycles_per_call > 0.0
		           ? gt_results[i].cycles_per_call /
		                 stock_results[i].cycles_per_call
		           : 0.0,
		       stock_results[i].instructions_per_call > 0.0
		           ? gt_results[i].instructions_per_call /
		                 stock_results[i].instructions_per_call
		           : 0.0,
		       i < start ? " discarded" : "");
	}

	printf("bench=%s mode=%s pmu_mode=%s calls=%llu rounds=%zu "
	       "discarded_first=%d included_rounds=%zu left=%s right=%s "
	       "sink=%llu\n",
	       PMU_BENCH_LABEL,
	       mode,
	       pmu->fixed_only ? "fixed" : "kpep",
	       (unsigned long long)calls,
	       rounds,
	       start != 0,
	       included,
	       PMU_COMPARE_LEFT_LABEL,
	       PMU_COMPARE_RIGHT_LABEL,
	       (unsigned long long)g_sink);
	print_compare_target_summary("left", stock_results, rounds, start);
	print_compare_target_summary("right", gt_results, rounds, start);
	print_compare_ratio_summary("cycles", cycles_ratios, included);
	print_compare_ratio_summary("instructions", instructions_ratios, included);

	free(stock_results);
	free(gt_results);
	free(cycles_ratios);
	free(instructions_ratios);
	return 1;
}
#endif

int main(void)
{
	const char *mode = PMU_BENCH_MODE;
	target_fn target;
	pmu_state pmu;
	const uint64_t calls = PMU_BENCH_CALLS;

#if !defined(__APPLE__) || !defined(__aarch64__)
	fprintf(stderr, "bench_pmu is only supported on macOS Apple Silicon.\n");
	return 1;
#else
	if (PMU_SYMBOLS_ONLY)
	{
		print_pmu_symbol_diagnostics();
		return 0;
	}

#if PMU_BASE_COMPARE
	if (strcmp(mode, "base_compare") != 0 &&
	    strcmp(mode, "basemul_compare") != 0 &&
	    strcmp(mode, "basemul_add_compare") != 0 &&
	    strcmp(mode, "base_add_compare") != 0 &&
	    !select_target(mode, &target))
	{
		return 1;
	}
#else
	if (!select_target(mode, &target))
	{
		return 1;
	}
#endif

	setup_inputs();
	if (strcmp(mode, "invntt") == 0 && !check_invntt_roundtrip())
	{
		return 1;
	}
	if (strcmp(mode, "kem_dec") == 0 && !setup_kem())
	{
		return 1;
	}

	(void)setup_thread_policy();

	for (int i = 0; i < PMU_BENCH_WARMUP; i++)
	{
#if PMU_BASE_COMPARE
		if (strcmp(mode, "base_compare") == 0 ||
		    strcmp(mode, "basemul_compare") == 0)
		{
			target_stock_basemul(1);
			target_gt_basemul(1);
		}
		else if (strcmp(mode, "basemul_add_compare") == 0 ||
		         strcmp(mode, "base_add_compare") == 0)
		{
			target_stock_basemul_add(1);
			target_gt_basemul_add(1);
		}
		else
		{
			target(1);
		}
#else
		target(1);
#endif
	}
	consume_output(mode);

	if (!pmu_setup(&pmu))
	{
		return 1;
	}

#if PMU_BASE_COMPARE
	if (strcmp(mode, "base_compare") == 0 ||
	    strcmp(mode, "basemul_compare") == 0 ||
	    strcmp(mode, "basemul_add_compare") == 0 ||
	    strcmp(mode, "base_add_compare") == 0)
	{
		const int ok = run_base_compare_rounds(&pmu, mode, calls);

		pmu_teardown(&pmu);
		return ok ? 0 : 1;
	}
#endif

	if (!run_single_rounds(&pmu, PMU_BENCH_LABEL, mode, target, calls))
	{
		pmu_teardown(&pmu);
		return 1;
	}
	pmu_teardown(&pmu);
	return 0;
#endif
}
