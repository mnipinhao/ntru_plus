#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { PK = 1296, SK = 2624, CT = 1296, SS = 32, N = 864, Q = 3457 };
typedef int (*keyfn)(uint8_t *, uint8_t *);
typedef int (*encfn)(uint8_t *, uint8_t *, const uint8_t *);
typedef int (*decfn)(uint8_t *, const uint8_t *, const uint8_t *);
struct api { keyfn key; encfn enc; decfn dec; };
static uint64_t state = 864;

void randombytes(uint8_t *out, size_t n)
{
    while (n--) {
        state ^= state << 13; state ^= state >> 7; state ^= state << 17;
        *out++ = (uint8_t)state;
    }
}

static void *must(void *handle, const char *name)
{
    void *symbol = dlsym(handle, name);
    if (!symbol) { fprintf(stderr, "missing %s: %s\n", name, dlerror()); exit(2); }
    return symbol;
}

static struct api load(const char *path)
{
    void *handle = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    if (!handle) { fprintf(stderr, "%s\n", dlerror()); exit(2); }
    return (struct api) { must(handle, "crypto_kem_keypair"), must(handle, "crypto_kem_enc"), must(handle, "crypto_kem_dec") };
}

static void set_coefficient(uint8_t *bytes, int position, uint16_t value)
{
    int pair = position / 2;
    if ((position & 1) == 0) {
        bytes[3 * pair] = (uint8_t)value;
        bytes[3 * pair + 1] = (uint8_t)((bytes[3 * pair + 1] & 0xf0) | (value >> 8));
    } else {
        bytes[3 * pair + 1] = (uint8_t)((bytes[3 * pair + 1] & 0x0f) | (value << 4));
        bytes[3 * pair + 2] = (uint8_t)(value >> 4);
    }
}

static int all_zero(const uint8_t *bytes, size_t length)
{
    uint8_t aggregate = 0;
    for (size_t i = 0; i < length; i++) aggregate |= bytes[i];
    return aggregate == 0;
}

int main(int argc, char **argv)
{
    if (argc != 3) return 2;
    struct api api[2] = { load(argv[1]), load(argv[2]) };
    uint8_t pk[PK], sk[SK], ct[CT], shared[SS], recovered[SS];
    state = 0x1234864;
    if (api[0].key(pk, sk) || api[0].enc(ct, shared, pk) || api[1].dec(recovered, ct, sk) || memcmp(shared, recovered, SS)) return 3;
    unsigned cases = 0;
    const uint16_t invalid_values[] = { Q, 4095 };
    for (unsigned implementation = 0; implementation < 2; implementation++) {
        for (unsigned value_index = 0; value_index < 2; value_index++) {
            for (int position = 0; position < N; position++) {
                uint8_t bad_pk[PK], bad_ct[CT], bad_sk[SK], out_ct[CT], out_ss[SS];
                memcpy(bad_pk, pk, PK); set_coefficient(bad_pk, position, invalid_values[value_index]);
                memset(out_ct, 0xa5, CT); memset(out_ss, 0xa5, SS);
                if (api[implementation].enc(out_ct, out_ss, bad_pk) != 1 || !all_zero(out_ct, CT) || !all_zero(out_ss, SS)) return 4;
                cases++;
                memcpy(bad_ct, ct, CT); set_coefficient(bad_ct, position, invalid_values[value_index]);
                memset(out_ss, 0xa5, SS);
                if (api[implementation].dec(out_ss, bad_ct, sk) != 1 || !all_zero(out_ss, SS)) return 5;
                cases++;
                memcpy(bad_sk, sk, SK); set_coefficient(bad_sk, position, invalid_values[value_index]);
                memset(out_ss, 0xa5, SS);
                if (api[implementation].dec(out_ss, ct, bad_sk) != 1 || !all_zero(out_ss, SS)) return 6;
                cases++;
                memcpy(bad_sk, sk, SK); set_coefficient(bad_sk + PK, position, invalid_values[value_index]);
                memset(out_ss, 0xa5, SS);
                if (api[implementation].dec(out_ss, ct, bad_sk) != 1 || !all_zero(out_ss, SS)) return 7;
                cases++;
            }
        }
    }
    printf("P4 KEM rejection: PASS implementations=2 cases=%u positions=%d values=q,4095 paths=enc-pk,dec-ct,dec-sk0,dec-sk1\n", cases, N);
    return 0;
}
