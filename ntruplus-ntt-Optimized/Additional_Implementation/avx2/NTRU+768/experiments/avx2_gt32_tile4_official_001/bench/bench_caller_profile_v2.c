#include "caller_profile.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

volatile long long profile_end;
volatile long long profile_start;
unsigned profile_rng_calls, profile_ftries;
profile_bank *profile_rng_bank;
/* SUPERCOP nontimecop declassification is a no-op; retain the external call. */
void crypto_declassify(const void *p,unsigned long long n) {(void)p;(void)n;}
typedef struct { const char *op; int cut; const char *label; char variant; profile_fn fn; } entry;
#include "entries.h"
#define COUNT (sizeof entries/sizeof entries[0])
static profile_bank seeds[8], expected[8], active;
static uint64_t rng=0x765432198abcdefULL;
static unsigned char byte(void) { rng^=rng<<13; rng^=rng>>7; rng^=rng<<17; return (unsigned char)rng; }
void randombytes(unsigned char *p, unsigned long long n) {
    if(n!=32 || profile_rng_calls>=64) abort();
    memcpy(p,profile_rng_bank->seeds[profile_rng_calls++],32);
}
static void reset(const profile_bank *b) {
    memcpy(&active,b,sizeof active); profile_rng_bank=&active;
    profile_rng_calls=0; profile_ftries=0; profile_end=0;profile_start=0;
}
static entry *optional(const char *op,const char *label,char v) {
    for(size_t i=0;i<COUNT;i++) if(entries[i].variant==v && !strcmp(entries[i].op,op) && !strcmp(entries[i].label,label)) return &entries[i];
    return NULL;
}
static entry *lookup(const char *op,const char *label,char v) {
    entry *e=optional(op,label,v);if(e)return e;
    abort();
}
static void guards(const profile_bank *b) {
    for(int i=0;i<8;i++) if(b->guard0[i]!=0xabcddcba13577531ULL || b->guard1[i]!=0xabcddcba13577531ULL) abort();
}
static void init(profile_bank *b) {
    memset(b,0,sizeof *b);
    for(int i=0;i<8;i++) b->guard0[i]=b->guard1[i]=0xabcddcba13577531ULL;
    for(size_t i=0;i<sizeof b->seeds;i++) ((unsigned char*)b->seeds)[i]=byte();
    for(size_t i=0;i<sizeof b->coins;i++) b->coins[i]=byte();
}
static void error(const entry *e,int vec,const char *why) {
    fprintf(stderr,"FAIL %s/%s/%c vector=%d %s\n",e->op,e->label,e->variant,vec,why);exit(1);
}
static void check(const entry *e,int rc,const profile_bank *input,const profile_bank *want,int vec) {
    guards(&active);
    if(rc) error(e,vec,"valid input rejected");
    if(memcmp(active.seeds,input->seeds,sizeof active.seeds)||memcmp(active.coins,input->coins,sizeof active.coins)) error(e,vec,"coins mutated");
    if(!strcmp(e->op,"keygen")) {
        if(memcmp(active.pk,want->pk,1152)||memcmp(active.sk,want->sk,2336)) error(e,vec,"PK/SK mismatch");
        if(profile_rng_calls!=want->totaltries) error(e,vec,"retry count mismatch");
        if(e->cut==0 && profile_ftries!=want->ftries) error(e,vec,"f retry mismatch");
    } else if(!strncmp(e->op,"encap",5)) {
        if(memcmp(active.ct,want->ct,1152)||memcmp(active.ss,want->ss,32)) error(e,vec,"CT/SS mismatch");
        if(memcmp(active.pk,input->pk,1152)||memcmp(active.sk,input->sk,2336)) error(e,vec,"PK/SK mutated");
    } else if(!strncmp(e->op,"decap",5)) {
        if(memcmp(active.ss,want->ss,32)) error(e,vec,"decapsulated SS mismatch");
        if(memcmp(active.ct,input->ct,1152)||memcmp(active.sk,input->sk,2336)) error(e,vec,"CT/SK mutated");
    }
}
static void prepare(profile_bank *input,profile_bank *want) {
    init(input); reset(input);
    if(lookup("keygen","f_retry_loop",'o')->fn(&active)) abort();
    active.ftries=profile_ftries;active.totaltries=profile_rng_calls;
    *input=active;
    if(lookup("encap","external_total",'o')->fn(&active)) abort();
    *input=active;*want=active;
}
static void invalid_check(const profile_bank *valid) {
    profile_bank bad=*valid; unsigned char refss[32],refct[1152];
    for(int kind=0;kind<3;kind++) {
        bad=*valid;
        if(kind==0) {bad.pk[0]=255;bad.pk[1]|=15;} // coefficient 4095
        if(kind==1) {bad.ct[0]=255;bad.ct[1]|=15;}
        if(kind==2) {bad.ct[0]=0;bad.ct[1]&=240;} // canonical tamper
        const char *op=kind?"decap":"encap";int refrc=-1;
        for(int v=0;v<(optional(op,"external_total",'m')?3:2);v++) {
            char tag="ogm"[v];reset(&bad);
            int rc=lookup(op,"external_total",tag)->fn(&active);guards(&active);
            if(!v) {refrc=rc;memcpy(refss,active.ss,32);memcpy(refct,active.ct,1152);}
            else if(rc!=refrc||memcmp(refss,active.ss,32)||memcmp(refct,active.ct,1152)) abort();
        }
        if(refrc!=1) abort();
        for(int j=0;j<32;j++) if(refss[j]) abort();
    }
}
int main(int argc,char **argv) {
    (void)argv; unsigned retries=0,maxtries=0;profile_bank in,want;
    for(int vec=0;vec<100;vec++) {
        prepare(&in,&want);retries+=want.totaltries-2;
        if(want.totaltries>maxtries)maxtries=want.totaltries;
        for(size_t e=0;e<COUNT;e++) {
            reset(&in);int rc=entries[e].fn(&active);check(&entries[e],rc,&in,&want,vec);
            if(strcmp(entries[e].label,"external_total") && !profile_end) error(&entries[e],vec,"end counter not reached");
        }
        invalid_check(&in);
        if(vec<8) {seeds[vec]=in;expected[vec]=want;}
        if(argc>1) printf("vector,%d,f_attempts,%u,g_attempts,%u\n",vec,want.ftries,want.totaltries-want.ftries);
    }
    fprintf(stderr,"preflight=pass vectors=100 all_cutpoints_exact invalid_PK_CT=pass retries=%u max_total_attempts=%u cpucycles_implementation=%s cpucycles_persecond=%lld\n",retries,maxtries,cpucycles_implementation(),cpucycles_persecond());
    if(argc>1)return 0;
    // All variants share the exact same mutable bank and reset/warm policy.
    printf("op,cut,label,variant,block,bank,cycles\n");
    const int orders[6][3]={{0,1,2},{1,2,0},{2,0,1},{2,1,0},{1,0,2},{0,2,1}};
    static long long raw[COUNT][96][3];
    for(int block=0;block<96;block++) for(size_t step=0;step<COUNT;step++) {
        size_t i=(block&1)?COUNT-1-step:step;
        entry *base=&entries[i];if(base->variant!='o')continue;
        entry *v[3]={base,lookup(base->op,base->label,'g'),NULL};
        int nv=optional(base->op,base->label,'m')?3:2;
        if(nv==3)v[2]=lookup(base->op,base->label,'m');
        for(int k=0;k<nv;k++) {
            int j=nv==3?orders[block%6][k]:((block&1)?1-k:k),bank=block%8;
            profile_fn fn=v[j]->fn;int external=!strcmp(base->label,"external_total");
            int window=strchr(base->op,'_')!=NULL && strncmp(base->op,"attempt",7)!=0;
            reset(&seeds[bank]);int rc=fn(&active);check(v[j],rc,&seeds[bank],&expected[bank],bank);
            reset(&seeds[bank]);
            long long start=window?0:cpucycles();
            rc=fn(&active);
            long long end=external?cpucycles():profile_end;
            if(window)start=profile_start;
            raw[i][block][j]=end-start;
            check(v[j],rc,&seeds[bank],&expected[bank],bank);
            if(end<=start) error(v[j],bank,"invalid counter delta");
        }
    }
    for(size_t i=0;i<COUNT;i++) if(entries[i].variant=='o')
        for(int block=0;block<96;block++)for(int j=0;j<(optional(entries[i].op,entries[i].label,'m')?3:2);j++)
            printf("%s,%d,%s,%c,%d,%d,%lld\n",entries[i].op,entries[i].cut,entries[i].label,"ogm"[j],block,block%8,raw[i][block][j]);
    return 0;
}
