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

enum { PK = 1296, SK = 2624, CT = 1296, SS = 32, N = 864 };
typedef struct { int16_t c[N]; } poly;
typedef int (*keyfn)(uint8_t *, uint8_t *);
typedef int (*encfn)(uint8_t *, uint8_t *, const uint8_t *);
typedef int (*decfn)(uint8_t *, const uint8_t *, const uint8_t *);
typedef void (*invfn)(poly *, const poly *);
struct api { keyfn key; encfn enc; decfn dec; invfn inverse; };
struct counts { uint64_t n, v[3]; };
static uint64_t state = 864;
static volatile unsigned sink;
static int fd;

void randombytes(uint8_t *out, size_t n) {
    while (n--) {
        state ^= state << 13;
        state ^= state >> 7;
        state ^= state << 17;
        *out++ = (uint8_t)state;
    }
}
static void *must(void *handle, const char *name) {
    void *symbol = dlsym(handle, name);
    if (!symbol) { fprintf(stderr, "missing %s: %s\n", name, dlerror()); exit(2); }
    return symbol;
}
static struct api load(const char *path) {
    void *handle = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    if (!handle) { fprintf(stderr, "%s\n", dlerror()); exit(2); }
    return (struct api) {
        must(handle, "crypto_kem_keypair"), must(handle, "crypto_kem_enc"),
        must(handle, "crypto_kem_dec"), must(handle, "gt864_native_inverse_ternary")
    };
}
static int event(uint64_t config, int group) {
    struct perf_event_attr attr = {0};
    attr.size = sizeof attr;
    attr.type = PERF_TYPE_HARDWARE;
    attr.config = config;
    attr.exclude_kernel = attr.exclude_hv = 1;
    attr.disabled = group < 0;
    attr.read_format = PERF_FORMAT_GROUP;
    return syscall(__NR_perf_event_open, &attr, 0, -1, group, 0);
}
static struct counts tick(void) {
    struct counts value;
    if (read(fd, &value, sizeof value) != sizeof value || value.n != 3) exit(3);
    return value;
}
static uint8_t pk[2][PK], sk[2][SK], ct[2][CT], ss[2][SS];
static void setup(struct api api, int slot, uint64_t seed) {
    uint8_t recovered[SS];
    state = seed;
    if (api.key(pk[slot], sk[slot])) exit(4);
    state = seed + 1;
    if (api.enc(ct[slot], ss[slot], pk[slot])) exit(4);
    if (api.dec(recovered, ct[slot], sk[slot]) || memcmp(recovered, ss[slot], SS)) exit(4);
}
static void fill_inverse_input(poly *input, uint64_t seed) {
    state = seed;
    for (int i = 0; i < N; i++) {
        uint16_t value;
        randombytes((uint8_t *)&value, sizeof value);
        input->c[i] = (int16_t)((int)(value % 4995) - 2497);
    }
}
int main(int argc, char **argv) {
    if (argc != 4) return 2;
    struct api api[2] = {load(argv[1]), load(argv[2])};
    int reverse = atoi(argv[3]);
    for (int trial = 0; trial < 24; trial++) {
        setup(api[0], 0, 100 + trial);
        setup(api[1], 1, 100 + trial);
        if (memcmp(pk[0], pk[1], PK) || memcmp(sk[0], sk[1], SK) ||
            memcmp(ct[0], ct[1], CT) || memcmp(ss[0], ss[1], SS)) return 5;
        uint8_t bad[CT], out0[SS], out1[SS];
        memcpy(bad, ct[0], CT);
        bad[11 + 37 * trial] ^= 128;
        if (api[0].dec(out0, bad, sk[0]) != api[1].dec(out1, bad, sk[1]) ||
            memcmp(out0, out1, SS)) return 6;
    }
    poly input, output[2], alias;
    for (int trial = 0; trial < 256; trial++) {
        fill_inverse_input(&input, 0x864000 + trial);
        api[0].inverse(&output[0], &input);
        api[1].inverse(&output[1], &input);
        if (memcmp(&output[0], &output[1], sizeof(poly))) return 7;
        alias = input;
        api[1].inverse(&alias, &alias);
        if (memcmp(&alias, &output[1], sizeof(poly))) return 8;
    }
    puts("correctness=pass valid=24 tampered=24 inverse_exact=256 alias=256");

    fd = event(PERF_COUNT_HW_CPU_CYCLES, -1);
    int fi = event(PERF_COUNT_HW_INSTRUCTIONS, fd);
    int fb = event(PERF_COUNT_HW_BRANCH_INSTRUCTIONS, fd);
    if (fd < 0 || fi < 0 || fb < 0) return 3;
    ioctl(fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
    const char *names[] = {"keygen", "encaps", "decaps"};
    for (int op = 0; op < 3; op++) for (int sample = -5; sample < 31; sample++) {
        for (int position = 0; position < 2; position++) {
            int candidate = position ^ reverse;
            int repetitions = op ? 20 : 4;
            setup(api[candidate], candidate, 0x9911);
            struct counts before = tick();
            for (int k = 0; k < repetitions; k++) {
                state = 0x880000 + (uint64_t)k * 0x9e3779b1ULL;
                int result = op == 0 ? api[candidate].key(pk[candidate], sk[candidate]) :
                    op == 1 ? api[candidate].enc(ct[candidate], ss[candidate], pk[candidate]) :
                    api[candidate].dec(ss[candidate], ct[candidate], sk[candidate]);
                if (result) exit(9);
                sink += ss[candidate][0];
            }
            struct counts after = tick();
            if (sample >= 0) printf("full,%s,%s,%.3f,%.3f,%.3f\n", names[op],
                candidate ? "candidate" : "baseline",
                (double)(after.v[0]-before.v[0])/repetitions,
                (double)(after.v[1]-before.v[1])/repetitions,
                (double)(after.v[2]-before.v[2])/repetitions);
        }
    }
    fill_inverse_input(&input, 0x123456);
    for (int sample = -10; sample < 61; sample++) for (int position = 0; position < 2; position++) {
        int candidate = position ^ reverse;
        struct counts before = tick();
        for (int k = 0; k < 64; k++) {
            api[candidate].inverse(&output[candidate], &input);
            sink += (unsigned)output[candidate].c[k % N];
        }
        struct counts after = tick();
        if (sample >= 0) printf("component,inverse_to_ternary,%s,%.3f,%.3f,%.3f\n",
            candidate ? "candidate" : "baseline",
            (double)(after.v[0]-before.v[0])/64,
            (double)(after.v[1]-before.v[1])/64,
            (double)(after.v[2]-before.v[2])/64);
    }
    return 0;
}
