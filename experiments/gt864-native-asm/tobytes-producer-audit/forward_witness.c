/* Execute current production K1 directly; observed extrema are NOT bounds. */
#include <stdint.h>
#include <stdio.h>
void gt864_forward_poly_ntt_p41_k1_kem_only(int16_t*,const int16_t*);
static uint32_t state=864;
static uint32_t rnd(void){state^=state<<13;state^=state>>17;state^=state<<5;return state;}
int main(void){
 int16_t in[864],out[864];
 for(int kind=0;kind<2;kind++){
  int min=32767,max=-32768,found=0;
  for(int trial=0;trial<128;trial++){
   uint32_t seed=state;
   for(int i=0;i<864;i++)in[i]=((int)(rnd()%3)-1)*(kind?3:1);
   if(kind)in[0]++;
   gt864_forward_poly_ntt_p41_k1_kem_only(out,in);
   for(int i=0;i<864;i++){
    if(out[i]<min)min=out[i];if(out[i]>max)max=out[i];
    if(!found&&(out[i]<=-3457||out[i]>=3457)){
     int no=out[i]+(out[i]<0?3457:0),canonical=out[i]%3457;if(canonical<0)canonical+=3457;
     printf("{\"domain\":\"%s\",\"trial\":%d,\"xorshift_seed\":%u,\"index\":%d,\"value\":%d,\"sign_add_only\":%d,\"canonical\":%d}\n",kind?"f=3*CBD+1":"CBD_small",trial,seed,i,out[i],no,canonical);found=1;
    }
   }
  }
  printf("{\"domain\":\"%s\",\"observed_min\":%d,\"observed_max\":%d,\"trials\":128,\"not_a_proof_bound\":true}\n",kind?"f=3*CBD+1":"CBD_small",min,max);
  if(!found)return 1;
 }
}
