#include <stdio.h>
#include <stdint.h>
#include <time.h>
void KeccakF1600_StatePermute(uint64_t*);                 /* Official 的可攜 C */
void ntruplus_keccak_f1600_x1_aarch64(uint64_t*, const uint64_t*);  /* GT 的手寫純量 */
extern const uint64_t KeccakF_RoundConstants[];
static inline uint64_t nsec(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
 return (uint64_t)t.tv_sec*1000000000ull+(uint64_t)t.tv_nsec;}
static volatile unsigned sink; static uint64_t st[25];
int main(void){
  for(int w=0;w<200000;w++){KeccakF1600_StatePermute(st); ntruplus_keccak_f1600_x1_aarch64(st,KeccakF_RoundConstants);}
  uint64_t b0=~0ull,b1=~0ull;
  for(int r=0;r<41;r++){
    uint64_t a=nsec(); for(int k=0;k<20000;k++){KeccakF1600_StatePermute(st); sink+=(unsigned)st[0];} uint64_t d=nsec()-a; if(d<b0)b0=d;
    a=nsec(); for(int k=0;k<20000;k++){ntruplus_keccak_f1600_x1_aarch64(st,KeccakF_RoundConstants); sink+=(unsigned)st[0];} d=nsec()-a; if(d<b1)b1=d; }
  printf("  Official 可攜 C        %6.1f ns/次\n  GT keccakf1600.S      %6.1f ns/次   (%.2fx)\n",
         (double)b0/20000,(double)b1/20000,(double)b0/(double)b1);
  return 0;}
