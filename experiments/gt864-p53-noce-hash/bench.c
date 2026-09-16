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

enum { PK = 1296, SK = 2624, CT = 1296, SS = 32, HASH_OUT = 216 };
typedef int (*keyfn)(uint8_t *, uint8_t *);
typedef int (*encfn)(uint8_t *, uint8_t *, const uint8_t *);
typedef int (*decfn)(uint8_t *, const uint8_t *, const uint8_t *);
typedef void (*hashfn)(uint8_t *, const uint8_t *);
struct api { keyfn key; encfn enc; decfn dec; hashfn hash; };
struct counts { uint64_t n, value[3]; };
static uint64_t rng_state = UINT64_C(0x864053);
static volatile unsigned sink;
static int group_fd;

void randombytes(uint8_t *out, size_t length)
{
    while (length--) {
        rng_state ^= rng_state << 13;
        rng_state ^= rng_state >> 7;
        rng_state ^= rng_state << 17;
        *out++ = (uint8_t)rng_state;
    }
}

static void *must(void *handle, const char *name)
{
    void *symbol = dlsym(handle, name);
    if (!symbol) { fprintf(stderr, "missing %s: %s\n", name, dlerror()); exit(2); }
    return symbol;
}

static struct api load(const char *path)
{
    void *handle = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    if (!handle) { fprintf(stderr, "%s\n", dlerror()); exit(2); }
    return (struct api){ must(handle, "crypto_kem_keypair"),
                         must(handle, "crypto_kem_enc"),
                         must(handle, "crypto_kem_dec"), must(handle, "hash_g") };
}

static int event(uint64_t config, int group)
{
    struct perf_event_attr attr = {0};
    attr.size = sizeof attr;
    attr.type = PERF_TYPE_HARDWARE;
    attr.config = config;
    attr.exclude_kernel = attr.exclude_hv = 1;
    attr.disabled = group < 0;
    attr.read_format = PERF_FORMAT_GROUP;
    return syscall(__NR_perf_event_open, &attr, 0, -1, group, 0);
}

static struct counts tick(void)
{
    struct counts result;
    if (read(group_fd, &result, sizeof result) != sizeof result || result.n != 3) exit(3);
    return result;
}

static uint8_t pk[2][PK], sk[2][SK], ct[2][CT], ss[2][SS];

static void setup(struct api api, int slot, uint64_t seed)
{
    uint8_t recovered[SS];
    rng_state = seed;
    if (api.key(pk[slot], sk[slot])) exit(4);
    rng_state = seed + 1;
    if (api.enc(ct[slot], ss[slot], pk[slot])) exit(4);
    if (api.dec(recovered, ct[slot], sk[slot]) || memcmp(recovered, ss[slot], SS)) exit(4);
}

int main(int argc, char **argv)
{
    if (argc != 4) return 2;
    struct api api[2] = { load(argv[1]), load(argv[2]) };
    int reverse = atoi(argv[3]);
    uint8_t input[CT], digest[2][HASH_OUT];
    for (size_t i = 0; i < sizeof input; i++) input[i] = (uint8_t)(i * 73 + 19);
    api[0].hash(digest[0], input);
    api[1].hash(digest[1], input);
    if (memcmp(digest[0], digest[1], HASH_OUT)) return 5;
    for (int trial = 0; trial < 24; trial++) {
        setup(api[0], 0, 100 + trial);
        setup(api[1], 1, 100 + trial);
        if (memcmp(pk[0], pk[1], PK) || memcmp(sk[0], sk[1], SK) ||
            memcmp(ct[0], ct[1], CT) || memcmp(ss[0], ss[1], SS)) return 6;
        uint8_t bad[CT], out[2][SS];
        memcpy(bad, ct[0], CT);
        bad[11 + 37 * trial] ^= 128;
        if (api[0].dec(out[0], bad, sk[0]) != api[1].dec(out[1], bad, sk[1]) ||
            memcmp(out[0], out[1], SS)) return 7;
    }
    puts("correctness=pass valid=24 tampered=24 hash_exact=1");

    group_fd = event(PERF_COUNT_HW_CPU_CYCLES, -1);
    int instructions_fd = event(PERF_COUNT_HW_INSTRUCTIONS, group_fd);
    int branches_fd = event(PERF_COUNT_HW_BRANCH_INSTRUCTIONS, group_fd);
    if (group_fd < 0 || instructions_fd < 0 || branches_fd < 0) return 3;
    ioctl(group_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);

    for (int sample = -10; sample < 61; sample++) {
        for (int position = 0; position < 2; position++) {
            int candidate = position ^ reverse;
            struct counts before = tick();
            for (int repetition = 0; repetition < 32; repetition++) {
                api[candidate].hash(digest[candidate], input);
                sink += digest[candidate][repetition % HASH_OUT];
            }
            struct counts after = tick();
            if (sample >= 0) printf("component,hash_g,%s,%.3f,%.3f,%.3f\n",
                candidate ? "candidate" : "baseline",
                (double)(after.value[0] - before.value[0]) / 32,
                (double)(after.value[1] - before.value[1]) / 32,
                (double)(after.value[2] - before.value[2]) / 32);
        }
    }

    const char *names[] = { "keygen", "encaps", "decaps" };
    for (int operation = 0; operation < 3; operation++) {
        for (int sample = -5; sample < 31; sample++) {
            for (int position = 0; position < 2; position++) {
                int candidate = position ^ reverse;
                int repetitions = operation ? 20 : 4;
                setup(api[candidate], candidate, UINT64_C(0x9911));
                struct counts before = tick();
                for (int k = 0; k < repetitions; k++) {
                    rng_state = UINT64_C(0x880000) + (uint64_t)k * UINT64_C(0x9e3779b1);
                    int result = operation == 0
                        ? api[candidate].key(pk[candidate], sk[candidate])
                        : operation == 1
                        ? api[candidate].enc(ct[candidate], ss[candidate], pk[candidate])
                        : api[candidate].dec(ss[candidate], ct[candidate], sk[candidate]);
                    if (result) return 8;
                    sink += ss[candidate][0];
                }
                struct counts after = tick();
                if (sample >= 0) printf("full,%s,%s,%.3f,%.3f,%.3f\n", names[operation],
                    candidate ? "candidate" : "baseline",
                    (double)(after.value[0] - before.value[0]) / repetitions,
                    (double)(after.value[1] - before.value[1]) / repetitions,
                    (double)(after.value[2] - before.value[2]) / repetitions);
            }
        }
    }
    return 0;
}
