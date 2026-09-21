#ifndef NTRUPLUS768_INTERNAL_LAYOUT_H
#define NTRUPLUS768_INTERNAL_LAYOUT_H

#include <stdint.h>

#include "poly.h"

/* Keygen-only CQ layout with the same storage ABI and alignment as poly. */
typedef struct {
    poly storage;
} gt_cq_poly;

typedef char gt_cq_poly_size_must_match_poly[
    sizeof(gt_cq_poly) == sizeof(poly) ? 1 : -1];
#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 201112L
_Static_assert(_Alignof(gt_cq_poly) == _Alignof(poly),
               "CQ storage alignment must match poly");
#endif

#endif
