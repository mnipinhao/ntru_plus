#include <assert.h>
#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "internal.h"
#include "poly.h"
#include "../generated/tile4_serialized_mapping.h"
#ifdef WAVEFRONT_SUPERCOP
#include "cpucycles.h"
#endif

typedef void (*forward_fn)(int16_t *, const int16_t *, int16_t *);
extern void ntruplus768_exp_encap_wavefront_1(int16_t *,const int16_t *,int16_t *);
extern void ntruplus768_exp_encap_wavefront_2(int16_t *,const int16_t *,int16_t *);
static void control(int16_t *out,const int16_t *in,int16_t *scratch) {
    ntruplus768_ntt_frontend_avx2(scratch,in);
    ntruplus768_ntt_m_avx2(out,scratch);
}
static forward_fn funcs[] = {control,ntruplus768_exp_encap_wavefront_1,ntruplus768_exp_encap_wavefront_2};
typedef struct __attribute__((aligned(64))) { uint8_t pre[64]; int16_t x[768]; uint8_t post[64]; } guarded;
static uint64_t seed=0x96f3384127adULL;
static uint32_t random32(void) { seed^=seed<<13;seed^=seed>>7;seed^=seed<<17;return (uint32_t)seed; }
static int mod(int64_t x) { int v=(int)(x%3457);return v<0?v+3457:v; }
static int power(int a,int e) { int r=1;for(;e;e>>=1,a=mod(a*a))if(e&1)r=mod(r*a);return r; }
static int reverse5(int x) { int y=0;for(int j=0;j<5;j++,x>>=1)y=2*y+(x&1);return y; }
static int index_m(int tile,int q,int c) {
    int lane=(q%4)*4+(q%16)/4;
    return 128*tile+64*(q/16)+16*c+lane;
}
static int lambda(int tile,int q) {
    return mod(power(675,(32*(tile/2)+3*reverse5(q))%96)*power(tile%2?22:2,3455));
}
static void init(guarded *g) { memset(g,0xA5,sizeof(*g)); }
static void guards(const guarded *g) {for(int i=0;i<64;i++)assert(g->pre[i]==0xA5 && g->post[i]==0xA5);}
static void encode(uint8_t *out,const int16_t *x) {
    for(int s=0;s<768;s+=2) {
        unsigned a=(unsigned)mod(x[gt32_tile4_serialized_to_bm_soa[s]]);
        unsigned b=(unsigned)mod(x[gt32_tile4_serialized_to_bm_soa[s+1]]);
        out[3*s/2]=(uint8_t)a;out[3*s/2+1]=(uint8_t)((a>>8)|(b<<4));out[3*s/2+2]=(uint8_t)(b>>4);
    }
}
static void oracle(const int16_t *input,const int16_t *out,int impulse) {
    for(int t=0;t<6;t++)for(int q=0;q<32;q++) {
        int lam=lambda(t,q);
        for(int c=0;c<4;c++) {
            int expected=0;
            if(impulse>=0) {
                if(c==impulse%4)expected=mod(input[impulse]*power(lam,impulse/4));
            } else {
                for(int k=191;k>=0;k--)expected=mod((int64_t)expected*lam+input[4*k+c]);
            }
            assert(mod(out[index_m(t,q,c)])==expected);
        }
    }
}
static void verify(void) {
    guarded input,work,ref,got,alias;init(&input);init(&work);init(&ref);init(&got);init(&alias);
    uint8_t bytes[192],msg[96];
    for(int trial=0;trial<11543;trial++) {
        for(unsigned j=0;j<sizeof bytes;j++)bytes[j]=(uint8_t)random32();
        for(unsigned j=0;j<sizeof msg;j++)msg[j]=(uint8_t)random32();
        if(trial<1536) {
            memset(input.x,0,sizeof input.x);input.x[trial/2]=(trial&1)?-1:1;
        } else if(trial<1540) {
            for(int j=0;j<768;j++) input.x[j]=(int16_t)(trial==1536?0:trial==1537?1:trial==1538?-1:(j&1?1:-1));
        } else if(trial&1)poly_cbd1((poly *)(void *)input.x,bytes);
        else poly_sotp_encode((poly *)(void *)input.x,msg,bytes);
        int16_t saved[768];memcpy(saved,input.x,sizeof saved);
        for(int j=0;j<768;j++)assert(input.x[j]>=-1 && input.x[j]<=1);
        control(ref.x,input.x,work.x);
        if(trial<1540 || trial<1604)oracle(input.x,ref.x,trial<1536?trial/2:-1);
        for(int v=1;v<3;v++) {
            funcs[v](got.x,input.x,work.x);
            if(memcmp(got.x,ref.x,sizeof ref.x)) {fprintf(stderr,"raw mismatch variant=%d trial=%d\n",v,trial);abort();}
            assert(!memcmp(input.x,saved,sizeof saved));
            memcpy(alias.x,input.x,sizeof alias.x);funcs[v](alias.x,alias.x,work.x);
            assert(!memcmp(alias.x,ref.x,sizeof ref.x));
            funcs[v](work.x,input.x,work.x);assert(!memcmp(work.x,ref.x,sizeof ref.x));
            guards(&got);guards(&work);guards(&alias);guards(&input);guards(&ref);
        }
    }
    // Exhaust the serializer's actual i16 domain, including low-word t*q wrap.
    uint8_t out[1216] __attribute__((aligned(64))),expected[1152];
    for(int start=-32768;start<32768;start+=768) {
        for(int j=0;j<768;j++)got.x[j]=(int16_t)(start+j>32767?32767:start+j);
        memcpy(ref.x,got.x,sizeof got.x);memset(out,0xA5,sizeof out);
        ntruplus768_pack_m_lazy10788_avx2(out,got.x);encode(expected,got.x);
        assert(!memcmp(out,expected,1152));assert(!memcmp(ref.x,got.x,sizeof got.x));
        for(int j=1152;j<1216;j++)assert(out[j]==0xA5);
    }
    // Actual Encap asymmetric B3 and +m, independently checked in each quartic.
    guarded r,m,h,c;init(&r);init(&m);init(&h);init(&c);
    for(int trial=0;trial<100;trial++) {
        for(int j=0;j<768;j++) {input.x[j]=(int16_t)(random32()%3)-1;h.x[j]=(int16_t)(random32()%3457);}
        control(r.x,input.x,work.x);
        for(int j=0;j<768;j++)input.x[j]=(int16_t)(random32()%3)-1;
        control(m.x,input.x,work.x);
        int16_t before[768];memcpy(before,r.x,sizeof before);
        ntruplus768_pack_m_lazy10788_avx2(out,r.x);assert(!memcmp(before,r.x,sizeof before));
        ntruplus768_basemul_general_m_avx2(c.x,h.x,r.x);
        for(int t=0;t<6;t++)for(int q=0;q<32;q++)for(int k=0;k<4;k++) {
            int64_t sum=0;
            for(int a=0;a<4;a++) {int b=(k+4-a)%4;sum+=(int64_t)h.x[index_m(t,q,a)]*r.x[index_m(t,q,b)]*(a+b>=4?lambda(t,q):1);}
            int idx=index_m(t,q,k);assert(mod(c.x[idx])==mod(sum));
            assert(abs(c.x[idx])<=1856);
            int value=c.x[idx]+m.x[idx];assert(abs(value)<=17461);c.x[idx]=(int16_t)value;
        }
        ntruplus768_pack_m_highrange12699_avx2(out,c.x);encode(expected,c.x);assert(!memcmp(out,expected,1152));
        guards(&r);guards(&m);guards(&h);guards(&c);
    }
    puts("{\"correctness\":\"pass\",\"forward_cases\":11543,\"signed_i16_serializer_values\":65536,\"asymmetric_B3_cases\":100}");
}
static int16_t ri[768] __attribute__((aligned(64))),mi[768] __attribute__((aligned(64)));
static int16_t rs[768] __attribute__((aligned(64))),ms[768] __attribute__((aligned(64)));
static int16_t hs[768] __attribute__((aligned(64))),cs[768] __attribute__((aligned(64))),scratch[768] __attribute__((aligned(64)));
static uint8_t wire[1152] __attribute__((aligned(64))),pk[1152] __attribute__((aligned(64)));
static void operation(int variant,int mode) {
    forward_fn f=funcs[variant];
    if(mode==1) {f(ms,mi,scratch);return;}
    f(rs,ri,scratch);
    if(mode==2)f(ms,mi,scratch);
    if(mode>=3)ntruplus768_pack_m_lazy10788_avx2(wire,rs);
    if(mode==4) {
        f(ms,mi,scratch);assert(!ntruplus768_unpack_m_avx2(hs,pk));
        ntruplus768_basemul_general_m_avx2(cs,hs,rs);
        for(int j=0;j<768;j++)cs[j]=(int16_t)(cs[j]+ms[j]);
        ntruplus768_pack_m_highrange12699_avx2(wire,cs);
    }
}
static uint64_t tick(void) {unsigned aux;_mm_lfence();uint64_t t=__rdtscp(&aux);_mm_lfence();return t;}
#ifdef WAVEFRONT_SUPERCOP
// Source-resolved variants: no mode/string dispatch in the counted region.
#define REGION(V,F) \
static void r##V(void){F(rs,ri,scratch);} \
static void m##V(void){F(ms,mi,scratch);} \
static void two##V(void){F(rs,ri,scratch);F(ms,mi,scratch);} \
static void dual##V(void){F(rs,ri,scratch);ntruplus768_pack_m_lazy10788_avx2(wire,rs);} \
static void island##V(void){F(rs,ri,scratch);ntruplus768_pack_m_lazy10788_avx2(wire,rs); \
F(ms,mi,scratch);int status=ntruplus768_unpack_m_avx2(hs,pk);if(status)abort(); \
ntruplus768_basemul_general_m_avx2(cs,hs,rs); \
poly_add((poly *)(void *)cs,(const poly *)(const void *)cs,(const poly *)(const void *)ms); \
ntruplus768_pack_m_highrange12699_avx2(wire,cs);}
REGION(0,control)
REGION(1,ntruplus768_exp_encap_wavefront_1)
REGION(2,ntruplus768_exp_encap_wavefront_2)
static void (*regions[5][3])(void) = {
    {r0,r1,r2},{m0,m1,m2},{two0,two1,two2},{dual0,dual1,dual2},{island0,island1,island2}
};
static void serious(int launch) {
    printf("{\"cpucycles_implementation\":\"%s\",\"cpucycles_persecond\":%lld}\n",cpucycles_implementation(),cpucycles_persecond());
    for(int mode=0;mode<5;mode++)for(int v=1;v<3;v++) {
        // Each measurement has freshly identical semantic inputs and residency.
        for(int warm=0;warm<32;warm++){regions[mode][0]();regions[mode][v]();}
        for(int round=0;round<3;round++)for(int side=0;side<2;side++) {
            int who=((round+launch+side)&1)?v:0;
            void (*op)(void)=regions[mode][who];
            long long timestamps[33];
            for(int i=0;i<32;i++){timestamps[i]=cpucycles();op();}
            timestamps[32]=cpucycles();
            for(int i=0;i<32;i++)printf("{\"derived\":true,\"mode\":%d,\"candidate\":%d,\"round\":%d,\"variant\":%d,\"cycles\":%lld}\n",mode,v,round,who,timestamps[i+1]-timestamps[i]);
        }
    }
}
#endif
int main(int argc,char **argv) {
    (void)argv;
    verify();
    if(argc==1)return 0;
    for(int j=0;j<768;j++){ri[j]=(int16_t)(random32()%3)-1;mi[j]=(int16_t)(random32()%3)-1;hs[j]=(int16_t)(random32()%3457);}
    encode(pk,hs);
#ifdef WAVEFRONT_SUPERCOP
    // Exact island output and retained-r preflight at the actual timed boundary.
    for(int mode=0;mode<5;mode++) {
        regions[mode][0]();
        int16_t saved_r[768],saved_m[768];uint8_t saved_wire[1152];
        memcpy(saved_r,rs,sizeof rs);memcpy(saved_m,ms,sizeof ms);memcpy(saved_wire,wire,sizeof wire);
        for(int v=1;v<3;v++) {
            regions[mode][v]();
            if(mode!=1)assert(!memcmp(rs,saved_r,sizeof rs));
            if(mode==1||mode==2||mode==4)assert(!memcmp(ms,saved_m,sizeof ms));
            if(mode>=3)assert(!memcmp(wire,saved_wire,sizeof wire));
        }
    }
    serious(atoi(argv[1]));return 0;
#endif
    for(int mode=0;mode<5;mode++)for(int v=1;v<3;v++) {
        for(int j=0;j<32;j++){operation(0,mode);operation(v,mode);}
        for(int block=0;block<96;block++)for(int pos=0;pos<4;pos++) {
            int who=((pos==0||pos==3)^(block&1))?0:v;
            uint64_t t=tick();operation(who,mode);t=tick()-t;
            printf("{\"diagnostic_rdtscp\":true,\"mode\":%d,\"candidate\":%d,\"block\":%d,\"variant\":%d,\"cycles\":%llu}\n",mode,v,block,who,(unsigned long long)t);
        }
    }
    return 0;
}
