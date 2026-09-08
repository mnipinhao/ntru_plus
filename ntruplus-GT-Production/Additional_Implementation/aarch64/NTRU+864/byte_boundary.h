#pragma once
#include <stdint.h>
void current_to(uint8_t *,const int16_t *);
void r9_to(uint8_t *,const int16_t *);
void c1_to(uint8_t *,const int16_t *);
void c2_to(uint8_t *,const int16_t *);
void current_from(int16_t *,const uint8_t *);
void r9_from(int16_t *,const uint8_t *);
void c1_from(int16_t *,const uint8_t *);
void c2_from(int16_t *,const uint8_t *);
void norm_only(int16_t *,const int16_t *);
void pack_only(uint8_t *,const int16_t *);
