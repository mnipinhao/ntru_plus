#define main kem_main
#include "harness.c"
#undef main
typedef void (*transform_fn)(int16_t*,const int16_t*);
typedef void (*multiply_fn)(int16_t*,const int16_t*,const int16_t*);
int main(void) {
    void *lib=dlopen("./raw.so",RTLD_NOW|RTLD_LOCAL);if(!lib){puts(dlerror());return 2;}
    transform_fn f=(transform_fn)dlsym(lib,"gt_d1_poly_ntt"),inv=(transform_fn)dlsym(lib,"gt_d1_poly_invntt");
    multiply_fn bm=(multiply_fn)dlsym(lib,"gt_d1_poly_basemul");if(!f||!inv||!bm)return 2;
    int16_t a[864],b[864],fa[864],fb[864],p[864],out[864];int64_t oracle[1727];
    for(int t=0;t<32;t++) {
        memset(oracle,0,sizeof oracle);
        for(int i=0;i<864;i++){uint8_t x[2];randombytes(x,2);a[i]=t==0?-3:t==1?4:(x[0]&7)-3;b[i]=t<2?a[i]:(x[1]&7)-3;}
        if(t==2){memset(a,0,sizeof a);a[863]=4;}
        for(int i=0;i<864;i++)for(int j=0;j<864;j++)oracle[i+j]+=(int)a[i]*b[j];
        for(int i=1726;i>=864;i--){oracle[i-432]+=oracle[i];oracle[i-864]-=oracle[i];}
        f(fa,a);f(fb,b);bm(p,fa,fb);inv(out,p);
        for(int i=0;i<864;i++)if((out[i]-oracle[i])%3457){fprintf(stderr,"product mismatch %d %d\n",t,i);return 4;}
    }
    puts("polynomial_product=pass cases=32 raw_2F_D1_I_vs_schoolbook=pass");return 0;
}
