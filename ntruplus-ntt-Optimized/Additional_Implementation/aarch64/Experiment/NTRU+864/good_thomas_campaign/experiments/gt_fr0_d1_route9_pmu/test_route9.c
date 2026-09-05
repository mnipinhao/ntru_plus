#include "route9.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef void (*route_fn)(int16_t *,const int16_t *);
static uint32_t state=1;
static uint32_t rnd(void){state=state*1664525u+1013904223u;return state;}
static int check(route_fn oracle,route_fn candidate,const int16_t *in)
{int16_t a[P3B1_N],b[P3B1_N];oracle(a,in);candidate(b,in);return memcmp(a,b,sizeof a)!=0;}
int main(void)
{
    int16_t fr0[P3B1_N],official[P3B1_N],round[P3B1_N]; int fail=0;
    route_fn fwd[]={p3b1_factor_f2o,p3b1_r9a_f2o,p3b1_r9b_f2o};
    route_fn rev[]={p3b1_factor_o2f,p3b1_r9a_o2f,p3b1_r9b_o2f};
    for(int i=0;i<P3B1_N;i++)fr0[i]=(int16_t)i;
    for(unsigned k=0;k<3;k++)fail+=check(p3b1_current_f2o,fwd[k],fr0);
    p3b1_current_f2o(official,fr0);
    for(unsigned k=0;k<3;k++)fail+=check(p3b1_current_o2f,rev[k],official);
    for(int t=0;t<128;t++){
        for(int i=0;i<P3B1_N;i++)fr0[i]=(int16_t)rnd();
        for(unsigned k=0;k<3;k++)fail+=check(p3b1_current_f2o,fwd[k],fr0);
        p3b1_current_f2o(official,fr0);
        for(unsigned k=0;k<3;k++)fail+=check(p3b1_current_o2f,rev[k],official);
        p3b1_r9a_f2o(official,fr0);p3b1_r9a_o2f(round,official);fail+=memcmp(fr0,round,sizeof fr0)!=0;
        p3b1_r9b_f2o(official,fr0);p3b1_r9b_o2f(round,official);fail+=memcmp(fr0,round,sizeof fr0)!=0;
    }
    printf("p3b1_route9=%s mismatches=%d tagged=864 random=128 directions=2\n",fail?"fail":"pass",fail);
    return fail!=0;
}
