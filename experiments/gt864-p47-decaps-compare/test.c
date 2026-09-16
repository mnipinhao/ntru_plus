#include <stdint.h>
#include <stdio.h>
#include <string.h>

void gt864_p18_tobytes_full_asm(uint8_t out[1296], const int16_t in[864]);
int gt864_p47_decaps_compare_asm(const uint8_t expected[1296], const int16_t in[864]);

static uint64_t state = UINT64_C(0x50343754455354);
static uint32_t next32(void) {
    state ^= state << 7;
    state ^= state >> 9;
    return (uint32_t)state;
}

int main(void) {
    _Alignas(16) int16_t input[864], saved[864];
    uint8_t guarded[16 + 1296 + 16];
    uint8_t *wire = guarded + 16;
    for (unsigned trial = 0; trial < 256; ++trial) {
        for (unsigned i = 0; i < 864; ++i) input[i] = (int16_t)next32();
        memcpy(saved, input, sizeof input);
        memset(guarded, 0xa5, sizeof guarded);
        gt864_p18_tobytes_full_asm(wire, input);
        if (gt864_p47_decaps_compare_asm(wire, input) != 0) return 1;
        if (memcmp(input, saved, sizeof input)) return 2;
        for (unsigned i = 0; i < 16; ++i)
            if (guarded[i] != 0xa5 || guarded[16 + 1296 + i] != 0xa5) return 3;
        for (unsigned position = 0; position < 1296; ++position) {
            wire[position] ^= (uint8_t)(1u << (position & 7));
            if (gt864_p47_decaps_compare_asm(wire, input) != 1) return 4;
            wire[position] ^= (uint8_t)(1u << (position & 7));
        }
    }
    puts("P47 native differential passed: 256 arbitrary FR0 inputs and every one-byte mismatch");
    return 0;
}
