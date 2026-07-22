#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "api.h"

static int hex_nibble(int c)
{
    if (c >= '0' && c <= '9')
        return c - '0';
    if (c >= 'A' && c <= 'F')
        return c - 'A' + 10;
    if (c >= 'a' && c <= 'f')
        return c - 'a' + 10;
    return -1;
}

static int read_first_field(const char *path, const char *name,
                            uint8_t *out, size_t outlen)
{
    char line[32768];
    char prefix[32];
    FILE *file;
    int prefix_len;

    prefix_len = snprintf(prefix, sizeof(prefix), "%s = ", name);
    if (prefix_len < 0 || (size_t)prefix_len >= sizeof(prefix))
        return -1;

    file = fopen(path, "r");
    if (file == NULL)
        return -1;

    while (fgets(line, sizeof(line), file) != NULL) {
        const char *hex;

        if (strncmp(line, prefix, (size_t)prefix_len) != 0)
            continue;

        hex = line + prefix_len;
        for (size_t i = 0; i < outlen; i++) {
            const int high = hex_nibble((unsigned char)hex[2 * i]);
            const int low = hex_nibble((unsigned char)hex[2 * i + 1]);

            if (high < 0 || low < 0) {
                fclose(file);
                return -1;
            }
            out[i] = (uint8_t)((high << 4) | low);
        }
        fclose(file);
        return 0;
    }

    fclose(file);
    return -1;
}

int main(int argc, char **argv)
{
    uint8_t sk[CRYPTO_SECRETKEYBYTES];
    uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
    uint8_t expected[CRYPTO_BYTES];
    uint8_t actual[CRYPTO_BYTES];
    unsigned mismatches = 0;
    int dec_rc;

    if (argc != 2) {
        fprintf(stderr, "usage: %s PQCkemKAT_*.rsp\n", argv[0]);
        return 2;
    }
    if (read_first_field(argv[1], "sk", sk, sizeof(sk)) != 0 ||
        read_first_field(argv[1], "ct", ct, sizeof(ct)) != 0 ||
        read_first_field(argv[1], "ss", expected, sizeof(expected)) != 0) {
        fprintf(stderr, "failed to parse first KAT vector from %s\n", argv[1]);
        return 2;
    }

    dec_rc = crypto_kem_dec(actual, ct, sk);
    for (size_t i = 0; i < sizeof(actual); i++)
        mismatches += actual[i] != expected[i];

    printf("cross_vector_decap_rc=%d\n", dec_rc);
    printf("cross_vector_ss_mismatches=%u\n", mismatches);
    return dec_rc == 0 && mismatches == 0 ? 0 : 1;
}
