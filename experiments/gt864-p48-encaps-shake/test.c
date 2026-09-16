#include <stdint.h>
#include <stdio.h>
#include <string.h>

void gt864_fr0_tobytes_full(uint8_t out[1296], const void *in);
void hash_g(uint8_t out[216], const uint8_t in[1296]);
void hash_g_fr0(uint8_t out[216], const int16_t in[864]);

typedef struct { _Alignas(16) int16_t coeffs[864]; } poly_local;

static uint64_t state = UINT64_C(0x50343854455354);
static uint32_t next32(void) {
    state ^= state << 7;
    state ^= state >> 9;
    return (uint32_t)state;
}

int main(void) {
    poly_local input, saved;
    uint8_t wire[1296];
    uint8_t guarded_a[16 + 216 + 16], guarded_b[16 + 216 + 16];
    for (unsigned trial = 0; trial < 1024; ++trial) {
        for (unsigned i = 0; i < 864; ++i) input.coeffs[i] = (int16_t)next32();
        memcpy(&saved, &input, sizeof input);
        memset(guarded_a, 0xa5, sizeof guarded_a);
        memset(guarded_b, 0x5a, sizeof guarded_b);
        gt864_fr0_tobytes_full(wire, &input);
        hash_g(guarded_a + 16, wire);
        hash_g_fr0(guarded_b + 16, input.coeffs);
        if (memcmp(guarded_a + 16, guarded_b + 16, 216)) return 1;
        if (memcmp(&input, &saved, sizeof input)) return 2;
        for (unsigned i = 0; i < 16; ++i) {
            if (guarded_a[i] != 0xa5 || guarded_a[232 + i] != 0xa5) return 3;
            if (guarded_b[i] != 0x5a || guarded_b[232 + i] != 0x5a) return 4;
        }
    }
    puts("P48 native differential passed: 1024 arbitrary FR0 inputs");
    return 0;
}
