#include "poly.h"
void poly_invntt_scale(poly*);
void off_invntt(void*p){ poly_invntt_scale((poly*)p); }
