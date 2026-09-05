#include "byte_boundary.h"
#include "route9.h"
#include "tables.h"
#include <arm_neon.h>
#include <string.h>
extern void stock_to(uint8_t *,const int16_t *);
extern void stock_from(int16_t *,const uint8_t *);
extern void stock_shuffle(int16_t *,const int16_t *);
extern void stock_shuffle2(int16_t *,const int16_t *);
#include "gather.h"
static inline uint16x8_t norm(uint16x8_t u) {
 int16x8_t v=vreinterpretq_s16_u16(u),q=vdupq_n_s16(3457);
 v=vmlsq_s16(v,vqrdmulhq_s16(v,vdupq_n_s16(9)),q);
 return vreinterpretq_u16_s16(vaddq_s16(v,vandq_s16(vshrq_n_s16(v,15),q)));
}
void norm_only(int16_t *o,const int16_t *s) {for(int i=0;i<864;i+=8)vst1q_u16((uint16_t*)(o+i),norm(vld1q_u16((const uint16_t*)(s+i))));}
/* Eight contiguous 12-bit coefficients -> exactly twelve bytes. */
static inline void pack8(uint8_t *o,uint16x8_t v) {
 uint16x8_t e=vuzp1q_u16(v,v),a=vuzp2q_u16(v,v);
 uint16x8_t lo=vorrq_u16(e,vshlq_n_u16(a,12)),hi=vshrq_n_u16(a,4);
 uint8x16x2_t t={{vreinterpretq_u8_u16(lo),vreinterpretq_u8_u16(hi)}};
 const uint8_t ix[16]={0,1,16,2,3,18,4,5,20,6,7,22,255,255,255,255};
 uint8x16_t bytes=vqtbl2q_u8(t,vld1q_u8(ix));
 vst1_u8(o,vget_low_u8(bytes));
 uint32_t last=vgetq_lane_u32(vreinterpretq_u32_u8(bytes),2);
 memcpy(o+8,&last,4);
}
static inline uint16x8_t unpack8(const uint8_t *s) {
 uint32_t tail;memcpy(&tail,s+8,4);
 uint8x16_t b=vcombine_u8(vld1_u8(s),vdup_n_u8(0));
 b=vreinterpretq_u8_u32(vsetq_lane_u32(tail,vreinterpretq_u32_u8(b),2));
 const uint8_t ix[16]={0,1,1,2,3,4,4,5,6,7,7,8,9,10,10,11};
 uint16x8_t v=vreinterpretq_u16_u8(vqtbl1q_u8(b,vld1q_u8(ix)));
 const int16_t shifts[8]={0,-4,0,-4,0,-4,0,-4};
 return vandq_u16(vshlq_u16(v,vld1q_s16(shifts)),vdupq_n_u16(4095));
}
void pack_only(uint8_t *o,const int16_t *s) {for(int q=0;q<108;q++)pack8(o+12*q,vld1q_u16((const uint16_t*)s+8*q));}
void current_to(uint8_t *o,const int16_t *s) {
 int16_t official[864],post[864];
 for(int q=0;q<108;q++){uint16_t t[8];for(int l=0;l<8;l++)t[l]=s[map_o[8*q+l]];
 vst1q_u16((uint16_t*)official+8*q,norm(vld1q_u16(t)));}
 stock_shuffle2(post,official);stock_to(o,post);
}
void current_from(int16_t *o,const uint8_t *s) {
 int16_t official[864];stock_from(official,s);stock_shuffle(official,official);
 for(int i=0;i<864;i++)o[map_o[i]]=official[i];
}
void r9_to(uint8_t *o,const int16_t *s) {
 int16_t official[864],post[864];p3b1_r9a_f2o(official,s);
 norm_only(official,official);stock_shuffle2(post,official);stock_to(o,post);
}
void r9_from(int16_t *o,const uint8_t *s) {
 int16_t official[864];stock_from(official,s);stock_shuffle(official,official);
 p3b1_r9a_o2f(o,official);
}
void c1_to(uint8_t *o,const int16_t *s) {
 for(int q=0;q<108;q+=4){uint16x8_t v[4];gather4_f(v,s,map_f+8*q);
 for(int j=0;j<4;j++)pack8(o+12*(q+j),norm(v[j]));}
}
void c1_from(int16_t *o,const uint8_t *s) {
 for(int q=0;q<108;q+=4){uint16x8_t v[4];gather4_r(v,s,addr_r+8*q,shift_r+8*q);
 for(int j=0;j<4;j++)vst1q_u16((uint16_t*)o+8*(q+j),v[j]);}
}
static inline uint16x8_t table_route(const void *s,const uint16_t *map,const uint8_t *ix,int decode) {
 uint8x16x4_t a,b;
 a.val[0]=decode?vreinterpretq_u8_u16(unpack8((const uint8_t*)s+12*(map[0]/8))):vld1q_u8((const uint8_t*)s+16*(map[0]/8));
 b.val[0]=decode?vreinterpretq_u8_u16(unpack8((const uint8_t*)s+12*(map[4]/8))):vld1q_u8((const uint8_t*)s+16*(map[4]/8));
 a.val[1]=decode?vreinterpretq_u8_u16(unpack8((const uint8_t*)s+12*(map[1]/8))):vld1q_u8((const uint8_t*)s+16*(map[1]/8));
 b.val[1]=decode?vreinterpretq_u8_u16(unpack8((const uint8_t*)s+12*(map[5]/8))):vld1q_u8((const uint8_t*)s+16*(map[5]/8));
 a.val[2]=decode?vreinterpretq_u8_u16(unpack8((const uint8_t*)s+12*(map[2]/8))):vld1q_u8((const uint8_t*)s+16*(map[2]/8));
 b.val[2]=decode?vreinterpretq_u8_u16(unpack8((const uint8_t*)s+12*(map[6]/8))):vld1q_u8((const uint8_t*)s+16*(map[6]/8));
 a.val[3]=decode?vreinterpretq_u8_u16(unpack8((const uint8_t*)s+12*(map[3]/8))):vld1q_u8((const uint8_t*)s+16*(map[3]/8));
 b.val[3]=decode?vreinterpretq_u8_u16(unpack8((const uint8_t*)s+12*(map[7]/8))):vld1q_u8((const uint8_t*)s+16*(map[7]/8));
 return vreinterpretq_u16_u8(vorrq_u8(vqtbl4q_u8(a,vld1q_u8(ix)),vqtbl4q_u8(b,vld1q_u8(ix+16))));
}
void c2_to(uint8_t *o,const int16_t *s) {
 for(int step=0;step<108;step++){int q=order_f[step];pack8(o+12*q,norm(table_route(s,map_f+8*q,idx_f+32*q,0)));}
}
void c2_from(int16_t *o,const uint8_t *s) {
 for(int step=0;step<108;step++){int q=order_r[step];vst1q_u16((uint16_t*)o+8*q,table_route(s,map_r+8*q,idx_r+32*q,1));}
}
