/* Does the patched permutation (a) compute the same thing and (b) preserve d8-d15? */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
extern void f1600(uint64_t*, const uint64_t*);
extern void f1600_abi(uint64_t*, const uint64_t*);
static const uint64_t RC[24]={
0x0000000000000001ULL,0x0000000000008082ULL,0x800000000000808aULL,0x8000000080008000ULL,
0x000000000000808bULL,0x0000000080000001ULL,0x8000000080008081ULL,0x8000000000008009ULL,
0x000000000000008aULL,0x0000000000000088ULL,0x0000000080008009ULL,0x000000008000000aULL,
0x000000008000808bULL,0x800000000000008bULL,0x8000000000008089ULL,0x8000000000008003ULL,
0x8000000000008002ULL,0x8000000000000080ULL,0x000000000000800aULL,0x800000008000000aULL,
0x8000000080008081ULL,0x8000000000008080ULL,0x0000000080000001ULL,0x8000000080008008ULL};
int main(void){
  uint64_t a[25],b[25];
  for(int i=0;i<25;i++) a[i]=b[i]=0x0123456789abcdefULL*(i+1);
  f1600(a,RC); f1600_abi(b,RC);
  printf("  輸出相同: %s\n", memcmp(a,b,sizeof a)?"NO":"yes");
  /* hold doubles in v8-v15 across each call and see which survives */
  for(int which=0;which<2;which++){
    register double d8 asm("d8")=1.5, d9 asm("d9")=2.5, d10 asm("d10")=3.5, d11 asm("d11")=4.5;
    register double d12 asm("d12")=5.5, d13 asm("d13")=6.5, d14 asm("d14")=7.5, d15 asm("d15")=8.5;
    uint64_t st[25]; for(int i=0;i<25;i++) st[i]=i;
    __asm__ volatile("" : "+w"(d8),"+w"(d9),"+w"(d10),"+w"(d11),"+w"(d12),"+w"(d13),"+w"(d14),"+w"(d15));
    if(which) f1600_abi(st,RC); else f1600(st,RC);
    __asm__ volatile("" : "+w"(d8),"+w"(d9),"+w"(d10),"+w"(d11),"+w"(d12),"+w"(d13),"+w"(d14),"+w"(d15));
    int ok = d8==1.5&&d9==2.5&&d10==3.5&&d11==4.5&&d12==5.5&&d13==6.5&&d14==7.5&&d15==8.5;
    printf("  %-14s d8-d15 保存: %s\n", which?"patched":"upstream", ok?"yes":"NO");
  }
  return 0;}
