#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>
static uint64_t state=864;
void randombytes(uint8_t*p,size_t n){while(n--){state^=state<<13;state^=state>>7;state^=state<<17;*p++=state;}}
typedef int(*keyfn)(uint8_t*,uint8_t*);typedef int(*encfn)(uint8_t*,uint8_t*,const uint8_t*);typedef int(*decfn)(uint8_t*,const uint8_t*,const uint8_t*);
static void put(uint8_t*b,int i,unsigned x){int j=3*(i/2);if(!(i&1)){b[j]=x;b[j+1]=(b[j+1]&240)|(x>>8);}else{b[j+1]=(b[j+1]&15)|(x<<4);b[j+2]=x>>4;}}
static int zero(const uint8_t*p,size_t n){while(n--)if(*p++)return 0;return 1;}
int main(void){void*h[2]={dlopen("./official.so",RTLD_NOW|RTLD_LOCAL),dlopen("./gt.so",RTLD_NOW|RTLD_LOCAL)};if(!h[0]||!h[1]){puts(dlerror());return 2;}
 keyfn key=(keyfn)dlsym(h[0],"crypto_kem_keypair");encfn enc[2];decfn dec[2];for(int k=0;k<2;k++){enc[k]=(encfn)dlsym(h[k],"crypto_kem_enc");dec[k]=(decfn)dlsym(h[k],"crypto_kem_dec");}
 uint8_t pk[1296],sk[2624],ct[1296],ss[32],bad[2624],out[2][32],co[2][1296];int cases=0;
 if(key(pk,sk)||enc[0](ct,ss,pk))return 3;
 for(int mode=0;mode<4;mode++)for(int i=0;i<864;i++)for(int v=0;v<3;v++){
  const uint8_t*src=mode==0?pk:mode==1?ct:sk;int n=mode<2?1296:2624;memcpy(bad,src,n);
  put(bad+(mode==3?1296:0),i,(unsigned[]){3456,3457,4095}[v]);
  int status[2];uint64_t after[2];uint8_t before[2624];memcpy(before,bad,n);
  for(int k=0;k<2;k++){memset(out[k],0xa5,32);memset(co[k],0xa5,1296);state=123456;
   status[k]=mode==0?enc[k](co[k],out[k],bad):dec[k](out[k],mode==1?bad:ct,mode>=2?bad:sk);after[k]=state;}
  if(memcmp(before,bad,n)){puts("FAIL input mutated");return 6;}
  if(status[0]!=status[1]||memcmp(out[0],out[1],32)||(mode==0&&memcmp(co[0],co[1],1296))||after[0]!=after[1]){printf("FAIL mode=%d pos=%d value=%d official=%d gt=%d\n",mode,i,v,status[0],status[1]);return 4;}
  if(v>0&&(status[1]!=1||!zero(out[1],32)||(mode==0&&!zero(co[1],1296)))){int j=3*(i/2)+(mode==3?1296:0);int16_t decoded[864] __attribute__((aligned(16)));int(*check)(void*,const uint8_t*)=(int(*)(void*,const uint8_t*))dlsym(h[1],"gt864_fr0_frombytes_checked");printf("FAIL rejection mode=%d pos=%d value=%u official=%d gt=%d ss_zero=%d ct_zero=%d bytes=%02x,%02x,%02x direct=%d\n",mode,i,(unsigned[]){3456,3457,4095}[v],status[0],status[1],zero(out[1],32),zero(co[1],1296),bad[j],bad[j+1],bad[j+2],check(decoded,bad+(mode==3?1296:0)));return 5;}
  cases++;
 }
 printf("PASS rejection differential: %d pk/ct/sk-f/sk-hinv boundary cases, status/output clearing/RNG consumption\n",cases);return 0;
}
