#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "fips202.h"
#include "symmetric.h"

static size_t clears, clear_bytes, bad_clear, image_clears, permutations;
static uint64_t rng = UINT64_C(0x7e415eed);
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
    image_clears += n == 1153;
    for (size_t i = 0; i < n; ++i) bad_clear += v[i] != 0;
}
static uint8_t next_byte(void)
{
    rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17;
    return (uint8_t)rng;
}
static void check(size_t n, size_t outlen, size_t align, uint8_t prefix)
{
    /* Exact end allocation makes ASan catch input-tail overreads. */
    uint8_t *storage = malloc(n + align ? n + align : 1), *msg = storage + align;
    uint8_t *joined = malloc(n + 1);
    uint8_t a[288], b[288];
    if (!storage || !joined) abort();
    for (size_t i = 0; i < n; ++i) msg[i] = next_byte();
    joined[0] = prefix;
    memcpy(joined + 1, msg, n);
    memset(a, 0xa5, sizeof a); memset(b, 0xa5, sizeof b);
    shake256(a + 1, outlen, joined, n + 1);
    ntruplus_shake256_prefix(b + 1, outlen, prefix, msg, n);
    if (memcmp(a, b, sizeof a)) {
        fprintf(stderr, "prefix mismatch n=%zu out=%zu align=%zu\n", n, outlen, align);
        exit(1);
    }
    free(joined); free(storage);
}
int main(void)
{
    const size_t lengths[] = {0,1,6,7,8,133,134,135,136,137,270,271,272,
                              1087,1088,1151,1152,1153,2048};
    const size_t outputs[] = {0,1,7,8,32,56,135,136,137,192,272,273};
    size_t cases = 0;
    for (size_t i = 0; i < sizeof lengths / sizeof lengths[0]; ++i)
        for (size_t j = 0; j < sizeof outputs / sizeof outputs[0]; ++j)
            for (size_t k = 0; k < 8; ++k) {
                check(lengths[i], outputs[j], k, next_byte());
                ++cases;
            }
    for (size_t k = 0; k < 256; ++k) {
        uint8_t msg[1152 + 32], joined[1153], expected[192];
        for (size_t i = 0; i < 1152; ++i) msg[i] = next_byte();
        joined[0] = 1; memcpy(joined + 1, msg, 1152);
        shake256(expected, sizeof expected, joined, sizeof joined);
        clears = clear_bytes = image_clears = permutations = 0;
        hash_g(msg + (k % 3) * 8, msg);
        if (memcmp(msg + (k % 3) * 8, expected, sizeof expected)) abort();
        if (clears != 3 || clear_bytes != 536 || image_clears || permutations != 10)
            abort();
        ++cases;
    }
    ntruplus_shake256_prefix(NULL, 0, 1, NULL, 0);
    if (bad_clear) abort();
    printf("PASS %zu differential/overlap cases; hash_g: 10 permutations, "
           "3 clears / 536 bytes, no input-image clear\n", cases);
    return 0;
}
