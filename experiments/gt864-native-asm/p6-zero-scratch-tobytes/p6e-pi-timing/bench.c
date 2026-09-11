#define _GNU_SOURCE
#include <dlfcn.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

enum { N = 864, BYTES = 1296, EVENTS = 5 };
typedef void (*tofn)(uint8_t *, const int16_t *);
struct counts { uint64_t n, v[EVENTS]; };

static int leader = -1;
static volatile uint32_t sink;
static uint64_t rng_state = 0x8647065dUL;

static uint32_t random32(void) {
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 7;
    rng_state ^= rng_state << 17;
    return (uint32_t)rng_state;
}

/* The production shared object intentionally imports the SUPERCOP RNG from
 * its caller.  ToBytes does not call it, but dlopen still requires the public
 * symbol to resolve. */
void randombytes(uint8_t *out, size_t length) {
    while (length--) *out++ = (uint8_t)random32();
}

static void *must_open(const char *path) {
    void *h = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    if (!h) { fprintf(stderr, "dlopen %s: %s\n", path, dlerror()); exit(2); }
    return h;
}

static tofn must_symbol(void *h, const char *name) {
    void *p = dlsym(h, name);
    if (!p) { fprintf(stderr, "dlsym %s: %s\n", name, dlerror()); exit(2); }
    return (tofn)p;
}

static int read_pmu_type(void) {
    FILE *f = fopen("/sys/bus/event_source/devices/armv8_cortex_a76/type", "r");
    int value = -1;
    if (!f || fscanf(f, "%d", &value) != 1) { perror("read PMU type"); exit(3); }
    fclose(f);
    return value;
}

static int open_event(uint32_t type, uint64_t config, int group) {
    struct perf_event_attr attr = {0};
    attr.size = sizeof attr;
    attr.type = type;
    attr.config = config;
    attr.exclude_kernel = 1;
    attr.exclude_hv = 1;
    attr.disabled = group < 0;
    attr.read_format = PERF_FORMAT_GROUP;
    int fd = syscall(__NR_perf_event_open, &attr, 0, -1, group, 0);
    if (fd < 0) { perror("perf_event_open"); exit(3); }
    return fd;
}

static void setup_perf(void) {
    leader = open_event(PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, -1);
    (void)open_event(PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, leader);
    (void)open_event(PERF_TYPE_HARDWARE, PERF_COUNT_HW_BRANCH_INSTRUCTIONS, leader);
    int type = read_pmu_type();
    /* Verified on this Pi 5 with `perf stat -vv`: A76 MEM_ACCESS_RD/WR. */
    (void)open_event((uint32_t)type, 0x66, leader);
    (void)open_event((uint32_t)type, 0x67, leader);
}

static struct counts measure(tofn fn, uint8_t *out, const int16_t *in, int iterations) {
    struct counts result;
    ioctl(leader, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    ioctl(leader, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(leader, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
    for (int i = 0; i < iterations; i++) {
        fn(out, in);
        sink += out[(i * 313) % BYTES];
    }
    ioctl(leader, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader, &result, sizeof result) != sizeof result || result.n != EVENTS) {
        fprintf(stderr, "incomplete PMU group\n"); exit(3);
    }
    return result;
}

static void fill_input(int16_t *in, int small, int case_id) {
    rng_state = 0x86400000UL + (uint64_t)case_id * 0x9e3779b1UL;
    for (int i = 0; i < N; i++) {
        uint32_t x = random32();
        in[i] = small ? (int16_t)((int)(x % 6913) - 3456) : (int16_t)x;
    }
    if (case_id == 0) {
        const int16_t full_edges[] = { INT16_MIN, INT16_MAX, -3457, -3456, -1, 0, 1, 3456, 3457 };
        const int16_t small_edges[] = { -3456, -1, 0, 1, 3456 };
        const int16_t *edges = small ? small_edges : full_edges;
        int count = small ? 5 : 9;
        for (int i = 0; i < N; i++) in[i] = edges[i % count];
    }
}

static void correctness(tofn base, tofn cand, int small) {
    _Alignas(16) int16_t in[N];
    uint8_t a[BYTES + 32], b[BYTES + 32];
    for (int c = 0; c < 513; c++) {
        fill_input(in, small, c);
        memset(a, 0xa5, sizeof a); memset(b, 0xa5, sizeof b);
        base(a + 16, in); cand(b + 16, in);
        if (memcmp(a, b, sizeof a)) { fprintf(stderr, "mismatch mode=%d case=%d\n", small, c); exit(4); }
    }
}

int main(int argc, char **argv) {
    if (argc != 5) return 2;
    void *hb = must_open(argv[1]), *hc = must_open(argv[2]);
    int small = !strcmp(argv[3], "small"), reverse = atoi(argv[4]);
    tofn fn[2] = {
        must_symbol(hb, small ? "gt864_fr0_tobytes_small" : "gt864_fr0_tobytes_full"),
        must_symbol(hc, small ? "gt864_p6d3_small_asm" : "gt864_p6d3_full_asm")
    };
    correctness(fn[0], fn[1], small);
    _Alignas(16) int16_t in[N];
    _Alignas(16) uint8_t out[2][BYTES];
    fill_input(in, small, 911);
    for (int v = 0; v < 2; v++) for (int i = 0; i < 128; i++) fn[v](out[v], in);
    setup_perf();
    puts("correctness=pass cases=513 canaries=pass");
    const int iterations = 128;
    for (int sample = 0; sample < 37; sample++) {
        for (int pos = 0; pos < 2; pos++) {
            int v = pos ^ reverse ^ (sample & 1);
            struct counts c = measure(fn[v], out[v], in, iterations);
            printf("sample,%s,%s,%d,%.3f,%.3f,%.3f,%.3f,%.3f\n",
                   small ? "small" : "full", v ? "candidate" : "baseline", sample,
                   (double)c.v[0] / iterations, (double)c.v[1] / iterations,
                   (double)c.v[2] / iterations, (double)c.v[3] / iterations,
                   (double)c.v[4] / iterations);
        }
    }
    return sink == 0xdeadbeefU;
}
