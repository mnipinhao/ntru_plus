#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include "fips202.h"
#include "symmetric.h"

static size_t clears, clear_bytes, bad_clear, permutations, cases;
static uint64_t rng = UINT64_C(0xc415eed);
void ntruplus_keccak_f1600_x1_aarch64(uint64_t *, const uint64_t *);
void counted_permute(uint64_t *s, const uint64_t *rc)
{
    ++permutations;
    ntruplus_keccak_f1600_x1_aarch64(s, rc);
}
void secure_clear_audit_hook(const void *p, size_t n)
{
    const volatile uint8_t *v = p;
    ++clears;
    clear_bytes += n;
    for (size_t i = 0; i < n; ++i) bad_clear += v[i] != 0;
}
static uint8_t next_byte(void)
{
    rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17;
    return (uint8_t)rng;
}
static void oracle(uint8_t out[192], const uint8_t msg[1152])
{
    uint8_t joined[1153];
    joined[0] = 1; memcpy(joined + 1, msg, 1152);
    shake256(out, 192, joined, 1153);
}
static void invoke(uint8_t *out, const uint8_t *msg)
{
    clears = clear_bytes = permutations = 0;
    hash_g(out, msg);
    if (clears != 1 || clear_bytes != 200 || permutations != 10 || bad_clear)
        abort();
    ++cases;
}
int main(void)
{
    for (size_t k = 0; k < 256; ++k) {
        for (size_t align = 0; align < 8; ++align) {
            uint8_t *allocation = malloc(1152 + align);
            uint8_t *msg = allocation + align;
            uint8_t expected[192], out[194];
            if (!allocation) abort();
            for (size_t i = 0; i < 1152; ++i)
                msg[i] = k == 0 ? 0 : k == 1 ? 255 : k == 2 ? (uint8_t)i : next_byte();
            oracle(expected, msg);
            memset(out, 0xa5, sizeof out);
            invoke(out + 1, msg);
            if (out[0] != 0xa5 || out[193] != 0xa5 ||
                memcmp(out + 1, expected, 192)) abort();
            free(allocation);
        }
    }
    /* Check complete memory images: only the requested output may change. */
    for (size_t k = 0; k < 256; ++k) {
        const int offsets[] = {-16, -1, 0, 1, 8, 136, 1080};
        for (size_t j = 0; j < sizeof offsets / sizeof offsets[0]; ++j) {
            uint8_t buffer[1440], image[1440], expected[192];
            for (size_t i = 0; i < sizeof buffer; ++i) buffer[i] = next_byte();
            uint8_t *msg = buffer + 32;
            oracle(expected, msg);
            memcpy(image, buffer, sizeof image);
            memcpy(image + 32 + offsets[j], expected, 192);
            invoke(msg + offsets[j], msg);
            if (memcmp(buffer, image, sizeof buffer)) abort();
        }
    }
    /* Guard the last readable message byte and final output byte. */
    long page = sysconf(_SC_PAGESIZE);
    if (page < 1152) abort();
    uint8_t *input_pages = mmap(NULL, 2 * page, PROT_READ | PROT_WRITE,
                               MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    uint8_t *output_pages = mmap(NULL, 2 * page, PROT_READ | PROT_WRITE,
                                MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (input_pages == MAP_FAILED || output_pages == MAP_FAILED) abort();
    if (mprotect(input_pages + page, page, PROT_NONE) ||
        mprotect(output_pages + page, page, PROT_NONE)) abort();
    uint8_t *msg = input_pages + page - 1152, *out = output_pages + page - 192;
    for (size_t i = 0; i < 1152; ++i) msg[i] = next_byte();
    uint8_t expected[192];
    oracle(expected, msg);
    if (mprotect(input_pages, page, PROT_READ)) abort();
    invoke(out, msg);
    if (memcmp(out, expected, 192)) abort();
    munmap(input_pages, 2 * page); munmap(output_pages, 2 * page);
    printf("PASS %zu fixed hash_g differential/alias/guard cases; "
           "10 permutations, 1 clear / 200 bytes\n", cases);
    return 0;
}
