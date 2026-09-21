/* Per-component decaps profile, one binary per tree, real decaps state. */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include "api.h"
#include "poly.h"
#ifdef GT
#include "unpack.h"
#endif
#include "symmetric.h"
#ifdef GT
#include "inverse.h"
#include "pack.h"
#endif
static int fd;
static uint64_t rd(void){uint64_t v;if(read(fd,&v,8)!=8)exit(3);return v;}
static int cmpu(const void*a,const void*b){uint64_t x=*(const uint64_t*)a,y=*(const uint64_t*)b;return(x>y)-(x<y);}
#define R 65
#define N 300
static uint64_t ov;
/* copy of the official's static inline verify(), which cannot be linked to */
static inline int my_verify(const uint8_t *a, const uint8_t *b, size_t len)
{
    uint8_t acc = 0;
    for (size_t i = 0; i < len; i++) acc |= (uint8_t)(a[i] ^ b[i]);
    return (int)((-(uint64_t)acc) >> 63);
}
#define TIME(label, stmt) do { \
    static uint64_t s[R]; \
    for (int r=0;r<R;r++){ uint64_t t0=rd(); for(int k=0;k<N;k++){ stmt; } s[r]=(rd()-t0-ov)/N; } \
    qsort(s,R,sizeof(uint64_t),cmpu); \
    printf("%-22s %llu\n", label, (unsigned long long)s[R/2]); } while(0)

static uint8_t pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES];
static uint8_t ct[CRYPTO_CIPHERTEXTBYTES], ss[CRYPTO_BYTES];
static poly c,f,hinv,m,t1,t2;
static uint8_t buf1[NTRUPLUS_POLYBYTES], buf2[64], buf3[64], msg[NTRUPLUS_SSBYTES];

int main(void){
  struct perf_event_attr a={0};a.size=sizeof a;a.type=PERF_TYPE_HARDWARE;
  a.config=PERF_COUNT_HW_CPU_CYCLES;a.exclude_kernel=1;a.exclude_hv=1;
  fd=syscall(__NR_perf_event_open,&a,0,-1,-1,0);if(fd<0){perror("perf");return 3;}
  {uint64_t t=rd();ov=rd()-t;}
  if(crypto_kem_keypair(pk,sk)||crypto_kem_enc(ct,ss,pk)){fputs("setup\n",stderr);return 1;}
  poly_frombytes(&c,ct); poly_frombytes(&f,sk); poly_frombytes(&hinv,sk+NTRUPLUS_POLYBYTES);

  TIME("frombytes x3", poly_frombytes(&t1,ct); poly_frombytes(&t2,sk); poly_frombytes(&t2,sk+NTRUPLUS_POLYBYTES));
#ifdef GT
  TIME("basemul_rinv",  poly_basemul_rinv(m.coeffs,c.coeffs,f.coeffs));
  poly_basemul_rinv(m.coeffs,c.coeffs,f.coeffs);
  TIME("invntt+crepmod3", poly_invntt_ternary(&t1,&m));
#else
  TIME("basemul",       poly_basemul(&m,&c,&f));
  poly_basemul(&m,&c,&f);
  TIME("invntt",        poly_invntt(&t1,&m));
  poly_invntt(&m,&m);
  TIME("crepmod3",      poly_crepmod3(&t1,&m));
#endif
  TIME("ntt",           poly_ntt(&t1,&m));
  TIME("sub",           poly_sub(&t1,&c,&t2));
  TIME("basemul(hinv)", poly_basemul(&t1,&c,&hinv));
#ifdef GT
  TIME("tobytes_small", poly_tobytes_small(buf1,&t1));
#else
  TIME("tobytes",       poly_tobytes(buf1,&t1));
#endif
  TIME("hash_g",        hash_g(buf2,buf1));
  TIME("sotp_decode",   poly_sotp_decode(msg,&m,buf2));
  TIME("hash_h",        hash_h(buf3,msg));
  TIME("cbd1",          poly_cbd1(&t1,buf3+NTRUPLUS_SSBYTES));
#ifdef GT
  TIME("tobytes_compare", poly_tobytes_compare(buf1,&t1));
#else
  TIME("tobytes(final)", poly_tobytes(buf2,&t1));
  { static uint8_t vb[NTRUPLUS_POLYBYTES]; static volatile int sink;
    TIME("verify(ct compare)", sink = my_verify(buf1, vb, NTRUPLUS_POLYBYTES)); }
#endif
  return 0;}
