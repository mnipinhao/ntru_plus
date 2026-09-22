#ifndef CALLER_PROFILE_H
#define CALLER_PROFILE_H
#include <stdint.h>
#include <stddef.h>
#include <cpucycles.h>
typedef struct __attribute__((aligned(64))) {
    uint64_t guard0[8];
    uint8_t pk[1152], sk[2336], ct[1152], ss[32], coins[96];
    uint8_t seeds[64][32];
    unsigned ftries, totaltries;
    uint64_t guard1[8];
} profile_bank;
typedef int (*profile_fn)(profile_bank *);
extern volatile long long profile_end;
extern volatile long long profile_start;
extern unsigned profile_rng_calls, profile_ftries;
extern profile_bank *profile_rng_bank;
void randombytes(unsigned char *, unsigned long long);
#endif
