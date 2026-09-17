#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define N 768
#define Q 3457
void gt103_basemul_general_ql2_avx2(int16_t*,const int16_t*,const int16_t*);
void gt135_basemul_general_ql2_native_e0(int16_t*,const int16_t*,const int16_t*);
static uint64_t s=UINT64_C(0x1359e3779b97f4a7);
static uint32_t rnd(void){s^=s<<13;s^=s>>7;s^=s<<17;return(uint32_t)s;}
static int modq(int x){x%=Q;if(x<0)x+=Q;return x;}
static void m_to_ql2(int16_t*out,const int16_t*in){
  static const int leaf[4][4]={{0,1,8,9},{2,3,10,11},{4,5,12,13},{6,7,14,15}};
  for(int g=0;g<12;g++)for(int r=0;r<4;r++)for(int k=0;k<4;k++)for(int c=0;c<4;c++)
    out[g*64+r*16+k*4+c]=in[g*64+c*16+leaf[r][k]];
}
static int equal_mod(const int16_t*a,const int16_t*b){for(int i=0;i<N;i++)if(modq(a[i])!=modq(b[i]))return i+1;return 0;}
int main(void){
  _Alignas(64) int16_t a[N],b[N],aq[N],bq[N],ref[N],got[N],tmp[N];
  for(int t=0;t<1000;t++){
    for(int i=0;i<N;i++){a[i]=(int16_t)((int)(rnd()%Q)-1728);b[i]=(int16_t)((int)(rnd()%Q)-1728);}
    m_to_ql2(aq,a);m_to_ql2(bq,b);gt103_basemul_general_ql2_avx2(ref,a,b);gt135_basemul_general_ql2_native_e0(got,aq,bq);
    int bad=equal_mod(ref,got);if(bad){fprintf(stderr,"mismatch trial=%d word=%d ref=%d got=%d\n",t,bad-1,ref[bad-1],got[bad-1]);return 1;}
    memcpy(tmp,aq,sizeof tmp);gt135_basemul_general_ql2_native_e0(tmp,tmp,bq);if(equal_mod(ref,tmp))return 2;
    memcpy(tmp,bq,sizeof tmp);gt135_basemul_general_ql2_native_e0(tmp,aq,tmp);if(equal_mod(ref,tmp))return 3;
  }
  puts("correctness=PASS trials=1000 alias_a=PASS alias_b=PASS");return 0;
}
