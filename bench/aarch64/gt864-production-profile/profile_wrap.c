#include "poly.h"
#include "symmetric.h"
#include <stddef.h>
#include <stdint.h>
extern uint64_t prof_start(void);
extern void prof_end(int,uint64_t);
void p3b12_candidate_tobytes(uint8_t r[NTRUPLUS_POLYBYTES], const poly *a);
void prof_poly_tobytes(uint8_t r[NTRUPLUS_POLYBYTES], const poly *a);
void prof_poly_tobytes(uint8_t r[NTRUPLUS_POLYBYTES], const poly *a){ uint64_t t=prof_start(); p3b12_candidate_tobytes(r,a); prof_end(0,t); }
void p3b12_candidate_frombytes(poly *r, const uint8_t a[NTRUPLUS_POLYBYTES]);
void prof_poly_frombytes(poly *r, const uint8_t a[NTRUPLUS_POLYBYTES]);
void prof_poly_frombytes(poly *r, const uint8_t a[NTRUPLUS_POLYBYTES]){ uint64_t t=prof_start(); p3b12_candidate_frombytes(r,a); prof_end(1,t); }
void poly_cbd1(poly *r, const uint8_t buf[NTRUPLUS_N/4]);
void prof_poly_cbd1(poly *r, const uint8_t buf[NTRUPLUS_N/4]);
void prof_poly_cbd1(poly *r, const uint8_t buf[NTRUPLUS_N/4]){ uint64_t t=prof_start(); poly_cbd1(r,buf); prof_end(2,t); }
void poly_sotp_encode(poly *r, const uint8_t msg[NTRUPLUS_N/8], const uint8_t buf[NTRUPLUS_N/4]);
void prof_poly_sotp_encode(poly *r, const uint8_t msg[NTRUPLUS_N/8], const uint8_t buf[NTRUPLUS_N/4]);
void prof_poly_sotp_encode(poly *r, const uint8_t msg[NTRUPLUS_N/8], const uint8_t buf[NTRUPLUS_N/4]){ uint64_t t=prof_start(); poly_sotp_encode(r,msg,buf); prof_end(3,t); }
int poly_sotp_decode(uint8_t msg[NTRUPLUS_N/8], const poly *a, const uint8_t buf[NTRUPLUS_N/4]);
int prof_poly_sotp_decode(uint8_t msg[NTRUPLUS_N/8], const poly *a, const uint8_t buf[NTRUPLUS_N/4]);
int prof_poly_sotp_decode(uint8_t msg[NTRUPLUS_N/8], const poly *a, const uint8_t buf[NTRUPLUS_N/4]){ uint64_t t=prof_start(); int prof_result=poly_sotp_decode(msg,a,buf); prof_end(4,t); return prof_result;}
void gt_d1_poly_ntt(poly *r, const poly *a);
void prof_poly_ntt(poly *r, const poly *a);
void prof_poly_ntt(poly *r, const poly *a){ uint64_t t=prof_start(); gt_d1_poly_ntt(r,a); prof_end(5,t); }
void gt_d1_poly_invntt(poly *r, const poly *a);
void prof_poly_invntt(poly *r, const poly *a);
void prof_poly_invntt(poly *r, const poly *a){ uint64_t t=prof_start(); gt_d1_poly_invntt(r,a); prof_end(6,t); }
int gt_d1_poly_baseinv(poly *r, const poly *a);
int prof_poly_baseinv(poly *r, const poly *a);
int prof_poly_baseinv(poly *r, const poly *a){ uint64_t t=prof_start(); int prof_result=gt_d1_poly_baseinv(r,a); prof_end(7,t); return prof_result;}
void gt_d1_poly_basemul(poly *r, const poly *a, const poly *b);
void prof_poly_basemul(poly *r, const poly *a, const poly *b);
void prof_poly_basemul(poly *r, const poly *a, const poly *b){ uint64_t t=prof_start(); gt_d1_poly_basemul(r,a,b); prof_end(8,t); }
void gt_d1_poly_basemul_add(poly *r, const poly *a, const poly *b, const poly *c);
void prof_poly_basemul_add(poly *r, const poly *a, const poly *b, const poly *c);
void prof_poly_basemul_add(poly *r, const poly *a, const poly *b, const poly *c){ uint64_t t=prof_start(); gt_d1_poly_basemul_add(r,a,b,c); prof_end(9,t); }
void poly_sub(poly *r, const poly *a, const poly *b);
void prof_poly_sub(poly *r, const poly *a, const poly *b);
void prof_poly_sub(poly *r, const poly *a, const poly *b){ uint64_t t=prof_start(); poly_sub(r,a,b); prof_end(10,t); }
void poly_triple(poly *r, const poly *a);
void prof_poly_triple(poly *r, const poly *a);
void prof_poly_triple(poly *r, const poly *a){ uint64_t t=prof_start(); poly_triple(r,a); prof_end(11,t); }
void poly_crepmod3(poly *r, const poly *a);
void prof_poly_crepmod3(poly *r, const poly *a);
void prof_poly_crepmod3(poly *r, const poly *a){ uint64_t t=prof_start(); poly_crepmod3(r,a); prof_end(12,t); }
void hash_f(uint8_t *buf, const uint8_t *msg);
void prof_hash_f(uint8_t *buf, const uint8_t *msg);
void prof_hash_f(uint8_t *buf, const uint8_t *msg){ uint64_t t=prof_start(); hash_f(buf,msg); prof_end(13,t); }
void hash_g(uint8_t *buf, const uint8_t *msg);
void prof_hash_g(uint8_t *buf, const uint8_t *msg);
void prof_hash_g(uint8_t *buf, const uint8_t *msg){ uint64_t t=prof_start(); hash_g(buf,msg); prof_end(14,t); }
void hash_h(uint8_t *buf, const uint8_t *msg);
void prof_hash_h(uint8_t *buf, const uint8_t *msg);
void prof_hash_h(uint8_t *buf, const uint8_t *msg){ uint64_t t=prof_start(); hash_h(buf,msg); prof_end(15,t); }
void shake256(uint8_t *out, size_t outlen, const uint8_t *in, size_t inlen);
void prof_shake256(uint8_t *out, size_t outlen, const uint8_t *in, size_t inlen);
void prof_shake256(uint8_t *out, size_t outlen, const uint8_t *in, size_t inlen){ uint64_t t=prof_start(); shake256(out,outlen,in,inlen); prof_end(16,t); }
void randombytes(uint8_t *out, size_t n);
void prof_randombytes(uint8_t *out, size_t n);
void prof_randombytes(uint8_t *out, size_t n){ uint64_t t=prof_start(); randombytes(out,n); prof_end(17,t); }
