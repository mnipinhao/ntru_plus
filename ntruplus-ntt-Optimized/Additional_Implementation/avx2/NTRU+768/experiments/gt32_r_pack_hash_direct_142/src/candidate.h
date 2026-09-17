#ifndef GT142_CANDIDATE_H
#define GT142_CANDIDATE_H
#include <stdint.h>
#include "params.h"
__attribute__((noinline))
void gt142_hash_g_from_m(uint8_t out[NTRUPLUS_N / 4],
                         const int16_t r_m[NTRUPLUS_N]);
int gt142_enc_derand(uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
                    uint8_t ss[NTRUPLUS_SSBYTES],
                    const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
                    const uint8_t coins[NTRUPLUS_N / 8]);
#endif
