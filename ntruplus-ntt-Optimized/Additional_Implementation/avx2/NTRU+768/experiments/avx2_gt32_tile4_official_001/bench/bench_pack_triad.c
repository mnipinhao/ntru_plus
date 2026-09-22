/* Reuse actual CBD1/SOTP setup and Official untimed oracle, not its timing loop. */
#define FN_PACK_IDENTITY14
#define ntruplus768_exp001_pack_identity14 ntruplus768_exp001_pack_triad_i
#define ntruplus768_exp001_pack_identity14_highrange ntruplus768_exp001_pack_triad_i_highrange
#define main legacy_unused_main
#include "bench_encap_fn.c"
#undef main

#define WRAPPERS(L) \
void ntruplus768_exp001_pack_triad_##L(uint8_t*,const int16_t*); \
void ntruplus768_exp001_pack_triad_##L##_highrange(uint8_t*,const int16_t*); \
static void L##_r(state*s){ntruplus768_exp001_pack_triad_##L(s->rb,s->r);} \
static void L##_c(state*s){ntruplus768_exp001_pack_triad_##L##_highrange(s->cb,s->c);} \
static void L##_dual(state*s){gt_r(s);L##_r(s);} \
static void L##_full(state*s){gt_decode(s);L##_dual(s);gt_m(s);gt_muladd(s);L##_c(s);}
WRAPPERS(c)
WRAPPERS(i)
WRAPPERS(m)
static operation triad[3][4]={{c_r,c_c,c_dual,c_full},{i_r,i_c,i_dual,i_full},{m_r,m_c,m_dual,m_full}};
int main(int argc,char**argv){
    preflight();
    state*s=&slots[0]; /* Identical addresses for all three implementations. */
    for(int b=0;b<BANKS;b++)for(int v=0;v<3;v++)for(int r=0;r<4;r++){
        bank_id=b;memcpy(s,&initial[1][b],sizeof *s);triad[v][r](s);
        if(memcmp(s->r,initial[1][b].r,sizeof s->r))fail("retained r");
        if(r!=1&&memcmp(s->rb,initial[1][b].rb,BYTES))fail("triad hash bytes");
        if((r==1||r==3)&&memcmp(s->cb,initial[1][b].cb,BYTES))fail("triad ciphertext bytes");
    }
    fprintf(stderr,"preflight=pass cpucycles=%s cpucycles_persecond=%lld input_address=%p\n",
        cpucycles_implementation(),(long long)cpucycles_persecond(),(void*)s);
    if(argc>1&&!strcmp(argv[1],"--check"))return 0;
    const int order[6][3]={{0,1,2},{1,2,0},{2,0,1},{2,1,0},{1,0,2},{0,2,1}};
    puts("region,variant,block,position,cycles");
    for(int r=0;r<4;r++)for(int block=0;block<96;block++){
        bank_id=block%BANKS;
        for(int position=0;position<3;position++){
            int v=order[block%6][position];operation fn=triad[v][r];
            memcpy(s,&initial[1][bank_id],sizeof *s);fn(s);
            memcpy(s,&initial[1][bank_id],sizeof *s);
            __asm__ volatile("":::"memory");
            long long t0=cpucycles();fn(s);long long t1=cpucycles();
            __asm__ volatile("":::"memory");
            printf("%d,%d,%d,%d,%lld\n",r,v,block,position,t1-t0);
        }
    }
    return 0;
}
