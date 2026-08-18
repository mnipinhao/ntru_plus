#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <limits.h>
#include <linux/perf_event.h>
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

#define WORDS GT32_TILE4_POLY_WORDS
#define STAGES 18U

typedef struct {
	uint8_t primary[sizeof(int16_t) * WORDS];
	uint8_t secondary[NTRUPLUS_POLYBYTES];
	uint8_t ss[NTRUPLUS_SSBYTES];
} snapshot_t;

typedef int (*prefix_fn)(unsigned, snapshot_t *);

typedef struct {
	int fd[4];
	uint64_t value[4];
	uint64_t time_enabled;
	uint64_t time_running;
} pmu_group_t;

static uint8_t pk[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t sk[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t coins[NTRUPLUS_N / 8] __attribute__((aligned(64)));
static int16_t edge_h[WORDS] __attribute__((aligned(64)));
static int16_t edge_r[WORDS] __attribute__((aligned(64)));
static int16_t edge_m[WORDS] __attribute__((aligned(64)));
static int16_t edge_c[WORDS] __attribute__((aligned(64)));
static uint8_t edge_bytes[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
static volatile uint64_t sink;

/* Shared-stage waterfall state.  This deliberately removes compiler-created
 * differences between duplicated "shared" source blocks: prework and middle
 * glue are one physical symbol for both predecessors. */
static uint8_t wf_msg[HASH_H_INBYTES] __attribute__((aligned(64)));
static uint8_t wf_buf[HASH_H_OUTBYTES] __attribute__((aligned(64)));
static uint8_t wf_rhat[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
static uint8_t wf_ss[NTRUPLUS_SSBYTES] __attribute__((aligned(64)));
static poly wf_coeff_r __attribute__((aligned(64)));
static poly wf_coeff_m __attribute__((aligned(64)));
static poly wf_off_h __attribute__((aligned(64)));
static poly wf_off_r __attribute__((aligned(64)));
static poly wf_off_m __attribute__((aligned(64)));
static poly wf_off_c __attribute__((aligned(64)));
static int16_t wf_gt_h[WORDS] __attribute__((aligned(64)));
static int16_t wf_gt_r[WORDS] __attribute__((aligned(64)));
static int16_t wf_gt_m[WORDS] __attribute__((aligned(64)));
static int16_t wf_gt_c[WORDS] __attribute__((aligned(64)));
static int16_t wf_gt_work[WORDS] __attribute__((aligned(64)));

static const char *const stage_names[STAGES + 1] = {
	"", "L01_decode_h", "L02_copy_coins", "L03_hash_f",
	"L04_hash_h", "L05_cbd_r", "L06_forward_r",
	"L07_serialize_rhat", "L08_hash_g", "L09_sotp_m",
	"L10_forward_m", "L11_basemul", "L12_add_m",
	"L13_serialize_ct", "L14_copy_ss", "L15_clear_msg",
	"L16_clear_buf", "L17_clear_r", "L18_clear_m"
};

static int perf_event_open_local(struct perf_event_attr *attributes,
	int group_fd)
{
	const long result = syscall(SYS_perf_event_open, attributes, 0, -1,
		group_fd, 0UL);
	return result < 0 || result > INT_MAX ? -1 : (int)result;
}

static int read_cpu_core_type(uint32_t *type)
{
	char text[32];
	char *end;
	unsigned long value;
	ssize_t length;
	const int fd = open("/sys/bus/event_source/devices/cpu_core/type",
		O_RDONLY);
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

static int open_pmu(pmu_group_t *group)
{
	uint32_t types[4];
	uint64_t configs[4];
	const char *mode = getenv("ENCAP_PMU_GROUP");
	uint32_t core_type;
	int leader = -1;

	memset(group, 0, sizeof *group);
	for (size_t i = 0; i < 4; i++)
		group->fd[i] = -1;
	if (read_cpu_core_type(&core_type) != 0)
		return -1;
	types[0] = PERF_TYPE_HARDWARE;
	configs[0] = PERF_COUNT_HW_CPU_CYCLES;
	if (mode != NULL && strcmp(mode, "cache") == 0) {
		types[1] = core_type;
		types[2] = core_type;
		types[3] = core_type;
		configs[1] = 0x81d0;     /* mem_inst_retired.all_loads */
		configs[2] = 0x08d1;     /* mem_load_retired.l1_miss */
		configs[3] = 0x10d1;     /* mem_load_retired.l2_miss */
	} else if (mode != NULL && strcmp(mode, "stalls") == 0) {
		types[1] = core_type;
		types[2] = core_type;
		types[3] = core_type;
		configs[1] = 0x050021a6; /* exe_activity.bound_on_loads */
		configs[2] = 0x01000148; /* l1d_pend_miss.pending_cycles */
		configs[3] = 0x02a4;     /* topdown.backend_bound_slots */
	} else if (mode != NULL && strcmp(mode, "blocks") == 0) {
		types[1] = core_type;
		types[2] = core_type;
		types[3] = core_type;
		configs[1] = 0x8203;     /* ld_blocks.store_forward */
		configs[2] = 0x0403;     /* ld_blocks.address_alias */
		configs[3] = 0x08a2;     /* resource_stalls.sb */
	} else if (mode != NULL && strcmp(mode, "frontend") == 0) {
		types[1] = core_type;
		types[2] = core_type;
		types[3] = core_type;
		configs[1] = 0x0879;     /* idq.dsb_uops */
		configs[2] = 0x0479;     /* idq.mite_uops */
		configs[3] = 0x019c;     /* idq_uops_not_delivered.core */
	} else if (mode != NULL && strcmp(mode, "frontend_ms") == 0) {
		types[1] = core_type;
		types[2] = core_type;
		types[3] = core_type;
		configs[1] = 0x0879;     /* idq.dsb_uops */
		configs[2] = 0x0479;     /* idq.mite_uops */
		configs[3] = 0x2079;     /* idq.ms_uops */
	} else if (mode != NULL && strcmp(mode, "branch") == 0) {
		types[1] = PERF_TYPE_HARDWARE;
		types[2] = PERF_TYPE_HARDWARE;
		types[3] = PERF_TYPE_HARDWARE;
		configs[1] = PERF_COUNT_HW_BRANCH_INSTRUCTIONS;
		configs[2] = PERF_COUNT_HW_BRANCH_MISSES;
		configs[3] = PERF_COUNT_HW_REF_CPU_CYCLES;
	} else {
		types[1] = PERF_TYPE_HARDWARE;
		types[2] = core_type;
		types[3] = core_type;
		configs[1] = PERF_COUNT_HW_INSTRUCTIONS;
		configs[2] = 0x81d0;     /* mem_inst_retired.all_loads */
		configs[3] = 0x82d0;     /* mem_inst_retired.all_stores */
	}
	for (size_t i = 0; i < 4; i++) {
		struct perf_event_attr attributes;
		memset(&attributes, 0, sizeof attributes);
		attributes.type = types[i];
		attributes.size = sizeof attributes;
		attributes.config = configs[i];
		attributes.disabled = i == 0 ? 1U : 0U;
		attributes.exclude_kernel = 1U;
		attributes.exclude_hv = 1U;
		if (i == 0)
			attributes.read_format = PERF_FORMAT_GROUP
				| PERF_FORMAT_TOTAL_TIME_ENABLED
				| PERF_FORMAT_TOTAL_TIME_RUNNING;
		group->fd[i] = perf_event_open_local(&attributes, leader);
		if (group->fd[i] < 0)
			return -1;
		if (i == 0)
			leader = group->fd[i];
	}
	return 0;
}

static void close_pmu(pmu_group_t *group)
{
	for (size_t i = 0; i < 4; i++)
		if (group->fd[i] >= 0)
			(void)close(group->fd[i]);
}

static int start_pmu(pmu_group_t *group)
{
	return ioctl(group->fd[0], PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP) == 0
		&& ioctl(group->fd[0], PERF_EVENT_IOC_ENABLE,
			PERF_IOC_FLAG_GROUP) == 0 ? 0 : -1;
}

static int stop_pmu(pmu_group_t *group)
{
	uint64_t data[7];
	if (ioctl(group->fd[0], PERF_EVENT_IOC_DISABLE,
		PERF_IOC_FLAG_GROUP) != 0)
		return -1;
	if (read(group->fd[0], data, sizeof data) != (ssize_t)sizeof data
		|| data[0] != 4U)
		return -1;
	group->time_enabled = data[1];
	group->time_running = data[2];
	for (size_t i = 0; i < 4; i++)
		group->value[i] = data[3U + i];
	return 0;
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

static void forward_gt(int16_t *out, int16_t *work, const int16_t *in)
{
	gt32_tile4_frontend_wide_raw_asm(work, in);
	gt32_tile4_attr_forward_all_bm_soa_asm(out, work);
}

static void snap_bytes(snapshot_t *snapshot, const void *input, size_t length)
{
	if (snapshot != NULL)
		memcpy(snapshot->primary, input, length);
}

static void snap_coeff(snapshot_t *snapshot, const int16_t *input)
{
	snap_bytes(snapshot, input, sizeof(int16_t) * WORDS);
}

__attribute__((always_inline)) static inline int official_prefix(
	unsigned stop, snapshot_t *snapshot)
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	uint8_t rhat[NTRUPLUS_POLYBYTES];
	uint8_t ss[NTRUPLUS_SSBYTES];
	poly c, h, r, m;

	if (poly_frombytes(&h, pk) != 0)
		return 1;
	if (stop == 1) {
		if (snapshot != NULL)
			poly_tobytes(snapshot->primary, &h);
		sink += (uint16_t)h.coeffs[0];
		return 0;
	}

	memcpy(msg, coins, NTRUPLUS_N / 8);
	if (stop == 2) {
		snap_bytes(snapshot, msg, NTRUPLUS_N / 8);
		sink += msg[0];
		return 0;
	}

	hash_f(msg + NTRUPLUS_N / 8, pk);
	if (stop == 3) {
		snap_bytes(snapshot, msg, sizeof msg);
		sink += msg[NTRUPLUS_N / 8];
		return 0;
	}

	hash_h(buf, msg);
	if (stop == 4) {
		snap_bytes(snapshot, buf, sizeof buf);
		sink += buf[0];
		return 0;
	}

	poly_cbd1(&r, buf + NTRUPLUS_SYMBYTES);
	if (stop == 5) {
		snap_coeff(snapshot, r.coeffs);
		sink += (uint16_t)r.coeffs[0];
		return 0;
	}

	poly_ntt(&r);
	if (stop == 6) {
		if (snapshot != NULL)
			poly_tobytes(snapshot->primary, &r);
		sink += (uint16_t)r.coeffs[0];
		return 0;
	}

	poly_tobytes(rhat, &r);
	if (stop == 7) {
		snap_bytes(snapshot, rhat, sizeof rhat);
		sink += rhat[0];
		return 0;
	}

	hash_g(rhat, rhat);
	if (stop == 8) {
		snap_bytes(snapshot, rhat, HASH_G_OUTBYTES);
		sink += rhat[0];
		return 0;
	}

	poly_sotp_encode(&m, msg, rhat);
	if (stop == 9) {
		snap_coeff(snapshot, m.coeffs);
		sink += (uint16_t)m.coeffs[0];
		return 0;
	}

	poly_ntt(&m);
	if (stop == 10) {
		if (snapshot != NULL)
			poly_tobytes(snapshot->primary, &m);
		sink += (uint16_t)m.coeffs[0];
		return 0;
	}

	poly_basemul(&c, &h, &r);
	if (stop == 11) {
		if (snapshot != NULL)
			poly_tobytes(snapshot->primary, &c);
		sink += (uint16_t)c.coeffs[0];
		return 0;
	}

	poly_add(&c, &c, &m);
	if (stop == 12) {
		if (snapshot != NULL)
			poly_tobytes(snapshot->primary, &c);
		sink += (uint16_t)c.coeffs[0];
		return 0;
	}

	poly_tobytes(rhat, &c);
	if (stop == 13) {
		snap_bytes(snapshot, rhat, sizeof rhat);
		sink += rhat[0];
		return 0;
	}

	memcpy(ss, buf, sizeof ss);
	if (stop == 14) {
		if (snapshot != NULL) {
			memcpy(snapshot->primary, rhat, sizeof rhat);
			memcpy(snapshot->ss, ss, sizeof ss);
		}
		sink += ss[0];
		return 0;
	}

	secure_clear(msg, sizeof msg);
	if (stop == 15) {
		snap_bytes(snapshot, msg, sizeof msg);
		sink += msg[0];
		return 0;
	}

	secure_clear(buf, sizeof buf);
	if (stop == 16) {
		snap_bytes(snapshot, buf, sizeof buf);
		sink += buf[0];
		return 0;
	}

	secure_clear(&r, sizeof r);
	if (stop == 17) {
		snap_coeff(snapshot, r.coeffs);
		sink += (uint16_t)r.coeffs[0];
		return 0;
	}

	secure_clear(&m, sizeof m);
	snap_coeff(snapshot, m.coeffs);
	sink += (uint16_t)m.coeffs[0];
	return 0;
}

__attribute__((always_inline)) static inline int gt_prefix_variant(
	unsigned stop, snapshot_t *snapshot, unsigned flags)
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	uint8_t rhat[NTRUPLUS_POLYBYTES];
	uint8_t ss[NTRUPLUS_SSBYTES];
	int16_t h[WORDS] __attribute__((aligned(64)));
	int16_t r[WORDS] __attribute__((aligned(64)));
	int16_t m[WORDS] __attribute__((aligned(64)));
	int16_t c[WORDS] __attribute__((aligned(64)));
	int16_t work[WORDS] __attribute__((aligned(64)));

	if (gt32_q24_decode_soa_asm(h, pk) != 0)
		return 1;
	if (stop == 1) {
		if (snapshot != NULL)
			gt32_q24_encode_soa_asm(snapshot->primary, h);
		sink += (uint16_t)h[0];
		return 0;
	}

	memcpy(msg, coins, NTRUPLUS_N / 8);
	if (stop == 2) {
		snap_bytes(snapshot, msg, NTRUPLUS_N / 8);
		sink += msg[0];
		return 0;
	}

	hash_f(msg + NTRUPLUS_N / 8, pk);
	if (stop == 3) {
		snap_bytes(snapshot, msg, sizeof msg);
		sink += msg[NTRUPLUS_N / 8];
		return 0;
	}

	hash_h(buf, msg);
	if (stop == 4) {
		snap_bytes(snapshot, buf, sizeof buf);
		sink += buf[0];
		return 0;
	}

	poly_cbd1((poly *)(void *)work, buf + NTRUPLUS_SYMBYTES);
	if (stop == 5) {
		snap_coeff(snapshot, work);
		sink += (uint16_t)work[0];
		return 0;
	}

	forward_gt(r, c, work);
	if (stop == 6) {
		if (snapshot != NULL)
			gt32_q24_encode_soa_lazy10788_asm(snapshot->primary, r);
		sink += (uint16_t)r[0];
		return 0;
	}

	if ((flags & 2U) != 0U)
		gt32_q24_encode_soa_lazy10788_rr_asm(rhat, r);
	else
		gt32_q24_encode_soa_lazy10788_asm(rhat, r);
	if (stop == 7) {
		snap_bytes(snapshot, rhat, sizeof rhat);
		sink += rhat[0];
		return 0;
	}

	hash_g(rhat, rhat);
	if (stop == 8) {
		snap_bytes(snapshot, rhat, HASH_G_OUTBYTES);
		sink += rhat[0];
		return 0;
	}

	poly_sotp_encode((poly *)(void *)work, msg, rhat);
	if (stop == 9) {
		snap_coeff(snapshot, work);
		sink += (uint16_t)work[0];
		return 0;
	}

	forward_gt(m, c, work);
	if (stop == 10) {
		if (snapshot != NULL)
			gt32_q24_encode_soa_lazy10788_asm(snapshot->primary, m);
		sink += (uint16_t)m[0];
		return 0;
	}

	if ((flags & 1U) != 0U && stop >= 12)
		gt32_tile4_basemul_general_soa_soa_add_m_asm(c, h, r, m);
	else
		gt32_tile4_basemul_general_soa_soa_to_soa_asm(c, h, r);
	if (stop == 11) {
		if (snapshot != NULL)
			gt32_q24_encode_soa_encap_hr_h1_asm(snapshot->primary, c);
		sink += (uint16_t)c[0];
		return 0;
	}

	if ((flags & 1U) == 0U)
		poly_add((poly *)(void *)c, (const poly *)(const void *)c,
			(const poly *)(const void *)m);
	if (stop == 12) {
		if (snapshot != NULL)
			gt32_q24_encode_soa_encap_hr_h1_asm(snapshot->primary, c);
		sink += (uint16_t)c[0];
		return 0;
	}

	if ((flags & 2U) != 0U)
		gt32_q24_encode_soa_lazy10788_rr_asm(rhat, c);
	else
		gt32_q24_encode_soa_encap_hr_h1_asm(rhat, c);
	if (stop == 13) {
		snap_bytes(snapshot, rhat, sizeof rhat);
		sink += rhat[0];
		return 0;
	}

	memcpy(ss, buf, sizeof ss);
	if (stop == 14) {
		if (snapshot != NULL) {
			memcpy(snapshot->primary, rhat, sizeof rhat);
			memcpy(snapshot->ss, ss, sizeof ss);
		}
		sink += ss[0];
		return 0;
	}

	secure_clear(msg, sizeof msg);
	if (stop == 15) {
		snap_bytes(snapshot, msg, sizeof msg);
		sink += msg[0];
		return 0;
	}

	secure_clear(buf, sizeof buf);
	if (stop == 16) {
		snap_bytes(snapshot, buf, sizeof buf);
		sink += buf[0];
		return 0;
	}

	secure_clear(r, sizeof r);
	if (stop == 17) {
		snap_coeff(snapshot, r);
		sink += (uint16_t)r[0];
		return 0;
	}

	secure_clear(m, sizeof m);
	snap_coeff(snapshot, m);
	sink += (uint16_t)m[0];
	return 0;
}

__attribute__((always_inline)) static inline int gt_prefix(
	unsigned stop, snapshot_t *snapshot)
{
	return gt_prefix_variant(stop, snapshot, 0);
}

/* Constant-cut wrappers let GCC remove all later stages and runtime stop
 * branches.  The generic 18-stage prefix remains the differential oracle. */
#define WATERFALL_WRAPPER(name, implementation, cut) \
	static int name(unsigned ignored, snapshot_t *snapshot) \
	{ \
		(void)ignored; \
		return implementation(cut, snapshot); \
	}
WATERFALL_WRAPPER(wf_off_D0, official_prefix, 1U)
WATERFALL_WRAPPER(wf_off_E0, official_prefix, 5U)
WATERFALL_WRAPPER(wf_off_E1, official_prefix, 7U)
WATERFALL_WRAPPER(wf_off_E2, official_prefix, 9U)
WATERFALL_WRAPPER(wf_off_E3, official_prefix, 13U)
WATERFALL_WRAPPER(wf_off_E4, official_prefix, 18U)
WATERFALL_WRAPPER(wf_gt_D0, gt_prefix, 1U)
WATERFALL_WRAPPER(wf_gt_E0, gt_prefix, 5U)
WATERFALL_WRAPPER(wf_gt_E1, gt_prefix, 7U)
WATERFALL_WRAPPER(wf_gt_E2, gt_prefix, 9U)
WATERFALL_WRAPPER(wf_gt_E3, gt_prefix, 13U)
WATERFALL_WRAPPER(wf_gt_E4, gt_prefix, 18U)
#undef WATERFALL_WRAPPER

static const char *const waterfall_names[6] = {
	"D0_decode", "E0_prework", "E1_prefix", "E2_middle", "E3_poly", "E4_full"
};
static prefix_fn const waterfall_official[6] = {
	wf_off_D0, wf_off_E0, wf_off_E1, wf_off_E2, wf_off_E3, wf_off_E4
};
static prefix_fn const waterfall_gt[6] = {
	wf_gt_D0, wf_gt_E0, wf_gt_E1, wf_gt_E2, wf_gt_E3, wf_gt_E4
};

/*
 * Causal outside-island waterfall.  Unlike the constant-cut wrappers above,
 * the shared work here is one physical function, not two compiler-generated
 * copies of the same source.  This makes architectural work deltas exact.
 * Latency is tested separately by transition_tsc(), because subtracting two
 * independently measured cumulative prefixes is not an additive timing model.
 */
#define WF_SHARED __attribute__((noinline, noclone))

WF_SHARED static int wf2_decode_official(void)
{
	return poly_frombytes(&wf_off_h, pk);
}

WF_SHARED static int wf2_decode_gt(void)
{
	return gt32_q24_decode_soa_asm(wf_gt_h, pk);
}

WF_SHARED static void wf2_shared_prework(void)
{
	memcpy(wf_msg, coins, NTRUPLUS_N / 8);
	hash_f(wf_msg + NTRUPLUS_N / 8, pk);
	hash_h(wf_buf, wf_msg);
	poly_cbd1(&wf_coeff_r, wf_buf + NTRUPLUS_SYMBYTES);
}

WF_SHARED static void wf2_rpath_official(void)
{
	wf_off_r = wf_coeff_r;
	poly_ntt(&wf_off_r);
	poly_tobytes(wf_rhat, &wf_off_r);
}

WF_SHARED static void wf2_rpath_gt(void)
{
	forward_gt(wf_gt_r, wf_gt_work, wf_coeff_r.coeffs);
	gt32_q24_encode_soa_lazy10788_asm(wf_rhat, wf_gt_r);
}

WF_SHARED static void wf2_shared_middle(void)
{
	hash_g(wf_rhat, wf_rhat);
	poly_sotp_encode(&wf_coeff_m, wf_msg, wf_rhat);
}

WF_SHARED static void wf2_final_official(void)
{
	wf_off_m = wf_coeff_m;
	poly_ntt(&wf_off_m);
	poly_basemul(&wf_off_c, &wf_off_h, &wf_off_r);
	poly_add(&wf_off_c, &wf_off_c, &wf_off_m);
	poly_tobytes(wf_rhat, &wf_off_c);
}

WF_SHARED static void wf2_final_gt(void)
{
	forward_gt(wf_gt_m, wf_gt_work, wf_coeff_m.coeffs);
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(
		wf_gt_c, wf_gt_h, wf_gt_r);
	poly_add((poly *)(void *)wf_gt_c, (const poly *)(const void *)wf_gt_c,
		(const poly *)(const void *)wf_gt_m);
	gt32_q24_encode_soa_encap_hr_h1_asm(wf_rhat, wf_gt_c);
}

WF_SHARED static void wf2_shared_tail(void)
{
	memcpy(wf_ss, wf_buf, sizeof wf_ss);
	secure_clear(wf_msg, sizeof wf_msg);
	secure_clear(wf_buf, sizeof wf_buf);
}

WF_SHARED static void wf2_clear_official(void)
{
	secure_clear(&wf_off_r, sizeof wf_off_r);
	secure_clear(&wf_off_m, sizeof wf_off_m);
}

WF_SHARED static void wf2_clear_gt(void)
{
	secure_clear(wf_gt_r, sizeof wf_gt_r);
	secure_clear(wf_gt_m, sizeof wf_gt_m);
}

__attribute__((always_inline)) static inline int wf2_run(
	unsigned cut, int use_gt, snapshot_t *snapshot)
{
	if ((use_gt ? wf2_decode_gt() : wf2_decode_official()) != 0)
		return 1;
	if (cut == 0U) {
		if (snapshot != NULL) {
			if (use_gt)
				gt32_q24_encode_soa_asm(snapshot->primary, wf_gt_h);
			else
				poly_tobytes(snapshot->primary, &wf_off_h);
		}
		sink += use_gt ? (uint16_t)wf_gt_h[0]
			: (uint16_t)wf_off_h.coeffs[0];
		return 0;
	}

	wf2_shared_prework();
	if (cut == 1U) {
		snap_coeff(snapshot, wf_coeff_r.coeffs);
		sink += (uint16_t)wf_coeff_r.coeffs[0];
		return 0;
	}

	if (use_gt)
		wf2_rpath_gt();
	else
		wf2_rpath_official();
	if (cut == 2U) {
		snap_bytes(snapshot, wf_rhat, sizeof wf_rhat);
		sink += wf_rhat[0];
		return 0;
	}

	wf2_shared_middle();
	if (cut == 3U) {
		snap_coeff(snapshot, wf_coeff_m.coeffs);
		sink += (uint16_t)wf_coeff_m.coeffs[0];
		return 0;
	}

	if (use_gt)
		wf2_final_gt();
	else
		wf2_final_official();
	if (cut == 4U) {
		snap_bytes(snapshot, wf_rhat, sizeof wf_rhat);
		sink += wf_rhat[0];
		return 0;
	}

	wf2_shared_tail();
	if (use_gt)
		wf2_clear_gt();
	else
		wf2_clear_official();
	if (snapshot != NULL) {
		memcpy(snapshot->primary, wf_rhat, sizeof wf_rhat);
		memcpy(snapshot->ss, wf_ss, sizeof wf_ss);
	}
	sink += wf_ss[0];
	return 0;
}

#define WATERFALL2_WRAPPER(name, use_gt, cut) \
	static int name(unsigned ignored, snapshot_t *snapshot) \
	{ \
		(void)ignored; \
		return wf2_run(cut, use_gt, snapshot); \
	}
WATERFALL2_WRAPPER(wf2_off_D0, 0, 0U)
WATERFALL2_WRAPPER(wf2_off_E0, 0, 1U)
WATERFALL2_WRAPPER(wf2_off_E1, 0, 2U)
WATERFALL2_WRAPPER(wf2_off_E2, 0, 3U)
WATERFALL2_WRAPPER(wf2_off_E3, 0, 4U)
WATERFALL2_WRAPPER(wf2_off_E4, 0, 5U)
WATERFALL2_WRAPPER(wf2_gt_D0, 1, 0U)
WATERFALL2_WRAPPER(wf2_gt_E0, 1, 1U)
WATERFALL2_WRAPPER(wf2_gt_E1, 1, 2U)
WATERFALL2_WRAPPER(wf2_gt_E2, 1, 3U)
WATERFALL2_WRAPPER(wf2_gt_E3, 1, 4U)
WATERFALL2_WRAPPER(wf2_gt_E4, 1, 5U)
#undef WATERFALL2_WRAPPER

static prefix_fn const waterfall2_official[6] = {
	wf2_off_D0, wf2_off_E0, wf2_off_E1, wf2_off_E2, wf2_off_E3, wf2_off_E4
};
static prefix_fn const waterfall2_gt[6] = {
	wf2_gt_D0, wf2_gt_E0, wf2_gt_E1, wf2_gt_E2, wf2_gt_E3, wf2_gt_E4
};

static int check_waterfall2(void)
{
	for (unsigned cut = 0; cut < 6U; cut++) {
		snapshot_t official;
		snapshot_t gt;
		memset(&official, 0, sizeof official);
		memset(&gt, 0, sizeof gt);
		if (waterfall2_official[cut](0, &official) != 0 ||
			waterfall2_gt[cut](0, &gt) != 0 ||
			memcmp(&official, &gt, sizeof official) != 0) {
			fprintf(stderr, "waterfall2 mismatch at %s\n",
				waterfall_names[cut]);
			return 0;
		}
	}
	return 1;
}

typedef void (*wf2_void_fn)(void);

WF_SHARED static void wf2_setup_prework_official(void)
{
	(void)wf2_decode_official();
}

WF_SHARED static void wf2_setup_prework_gt(void)
{
	(void)wf2_decode_gt();
}

WF_SHARED static void wf2_setup_middle_official(void)
{
	(void)wf2_decode_official();
	wf2_shared_prework();
	wf2_rpath_official();
}

WF_SHARED static void wf2_setup_middle_gt(void)
{
	(void)wf2_decode_gt();
	wf2_shared_prework();
	wf2_rpath_gt();
}

WF_SHARED static void wf2_setup_tail_official(void)
{
	wf2_setup_middle_official();
	wf2_shared_middle();
	wf2_final_official();
}

WF_SHARED static void wf2_setup_tail_gt(void)
{
	wf2_setup_middle_gt();
	wf2_shared_middle();
	wf2_final_gt();
}

static int compare_double(const void *left, const void *right)
{
	const double a = *(const double *)left;
	const double b = *(const double *)right;
	return (a > b) - (a < b);
}

static int transition_tsc(const char *stage, int use_gt, unsigned iterations)
{
	wf2_void_fn setup;
	wf2_void_fn consumer;
	double samples[101];
	const unsigned batches = 101U;
	const unsigned per_batch = iterations / batches != 0U
		? iterations / batches : 1U;

	if (strcmp(stage, "shared_prework") == 0) {
		setup = use_gt ? wf2_setup_prework_gt : wf2_setup_prework_official;
		consumer = wf2_shared_prework;
	} else if (strcmp(stage, "middle_glue") == 0) {
		setup = use_gt ? wf2_setup_middle_gt : wf2_setup_middle_official;
		consumer = wf2_shared_middle;
	} else if (strcmp(stage, "shared_tail") == 0) {
		setup = use_gt ? wf2_setup_tail_gt : wf2_setup_tail_official;
		consumer = wf2_shared_tail;
	} else {
		fprintf(stderr, "unknown transition: %s\n", stage);
		return 2;
	}

	for (unsigned i = 0; i < 100U; i++) {
		setup();
		consumer();
	}
	for (unsigned batch = 0; batch < batches; batch++) {
		uint64_t total = 0;
		for (unsigned i = 0; i < per_batch; i++) {
			uint64_t begin;
			setup();
			begin = start_tsc();
			consumer();
			total += stop_tsc() - begin;
		}
		samples[batch] = (double)total / per_batch;
	}
	qsort(samples, batches, sizeof samples[0], compare_double);
	printf("TRANSITION,%s,%s,%.9f,%u,%u\n", stage,
		use_gt ? "gt" : "official", samples[batches / 2U],
		batches, per_batch);
	return 0;
}
#undef WF_SHARED

static int gt_fused_prefix(unsigned stop, snapshot_t *snapshot)
{
	return gt_prefix_variant(stop, snapshot, 1);
}

static int gt_rr_prefix(unsigned stop, snapshot_t *snapshot)
{
	return gt_prefix_variant(stop, snapshot, 2);
}

static int prepare_bm_add_edge(void)
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	uint8_t rhat[NTRUPLUS_POLYBYTES];
	int16_t scratch[WORDS] __attribute__((aligned(64)));
	int16_t work[WORDS] __attribute__((aligned(64)));

	if (gt32_q24_decode_soa_asm(edge_h, pk) != 0)
		return 0;
	memcpy(msg, coins, NTRUPLUS_N / 8);
	hash_f(msg + NTRUPLUS_N / 8, pk);
	hash_h(buf, msg);
	poly_cbd1((poly *)(void *)work, buf + NTRUPLUS_SYMBYTES);
	forward_gt(edge_r, scratch, work);
	gt32_q24_encode_soa_lazy10788_asm(rhat, edge_r);
	hash_g(rhat, rhat);
	poly_sotp_encode((poly *)(void *)work, msg, rhat);
	forward_gt(edge_m, scratch, work);
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(
		edge_c, edge_h, edge_r);
	poly_add((poly *)(void *)edge_c, (const poly *)(const void *)edge_c,
		(const poly *)(const void *)edge_m);
	return 1;
}

static int edge_bm_add_control(unsigned stop, snapshot_t *snapshot)
{
	(void)stop;
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(edge_c, edge_h, edge_r);
	poly_add((poly *)(void *)edge_c, (const poly *)(const void *)edge_c,
		(const poly *)(const void *)edge_m);
	if (snapshot != NULL)
		snap_coeff(snapshot, edge_c);
	sink += (uint16_t)edge_c[0];
	return 0;
}

static int edge_bm_add_fused(unsigned stop, snapshot_t *snapshot)
{
	(void)stop;
	gt32_tile4_basemul_general_soa_soa_add_m_asm(
		edge_c, edge_h, edge_r, edge_m);
	if (snapshot != NULL)
		snap_coeff(snapshot, edge_c);
	sink += (uint16_t)edge_c[0];
	return 0;
}

static int edge_pack_r_control(unsigned stop, snapshot_t *snapshot)
{
	(void)stop;
	gt32_q24_encode_soa_lazy10788_asm(edge_bytes, edge_r);
	if (snapshot != NULL)
		snap_bytes(snapshot, edge_bytes, sizeof edge_bytes);
	sink += edge_bytes[0];
	return 0;
}

static int edge_pack_r_rr(unsigned stop, snapshot_t *snapshot)
{
	(void)stop;
	gt32_q24_encode_soa_lazy10788_rr_asm(edge_bytes, edge_r);
	if (snapshot != NULL)
		snap_bytes(snapshot, edge_bytes, sizeof edge_bytes);
	sink += edge_bytes[0];
	return 0;
}

static int edge_pack_ct_control(unsigned stop, snapshot_t *snapshot)
{
	(void)stop;
	gt32_q24_encode_soa_encap_hr_h1_asm(edge_bytes, edge_c);
	if (snapshot != NULL)
		snap_bytes(snapshot, edge_bytes, sizeof edge_bytes);
	sink += edge_bytes[0];
	return 0;
}

static int edge_pack_ct_rr(unsigned stop, snapshot_t *snapshot)
{
	(void)stop;
	gt32_q24_encode_soa_lazy10788_rr_asm(edge_bytes, edge_c);
	if (snapshot != NULL)
		snap_bytes(snapshot, edge_bytes, sizeof edge_bytes);
	sink += edge_bytes[0];
	return 0;
}

static double measure(prefix_fn fn, unsigned stop, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		sink += (unsigned)fn(stop, NULL);
	return (double)(stop_tsc() - begin) / iterations;
}

static int self_pmu(prefix_fn fn, unsigned stop, unsigned iterations,
	const char *stage, const char *impl)
{
	pmu_group_t pmu;
	uint64_t begin;
	uint64_t end;
	if (open_pmu(&pmu) != 0) {
		perror("perf_event_open");
		close_pmu(&pmu);
		return 1;
	}
	for (unsigned i = 0; i < 100; i++)
		sink += (unsigned)fn(stop, NULL);
	if (start_pmu(&pmu) != 0) {
		perror("PMU enable");
		close_pmu(&pmu);
		return 1;
	}
	begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		sink += (unsigned)fn(stop, NULL);
	end = stop_tsc();
	if (stop_pmu(&pmu) != 0) {
		perror("PMU read");
		close_pmu(&pmu);
		return 1;
	}
	printf("SELFPMU,%s,%s,%.9f,%.9f,%.9f,%.9f,%.9f,%" PRIu64
		",%" PRIu64 "\n", stage, impl,
		(double)(end - begin) / iterations,
		(double)pmu.value[0] / iterations,
		(double)pmu.value[1] / iterations,
		(double)pmu.value[2] / iterations,
		(double)pmu.value[3] / iterations,
		pmu.time_enabled, pmu.time_running);
	close_pmu(&pmu);
	return 0;
}

static int check_prefixes(void)
{
	for (unsigned stop = 1; stop <= STAGES; stop++) {
		snapshot_t official = {0};
		snapshot_t gt = {0};
		if (official_prefix(stop, &official) != 0 ||
			gt_prefix(stop, &gt) != 0 ||
			memcmp(&official, &gt, sizeof official) != 0) {
			fprintf(stderr, "load-attribution prefix %u failed\n", stop);
			return 0;
		}
	}
	for (unsigned stop = 12; stop <= STAGES; stop++) {
		snapshot_t control = {0};
		snapshot_t fused = {0};
		if (gt_prefix(stop, &control) != 0 ||
			gt_fused_prefix(stop, &fused) != 0 ||
			memcmp(&control, &fused, sizeof control) != 0) {
			fprintf(stderr, "fused B3+add prefix %u failed\n", stop);
			return 0;
		}
	}
	for (unsigned stop = 7; stop <= STAGES; stop++) {
		snapshot_t control = {0};
		snapshot_t rr = {0};
		if (gt_prefix(stop, &control) != 0 ||
			gt_rr_prefix(stop, &rr) != 0 ||
			memcmp(&control, &rr, sizeof control) != 0) {
			fprintf(stderr, "RR Q24 prefix %u failed\n", stop);
			return 0;
		}
	}
	{
		snapshot_t control = {0};
		snapshot_t fused = {0};
		snapshot_t pack_r = {0};
		snapshot_t pack_r_rr = {0};
		snapshot_t pack_ct = {0};
		snapshot_t pack_ct_rr = {0};
		if (!prepare_bm_add_edge() ||
			edge_bm_add_control(0, &control) != 0 ||
			edge_bm_add_fused(0, &fused) != 0 ||
			memcmp(&control, &fused, sizeof control) != 0 ||
			edge_pack_r_control(0, &pack_r) != 0 ||
			edge_pack_r_rr(0, &pack_r_rr) != 0 ||
			memcmp(&pack_r, &pack_r_rr, sizeof pack_r) != 0 ||
			edge_pack_ct_control(0, &pack_ct) != 0 ||
			edge_pack_ct_rr(0, &pack_ct_rr) != 0 ||
			memcmp(&pack_ct, &pack_ct_rr, sizeof pack_ct) != 0) {
			fprintf(stderr, "direct fused B3+add edge failed\n");
			return 0;
		}
	}
	return 1;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 4
		? (unsigned)strtoul(argv[4], NULL, 10) : 1000U;
	uint8_t entropy[48];
	cpu_set_t set;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof set, &set) != 0)
		perror("sched_setaffinity");
	for (size_t i = 0; i < sizeof entropy; i++)
		entropy[i] = (uint8_t)(31U + 7U * i);
	randombytes_init(entropy, NULL, 256);
	if (crypto_kem_keypair(pk, sk) != 0)
		return 1;
	for (size_t i = 0; i < sizeof coins; i++)
		coins[i] = (uint8_t)(11U + 37U * i);
	if (!check_prefixes())
		return 1;
	if (!check_waterfall2())
		return 1;
	if (argc > 4 && strcmp(argv[1], "--transition-tsc") == 0)
		return transition_tsc(argv[2], strcmp(argv[3], "gt") == 0,
			iterations);
	if (argc > 4 && strcmp(argv[1], "--paired-pmu") == 0) {
		prefix_fn control;
		prefix_fn fused;
		unsigned stop;
		if (strcmp(argv[2], "EDGE_bm_add") == 0) {
			control = edge_bm_add_control;
			fused = edge_bm_add_fused;
			stop = 0;
		} else if (strcmp(argv[2], "EDGE_pack_r") == 0) {
			control = edge_pack_r_control;
			fused = edge_pack_r_rr;
			stop = 0;
		} else if (strcmp(argv[2], "EDGE_pack_ct") == 0) {
			control = edge_pack_ct_control;
			fused = edge_pack_ct_rr;
			stop = 0;
		} else if (strcmp(argv[2], "L18_clear_m") == 0) {
			control = gt_prefix;
			fused = strstr(argv[3], "rr") != NULL
				? gt_rr_prefix : gt_fused_prefix;
			stop = 18;
		} else {
			fprintf(stderr, "unknown paired stage: %s\n", argv[2]);
			return 2;
		}
		if (strncmp(argv[3], "gt-first", 8) == 0) {
			if (self_pmu(control, stop, iterations, argv[2], "gt") != 0)
				return 1;
			return self_pmu(fused, stop, iterations, argv[2], "gt-fused");
		}
		if (self_pmu(fused, stop, iterations, argv[2], "gt-fused") != 0)
			return 1;
		return self_pmu(control, stop, iterations, argv[2], "gt");
	}
	if (argc > 4 && strcmp(argv[1], "--self-pmu-waterfall") == 0) {
		for (unsigned cut = 0; cut < 6; cut++) {
			if (strcmp(argv[2], waterfall_names[cut]) == 0) {
				prefix_fn fn = strcmp(argv[3], "gt") == 0
					? waterfall_gt[cut] : waterfall_official[cut];
				return self_pmu(fn, 0, iterations, argv[2], argv[3]);
			}
		}
		fprintf(stderr, "unknown waterfall cut: %s\n", argv[2]);
		return 2;
	}
	if (argc > 4 && strcmp(argv[1], "--self-pmu-waterfall2") == 0) {
		for (unsigned cut = 0; cut < 6; cut++) {
			if (strcmp(argv[2], waterfall_names[cut]) == 0) {
				prefix_fn fn = strcmp(argv[3], "gt") == 0
					? waterfall2_gt[cut] : waterfall2_official[cut];
				return self_pmu(fn, 0, iterations, argv[2], argv[3]);
			}
		}
		fprintf(stderr, "unknown waterfall2 cut: %s\n", argv[2]);
		return 2;
	}

	if (argc > 1 && (strcmp(argv[1], "--perf") == 0
		|| strcmp(argv[1], "--self-pmu") == 0)) {
		if (argc <= 4) {
			fprintf(stderr, "usage: --perf stage impl iterations\n");
			return 2;
		}
		if (strcmp(argv[2], "noop") == 0) {
			printf("PERF,noop,%s,0.000000\n", argv[3]);
			return 0;
		}
		if (strcmp(argv[2], "EDGE_bm_add") == 0) {
			prefix_fn fn = strcmp(argv[3], "gt-fused") == 0
				? edge_bm_add_fused : edge_bm_add_control;
			if (strcmp(argv[1], "--self-pmu") == 0)
				return self_pmu(fn, 0, iterations, argv[2], argv[3]);
			printf("PERF,%s,%s,%.6f\n", argv[2], argv[3],
				measure(fn, 0, iterations));
			return 0;
		}
		if (strcmp(argv[2], "EDGE_pack_r") == 0 ||
			strcmp(argv[2], "EDGE_pack_ct") == 0) {
			const int is_r = strcmp(argv[2], "EDGE_pack_r") == 0;
			prefix_fn fn = strcmp(argv[3], "gt-rr") == 0
				? (is_r ? edge_pack_r_rr : edge_pack_ct_rr)
				: (is_r ? edge_pack_r_control : edge_pack_ct_control);
			if (strcmp(argv[1], "--self-pmu") == 0)
				return self_pmu(fn, 0, iterations, argv[2], argv[3]);
			printf("PERF,%s,%s,%.6f\n", argv[2], argv[3],
				measure(fn, 0, iterations));
			return 0;
		}
		for (unsigned stop = 1; stop <= STAGES; stop++) {
			if (strcmp(argv[2], stage_names[stop]) == 0) {
				prefix_fn fn = strcmp(argv[3], "gt") == 0
					? gt_prefix : strcmp(argv[3], "gt-fused") == 0
					? gt_fused_prefix : strcmp(argv[3], "gt-rr") == 0
					? gt_rr_prefix : official_prefix;
				if (strcmp(argv[1], "--self-pmu") == 0)
					return self_pmu(fn, stop, iterations,
						stage_names[stop], argv[3]);
				printf("PERF,%s,%s,%.6f\n", stage_names[stop], argv[3],
					measure(fn, stop, iterations));
				return 0;
			}
		}
		fprintf(stderr, "unknown stage: %s\n", argv[2]);
		return 2;
	}

	printf("META,correctness=18-prefix-byte-exact-pass+fused-12-18-pass\n");
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
