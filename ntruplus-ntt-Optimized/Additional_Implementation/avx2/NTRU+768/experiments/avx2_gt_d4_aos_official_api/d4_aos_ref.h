#ifndef D4_AOS_REF_H
#define D4_AOS_REF_H

#include <stdint.h>
#include "poly.h"

#define D4AOS_Q 3457
#define D4AOS_N 768

typedef struct { int16_t coeff[768]; } d4aos_coeff_poly __attribute__((aligned(32)));
typedef struct { int16_t coeff[768]; } official_ntt_poly __attribute__((aligned(32)));
typedef struct { int16_t lane[768]; } d4aos_ntt_poly __attribute__((aligned(32)));
typedef struct { uint8_t byte[1152]; } official_wire12 __attribute__((aligned(32)));

_Static_assert(sizeof(d4aos_coeff_poly) == sizeof(poly), "coefficient size");
_Static_assert(sizeof(official_ntt_poly) == sizeof(poly), "official NTT size");
_Static_assert(sizeof(d4aos_ntt_poly) == sizeof(poly), "d4AoS NTT size");
_Static_assert(sizeof(((d4aos_coeff_poly *)0)->coeff) == D4AOS_N*sizeof(int16_t), "coefficient words");
_Static_assert(sizeof(((official_ntt_poly *)0)->coeff) == D4AOS_N*sizeof(int16_t), "official words");
_Static_assert(sizeof(((d4aos_ntt_poly *)0)->lane) == D4AOS_N*sizeof(int16_t), "d4AoS words");
_Static_assert(sizeof(d4aos_coeff_poly) == sizeof(((d4aos_coeff_poly *)0)->coeff), "coefficient padding");
_Static_assert(sizeof(official_ntt_poly) == sizeof(((official_ntt_poly *)0)->coeff), "official padding");
_Static_assert(sizeof(d4aos_ntt_poly) == sizeof(((d4aos_ntt_poly *)0)->lane), "d4AoS padding");
_Static_assert(_Alignof(d4aos_coeff_poly) >= 32, "coefficient alignment");
_Static_assert(_Alignof(official_ntt_poly) >= 32, "official NTT alignment");
_Static_assert(_Alignof(d4aos_ntt_poly) >= 32, "d4AoS NTT alignment");
_Static_assert(sizeof(official_wire12) == 1152, "wire size");
_Static_assert(_Alignof(official_wire12) >= 32, "wire alignment");
_Static_assert(sizeof(official_wire12) == sizeof(((official_wire12 *)0)->byte), "wire padding");

void d4aos_ref_forward(d4aos_ntt_poly *out, const d4aos_coeff_poly *in);
void d4aos_ref_inverse(d4aos_coeff_poly *out, const d4aos_ntt_poly *in);
void d4aos_ref_basemul(d4aos_ntt_poly *out, const d4aos_ntt_poly *a,
                        const d4aos_ntt_poly *b);
void d4aos_ref_quartic_oracle(int16_t out[4], const int16_t a[4],
                               const int16_t b[4], int16_t zeta);
void d4aos_ref_quartic_formula(int16_t out[4], const int16_t a[4],
                                const int16_t b[4], int16_t zeta);
void ntruplus_poly_mul_coeff_d4aos_ref(poly *r, const poly *a, const poly *b);

#endif
