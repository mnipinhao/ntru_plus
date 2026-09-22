#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "internal.h"
#include "poly.h"
#include "cpucycles.h"

void official_poly_ntt(int16_t *);
void official_poly_basemul(int16_t *,const int16_t *,const int16_t *);
int official_poly_frombytes(int16_t *,const uint8_t *);
void official_poly_tobytes(uint8_t *,const int16_t *);
void ntruplus768_exp001_basemul_eager_m(int16_t *,const int16_t *,const int16_t *);
enum { N=768, BYTES=1152, BANKS=8, REGIONS=12, BLOCKS=48 };
typedef struct __attribute__((aligned(64))) {
    int16_t h[N],r[N],m[N],c[N],work[N],fr[N];
    uint8_t rb[BYTES],cb[BYTES];
} state;
static state initial[3][BANKS], slots[3];
static _Alignas(64) int16_t rin[BANKS][N],minput[BANKS][N];
static uint8_t pk[BANKS][BYTES];
static int bank_id;
static uint64_t seed=UINT64_C(0x928fc21);
static uint32_t rnd(void){seed^=seed<<13;seed^=seed>>7;seed^=seed<<17;return (uint32_t)seed;}
static void fail(const char *s){fprintf(stderr,"preflight FAIL %s\n",s);exit(1);}
static void off_r(state*s){official_poly_ntt(s->r);}
static void off_m(state*s){official_poly_ntt(s->m);}
static void off_two(state*s){off_r(s);off_m(s);}
static void off_decode(state*s){if(official_poly_frombytes(s->h,pk[bank_id]))abort();}
static void off_mul(state*s){official_poly_basemul(s->c,s->h,s->r);}
static void off_packr(state*s){official_poly_tobytes(s->rb,s->r);}
static void off_packc(state*s){official_poly_tobytes(s->cb,s->c);}
static void add(state*s){poly_add((poly*)s->c,(const poly*)s->c,(const poly*)s->m);}
static void off_muladd(state*s){off_mul(s);add(s);}
static void off_dual(state*s){off_r(s);off_packr(s);}
static void off_full(state*s){off_decode(s);off_dual(s);off_m(s);off_muladd(s);off_packc(s);}
static void gt_front(state*s){ntruplus768_ntt_frontend_avx2(s->work,rin[bank_id]);}
static void gt_terminal(state*s){ntruplus768_ntt_m_avx2(s->r,s->fr);}
static void gt_r(state*s){gt_front(s);ntruplus768_ntt_m_avx2(s->r,s->work);}
static void gt_m(state*s){ntruplus768_ntt_frontend_avx2(s->work,minput[bank_id]);ntruplus768_ntt_m_avx2(s->m,s->work);}
static void gt_two(state*s){gt_r(s);gt_m(s);}
static void gt_decode(state*s){if(ntruplus768_unpack_m_avx2(s->h,pk[bank_id]))abort();}
static void gt_mul(state*s){ntruplus768_basemul_general_m_avx2(s->c,s->h,s->r);}
static void eager_mul(state*s){ntruplus768_exp001_basemul_eager_m(s->c,s->h,s->r);}
static void gt_packr(state*s){ntruplus768_pack_m_lazy10788_avx2(s->rb,s->r);}
static void gt_packc(state*s){ntruplus768_pack_m_highrange12699_avx2(s->cb,s->c);}
static void gt_muladd(state*s){gt_mul(s);add(s);}
static void eager_muladd(state*s){eager_mul(s);add(s);}
static void gt_dual(state*s){gt_r(s);gt_packr(s);}
static void gt_full(state*s){gt_decode(s);gt_dual(s);gt_m(s);gt_muladd(s);gt_packc(s);}
static void eager_full(state*s){gt_decode(s);gt_dual(s);gt_m(s);eager_muladd(s);gt_packc(s);}
#ifdef FN_PACK_IDENTITY14
void ntruplus768_exp001_pack_identity14(uint8_t*,const int16_t*);
void ntruplus768_exp001_pack_identity14_highrange(uint8_t*,const int16_t*);
static void id_packr(state*s){ntruplus768_exp001_pack_identity14(s->rb,s->r);}
static void id_packc(state*s){ntruplus768_exp001_pack_identity14_highrange(s->cb,s->c);}
static void id_dual(state*s){gt_r(s);id_packr(s);}
static void id_full(state*s){gt_decode(s);id_dual(s);gt_m(s);gt_muladd(s);id_packc(s);}
#endif
typedef void (*operation)(state*);
static operation ops[3][REGIONS]={
 {off_r,off_m,off_two,off_decode,off_mul,off_muladd,off_packr,off_packc,off_dual,off_full,NULL,NULL},
 {gt_r,gt_m,gt_two,gt_decode,gt_mul,gt_muladd,gt_packr,gt_packc,gt_dual,gt_full,gt_front,gt_terminal},
#ifdef FN_PACK_IDENTITY14
 {gt_r,gt_m,gt_two,gt_decode,gt_mul,gt_muladd,id_packr,id_packc,id_dual,id_full,gt_front,gt_terminal}};
#else
 {gt_r,gt_m,gt_two,gt_decode,eager_mul,eager_muladd,gt_packr,gt_packc,gt_dual,eager_full,gt_front,gt_terminal}};
#endif

static void reset(state*s,int v,int region,int b) {
    memcpy(s,&initial[v][b],sizeof *s);
    if(v==0&&(region==0||region==2||region==8||region==9)) memcpy(s->r,rin[b],sizeof s->r);
    if(v==0&&(region==1||region==2||region==9)) memcpy(s->m,minput[b],sizeof s->m);
}
static void preflight(void) {
    for(int b=0;b<BANKS;b++){
        bank_id=b;
        uint8_t noise[N/4],msg[N/8];
        for(size_t i=0;i<sizeof noise;i++)noise[i]=(uint8_t)rnd();
        for(size_t i=0;i<sizeof msg;i++)msg[i]=(uint8_t)rnd();
        poly_cbd1((poly*)rin[b],noise);
        poly_sotp_encode((poly*)minput[b],msg,noise);
        for(int i=0;i<N;i+=2){
            unsigned a=rnd()%3457,c=rnd()%3457,k=(unsigned)(3*i/2);
            pk[b][k]=(uint8_t)a;pk[b][k+1]=(uint8_t)((a>>8)|((c&15)<<4));pk[b][k+2]=(uint8_t)(c>>4);
        }
        for(int v=0;v<3;v++){
            state*s=&initial[v][b];
            memcpy(s->r,rin[b],sizeof s->r);memcpy(s->m,minput[b],sizeof s->m);
            ops[v][3](s);ops[v][2](s);ops[v][5](s);
            ntruplus768_ntt_frontend_avx2(s->fr,rin[b]);
            ops[v][6](s);ops[v][7](s);
        }
        for(int v=1;v<3;v++)
            if(memcmp(initial[0][b].rb,initial[v][b].rb,BYTES)||
               memcmp(initial[0][b].cb,initial[v][b].cb,BYTES)) fail("Official vs GT wire bytes");
        for(int region=0;region<REGIONS;region++) for(int v=0;v<3;v++) {
            if(!ops[v][region])continue;
            state*s=&slots[v];reset(s,v,region,b);
            ops[v][region](s);
            const state*ref=&initial[v][b];
            if(region==0||region==2||region==8||region==9||region==11) {
                if(memcmp(s->r,ref->r,sizeof s->r))fail("forward/raw");
            }
            if(region==1||region==2||region==9)if(memcmp(s->m,ref->m,sizeof s->m))fail("m");
            if(region==3)if(memcmp(s->h,ref->h,sizeof s->h))fail("decode");
            if(region==4)add(s);
            if(region==4||region==5||region==9)if(memcmp(s->c,ref->c,sizeof s->c))fail("muladd");
            if(region==6||region==8||region==9)if(memcmp(s->rb,ref->rb,BYTES))fail("hashbytes");
            if(region==7||region==9)if(memcmp(s->cb,ref->cb,BYTES))fail("ciphertext");
            if(region==10)if(memcmp(s->work,ref->fr,sizeof s->work))fail("frontend");
        }
    }
}
int main(int argc,char**argv) {
    preflight();
    fprintf(stderr,"preflight=pass cpucycles=%s cpucycles_persecond=%lld\n",
            cpucycles_implementation(),(long long)cpucycles_persecond());
    if(argc>1&&!strcmp(argv[1],"--check"))return 0;
    puts("region,variant,block,slot,cycles");
    for(int region=0;region<REGIONS;region++) for(int block=0;block<BLOCKS;block++){
        bank_id=block%BANKS;
        /* Three-way balanced sequence; reverse order each block. Rotate data slots. */
        for(int phase=0;phase<6;phase++) {
            int v=(int[]){0,1,2,2,1,0}[phase];
            if(block&1)v=2-v;
            operation fn=ops[v][region];
            if(!fn)continue;
            state*s=&slots[(v+block)%3];
            reset(s,v,region,bank_id);fn(s); /* matching warmup */
            reset(s,v,region,bank_id);      /* destructive Official input reset is untimed */
            __asm__ volatile("":::"memory");
            long long t0=cpucycles();
            fn(s);
            long long t1=cpucycles();
            __asm__ volatile("":::"memory");
            printf("%d,%d,%d,%d,%lld\n",region,v,block,phase,t1-t0);
        }
    }
    return 0;
}
