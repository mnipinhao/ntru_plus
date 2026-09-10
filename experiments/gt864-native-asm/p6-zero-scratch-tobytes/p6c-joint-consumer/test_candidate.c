#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../../../../ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/byte_merge_tables.h"

#define Q 3457

extern void p6c_pack(uint8_t *, const int16_t *, const void *, const uint8_t *, uint8_t *)
    __asm("gt864_p6c_pack_a_oracle_wrapper");
extern void p6c_row0(uint8_t *, const void *, const uint8_t *, const uint8_t *, uint8_t *, const uint8_t *)
    __asm("gt864_p6c_row0_oracle_wrapper");

static uint32_t rng_state = 0x503643u;
static uint32_t rng32(void) {
    uint32_t x = rng_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    return rng_state = x;
}

static uint16_t canonical(int16_t x) {
    int r = x % Q;
    return (uint16_t)(r < 0 ? r + Q : r);
}

static void high4(uint8_t out[4], const uint16_t row[8]) {
    for (int i = 0; i < 4; i++)
        out[i] = (uint8_t)((row[2 * i] >> 8) | ((row[2 * i + 1] >> 8) << 4));
}

static void expected_pack(uint8_t out[112], const int16_t in[72]) {
    uint16_t a[9][8];
    uint8_t h[9][4];
    memset(out, 0, 112);
    for (int r = 0; r < 9; r++) {
        for (int k = 0; k < 8; k++) a[r][k] = canonical(in[8 * r + k]);
        high4(h[r], a[r]);
    }
    for (int r = 0; r < 8; r++)
        for (int k = 0; k < 8; k++) out[16 * (r / 2) + 8 * (r & 1) + k] = (uint8_t)a[r][k];
    for (int k = 0; k < 8; k++) out[64 + k] = (uint8_t)a[8][k];
    memcpy(out + 72, h[8], 4);
    for (int r = 0; r < 4; r++) memcpy(out + 80 + 4 * r, h[r], 4);
    for (int r = 4; r < 8; r++) memcpy(out + 96 + 4 * (r - 4), h[r], 4);
}

static void pair_stream(uint8_t out[24], const uint16_t a[8], const uint16_t b[8]) {
    for (int k = 0; k < 8; k++) {
        out[3 * k] = (uint8_t)a[k];
        out[3 * k + 1] = (uint8_t)((a[k] >> 8) | ((b[k] & 15) << 4));
        out[3 * k + 2] = (uint8_t)(b[k] >> 4);
    }
}

static void expected_row(uint8_t out[72], const uint8_t pairs[3][24]) {
    for (int k = 0; k < 8; k++)
        for (int p = 0; p < 3; p++)
            memcpy(out + 9 * k + 3 * p, pairs[p] + 3 * k, 3);
}

static int check_pack(const int16_t in[72], const uint8_t seed[208], uint8_t packed[112]) {
    uint8_t want[112], sink[208];
    memset(packed, 0xa5, 112);
    memset(sink, 0x5a, sizeof(sink));
    p6c_pack(packed, in, NULL, seed, sink);
    expected_pack(want, in);
    if (memcmp(packed, want, 108) || memcmp(seed, sink, 208)) return 0;
    return 1;
}

static int check_row(const int16_t a_in[72], int16_t b0) {
    _Alignas(16) uint8_t seed[208], packed[112], state[464], sink[400], out[72], want[72];
    _Alignas(16) uint8_t constants[48] = {0}, indices[240];
    uint16_t pvals[2][2][8], aa[8], bb[8];
    uint8_t pairs[3][24];
    for (unsigned i = 0; i < sizeof(seed); i++) seed[i] = (uint8_t)rng32();
    if (!check_pack(a_in, seed, packed)) return 0;
    memset(state, 0, sizeof(state));
    for (int p = 0; p < 2; p++) {
        for (int side = 0; side < 2; side++)
            for (int k = 0; k < 8; k++) pvals[p][side][k] = (uint16_t)(rng32() % Q);
        pair_stream(pairs[p], pvals[p][0], pvals[p][1]);
    }
    memcpy(state, pairs[0], 24);
    memcpy(state + 24, pairs[1], 24);
    for (int i = 48; i < 208; i++) state[i] = (uint8_t)rng32();
    memcpy(state + 208, packed, 112);
    for (int k = 0; k < 8; k++) {
        aa[k] = canonical(a_in[k]);
        bb[k] = canonical((int16_t)(b0 + k));
    }
    memcpy(state + 320, &b0, 2);
    for (int k = 1; k < 8; k++) {
        int16_t x = (int16_t)(b0 + k);
        memcpy(state + 320 + 2 * k, &x, 2);
    }
    for (int r = 1; r < 9; r++)
        for (int k = 0; k < 8; k++) {
            int16_t x = (int16_t)rng32();
            memcpy(state + 320 + 16 * r + 2 * k, &x, 2);
        }
    pair_stream(pairs[2], aa, bb);
    expected_row(want, pairs);
    memset(constants + 32, 15, 16);
    memcpy(indices, gt864_byte_merge_indices, sizeof(indices));
    for (int chunk = 0; chunk < 5; chunk++)
        for (int i = 0; i < 16; i++) {
            int pos = 48 * chunk + 16 + i;
            if (indices[pos] != 255) indices[pos] = (uint8_t)(indices[pos] + 8);
        }
    memset(out, 0xa5, sizeof(out));
    memset(sink, 0x5a, sizeof(sink));
    p6c_row0(out, NULL, constants, state, sink, indices);
    if (memcmp(out, want, 72)) return 0;
    if (memcmp(sink, state + 48, 160)) return 0;
    if (memcmp(sink + 160, packed, 112)) return 0;
    if (memcmp(sink + 272, state + 336, 128)) return 0;
    return 1;
}

int main(void) {
    _Alignas(16) int16_t in[72];
    _Alignas(16) uint8_t seed[208], packed[112];
    unsigned pack_cases = 0, row_cases = 0;
    for (unsigned i = 0; i < sizeof(seed); i++) seed[i] = (uint8_t)rng32();
    for (int base = -32768; base <= 32760; base += 8) {
        for (int i = 0; i < 72; i++) in[i] = (int16_t)(base + (i & 7));
        if (!check_pack(in, seed, packed)) return fprintf(stderr, "pack mismatch at %d\n", base), 1;
        pack_cases++;
    }
    for (int trial = 0; trial < 4096; trial++) {
        for (int i = 0; i < 72; i++) in[i] = (int16_t)rng32();
        if (!check_pack(in, seed, packed)) return fprintf(stderr, "random pack mismatch %d\n", trial), 1;
        pack_cases++;
        if (!check_row(in, (int16_t)rng32())) return fprintf(stderr, "row mismatch %d\n", trial), 1;
        row_cases++;
    }
    printf("PASS pack_cases=%u row_cases=%u\n", pack_cases, row_cases);
    return 0;
}
