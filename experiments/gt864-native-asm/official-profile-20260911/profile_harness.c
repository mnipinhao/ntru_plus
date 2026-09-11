#define _GNU_SOURCE
#include <dlfcn.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/syscall.h>
#include <unistd.h>

enum { GROUPS = 21, PK = 1296, SK = 2624, CT = 1296, SS = 32 };
static const char *group_names[GROUPS] = {
    "Forward", "BaseInv", "BaseMul_R0", "BaseMul_Rinv", "BaseMulAdd",
    "Inverse", "ToBytes_full", "ToBytes_small", "FromBytes_checked", "CBD",
    "SOTP_encode", "SOTP_decode", "Triple", "Sub", "Crepmod3", "hash_f",
    "hash_g", "hash_h", "SHAKE_sampling", "RNG", "cleanup"
};
typedef int (*keyfn)(uint8_t *, uint8_t *);
typedef int (*encfn)(uint8_t *, uint8_t *, const uint8_t *);
typedef int (*decfn)(uint8_t *, const uint8_t *, const uint8_t *);
struct api { keyfn key; encfn enc; decfn dec; };
static int perf_fd, active;
static uint64_t totals[GROUPS], calls[GROUPS], rng_state;

void randombytes(uint8_t *out, size_t length) {
    while (length--) {
        rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17;
        *out++ = (uint8_t)rng_state;
    }
}
static uint64_t tick(void) { uint64_t x; if (read(perf_fd, &x, sizeof x) != sizeof x) exit(3); return x; }
__attribute__((noinline)) uint64_t prof_start(void) { return active ? tick() : 0; }
__attribute__((noinline)) void prof_end(int group, uint64_t start) {
    if (active) { totals[group] += tick() - start; calls[group]++; }
}
static void *must_symbol(void *h, const char *name) {
    void *p = dlsym(h, name); if (!p) { fprintf(stderr, "missing %s: %s\n", name, dlerror()); exit(2); } return p;
}
static struct api load(const char *path) {
    void *h = dlopen(path, RTLD_NOW | RTLD_LOCAL); if (!h) { fprintf(stderr, "%s\n", dlerror()); exit(2); }
    return (struct api){ must_symbol(h,"crypto_kem_keypair"), must_symbol(h,"crypto_kem_enc"), must_symbol(h,"crypto_kem_dec") };
}
static uint8_t pk[PK], sk[SK], ct[CT], ss[SS];
static void setup(struct api a) {
    rng_state=0xb6123001; if (a.key(pk,sk)) exit(4);
    rng_state=0xb6123002; if (a.enc(ct,ss,pk)) exit(4);
    uint8_t out[SS]; if (a.dec(out,ct,sk) || memcmp(out,ss,SS)) exit(4);
}
static void invoke(struct api a, int op, int iteration) {
    rng_state=0xb6000000ULL+(uint64_t)iteration*0x9e3779b1ULL;
    int result = op==0 ? a.key(pk,sk) : op==1 ? a.enc(ct,ss,pk) : a.dec(ss,ct,sk);
    if (result) exit(4);
}
static int compare_u64(const void *a, const void *b) {
    uint64_t x=*(const uint64_t *)a, y=*(const uint64_t *)b; return (x>y)-(x<y);
}
int main(int argc, char **argv) {
    if (argc != 4) return 2;
    const char *label=argv[1]; struct api plain=load(argv[2]), profiled=load(argv[3]);
    struct perf_event_attr attr={0}; attr.size=sizeof attr; attr.type=PERF_TYPE_HARDWARE;
    attr.config=PERF_COUNT_HW_CPU_CYCLES; attr.exclude_kernel=1; attr.exclude_hv=1;
    perf_fd=syscall(__NR_perf_event_open,&attr,0,-1,-1,0); if(perf_fd<0){perror("perf");return 3;}
    uint64_t overhead_samples[1001]; active=1;
    for(int i=0;i<1001;i++){uint64_t t=prof_start();prof_end(0,t);overhead_samples[i]=totals[0];totals[0]=calls[0]=0;}
    qsort(overhead_samples,1001,sizeof(uint64_t),compare_u64); double overhead=overhead_samples[500];
    uint8_t saved[PK+SK+CT+SS]; active=0; setup(plain);
    memcpy(saved,pk,PK);memcpy(saved+PK,sk,SK);memcpy(saved+PK+SK,ct,CT);memcpy(saved+PK+SK+CT,ss,SS);
    active=1;setup(profiled);active=0;
    if(memcmp(saved,pk,PK)||memcmp(saved+PK,sk,SK)||memcmp(saved+PK+SK,ct,CT)||memcmp(saved+PK+SK+CT,ss,SS)) return 5;
    printf("instrumentation_equivalence=pass,label=%s,overhead=%.3f\n",label,overhead);
    const char *operations[]={"keygen","encaps","decaps"};
    for(int op=0;op<3;op++) for(int sample=-3;sample<21;sample++) {
        active=0;setup(profiled);memset(totals,0,sizeof totals);memset(calls,0,sizeof calls);active=1;
        int repetitions=op==0?4:20;for(int i=0;i<repetitions;i++)invoke(profiled,op,i);active=0;
        if(sample>=0)for(int group=0;group<GROUPS;group++)if(calls[group])
            printf("profile,%s,%s,%s,%.3f,%.3f,%.3f\n",operations[op],label,group_names[group],
                   (double)totals[group]/repetitions,
                   ((double)totals[group]-overhead*calls[group])/repetitions,
                   (double)calls[group]/repetitions);
    }
    return 0;
}
