#define _GNU_SOURCE

#include <errno.h>
#include <inttypes.h>
#include <linux/perf_event.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#include "api.h"

#ifndef NTESTS
#define NTESTS 31
#endif

#ifndef NITERATIONS
#define NITERATIONS 2000
#endif

#ifndef NWARMUP
#define NWARMUP 100
#endif

struct sample {
    uint64_t cycles;
    uint64_t instructions;
};

static int cycle_fd = -1;
static int instruction_fd = -1;
static volatile uint64_t sink;

static int perf_event_open_wrap(struct perf_event_attr *attr)
{
    return (int)syscall(__NR_perf_event_open, attr, 0, -1, -1, 0);
}

static int open_event(uint64_t config)
{
    struct perf_event_attr attr;
    memset(&attr, 0, sizeof attr);
    attr.type = PERF_TYPE_HARDWARE;
    attr.size = sizeof attr;
    attr.config = config;
    attr.disabled = 1;
    attr.exclude_kernel = 1;
    attr.exclude_hv = 1;
    return perf_event_open_wrap(&attr);
}

static void open_events(void)
{
    cycle_fd = open_event(PERF_COUNT_HW_CPU_CYCLES);
    instruction_fd = open_event(PERF_COUNT_HW_INSTRUCTIONS);
    if (cycle_fd < 0 || instruction_fd < 0) {
        fprintf(stderr, "perf_event_open: %s\n", strerror(errno));
        exit(2);
    }
}

static void start_events(void)
{
    ioctl(cycle_fd, PERF_EVENT_IOC_RESET, 0);
    ioctl(instruction_fd, PERF_EVENT_IOC_RESET, 0);
    ioctl(cycle_fd, PERF_EVENT_IOC_ENABLE, 0);
    ioctl(instruction_fd, PERF_EVENT_IOC_ENABLE, 0);
}

static struct sample stop_events(void)
{
    struct sample result;
    ioctl(cycle_fd, PERF_EVENT_IOC_DISABLE, 0);
    ioctl(instruction_fd, PERF_EVENT_IOC_DISABLE, 0);
    if (read(cycle_fd, &result.cycles, sizeof result.cycles) !=
            (ssize_t)sizeof result.cycles ||
        read(instruction_fd, &result.instructions,
             sizeof result.instructions) !=
            (ssize_t)sizeof result.instructions) {
        perror("read perf event");
        exit(2);
    }
    return result;
}

static int compare_u64(const void *left, const void *right)
{
    uint64_t a = *(const uint64_t *)left;
    uint64_t b = *(const uint64_t *)right;
    return (a > b) - (a < b);
}

static void pin_core(int core)
{
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(core, &set);
    if (sched_setaffinity(0, sizeof set, &set) != 0) {
        perror("sched_setaffinity");
        exit(2);
    }
}

static void prepare(uint8_t *pk, uint8_t *sk, uint8_t *ct,
                    uint8_t *enc_ss, uint8_t *dec_ss)
{
    if (crypto_kem_keypair(pk, sk) != 0 ||
        crypto_kem_enc(ct, enc_ss, pk) != 0 ||
        crypto_kem_dec(dec_ss, ct, sk) != 0 ||
        memcmp(enc_ss, dec_ss, CRYPTO_BYTES) != 0) {
        fprintf(stderr, "KEM setup failed\n");
        exit(1);
    }
}

static void run_mode(const char *mode, int iterations,
                     uint8_t *pk, uint8_t *sk, uint8_t *ct,
                     uint8_t *enc_ss, uint8_t *dec_ss)
{
    if (strcmp(mode, "keygen") == 0) {
        for (int i = 0; i < iterations; i++)
            sink += (uint64_t)crypto_kem_keypair(pk, sk);
    } else if (strcmp(mode, "encap") == 0) {
        for (int i = 0; i < iterations; i++)
            sink += (uint64_t)crypto_kem_enc(ct, enc_ss, pk);
    } else if (strcmp(mode, "decap") == 0) {
        for (int i = 0; i < iterations; i++)
            sink += (uint64_t)crypto_kem_dec(dec_ss, ct, sk);
    } else if (strcmp(mode, "mixed") == 0) {
        for (int i = 0; i < iterations; i++) {
            sink += (uint64_t)crypto_kem_keypair(pk, sk);
            sink += (uint64_t)crypto_kem_enc(ct, enc_ss, pk);
            sink += (uint64_t)crypto_kem_dec(dec_ss, ct, sk);
        }
    } else {
        fprintf(stderr, "unknown mode: %s\n", mode);
        exit(2);
    }
}

int main(int argc, char **argv)
{
    const char *mode = argc > 1 ? argv[1] : "encap";
    int iterations = argc > 2 ? atoi(argv[2]) : NITERATIONS;
    int core = argc > 3 ? atoi(argv[3]) : 3;
    struct sample samples[NTESTS];
    uint64_t cycles[NTESTS];
    uint64_t instructions[NTESTS];
    uint8_t pk[CRYPTO_PUBLICKEYBYTES];
    uint8_t sk[CRYPTO_SECRETKEYBYTES];
    uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
    uint8_t enc_ss[CRYPTO_BYTES];
    uint8_t dec_ss[CRYPTO_BYTES];

    pin_core(core);
    prepare(pk, sk, ct, enc_ss, dec_ss);
    run_mode(mode, NWARMUP, pk, sk, ct, enc_ss, dec_ss);
    open_events();

    for (int test = 0; test < NTESTS; test++) {
        start_events();
        run_mode(mode, iterations, pk, sk, ct, enc_ss, dec_ss);
        samples[test] = stop_events();
        cycles[test] = samples[test].cycles / (uint64_t)iterations;
        instructions[test] =
            samples[test].instructions / (uint64_t)iterations;
    }

    qsort(cycles, NTESTS, sizeof cycles[0], compare_u64);
    qsort(instructions, NTESTS, sizeof instructions[0], compare_u64);
    printf("mode=%s iterations=%d tests=%d core=%d\n",
           mode, iterations, NTESTS, core);
    printf("cycles_min=%" PRIu64 " cycles_p50=%" PRIu64
           " cycles_max=%" PRIu64 "\n",
           cycles[0], cycles[NTESTS / 2], cycles[NTESTS - 1]);
    printf("instructions_min=%" PRIu64 " instructions_p50=%" PRIu64
           " instructions_max=%" PRIu64 "\n",
           instructions[0], instructions[NTESTS / 2],
           instructions[NTESTS - 1]);
    printf("cpi_p50=%.6f sink=%" PRIu64 "\n",
           (double)cycles[NTESTS / 2] /
               (double)instructions[NTESTS / 2],
           sink);
    return 0;
}
