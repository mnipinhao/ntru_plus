#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "api.h"
#include "params.h"

static void set_coefficient(uint8_t bytes[NTRUPLUS_POLYBYTES],
                            size_t position, uint16_t value)
{
    const size_t offset = 3 * (position / 2);

    if ((position & 1u) == 0) {
        bytes[offset] = (uint8_t)value;
        bytes[offset + 1] =
            (uint8_t)((bytes[offset + 1] & 0xf0u) | (value >> 8));
    } else {
        bytes[offset + 1] =
            (uint8_t)((bytes[offset + 1] & 0x0fu) |
                      ((value & 0x0fu) << 4));
        bytes[offset + 2] = (uint8_t)(value >> 4);
    }
}

static int all_zero(const uint8_t *bytes, size_t length)
{
    uint8_t accumulator = 0;

    for (size_t i = 0; i < length; i++)
        accumulator |= bytes[i];
    return accumulator == 0;
}

int main(void)
{
    static const uint16_t invalid_values[] = {
        NTRUPLUS_Q, NTRUPLUS_Q + 1, 4095
    };
    uint8_t pk[CRYPTO_PUBLICKEYBYTES];
    uint8_t sk[CRYPTO_SECRETKEYBYTES];
    uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
    uint8_t ss_enc[CRYPTO_BYTES];
    uint8_t ss_dec[CRYPTO_BYTES];
    uint8_t candidate_pk[CRYPTO_PUBLICKEYBYTES];
    uint8_t candidate_sk[CRYPTO_SECRETKEYBYTES];
    uint8_t candidate_ct[CRYPTO_CIPHERTEXTBYTES];
    size_t cases = 0;
    size_t failures = 0;

    if (crypto_kem_keypair(pk, sk) != 0 ||
        crypto_kem_enc(ct, ss_enc, pk) != 0 ||
        crypto_kem_dec(ss_dec, ct, sk) != 0 ||
        memcmp(ss_enc, ss_dec, sizeof ss_enc) != 0) {
        puts("canonical-boundary: valid round trip failed");
        return 1;
    }

    for (size_t value_index = 0;
         value_index < sizeof invalid_values / sizeof invalid_values[0];
         value_index++) {
        for (size_t position = 0; position < NTRUPLUS_N; position++) {
            memcpy(candidate_pk, pk, sizeof candidate_pk);
            set_coefficient(candidate_pk, position,
                            invalid_values[value_index]);
            memset(candidate_ct, 0xa5, sizeof candidate_ct);
            memset(ss_dec, 0xa5, sizeof ss_dec);
            failures += (size_t)(
                crypto_kem_enc(candidate_ct, ss_dec, candidate_pk) != 1);
            failures += (size_t)!all_zero(
                candidate_ct, sizeof candidate_ct);
            failures += (size_t)!all_zero(ss_dec, sizeof ss_dec);
            cases++;

            memcpy(candidate_ct, ct, sizeof candidate_ct);
            set_coefficient(candidate_ct, position,
                            invalid_values[value_index]);
            memset(ss_dec, 0xa5, sizeof ss_dec);
            failures += (size_t)(
                crypto_kem_dec(ss_dec, candidate_ct, sk) != 1);
            failures += (size_t)!all_zero(ss_dec, sizeof ss_dec);
            cases++;

            memcpy(candidate_sk, sk, sizeof candidate_sk);
            set_coefficient(candidate_sk, position,
                            invalid_values[value_index]);
            memset(ss_dec, 0xa5, sizeof ss_dec);
            failures += (size_t)(
                crypto_kem_dec(ss_dec, ct, candidate_sk) != 1);
            failures += (size_t)!all_zero(ss_dec, sizeof ss_dec);
            cases++;

            memcpy(candidate_sk, sk, sizeof candidate_sk);
            set_coefficient(
                candidate_sk + NTRUPLUS_POLYBYTES, position,
                invalid_values[value_index]);
            memset(ss_dec, 0xa5, sizeof ss_dec);
            failures += (size_t)(
                crypto_kem_dec(ss_dec, ct, candidate_sk) != 1);
            failures += (size_t)!all_zero(ss_dec, sizeof ss_dec);
            cases++;
        }
    }

    printf("canonical-boundary: cases=%zu failures=%zu\n",
           cases, failures);
    return failures != 0;
}
