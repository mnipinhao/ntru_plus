#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#include "../generated/encap_wire_map.h"

enum { N = 768, Q = 3457, BYTES = 1152 };
void ntruplus768_ntt_frontend_avx2(int16_t *, const int16_t *);
void ntruplus768_ntt_m_avx2(int16_t *, const int16_t *);
void ntruplus768_wire_research_forward(int16_t *, const int16_t *);
int ntruplus768_unpack_m_avx2(int16_t *, const uint8_t *);
int ntruplus768_wire_research_decode(int16_t *, const uint8_t *);
void ntruplus768_pack_m_lazy10788_avx2(uint8_t *, const int16_t *);
void ntruplus768_wire_research_pack(uint8_t *, const int16_t *);
void ntruplus768_basemul_general_m_avx2(int16_t *, const int16_t *, const int16_t *);
void ntruplus768_wire_research_muladd_1(int16_t *,const int16_t *,const int16_t *,const int16_t *);
void ntruplus768_wire_research_muladd_2(int16_t *,const int16_t *,const int16_t *,const int16_t *);
int ntruplus768_enc_derand_impl(uint8_t *,uint8_t *,const uint8_t *,const uint8_t *);
int ntruplus768_wire_research_enc_derand_impl(uint8_t *,uint8_t *,const uint8_t *,
    const uint8_t *,int);

static uint64_t seed = UINT64_C(0x768b1c5aaf002133);
static uint32_t rnd(void) {
    seed ^= seed << 13; seed ^= seed >> 7; seed ^= seed << 17;
    return (uint32_t)seed;
}
static int modq(int x) { x %= Q; return x < 0 ? x+Q : x; }
static void die(const char *what, int caseid, int at, int got, int want) {
    fprintf(stderr,"%s case=%d at=%d got=%d want=%d\n",what,caseid,at,got,want);
    exit(1);
}
static void m_to_w(int16_t *w, const int16_t *m) {
    for (int i=0;i<N;i++) w[i]=m[wire_to_m[i]];
}
static void w_to_m(int16_t *m, const int16_t *w) {
    for (int i=0;i<N;i++) m[wire_to_m[i]]=w[i];
}
static void raw12(uint8_t out[BYTES],const int16_t in[N]) {
    for (int i=0;i<N;i+=2) {
        int a=in[i], b=in[i+1];
        out[3*i/2]=(uint8_t)a;
        out[3*i/2+1]=(uint8_t)((a>>8)|((b&15)<<4));
        out[3*i/2+2]=(uint8_t)(b>>4);
    }
}
int main(void) {
    _Alignas(64) int16_t coeff[N], frontend[N], m[N], w[N], expected[N];
    _Alignas(64) int16_t h_m[N],r_m[N],msg_m[N],h_w[N],r_w[N],msg_w[N];
    _Alignas(64) int16_t h_copy[N],r_copy[N],msg_copy[N];
    _Alignas(64) int16_t c_m[N],c_w1[N],c_w2[N];
    uint8_t pk[BYTES],wire_bytes[BYTES],control_bytes[BYTES];
    for(int i=0;i<N;i++) m[i]=(int16_t)i;
    ntruplus768_pack_m_lazy10788_avx2(control_bytes,m);
    for(int i=0;i<N;i++) {
        int off=3*(i/2);
        int got=(i&1)?((control_bytes[off+1]>>4)|(control_bytes[off+2]<<4)):
            (control_bytes[off]|((control_bytes[off+1]&15)<<8));
        if(got!=wire_to_m[i]) die("M map",0,i,got,wire_to_m[i]);
    }
    for (int t=0;t<160;t++) {
        for (int i=0;i<N;i++) coeff[i]=(int16_t)((int)(rnd()%3)-1);
        if (t<4) {
            memset(coeff,0,sizeof coeff);
            if (t==1) coeff[0]=1;
            if (t==2) coeff[N-1]=-1;
            if (t==3) for (int i=0;i<N;i++) coeff[i]=(i&1)?-1:1;
        }
        ntruplus768_ntt_frontend_avx2(frontend,coeff);
        ntruplus768_ntt_m_avx2(m,frontend);
        ntruplus768_wire_research_forward(w,frontend);
        m_to_w(expected,m);
        for (int i=0;i<N;i++) if (w[i]!=expected[i]) {
            for (int j=0;j<32;j++) fprintf(stderr,"%d:%d/%d ",j,w[j],expected[j]);
            fputc('\n',stderr);
            die("forward raw",t,i,w[i],expected[i]);
        }
        ntruplus768_pack_m_lazy10788_avx2(control_bytes,m);
        ntruplus768_wire_research_pack(wire_bytes,w);
        if (memcmp(control_bytes,wire_bytes,BYTES)) die("forward pack",t,0,wire_bytes[0],control_bytes[0]);
    }
    for (int t=0;t<160;t++) {
        for (int i=0;i<N;i++) {
            h_w[i]=(int16_t)(rnd()%Q);
            r_w[i]=(int16_t)((int)(rnd()%31001)-15500);
            msg_w[i]=(int16_t)((int)(rnd()%31001)-15500);
        }
        raw12(pk,h_w);
        int status=ntruplus768_wire_research_decode(h_w,pk);
        int status_m=ntruplus768_unpack_m_avx2(h_m,pk);
        if (status!=status_m) die("decode status",t,0,status,status_m);
        m_to_w(expected,h_m);
        for (int i=0;i<N;i++) if(h_w[i]!=expected[i]) die("decode",t,i,h_w[i],expected[i]);
        w_to_m(r_m,r_w); w_to_m(msg_m,msg_w);
        memcpy(h_copy,h_w,sizeof h_w);
        memcpy(r_copy,r_w,sizeof r_w);
        memcpy(msg_copy,msg_w,sizeof msg_w);
        ntruplus768_basemul_general_m_avx2(c_m,h_m,r_m);
        for (int i=0;i<N;i++) c_m[i]=(int16_t)(c_m[i]+msg_m[i]);
        ntruplus768_wire_research_muladd_1(c_w1,h_w,r_w,msg_w);
        ntruplus768_wire_research_muladd_2(c_w2,h_w,r_w,msg_w);
        if(memcmp(h_copy,h_w,sizeof h_w) || memcmp(r_copy,r_w,sizeof r_w) ||
           memcmp(msg_copy,msg_w,sizeof msg_w)) die("immutable input",t,0,1,0);
        m_to_w(expected,c_m);
        for (int i=0;i<N;i++) {
            if (modq(c_w1[i])!=modq(expected[i])) die("muladd1",t,i,c_w1[i],expected[i]);
            if (modq(c_w2[i])!=modq(expected[i])) die("muladd2",t,i,c_w2[i],expected[i]);
        }
        ntruplus768_pack_m_lazy10788_avx2(control_bytes,c_m);
        ntruplus768_wire_research_pack(wire_bytes,c_w1);
        if (memcmp(control_bytes,wire_bytes,BYTES)) die("ciphertext1",t,0,wire_bytes[0],control_bytes[0]);
        ntruplus768_wire_research_pack(wire_bytes,c_w2);
        if (memcmp(control_bytes,wire_bytes,BYTES)) die("ciphertext2",t,0,wire_bytes[0],control_bytes[0]);
    }
    for (int packet=0;packet<48;packet++) {
        memset(h_w,0,sizeof h_w);
        h_w[16*packet+15]=Q;
        raw12(pk,h_w);
        if (ntruplus768_wire_research_decode(h_w,pk)!=1) die("invalid pk",packet,0,0,1);
    }
    {
        size_t page=(size_t)sysconf(_SC_PAGESIZE);
        if(page<4096) abort();
        uint8_t *input=mmap(NULL,2*page,PROT_READ|PROT_WRITE,
                            MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
        uint8_t *output=mmap(NULL,2*page,PROT_READ|PROT_WRITE,
                             MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
        if(input==MAP_FAILED || output==MAP_FAILED) abort();
        if(mprotect(input+page,page,PROT_NONE) ||
           mprotect(output+page,page,PROT_NONE)) abort();
        uint8_t *pk_tail=input+page-BYTES;
        int16_t *w_tail=(int16_t *)(void *)(output+page-2*N);
        for(int i=0;i<N;i++) h_w[i]=(int16_t)(rnd()%Q);
        raw12(pk,h_w);
        memcpy(pk_tail,pk,BYTES);
        if(ntruplus768_wire_research_decode(w_tail,pk_tail)) abort();
        for(int i=0;i<N;i++) if(w_tail[i]!=h_w[i])
            die("guard decode",0,i,w_tail[i],h_w[i]);
        uint8_t *bytes_tail=output+page-BYTES;
        memcpy((int16_t *)(void *)(input+page-2*N),h_w,sizeof h_w);
        ntruplus768_wire_research_pack(bytes_tail,
            (const int16_t *)(const void *)(input+page-2*N));
        ntruplus768_wire_research_pack(wire_bytes,h_w);
        if(memcmp(bytes_tail,wire_bytes,BYTES)) abort();
        munmap(input,2*page); munmap(output,2*page);
    }
    {
        struct { uint64_t before; int16_t data[N]; uint64_t after; } guarded;
        guarded.before=UINT64_C(0x123456789abcdef0);
        guarded.after=UINT64_C(0xfedcba9876543210);
        for(int i=0;i<N;i++) h_w[i]=r_w[i]=msg_w[i]=0;
        ntruplus768_wire_research_muladd_1(guarded.data,h_w,r_w,msg_w);
        if(guarded.before!=UINT64_C(0x123456789abcdef0) ||
           guarded.after!=UINT64_C(0xfedcba9876543210)) abort();
        ntruplus768_wire_research_muladd_2(guarded.data,h_w,r_w,msg_w);
        if(guarded.before!=UINT64_C(0x123456789abcdef0) ||
           guarded.after!=UINT64_C(0xfedcba9876543210)) abort();
    }
    {
        uint8_t coins[N/8],ct0[BYTES],ct1[BYTES],ss0[32],ss1[32];
        for(int t=0;t<100;t++) {
            for(int i=0;i<N;i++) h_w[i]=(int16_t)(rnd()%Q);
            raw12(pk,h_w);
            for(size_t i=0;i<sizeof coins;i++) coins[i]=(uint8_t)rnd();
            int rc0=ntruplus768_enc_derand_impl(ct0,ss0,pk,coins);
            int rc1=ntruplus768_wire_research_enc_derand_impl(ct1,ss1,pk,coins,t&1);
            if(rc0!=rc1 || memcmp(ct0,ct1,sizeof ct0) || memcmp(ss0,ss1,sizeof ss0))
                die("encap KAT",t,0,ct1[0],ct0[0]);
        }
        for(int packet=0;packet<48;packet++) {
            memset(h_w,0,sizeof h_w);
            h_w[16*packet+15]=Q;
            raw12(pk,h_w);
            memset(ct0,0xa5,sizeof ct0); memset(ct1,0xa5,sizeof ct1);
            memset(ss0,0xa5,sizeof ss0); memset(ss1,0xa5,sizeof ss1);
            int rc0=ntruplus768_enc_derand_impl(ct0,ss0,pk,coins);
            int rc1=ntruplus768_wire_research_enc_derand_impl(ct1,ss1,pk,coins,packet&1);
            if(rc0!=rc1 || memcmp(ct0,ct1,sizeof ct0) || memcmp(ss0,ss1,sizeof ss0))
                die("invalid Encap",packet,0,rc1,rc0);
        }
    }
    puts("wire ASM differential: pass");
    return 0;
}
