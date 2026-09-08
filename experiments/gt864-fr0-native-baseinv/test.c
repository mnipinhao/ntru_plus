#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <dlfcn.h>
#include "poly.h"
#include "gt864_fr0_basemul_tables.h"
int fr0_native_baseinv(poly *,const poly *);
typedef int (*invfn)(poly *,const poly *);
static uint32_t state=1;
static uint32_t rnd(void){state^=state<<13;state^=state>>17;state^=state<<5;return state;}
static int mod(int64_t x){int r=x%3457;return r<0?r+3457:r;}
int main(int argc,char **argv){
    if(argc!=2)return 2;
    void *h=dlopen(argv[1],RTLD_NOW);if(!h){puts(dlerror());return 2;}
    invfn old=(invfn)dlsym(h,"gt_d1_poly_baseinv");if(!old)return 2;
    poly a,b,c,alias;
    for(int t=0;t<512;++t){
        for(int j=0;j<864;++j)a.coeffs[j]=(int16_t)rnd();
        if(t<6)for(int j=0;j<864;++j)a.coeffs[j]=(int16_t[]){0,1,-1,32767,-32768,3457}[t];
        if(t>=6&&t<294){int leaf=t-6,j=leaf/8,l=leaf%8;
            a.coeffs[24*j+l]=a.coeffs[24*j+8+l]=a.coeffs[24*j+16+l]=0;}
        int r0=old(&b,&a),r1=fr0_native_baseinv(&c,&a);
        if(r0!=r1){printf("status mismatch %d %d %d\n",t,r0,r1);return 1;}
        for(int j=0;j<864;++j)if(mod(b.coeffs[j]-c.coeffs[j])||c.coeffs[j]<-1728||c.coeffs[j]>1728){printf("value mismatch %d %d\n",t,j);return 1;}
        alias=a;if(fr0_native_baseinv(&alias,&alias)!=r1||memcmp(&alias,&c,sizeof c))return 1;
        if(!r1)for(int j=0;j<36;++j)for(int l=0;l<8;++l){
            /* R^-1 mod q = 2775; checked by proof.py. */
            int z=mod((int64_t)gt864_fr0_zetas_mul[j][l]*2775);
            int64_t x=a.coeffs[24*j+l],y=a.coeffs[24*j+8+l],w=a.coeffs[24*j+16+l];
            int64_t u=c.coeffs[24*j+l],v=c.coeffs[24*j+8+l],s=c.coeffs[24*j+16+l];
            if(mod(x*u+z*(y*s+w*v))!=1||mod(x*v+y*u+z*w*s)||mod(x*s+y*v+w*u)){printf("leaf product mismatch %d %d %d\n",t,j,l);return 1;}
        }
    }
    puts("PASS 512 boundary/random cases; all 288 zero-leaf locations; alias; cubic identity");
}
/* Shared library imports this even though this test only exercises BaseInv. */
void randombytes(unsigned char *out,size_t n){while(n--)*out++=(unsigned char)rnd();}
