#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>
static uint64_t state=864;
void randombytes(uint8_t*p,size_t n){while(n--){state^=state<<13;state^=state>>7;state^=state<<17;*p++=state;}}
typedef int(*keyfn)(uint8_t*,uint8_t*);
typedef int(*encfn)(uint8_t*,uint8_t*,const uint8_t*);
typedef int(*decfn)(uint8_t*,const uint8_t*,const uint8_t*);
int main(int argc,char**argv){
 void*o=dlopen("./official.so",RTLD_NOW|RTLD_LOCAL),*g=dlopen(argc>1?argv[1]:"./gt.so",RTLD_NOW|RTLD_LOCAL);if(!o||!g){puts(dlerror());return 2;}
 keyfn key=(keyfn)dlsym(o,"crypto_kem_keypair");encfn enc=(encfn)dlsym(o,"crypto_kem_enc");
 decfn dec[2]={(decfn)dlsym(o,"crypto_kem_dec"),(decfn)dlsym(g,"crypto_kem_dec")};
 uint8_t pk[1296],sk[2624],ct[1296],bad[1296],ss[32],out[2][32];int tested=0,different=0;
 if(key(pk,sk)||enc(ct,ss,pk))return 3;
 for(int j=0;j<1296;j+=3){
  int x=ct[j]|((ct[j+1]&15)<<8);if(x>638)continue;
  memcpy(bad,ct,1296);x+=3457;bad[j]=x;bad[j+1]=(bad[j+1]&240)|(x>>8);
  int a=dec[0](out[0],bad,sk),b=dec[1](out[1],bad,sk);tested++;
  if(a!=b||memcmp(out[0],out[1],32)){different++;if(different<=3)printf("difference offset=%d official=%d gt=%d gt_matches_valid_ss=%d\n",j,a,b,!memcmp(out[1],ss,32));}
 }
 printf("noncanonical_tested=%d differences=%d\n",tested,different);
 return tested?0:4;
}
