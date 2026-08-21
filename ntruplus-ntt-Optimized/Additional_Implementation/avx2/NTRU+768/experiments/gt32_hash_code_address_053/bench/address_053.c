#define _GNU_SOURCE
#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#include "KeccakP-1600-SnP.h"
#include "templates.h"

#define SAMPLES 1024
#define REGION_SIZE 0xc000

typedef struct {
    void (*initialize)(void *);
    void (*add_bytes)(void *, const unsigned char *, unsigned int, unsigned int);
    void (*add_byte)(void *, unsigned char, unsigned int);
    void (*permute)(void *);
    void (*extract)(const void *, unsigned char *, unsigned int, unsigned int);
} ops_t;
typedef void (*shake_fn)(uint8_t *, size_t, const uint8_t *, size_t, const ops_t *);
typedef void (*hash_fn)(uint8_t *, const uint8_t *, shake_fn, const ops_t *);

enum { H_O=0x0b20, H_G=0x2000, S_O=0x42d0, S_G=0x5f80,
       H_DUP=0x8b20, S_DUP=0xa2d0 };

static volatile uint8_t sink;
static inline uint64_t begin_ticks(void) { _mm_lfence(); return __rdtsc(); }
static inline uint64_t end_ticks(void) { unsigned a; uint64_t x=__rdtscp(&a); _mm_lfence(); return x; }
static int cmp64(const void *a,const void *b) { uint64_t x=*(const uint64_t*)a,y=*(const uint64_t*)b; return x>y?1:x<y?-1:0; }

static void install(unsigned char *base, size_t off, const unsigned char *src, size_t n) {
    if (off + n > REGION_SIZE) abort();
    memcpy(base + off, src, n);
}

static uint64_t measure(hash_fn h, shake_fn s, const ops_t *ops,
                        uint8_t *out, const uint8_t *in) {
    for (int i=0;i<4;i++) h(out,in,s,ops);
    uint64_t a=begin_ticks(); h(out,in,s,ops); uint64_t b=end_ticks();
    sink ^= out[17]; return b-a;
}

int main(void) {
    long page=sysconf(_SC_PAGESIZE); if(page!=4096) return 2;
    unsigned char *code=mmap(NULL,REGION_SIZE,PROT_READ|PROT_WRITE,
        MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    if(code==MAP_FAILED) return 3;
    install(code,H_O,hash_template_bytes,sizeof(hash_template_bytes));
    install(code,H_G,hash_template_bytes,sizeof(hash_template_bytes));
    install(code,H_DUP,hash_template_bytes,sizeof(hash_template_bytes));
    install(code,S_O,shake_template_bytes,sizeof(shake_template_bytes));
    install(code,S_G,shake_template_bytes,sizeof(shake_template_bytes));
    install(code,S_DUP,shake_template_bytes,sizeof(shake_template_bytes));
    if(mprotect(code,REGION_SIZE,PROT_READ|PROT_EXEC)) return 4;

    hash_fn ho=(hash_fn)(void *)(code+H_O), hg=(hash_fn)(void *)(code+H_G),
            hd=(hash_fn)(void *)(code+H_DUP);
    shake_fn so=(shake_fn)(void *)(code+S_O), sg=(shake_fn)(void *)(code+S_G),
             sd=(shake_fn)(void *)(code+S_DUP);
    ops_t ops={(void*)KeccakP1600_Initialize,(void*)KeccakP1600_AddBytes,
        (void*)KeccakP1600_AddByte,(void*)KeccakP1600_Permute_24rounds,
        (void*)KeccakP1600_ExtractBytes};
    uint8_t *in=aligned_alloc(64,1152), *out=aligned_alloc(64,192), ref[192];
    if(!in||!out) return 5;
    for(int i=0;i<1152;i++) in[i]=(uint8_t)(37*i+11);
    ho(ref,in,so,&ops);
    hash_fn hs[5]={ho,hg,ho,hg,hd}; shake_fn ss[5]={so,so,sg,sg,sd};
    for(int k=0;k<5;k++) { hs[k](out,in,ss[k],&ops); if(memcmp(ref,out,192)) return 6; }

    uint64_t v[5][SAMPLES];
    for(int i=0;i<SAMPLES;i++) {
        int start=i%5;
        for(int j=0;j<5;j++) { int k=(start+j)%5; v[k][i]=measure(hs[k],ss[k],&ops,out,in); }
    }
    const char *names[5]={"OO","GO","OG","GG","DUP"};
    fprintf(stderr,"code_base=%p hash_bytes=%zu shake_bytes=%zu\n",code,
            sizeof(hash_template_bytes),sizeof(shake_template_bytes));
    for(int k=0;k<5;k++) { qsort(v[k],SAMPLES,sizeof(uint64_t),cmp64);
        printf("%s %llu\n",names[k],(unsigned long long)((v[k][511]+v[k][512])/2)); }
    free(in);free(out);munmap(code,REGION_SIZE);return sink==255;
}

