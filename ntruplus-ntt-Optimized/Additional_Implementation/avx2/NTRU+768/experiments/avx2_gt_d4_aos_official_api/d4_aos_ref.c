#include "d4_aos_ref.h"
#include <stddef.h>

enum { ROWS = 96, Q = 3457, ALPHA0 = 2735, ALPHA1 = 723, BETA0 = 22,
       BETA1 = 2, OMEGA = 641, INV96 = 3421 };
static int16_t fwd[2][ROWS][ROWS], inv[2][ROWS][ROWS];
static int tables_ready;
static int modq(int64_t x) { x %= Q; return (int)(x < 0 ? x + Q : x); }
static int power(int a, int e) { int r = 1; while (e) { if (e & 1) r = modq((int64_t)r*a); a=modq((int64_t)a*a); e>>=1; } return r; }
static int out_k(int k3, int k32) { return (32*k3 + 3*k32) % ROWS; }
static size_t at(int b,int k3,int k32,int c) {
 return 16U*(16U*(size_t)k3+(size_t)k32/2U)+8U*(size_t)b+
        4U*(size_t)(k32&1)+(size_t)c;
}
static void clear(void *p, size_t n) { volatile uint8_t *v = p; while (n--) *v++=0; }
static void init(void) {
 if (tables_ready) return;
 const int beta[2]={BETA0,BETA1};
 for(int b=0;b<2;b++) for(int k=0;k<ROWS;k++) {
  int g=modq((int64_t)beta[b]*power(OMEGA,k));
  for(int i=0;i<ROWS;i++) {
   fwd[b][k][i]=(int16_t)power(g,i);
   inv[b][k][i]=(int16_t)power(g,Q-1-i);
  }
 }
 tables_ready=1;
}
static void from_poly(d4aos_coeff_poly *d,const poly *p){for(int i=0;i<D4AOS_N;i++)d->coeff[i]=(int16_t)modq(p->coeffs[i]);}
static void to_poly(poly *p,const d4aos_coeff_poly *d){for(int i=0;i<D4AOS_N;i++)p->coeffs[i]=d->coeff[i];}
void d4aos_ref_forward(d4aos_ntt_poly *o,const d4aos_coeff_poly *in) {
 const int alpha[2]={ALPHA0,ALPHA1}; init();
 for(int b=0;b<2;b++) for(int k3=0;k3<3;k3++) for(int k32=0;k32<32;k32++) for(int c=0;c<4;c++) { int64_t sum=0; int k=out_k(k3,k32); for(int i=0;i<ROWS;i++) sum+=(in->coeff[4*i+c]+(int64_t)alpha[b]*in->coeff[384+4*i+c])*fwd[b][k][i]; o->lane[at(b,k3,k32,c)]=(int16_t)modq(sum); }
}
void d4aos_ref_inverse(d4aos_coeff_poly *o,const d4aos_ntt_poly *in) {
 int16_t u[2][4][ROWS]; init();
 for(int b=0;b<2;b++) for(int c=0;c<4;c++) for(int i=0;i<ROWS;i++){int64_t sum=0;for(int k3=0;k3<3;k3++)for(int k32=0;k32<32;k32++)sum+=(int64_t)in->lane[at(b,k3,k32,c)]*inv[b][out_k(k3,k32)][i];u[b][c][i]=(int16_t)modq(sum*INV96);}
 const int delta_inv=power(modq(ALPHA0-ALPHA1),Q-2);
 for(int c=0;c<4;c++)for(int i=0;i<ROWS;i++){int hi=modq((int64_t)(u[0][c][i]-u[1][c][i])*delta_inv);o->coeff[4*i+c]=(int16_t)modq(u[0][c][i]-(int64_t)ALPHA0*hi);o->coeff[384+4*i+c]=(int16_t)hi;}
 clear(u,sizeof u);
}
void d4aos_ref_quartic_formula(int16_t o[4],const int16_t a[4],const int16_t b[4],int16_t z){
 int64_t d0=(int64_t)a[0]*b[0], d1=(int64_t)a[0]*b[1]+(int64_t)a[1]*b[0], d2=(int64_t)a[0]*b[2]+(int64_t)a[1]*b[1]+(int64_t)a[2]*b[0], d3=(int64_t)a[0]*b[3]+(int64_t)a[1]*b[2]+(int64_t)a[2]*b[1]+(int64_t)a[3]*b[0], d4=(int64_t)a[1]*b[3]+(int64_t)a[2]*b[2]+(int64_t)a[3]*b[1], d5=(int64_t)a[2]*b[3]+(int64_t)a[3]*b[2], d6=(int64_t)a[3]*b[3];
 o[0]=(int16_t)modq(d0+(int64_t)z*d4);
 o[1]=(int16_t)modq(d1+(int64_t)z*d5);
 o[2]=(int16_t)modq(d2+(int64_t)z*d6);
 o[3]=(int16_t)modq(d3);
}
void d4aos_ref_quartic_oracle(int16_t o[4],const int16_t a[4],const int16_t b[4],int16_t z){int64_t w[7]={0};for(int i=0;i<4;i++)for(int j=0;j<4;j++)w[i+j]+=(int64_t)a[i]*b[j];for(int i=6;i>=4;i--)w[i-4]+=(int64_t)z*w[i];for(int i=0;i<4;i++)o[i]=(int16_t)modq(w[i]);}
void d4aos_ref_basemul(d4aos_ntt_poly *o,const d4aos_ntt_poly *a,const d4aos_ntt_poly *b){const int beta[2]={BETA0,BETA1};for(int br=0;br<2;br++)for(int k3=0;k3<3;k3++)for(int k32=0;k32<32;k32++){int16_t x[4],y[4],z[4];int root=modq((int64_t)beta[br]*power(OMEGA,out_k(k3,k32)));for(int c=0;c<4;c++){x[c]=a->lane[at(br,k3,k32,c)];y[c]=b->lane[at(br,k3,k32,c)];}d4aos_ref_quartic_formula(z,x,y,(int16_t)root);for(int c=0;c<4;c++)o->lane[at(br,k3,k32,c)]=z[c];}}
void ntruplus_poly_mul_coeff_d4aos_ref(poly *r,const poly *a,const poly *b){d4aos_coeff_poly x,y,z;d4aos_ntt_poly tx,ty,tp;from_poly(&x,a);from_poly(&y,b);d4aos_ref_forward(&tx,&x);d4aos_ref_forward(&ty,&y);d4aos_ref_basemul(&tp,&tx,&ty);d4aos_ref_inverse(&z,&tp);to_poly(r,&z);clear(&x,sizeof x);clear(&y,sizeof y);clear(&tx,sizeof tx);clear(&ty,sizeof ty);clear(&tp,sizeof tp);clear(&z,sizeof z);}
