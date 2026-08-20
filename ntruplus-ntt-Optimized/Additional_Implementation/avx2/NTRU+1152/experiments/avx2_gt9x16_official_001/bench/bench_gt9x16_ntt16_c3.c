#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <immintrin.h>
#include "gt9x16_ntt16_asm.h"

#define SAMPLES 201
#define CALLS 4096
typedef void (*row_function)(ntruplus1152_exp001_gt_ntt16_row_pair *,
                             const ntruplus1152_exp001_gt_ntt16_row_pair *);
static uint64_t start_cycles(void) { unsigned int a; _mm_lfence(); return __rdtscp(&a); }
static uint64_t stop_cycles(void) { unsigned int a; uint64_t v=__rdtscp(&a); _mm_lfence(); return v; }
static int cmp(const void *a,const void *b){uint64_t x=*(const uint64_t*)a,y=*(const uint64_t*)b;return(x>y)-(x<y);}
static uint64_t measure(row_function f) {
  ntruplus1152_exp001_gt_ntt16_row_pair a,b; uint64_t s[SAMPLES]; int c,i,j;
  for(i=0;i<2;i++) for(j=0;j<16;j++) a.coefficient[i][j]=(int16_t)(i*997+j*131-1728);
  for(i=0;i<SAMPLES;i++){uint64_t t=start_cycles();for(c=0;c<CALLS;c+=2){f(&b,&a);f(&a,&b);}s[i]=stop_cycles()-t;}
  qsort(s,SAMPLES,sizeof s[0],cmp); if(a.coefficient[i&1][i&15]==INT16_C(0x5a5a))fputs("sink\n",stderr); return s[SAMPLES/2];
}
static void print(const char*n,uint64_t c){printf("  \"%s\": {\"batch_cycles_median\": %"PRIu64", \"calls\": %d, \"cycles_per_row_pair\": %.3f}",n,c,CALLS,(double)c/CALLS);}
int main(void){uint64_t c2=measure(ntruplus1152_exp001_gt9x16_ntt16_c2_row_pair),c3=measure(ntruplus1152_exp001_gt9x16_ntt16_c3_row_pair);puts("{");puts("  \"benchmark_class\": \"repository-local-diagnostic-not-for-promotion\",");printf("  \"samples\": %d,\n",SAMPLES);print("c2_reconstruct_each_layer",c2);puts(",");print("c3_official_persistent_sd",c3);puts("\n}");}
