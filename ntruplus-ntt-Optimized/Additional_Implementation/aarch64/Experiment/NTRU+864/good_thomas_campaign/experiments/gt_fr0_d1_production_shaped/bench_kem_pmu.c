#if !defined(__linux__)
#error "D1-P1 PMU requires Linux"
#endif
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include "api.h"
#include "gt864_poly_api.h"
#include "randombytes.h"

#include <asm/unistd.h>
#include <inttypes.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#define NSAMPLES 41
#define NVARIANTS 3
#define NOPS 5

typedef int (*keypair_fn)(uint8_t *, uint8_t *);
typedef int (*enc_fn)(uint8_t *, uint8_t *, const uint8_t *);
typedef int (*dec_fn)(uint8_t *, const uint8_t *, const uint8_t *);
typedef void (*mul_fn)(poly *, const poly *, const poly *);
typedef void (*muladd_fn)(poly *, const poly *, const poly *, const poly *);
typedef void (*ntt_fn)(poly *, const poly *);

int gt_old_crypto_kem_keypair(uint8_t *, uint8_t *);
int gt_old_crypto_kem_enc(uint8_t *, uint8_t *, const uint8_t *);
int gt_old_crypto_kem_dec(uint8_t *, const uint8_t *, const uint8_t *);
int gt_d1_crypto_kem_keypair(uint8_t *, uint8_t *);
int gt_d1_crypto_kem_enc(uint8_t *, uint8_t *, const uint8_t *);
int gt_d1_crypto_kem_dec(uint8_t *, const uint8_t *, const uint8_t *);

struct variant {
    char code;
    const char *name;
    keypair_fn keypair;
    enc_fn enc;
    dec_fn dec;
    mul_fn mul;
    muladd_fn muladd;
    ntt_fn ntt;
};
struct operation { const char *name; int iterations; };
struct counts { uint64_t cycles, instructions, branches; };

static uint64_t random_state;
static poly a[3], b[3], c[3], product;
static uint8_t pk[3][CRYPTO_PUBLICKEYBYTES];
static uint8_t sk[3][CRYPTO_SECRETKEYBYTES];
static uint8_t ct[3][CRYPTO_CIPHERTEXTBYTES];
static uint8_t ss[CRYPTO_BYTES];
static volatile uint64_t sink;
static int leader = -1, instructions_fd = -1, branches_fd = -1;

static void reset_random(uint64_t seed) { random_state = seed ? seed : 1; }

void randombytes(uint8_t *out, size_t outlen)
{
    for (size_t i = 0; i < outlen; i++) {
        random_state ^= random_state << 13;
        random_state ^= random_state >> 7;
        random_state ^= random_state << 17;
        out[i] = (uint8_t)random_state;
    }
}

static uint32_t next_u32(void)
{
    uint32_t value;
    randombytes((uint8_t *)&value, sizeof value);
    return value;
}

static int perf_open(uint64_t config, int group)
{
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof pe);
    pe.type = PERF_TYPE_HARDWARE; pe.size = sizeof pe; pe.config = config;
    pe.disabled = group == -1; pe.exclude_kernel = 1; pe.exclude_hv = 1;
    pe.read_format = PERF_FORMAT_GROUP;
    return (int)syscall(__NR_perf_event_open, &pe, 0, -1, group, 0);
}

static struct counts measure(const struct variant *v, int variant_index,
                             const struct operation *op, int op_index)
{
    struct { uint64_t nr, value[3]; } data = {0, {0, 0, 0}};
    ioctl(leader, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(leader, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
    for (int i = 0; i < op->iterations; i++) {
        uint64_t seed = 0xd1f30000ULL + (uint64_t)i * 0x9e3779b1ULL;
        switch (op_index) {
        case 0: v->mul(&product, &a[variant_index], &b[variant_index]); break;
        case 1: v->muladd(&product, &a[variant_index], &b[variant_index],
                          &c[variant_index]); break;
        case 2: reset_random(seed); v->keypair(pk[variant_index], sk[variant_index]); break;
        case 3: reset_random(seed); v->enc(ct[variant_index], ss, pk[variant_index]); break;
        case 4: v->dec(ss, ct[variant_index], sk[variant_index]); break;
        default: exit(3);
        }
    }
    ioctl(leader, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader, &data, sizeof data) != (ssize_t)sizeof data || data.nr != 3)
        exit(2);
    sink += (uint16_t)product.coeffs[(op_index * 173) % NTRUPLUS_N];
    sink += ss[op_index % CRYPTO_BYTES];
    return (struct counts){data.value[0], data.value[1], data.value[2]};
}

int main(int argc, char **argv)
{
    const struct variant variants[] = {
        {'O', "official", crypto_kem_keypair, crypto_kem_enc, crypto_kem_dec,
         poly_basemul, poly_basemul_add, poly_ntt},
        {'G', "gt_old", gt_old_crypto_kem_keypair, gt_old_crypto_kem_enc,
         gt_old_crypto_kem_dec, gt_old_poly_basemul, gt_old_poly_basemul_add,
         gt_old_poly_ntt},
        {'D', "gt_d1", gt_d1_crypto_kem_keypair, gt_d1_crypto_kem_enc,
         gt_d1_crypto_kem_dec, gt_d1_poly_basemul, gt_d1_poly_basemul_add,
         gt_d1_poly_ntt},
    };
    const struct operation operations[] = {
        {"basemul", 1000}, {"basemuladd", 1000}, {"keypair", 4},
        {"encaps", 40}, {"decaps", 20},
    };
    poly natural_a, natural_b, natural_c;
    if (argc != 2 || strlen(argv[1]) != NVARIANTS) return 2;

    reset_random(0xd1f3b864ULL);
    for (int i = 0; i < NTRUPLUS_N; i++) {
        natural_a.coeffs[i] = (int16_t)((int)(next_u32() % 6913U) - 3456);
        natural_b.coeffs[i] = (int16_t)((int)(next_u32() % 6913U) - 3456);
        natural_c.coeffs[i] = (int16_t)((int)(next_u32() % 6913U) - 3456);
    }
    for (int v = 0; v < NVARIANTS; v++) {
        variants[v].ntt(&a[v], &natural_a);
        variants[v].ntt(&b[v], &natural_b);
        variants[v].ntt(&c[v], &natural_c);
        reset_random(0xd1f3c001ULL);
        variants[v].keypair(pk[v], sk[v]);
        reset_random(0xd1f3c002ULL);
        variants[v].enc(ct[v], ss, pk[v]);
    }
    puts("correctness,status=prepared,production_shaped_variants=3");

    leader = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1);
    instructions_fd = perf_open(PERF_COUNT_HW_INSTRUCTIONS, leader);
    branches_fd = perf_open(PERF_COUNT_HW_BRANCH_INSTRUCTIONS, leader);
    if (leader < 0 || instructions_fd < 0 || branches_fd < 0) return 2;

    for (int op = 0; op < NOPS; op++) {
        for (int sample = 0; sample < NSAMPLES; sample++) {
            for (int position = 0; position < NVARIANTS; position++) {
                const struct variant *selected = NULL;
                int selected_index = -1;
                for (int v = 0; v < NVARIANTS; v++)
                    if (variants[v].code == argv[1][position]) {
                        selected = &variants[v]; selected_index = v;
                    }
                if (selected == NULL) return 2;
                struct counts value = measure(selected, selected_index,
                                              &operations[op], op);
                printf("sample,operation=%s,index=%d,position=%d,variant=%s,"
                       "cycles=%.6f,instructions=%.6f,branches=%.6f\n",
                       operations[op].name, sample, position, selected->name,
                       (double)value.cycles / operations[op].iterations,
                       (double)value.instructions / operations[op].iterations,
                       (double)value.branches / operations[op].iterations);
            }
        }
    }
    printf("meta,sink=%" PRIu64 "\n", sink);
    close(branches_fd); close(instructions_fd); close(leader);
    return 0;
}
