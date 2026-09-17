/*
 * Microbenchmark for the layout question.
 *
 * Every codec call in kem.c sees Good-Thomas-layout data, because it is fed by
 * the forward NTT or by basemul.  poly_invntt_ternary already stores natural
 * order and its result never reaches the codec, so the question is not about
 * the inverse at all -- it is whether the FORWARD should store natural order.
 *
 * If it did: the codec loses its permutation entirely, basemul and baseinv must
 * consume natural order through LD4/ST4 instead of LD1/ST1, and packed_i9 must
 * read natural order.  This measures the three pieces that decides it.
 */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include <arm_neon.h>
#include "codec_perm.h"

#define N 1152
#define PB 1728
#define Q 3457

static int fd;
static uint64_t rd(void) { uint64_t v; if (read(fd, &v, 8) != 8) _exit(3); return v; }

static int16_t gt[N], nat[N], out[N];
static uint8_t bytes[PB];
static volatile int16_t sink;

/* ---- the permutation alone ---- */
#define SC(k) vst4q_lane_s16((int16_t *)((uint8_t *)nat + off[k]), v, k)
static void perm_gt_to_nat(void)
{
    for (int g = 0; g < CODEC_GROUPS; g++) {
        const uint16_t *off = leaf_byte_offset[g];
        int16x8x4_t v;
        v.val[0] = vld1q_s16(gt + 32*g);      v.val[1] = vld1q_s16(gt + 32*g + 8);
        v.val[2] = vld1q_s16(gt + 32*g + 16); v.val[3] = vld1q_s16(gt + 32*g + 24);
        SC(0); SC(1); SC(2); SC(3); SC(4); SC(5); SC(6); SC(7);
    }
}
#define GA(k) v = vld4q_lane_s16((const int16_t *)((const uint8_t *)nat + off[k]), v, k)
static void perm_nat_to_gt(void)
{
    for (int g = 0; g < CODEC_GROUPS; g++) {
        const uint16_t *off = leaf_byte_offset[g];
        int16x8x4_t v = {{vdupq_n_s16(0), vdupq_n_s16(0), vdupq_n_s16(0), vdupq_n_s16(0)}};
        GA(0); GA(1); GA(2); GA(3); GA(4); GA(5); GA(6); GA(7);
        vst1q_s16(out + 32*g,      v.val[0]); vst1q_s16(out + 32*g + 8,  v.val[1]);
        vst1q_s16(out + 32*g + 16, v.val[2]); vst1q_s16(out + 32*g + 24, v.val[3]);
    }
}

/* ---- a plain contiguous copy, as the floor any pass must pay ---- */
static void copy_pass(void)
{
    for (int i = 0; i < N; i += 8) vst1q_s16(out + i, vld1q_s16(gt + i));
}

/* ---- SoA load/store of 32 coefficients: LD1x4 (GT) versus LD4 (natural) ---- */
static void soa_ld1(void)
{
    int16x8_t acc = vdupq_n_s16(0);
    for (int g = 0; g < CODEC_GROUPS; g++) {
        int16x8_t a = vld1q_s16(gt + 32*g),      b = vld1q_s16(gt + 32*g + 8);
        int16x8_t c = vld1q_s16(gt + 32*g + 16), d = vld1q_s16(gt + 32*g + 24);
        acc = vaddq_s16(acc, vaddq_s16(vaddq_s16(a, b), vaddq_s16(c, d)));
        vst1q_s16(out + 32*g, a);      vst1q_s16(out + 32*g + 8, b);
        vst1q_s16(out + 32*g + 16, c); vst1q_s16(out + 32*g + 24, d);
    }
    sink = vgetq_lane_s16(acc, 0);
}
static void soa_ld4(void)
{
    int16x8_t acc = vdupq_n_s16(0);
    for (int g = 0; g < CODEC_GROUPS; g++) {
        int16x8x4_t v = vld4q_s16(gt + 32*g);
        acc = vaddq_s16(acc, vaddq_s16(vaddq_s16(v.val[0], v.val[1]),
                                       vaddq_s16(v.val[2], v.val[3])));
        vst4q_s16(out + 32*g, v);
    }
    sink = vgetq_lane_s16(acc, 0);
}

/* ---- the 12-bit codec proper, no permutation ---- */
static void pack_only(void)
{
    for (int i = 0; i < N/2; i += 16) {
        uint16x8_t a0 = vld1q_u16((uint16_t*)nat + 2*i),      a1 = vld1q_u16((uint16_t*)nat + 2*i + 8);
        uint16x8_t a2 = vld1q_u16((uint16_t*)nat + 2*i + 16), a3 = vld1q_u16((uint16_t*)nat + 2*i + 24);
        uint16x8_t t0 = vuzp1q_u16(a0,a1), t1 = vuzp2q_u16(a0,a1);
        uint16x8_t t2 = vuzp1q_u16(a2,a3), t3 = vuzp2q_u16(a2,a3);
        uint8x16_t b0 = vuzp1q_u8(vreinterpretq_u8_u16(t0), vreinterpretq_u8_u16(t2));
        uint16x8_t lo = vorrq_u16(vshrq_n_u16(t0,8), vshlq_n_u16(t1,4));
        uint16x8_t hi = vorrq_u16(vshrq_n_u16(t2,8), vshlq_n_u16(t3,4));
        uint8x16_t b1 = vuzp1q_u8(vreinterpretq_u8_u16(lo), vreinterpretq_u8_u16(hi));
        uint8x16_t b2 = vuzp1q_u8(vreinterpretq_u8_u16(vshrq_n_u16(t1,4)),
                                  vreinterpretq_u8_u16(vshrq_n_u16(t3,4)));
        uint8x16x3_t tr = {{b0,b1,b2}};
        vst3q_u8(bytes + 3*i, tr);
    }
}

static double bench(void (*f)(void), int reps)
{
    for (int i = 0; i < 50; i++) f();          /* warm */
    uint64_t a = rd();
    for (int i = 0; i < reps; i++) f();
    return (double)(rd() - a) / reps;
}

int main(void)
{
    struct perf_event_attr at = {0};
    at.size = sizeof at; at.type = PERF_TYPE_HARDWARE;
    at.config = PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel = 1; at.exclude_hv = 1;
    fd = syscall(__NR_perf_event_open, &at, 0, -1, -1, 0);
    if (fd < 0) { perror("perf"); return 2; }
    ioctl(fd, PERF_EVENT_IOC_ENABLE, 0);

    for (int i = 0; i < N; i++) { gt[i] = (int16_t)(i * 37 % Q); nat[i] = gt[i]; }

    const int R = 20000;
    printf("cycles per call, %d reps after 50 warm-ups\n\n", R);
    printf("  %-34s %8.1f\n", "contiguous copy (floor)",   bench(copy_pass, R));
    printf("  %-34s %8.1f\n", "permute GT -> natural",     bench(perm_gt_to_nat, R));
    printf("  %-34s %8.1f\n", "permute natural -> GT",     bench(perm_nat_to_gt, R));
    printf("  %-34s %8.1f\n", "12-bit pack only",          bench(pack_only, R));
    printf("\n");
    printf("  %-34s %8.1f\n", "SoA pass with LD1x4/ST1x4", bench(soa_ld1, R));
    printf("  %-34s %8.1f\n", "SoA pass with LD4/ST4",     bench(soa_ld4, R));
    return 0;
}
