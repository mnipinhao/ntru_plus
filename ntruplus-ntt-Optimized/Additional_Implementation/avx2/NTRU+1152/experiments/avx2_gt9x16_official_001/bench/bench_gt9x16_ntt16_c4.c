#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <immintrin.h>
#include "gt9x16_ntt16_asm.h"
#define SAMPLES 201
#define CALLS 1024
typedef void (*kernel)(void *, const void *);
static uint64_t begin(void){unsigned int a;_mm_lfence();return __rdtscp(&a);}static uint64_t end(void){unsigned int a;uint64_t v=__rdtscp(&a);_mm_lfence();return v;}static int cmp(const void*a,const void*b){uint64_t x=*(const uint64_t*)a,y=*(const uint64_t*)b;return(x>y)-(x<y);}
static uint64_t measure(kernel f){ntruplus1152_exp001_gt_row_pair in;ntruplus1152_exp001_gt_persistent_pair out;uint64_t s[SAMPLES];int c,i,j,k;for(i=0;i<2;i++)for(j=0;j<9;j++)for(k=0;k<16;k++)in.coefficient[i].values[j][k]=(int16_t)(i*997+j*131+k*17-1728);for(i=0;i<SAMPLES;i++){uint64_t t=begin();for(c=0;c<CALLS;c++)f(&out,&in);s[i]=end()-t;}qsort(s,SAMPLES,sizeof s[0],cmp);if(out.state[i%9][i&1][i&15]==INT16_C(0x5a5a))fputs("sink\n",stderr);return s[SAMPLES/2];}
static void print(const char*n,uint64_t c){printf("  \"%s\": {\"batch_cycles_median\": %"PRIu64", \"calls\": %d, \"cycles_per_nine_row_pair\": %.3f}",n,c,CALLS,(double)c/CALLS);}
int main(void){uint64_t c0=measure((kernel)ntruplus1152_exp001_gt9x16_ntt16_c0_pair),seq=measure((kernel)ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_sequential),pipe=measure((kernel)ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_pipelined),natural=measure((kernel)ntruplus1152_exp001_gt9x16_ntt16_c4_with_shear);puts("{");puts("  \"benchmark_class\": \"repository-local-diagnostic-not-for-promotion\",");printf("  \"samples\": %d,\n",SAMPLES);print("c0_two_islands_natural",c0);puts(",");print("c4_from_z_sequential",seq);puts(",");print("c4_from_z_two_row_pipeline",pipe);puts(",");print("c4_natural_zero_materialization",natural);puts("\n}");}
