#if !defined(__linux__)
#error "Pi5 Linux PMU required"
#endif
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include "api.h"
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
#define NOPS 3
typedef int (*key_fn)(uint8_t *, uint8_t *);
typedef int (*enc_fn)(uint8_t *, uint8_t *, const uint8_t *);
typedef int (*dec_fn)(uint8_t *, const uint8_t *, const uint8_t *);
int gt_base_crypto_kem_keypair(uint8_t *, uint8_t *);
int gt_base_crypto_kem_enc(uint8_t *, uint8_t *, const uint8_t *);
int gt_base_crypto_kem_dec(uint8_t *, const uint8_t *, const uint8_t *);
int gt_bytes_crypto_kem_keypair(uint8_t *, uint8_t *);
int gt_bytes_crypto_kem_enc(uint8_t *, uint8_t *, const uint8_t *);
int gt_bytes_crypto_kem_dec(uint8_t *, const uint8_t *, const uint8_t *);
struct variant { char code; const char *name; key_fn key; enc_fn enc; dec_fn dec; };
struct operation { const char *name; int iterations; };
struct counts { uint64_t cycles, instructions, branches; };
static uint64_t random_state;
static uint8_t pk[3][CRYPTO_PUBLICKEYBYTES], sk[3][CRYPTO_SECRETKEYBYTES];
static uint8_t ct[3][CRYPTO_CIPHERTEXTBYTES], ss[CRYPTO_BYTES];
static volatile uint64_t sink;
static int leader = -1, ifd = -1, bfd = -1;
static void reset_random(uint64_t seed) { random_state = seed ? seed : 1; }
void randombytes(uint8_t *out, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        random_state ^= random_state << 13; random_state ^= random_state >> 7;
        random_state ^= random_state << 17; out[i] = (uint8_t)random_state;
    }
}
static int perf_open(uint64_t config, int group)
{
    struct perf_event_attr pe; memset(&pe, 0, sizeof pe);
    pe.type=PERF_TYPE_HARDWARE; pe.size=sizeof pe; pe.config=config;
    pe.disabled=group == -1; pe.exclude_kernel=1; pe.exclude_hv=1;
    pe.read_format=PERF_FORMAT_GROUP;
    return (int)syscall(__NR_perf_event_open,&pe,0,-1,group,0);
}
static struct counts measure(const struct variant *v, int vi, int op, int iters)
{
    struct { uint64_t nr, value[3]; } d={0,{0,0,0}};
    ioctl(leader,PERF_EVENT_IOC_RESET,PERF_IOC_FLAG_GROUP);
    ioctl(leader,PERF_EVENT_IOC_ENABLE,PERF_IOC_FLAG_GROUP);
    for (int i=0;i<iters;i++) {
        uint64_t seed=0xb6000000ULL+(uint64_t)i*0x9e3779b1ULL;
        if (op==0) { reset_random(seed); v->key(pk[vi],sk[vi]); }
        else if (op==1) { reset_random(seed); v->enc(ct[vi],ss,pk[vi]); }
        else v->dec(ss,ct[vi],sk[vi]);
    }
    ioctl(leader,PERF_EVENT_IOC_DISABLE,PERF_IOC_FLAG_GROUP);
    if (read(leader,&d,sizeof d)!=(ssize_t)sizeof d || d.nr!=3) exit(2);
    sink += ss[op];
    return (struct counts){d.value[0],d.value[1],d.value[2]};
}
int main(int argc,char **argv)
{
    const struct variant v[]={
        {'O',"official",crypto_kem_keypair,crypto_kem_enc,crypto_kem_dec},
        {'D',"gt_base",gt_base_crypto_kem_keypair,gt_base_crypto_kem_enc,gt_base_crypto_kem_dec},
        {'B',"gt_bytes",gt_bytes_crypto_kem_keypair,gt_bytes_crypto_kem_enc,gt_bytes_crypto_kem_dec}};
    const struct operation ops[]={{"keypair",4},{"encaps",40},{"decaps",20}};
    if(argc!=2 || strlen(argv[1])!=NVARIANTS) return 2;
    for(int i=0;i<NVARIANTS;i++) {
        reset_random(0xb6123001ULL); v[i].key(pk[i],sk[i]);
        reset_random(0xb6123002ULL); v[i].enc(ct[i],ss,pk[i]);
    }
    puts("correctness,status=prepared,production_shaped_variants=3");
    leader=perf_open(PERF_COUNT_HW_CPU_CYCLES,-1);
    ifd=perf_open(PERF_COUNT_HW_INSTRUCTIONS,leader);
    bfd=perf_open(PERF_COUNT_HW_BRANCH_INSTRUCTIONS,leader);
    if(leader<0 || ifd<0 || bfd<0) return 2;
    for(int op=0;op<NOPS;op++) for(int sample=0;sample<NSAMPLES;sample++)
        for(int pos=0;pos<NVARIANTS;pos++) {
            int vi=-1; for(int i=0;i<NVARIANTS;i++) if(v[i].code==argv[1][pos]) vi=i;
            if(vi<0) return 2;
            struct counts c=measure(&v[vi],vi,op,ops[op].iterations);
            printf("sample,operation=%s,index=%d,position=%d,variant=%s,cycles=%.6f,instructions=%.6f,branches=%.6f\n",
                   ops[op].name,sample,pos,v[vi].name,(double)c.cycles/ops[op].iterations,
                   (double)c.instructions/ops[op].iterations,(double)c.branches/ops[op].iterations);
        }
    printf("meta,sink=%" PRIu64 "\n",sink);
    close(bfd);close(ifd);close(leader);return 0;
}
