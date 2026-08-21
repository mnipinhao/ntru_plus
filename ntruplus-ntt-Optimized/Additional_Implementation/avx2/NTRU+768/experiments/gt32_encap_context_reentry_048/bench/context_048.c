#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "api.h"
#include "params.h"
#include "poly.h"
#include "symmetric.h"
#include "vector_048.h"
#ifdef GT_IMPL
#include "internal.h"
#endif

#define SAMPLES 2048
#define HOT_REPEATS 8
static volatile uint8_t sink;
static uint64_t digest(const uint8_t *p,size_t n) {
 uint64_t h=UINT64_C(1469598103934665603);
 for(size_t i=0;i<n;i++) { h^=p[i]; h*=UINT64_C(1099511628211); }
 return h;
}
static inline uint64_t begin_ticks(void) { _mm_lfence(); return __rdtsc(); }
static inline uint64_t end_ticks(void) { unsigned aux; uint64_t x = __rdtscp(&aux); _mm_lfence(); return x; }
static int cmp64(const void *a, const void *b) { uint64_t x=*(const uint64_t *)a,y=*(const uint64_t *)b; return x>y?1:x<y?-1:0; }

#ifdef GT_IMPL
typedef struct __attribute__((aligned(64))) {
 int16_t h[NTRUPLUS_N],r[NTRUPLUS_N],m[NTRUPLUS_N],c[NTRUPLUS_N],work[NTRUPLUS_N];
 uint8_t msg[HASH_H_INBYTES],buf[HASH_H_OUTBYTES],ct[NTRUPLUS_POLYBYTES];
} state_t;
static void prefix_r2(state_t *s) {
 if (ntruplus768_unpack_m_avx2(s->h,kat_pk)) abort();
 memcpy(s->msg,test_coins,NTRUPLUS_N/8);
 hash_f(s->msg+NTRUPLUS_N/8,kat_pk); hash_h(s->buf,s->msg);
 poly_cbd1((poly *)(void *)s->work,s->buf+NTRUPLUS_SYMBYTES);
}
static void target_r2(state_t *s) {
 ntruplus768_ntt_frontend_avx2(s->c,s->work); ntruplus768_ntt_m_avx2(s->r,s->c);
 ntruplus768_pack_m_lazy10788_avx2(s->ct,s->r); sink^=s->ct[0];
}
static void prefix_r3(state_t *s) {
 prefix_r2(s); target_r2(s); hash_g(s->ct,s->ct);
 poly_sotp_encode((poly *)(void *)s->work,s->msg,s->ct);
}
static void target_r3(state_t *s) {
 ntruplus768_ntt_frontend_avx2(s->c,s->work); ntruplus768_ntt_m_avx2(s->m,s->c);
 ntruplus768_basemul_general_m_avx2(s->c,s->h,s->r);
 poly_add((poly *)(void *)s->c,(poly *)(void *)s->c,(poly *)(void *)s->m);
 ntruplus768_pack_m_highrange12699_avx2(s->ct,s->c); sink^=s->ct[1];
}
#else
typedef struct __attribute__((aligned(64))) {
 poly h,r,m,c,rcoef,mcoef;
 uint8_t msg[HASH_H_INBYTES],buf[HASH_H_OUTBYTES],ct[NTRUPLUS_POLYBYTES];
} state_t;
static void prefix_r2(state_t *s) {
 if (poly_frombytes(&s->h,kat_pk)) abort();
 memcpy(s->msg,test_coins,NTRUPLUS_N/8);
 hash_f(s->msg+NTRUPLUS_N/8,kat_pk); hash_h(s->buf,s->msg);
 poly_cbd1(&s->rcoef,s->buf+NTRUPLUS_SYMBYTES); s->r=s->rcoef;
}
static void target_r2(state_t *s) { poly_ntt(&s->r); poly_tobytes(s->ct,&s->r); sink^=s->ct[0]; }
static void prefix_r3(state_t *s) {
 prefix_r2(s); target_r2(s); hash_g(s->ct,s->ct);
 poly_sotp_encode(&s->mcoef,s->msg,s->ct); s->m=s->mcoef;
}
static void target_r3(state_t *s) {
 poly_ntt(&s->m); poly_basemul(&s->c,&s->h,&s->r);
 poly_add(&s->c,&s->c,&s->m); poly_tobytes(s->ct,&s->c); sink^=s->ct[1];
}
#endif

static void reset_r2(state_t *s) {
#ifndef GT_IMPL
 s->r=s->rcoef;
#else
 (void)s;
#endif
}
static void reset_r3(state_t *s) {
#ifndef GT_IMPL
 s->m=s->mcoef;
#else
 (void)s;
#endif
}
static uint64_t measure_one(state_t *s,int target,int real) {
 if (real) { if(target==2) prefix_r2(s); else prefix_r3(s); }
 else {
  if(target==2) prefix_r2(s); else prefix_r3(s);
  for(int i=0;i<HOT_REPEATS;i++) {
   if(target==2) { reset_r2(s); target_r2(s); }
   else { reset_r3(s); target_r3(s); }
  }
 }
 if(target==2) reset_r2(s); else reset_r3(s);
 uint64_t a=begin_ticks();
 if(target==2) target_r2(s); else target_r3(s);
 return end_ticks()-a;
}
int main(void) {
 state_t *s=aligned_alloc(64,sizeof(state_t)); if(!s) return 1; memset(s,0,sizeof(*s));
 prefix_r2(s); target_r2(s); uint64_t check_r2=digest(s->ct,sizeof s->ct);
 prefix_r3(s); target_r3(s); uint64_t check_r3=digest(s->ct,sizeof s->ct);
 fprintf(stderr,"checks %016llx %016llx\n",(unsigned long long)check_r2,(unsigned long long)check_r3);
 uint64_t v[4][SAMPLES];
 for(int i=0;i<SAMPLES;i++) {
  int base=i&3;
  for(int j=0;j<4;j++) { int k=(base+j)&3; v[k][i]=measure_one(s,k<2?2:3,k&1); }
 }
 const char *names[4]={"r2_hot","r2_real","r3_hot","r3_real"};
 for(int k=0;k<4;k++) {
  qsort(v[k],SAMPLES,sizeof(uint64_t),cmp64);
  printf("%s %llu\n",names[k],(unsigned long long)((v[k][SAMPLES/2-1]+v[k][SAMPLES/2])/2));
 }
 free(s); return sink==255;
}
