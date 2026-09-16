/* Portable semantic reference, NOT constant-time production code.
 * Explicitly model int16 wrap and signed rounding; no signed-shift assumptions.
 */
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
static int32_t floor_div(int32_t x,int32_t d){
    return x>=0 ? x/d : -((-x+d-1)/d);
}
static int32_t s16(int32_t x){
    uint32_t lo=(uint32_t)x & 65535u;
    return lo<32768u ? (int32_t)lo : (int32_t)lo-65536;
}
static int32_t fixed(int32_t a,int32_t b,int32_t bhat){
    int32_t t=floor_div(a*bhat+16384,32768);
    if(t>32767)t=32767;
    if(t< -32768)t=-32768;
    return s16(s16(a*b)-t*3457);
}
static int32_t redc(int32_t x){
    int32_t correction=s16((int32_t)(((uint32_t)x*(uint32_t)-12929)&65535u));
    return (x+correction*3457)/65536;
}
int main(void){
    int min=4000,max=-4000;
    for(int x=-32768;x<=32767;x++){
        int y=fixed(x,-147,-1393),old=redc(x*867);
        assert((y-old)%3457==0);
        if(y<min)min=y;if(y>max)max=y;
    }
    assert(min==-3013 && max==3013);
    min=4000;max=-4000;
    for(int x=-2000;x<=2000;x++){
        int y=fixed(x,-682,-6464),old=redc(x);
        assert((y-old)%3457==0);
        if(y<min)min=y;if(y>max)max=y;
    }
    assert(min==-1824 && max==1824);
    puts("PASS 69537 exhaustive fixed-scale conversions; exact int16 semantics");
}
