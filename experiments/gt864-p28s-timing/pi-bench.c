#define _GNU_SOURCE
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#include "gt864_native_scaled_tables.h"
#include "gt864_p13b_composite_tables.h"
#include "route-masks.h"

void p13b_i16(int16_t *, const int16_t *, const void *, const int16_t *, const int16_t *);
void p13c_itail(int16_t *, const int16_t *, const void *, const int16_t *, const int16_t *);
void gt864_crepmod3_raw(int16_t *);
void p28_paired_i16(int16_t *, int16_t *, const void *, const int16_t *, const int16_t *);
void p28_dense_tail(int16_t *, const void *, const void *, const int16_t *, const int16_t *);
void p28_route_ternary(int16_t *, const int16_t *, const uint8_t *);

enum { REPS = 32, N = 864, SCRATCH = 896 };
static _Alignas(16) int16_t work[2][REPS][SCRATCH];
static _Alignas(16) int16_t output[2][REPS][N];
static volatile unsigned sink;
struct counts { uint64_t n, v[3]; };
static int fd;

static int event(uint64_t config, int group) {
  struct perf_event_attr attr = {0};
  attr.size = sizeof attr; attr.type = PERF_TYPE_HARDWARE; attr.config = config;
  attr.exclude_kernel = attr.exclude_hv = 1; attr.disabled = group < 0;
  attr.read_format = PERF_FORMAT_GROUP;
  return syscall(__NR_perf_event_open, &attr, 0, -1, group, 0);
}
static struct counts tick(void) {
  struct counts value;
  if (read(fd, &value, sizeof value) != sizeof value || value.n != 3) exit(3);
  return value;
}
static void fill(unsigned sample) {
  uint32_t state = 0x864000u + sample;
  for (unsigned k = 0; k < REPS; k++) for (unsigned i = 0; i < SCRATCH; i++) {
    state ^= state << 13; state ^= state >> 17; state ^= state << 5;
    int16_t value = (int16_t)((int)(state % 5235) - 2617);
    work[0][k][i] = work[1][k][i] = value;
  }
}
static void baseline(int16_t *out, const int16_t *scratch) {
  for (unsigned component = 0; component < 3; component++) for (unsigned half = 0; half < 2; half++) {
    unsigned block = 2 * component + half;
    p13b_i16(out + component + 12 * half, scratch + 128 * block, 0,
             &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_main[0][0]);
  }
  p13c_itail(out + 24, scratch + 768, 0,
             &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_tail[0][0]);
  gt864_crepmod3_raw(out);
}
static void candidate(int16_t *out, int16_t *scratch) {
  p28_paired_i16(scratch + 0, scratch + 256, 0,
                 &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_main[0][0]);
  p28_paired_i16(scratch + 128, scratch + 512, 0,
                 &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_main[0][0]);
  p28_paired_i16(scratch + 384, scratch + 640, 0,
                 &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_main[0][0]);
  p28_dense_tail(scratch + 768, 0, 0,
                 &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_tail[0][0]);
  p28_route_ternary(out, scratch, &gt864_p28_route_masks[0][0][0]);
}
int main(void) {
  fill(0);
  baseline(output[0][0], work[0][0]); candidate(output[1][0], work[1][0]);
  if (memcmp(output[0][0], output[1][0], sizeof output[0][0])) return 2;
  puts("correctness=pass");
  fd = event(PERF_COUNT_HW_CPU_CYCLES, -1);
  int fi = event(PERF_COUNT_HW_INSTRUCTIONS, fd);
  int fb = event(PERF_COUNT_HW_BRANCH_INSTRUCTIONS, fd);
  if (fd < 0 || fi < 0 || fb < 0) return 3;
  ioctl(fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
  for (unsigned sample = 0; sample < 100; sample++) {
    fill(sample + 1);
    for (unsigned position = 0; position < 2; position++) {
      unsigned which = position ^ (sample & 1);
      struct counts before = tick();
      for (unsigned k = 0; k < REPS; k++) {
        if (which) candidate(output[1][k], work[1][k]);
        else baseline(output[0][k], work[0][k]);
        sink += (unsigned)output[which][k][k % N];
      }
      struct counts after = tick();
      if (sample >= 10) printf("p28,%s,%.3f,%.3f,%.3f\n", which ? "candidate" : "baseline",
          (double)(after.v[0]-before.v[0])/REPS,
          (double)(after.v[1]-before.v[1])/REPS,
          (double)(after.v[2]-before.v[2])/REPS);
    }
  }
  return 0;
}
