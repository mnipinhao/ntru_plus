#include "d4_aos_ref.h"
#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <stddef.h>

static unsigned state=1; static int rnd(void){state=1664525U*state+1013904223U;return (int)(state>>16);}
static int modq(long long x){x%=3457;return (int)(x<0?x+3457:x);}
static int eq(const int16_t *a,const int16_t *b){return memcmp(a,b,1536)==0;}
static void school(poly *o,const poly *a,const poly *b){long long w[1535]={0};for(int i=0;i<768;i++)for(int j=0;j<768;j++)w[i+j]+=(long long)modq(a->coeffs[i])*modq(b->coeffs[j]);for(int i=1534;i>=768;i--){w[i-384]+=w[i];w[i-768]-=w[i];}for(int i=0;i<768;i++)o->coeffs[i]=(int16_t)modq(w[i]);}
static int d4canonical(const d4aos_ntt_poly *p){for(int i=0;i<768;i++)if(p->lane[i]<0||p->lane[i]>=3457)return 0;return 1;}
static int rt(const poly *p){d4aos_coeff_poly c,d;d4aos_ntt_poly t;for(int i=0;i<768;i++)c.coeff[i]=(int16_t)modq(p->coeffs[i]);d4aos_ref_forward(&t,&c);d4aos_ref_inverse(&d,&t);return d4canonical(&t)&&eq(c.coeff,d.coeff);}
static void fill(poly *p,int mode){for(int i=0;i<768;i++)p->coeffs[i]=(int16_t)(mode?((rnd()%7)-3):0);}
static int power(int a,int e){int r=1;while(e){if(e&1)r=modq((long long)r*a);a=modq((long long)a*a);e>>=1;}return r;}
static int root(int br,int k3,int k32){int beta=br?2:22;return modq((long long)beta*power(641,(32*k3+3*k32)%96));}
static int canonical(const poly *p){for(int i=0;i<768;i++)if(p->coeffs[i]<0||p->coeffs[i]>=3457)return 0;return 1;}
struct guarded_poly { uint64_t lo; poly value; uint64_t hi; };
_Static_assert(offsetof(struct guarded_poly,value)%32==0,"poly canary alignment");
static int canary(const struct guarded_poly *p){return p->lo==UINT64_C(0x9e3779b97f4a7c15)&&p->hi==UINT64_C(0xd1b54a32d192ed03);}
int main(void){poly a,b,got,want,zero; d4aos_coeff_poly c; d4aos_ntt_poly t,u; int16_t q[4],x[4],y[4],f[4];
 for(int i=0;i<768;i++){memset(&a,0,sizeof a);a.coeffs[i]=1;if(!rt(&a)){printf("basis-fi %d\n",i);return 1;}}
 for(int i=0;i<768;i++){memset(&t,0,sizeof t);t.lane[i]=1;d4aos_ref_inverse(&c,&t);d4aos_ref_forward(&u,&c);if(!eq(t.lane,u.lane)){printf("lane-fi %d\n",i);return 1;}}
 {int rv[]={0,1,3455,3456};for(int v=0;v<4;v++){for(int i=0;i<768;i++)t.lane[i]=(int16_t)rv[v];d4aos_ref_inverse(&c,&t);d4aos_ref_forward(&u,&c);if(!d4canonical(&u)||!eq(t.lane,u.lane)){printf("lane-range %d\n",rv[v]);return 1;}}}
 for(int br=0;br<2;br++)for(int k3=0;k3<3;k3++)for(int k=0;k<32;k++)for(int i=0;i<4;i++)for(int j=0;j<4;j++){memset(x,0,sizeof x);memset(y,0,sizeof y);x[i]=y[j]=1;d4aos_ref_quartic_oracle(q,x,y,(int16_t)root(br,k3,k));d4aos_ref_quartic_formula(f,x,y,(int16_t)root(br,k3,k));if(memcmp(q,f,sizeof q)){printf("quartic-fi br=%d k3=%d k32=%d i=%d j=%d\n",br,k3,k,i,j);return 1;}}
 for(int n=0;n<10000;n++){fill(&a,1);if(!rt(&a)){printf("random-fi %d\n",n);return 1;}}
 for(int n=0;n<1000;n++){fill(&a,1);fill(&b,1);school(&want,&a,&b);ntruplus_poly_mul_coeff_d4aos_ref(&got,&a,&b);if(!eq(got.coeffs,want.coeffs)||!canonical(&got)){printf("product-fi %d\n",n);return 1;}}
 memset(&zero,0,sizeof zero);fill(&a,1);ntruplus_poly_mul_coeff_d4aos_ref(&got,&zero,&a);if(!eq(got.coeffs,zero.coeffs))return 1;
 for(int i=0;i<768;i++){memset(&a,0,sizeof a);memset(&b,0,sizeof b);a.coeffs[i]=1;b.coeffs[(37*i)%768]=1;school(&want,&a,&b);ntruplus_poly_mul_coeff_d4aos_ref(&got,&a,&b);if(!eq(got.coeffs,want.coeffs)){printf("monomial %d\n",i);return 1;}}
 {int z[]={0,1,-1,2,-2,3,-3,3456,-3456,INT16_MAX,INT16_MIN};for(int v=0;v<11;v++){for(int i=0;i<768;i++)a.coeffs[i]=(int16_t)z[v];if(!rt(&a)){printf("range-fi %d\n",v);return 1;}}}
 fill(&a,1);fill(&b,1);school(&want,&a,&b);ntruplus_poly_mul_coeff_d4aos_ref(&a,&a,&b);if(!eq(a.coeffs,want.coeffs))return 1;
 fill(&a,1);fill(&b,1);school(&want,&a,&b);ntruplus_poly_mul_coeff_d4aos_ref(&b,&a,&b);if(!eq(b.coeffs,want.coeffs))return 1;
 fill(&a,1);school(&want,&a,&a);ntruplus_poly_mul_coeff_d4aos_ref(&got,&a,&a);if(!eq(got.coeffs,want.coeffs))return 1;
 fill(&a,1);school(&want,&a,&a);ntruplus_poly_mul_coeff_d4aos_ref(&a,&a,&a);if(!eq(a.coeffs,want.coeffs))return 1;
 {struct guarded_poly ga,gb,gr;ga.lo=gb.lo=gr.lo=UINT64_C(0x9e3779b97f4a7c15);ga.hi=gb.hi=gr.hi=UINT64_C(0xd1b54a32d192ed03);memset(&ga.value,0,sizeof ga.value);memset(&gb.value,0,sizeof gb.value);memset(&gr.value,0,sizeof gr.value);fill(&ga.value,1);fill(&gb.value,1);school(&want,&ga.value,&gb.value);ntruplus_poly_mul_coeff_d4aos_ref(&gr.value,&ga.value,&gb.value);if(!canary(&ga)||!canary(&gb)||!canary(&gr)||!eq(gr.value.coeffs,want.coeffs))return 1;}
 puts("d4aos-ref=passed fi=10000 products=1000 monomials=768 aliases=4 canaries=1");return 0;}
