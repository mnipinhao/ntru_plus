/*
 * SysV x86-64 ABI check of the three public entry points and every kernel.
 *
 * For each function and both SysV-legal stack alignments at the call (0 and
 * 16 mod 32): rbx, rbp and r12-r15 are preserved, rsp comes back unchanged,
 * MXCSR, the x87 control word and RFLAGS.DF are preserved/clear.  The public
 * entry points must also return with a clean upper YMM state (XINUSE[2] = 0,
 * one vzeroupper at each API exit); the internal kernels are reported only.
 */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <cpuid.h>

#include "api.h"
#include "fips202.h"
#include "poly.h"
#include "symmetric.h"

typedef void (*abi_fn)(void);

struct abi_call {
    abi_fn fn;                /* 0 */
    uint64_t a0, a1, a2;      /* 8, 16, 24 */
    uint64_t misalign;        /* 32 */
    uint64_t ret;             /* 40 */
    uint32_t have_xinuse;     /* 48 */
    uint32_t pad0;
    uint32_t xinuse;          /* 56 */
    uint32_t pad1;
    uint64_t rbp;             /* 64 */
    uint64_t rflags;          /* 72 */
    uint32_t mxcsr_before;    /* 80 */
    uint32_t mxcsr_after;     /* 84 */
    uint16_t fcw_before;      /* 88 */
    uint16_t fcw_after;       /* 90 */
    uint32_t pad2;
    uint64_t r12, r13, r14, r15; /* 96 .. 120 */
    uint64_t rbx;             /* 128 */
    uint64_t rsp_changed;     /* 136 */
};
_Static_assert(offsetof(struct abi_call, xinuse) == 56, "layout");
_Static_assert(offsetof(struct abi_call, mxcsr_before) == 80, "layout");
_Static_assert(offsetof(struct abi_call, r12) == 96, "layout");
_Static_assert(offsetof(struct abi_call, rsp_changed) == 136, "layout");

uint64_t abi_probe(struct abi_call *c);

static void shake256_32(uint8_t *out, const uint8_t *in) { mlk_shake256(out, 32, in, 64); }

int main(void)
{
    static uint8_t pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES];
    static uint8_t ct[CRYPTO_CIPHERTEXTBYTES], ss[CRYPTO_BYTES], ss2[CRYPTO_BYTES];
    static uint8_t bytes[NTRUPLUS_POLYBYTES], msg[NTRUPLUS_N / 8 + 32], buf[NTRUPLUS_N / 2 + 64];
    static poly a, b, c;
    static __m256i den[18];
    unsigned eax, ebx, ecx, edx;
    uint32_t have_xinuse = 0;
    struct item { const char *name; abi_fn fn; void *x, *y, *z; int api; } items[] = {
        {"crypto_kem_keypair", (abi_fn)crypto_kem_keypair, pk, sk, 0, 1},
        {"crypto_kem_enc", (abi_fn)crypto_kem_enc, ct, ss, pk, 1},
        {"crypto_kem_dec", (abi_fn)crypto_kem_dec, ss2, ct, sk, 1},
        {"poly_ntt", (abi_fn)poly_ntt, &a, 0, 0, 0},
        {"poly_invntt_crepmod3", (abi_fn)poly_invntt_crepmod3, &a, 0, 0, 0},
        {"poly_basemul_scale", (abi_fn)poly_basemul_scale, &c, &a, &b, 0},
        {"poly_basemul_montgomery", (abi_fn)poly_basemul_montgomery, &c, &a, &b, 0},
        {"poly_basemul_shoup", (abi_fn)poly_basemul_shoup, &c, &a, &b, 0},
        {"poly_baseinv_1", (abi_fn)poly_baseinv_1, &c, den, &a, 0},
        {"poly_baseinv", (abi_fn)poly_baseinv, &c, &a, 0, 0},
        {"poly_tobytes", (abi_fn)poly_tobytes, bytes, &a, 0, 0},
        {"poly_frombytes", (abi_fn)poly_frombytes, &a, bytes, 0, 0},
        {"poly_cbd1", (abi_fn)poly_cbd1, &a, buf, 0, 0},
        {"poly_sotp_encode", (abi_fn)poly_sotp_encode, &a, msg, buf, 0},
        {"poly_sotp_decode", (abi_fn)poly_sotp_decode, msg, &a, buf, 0},
        {"poly_add", (abi_fn)poly_add, &c, &a, &b, 0},
        {"poly_sub", (abi_fn)poly_sub, &c, &a, &b, 0},
        {"poly_triple", (abi_fn)poly_triple, &a, 0, 0, 0},
        {"hash_f", (abi_fn)hash_f, buf, bytes, 0, 0},
        {"hash_g", (abi_fn)hash_g, buf, bytes, 0, 0},
        {"hash_h", (abi_fn)hash_h, buf, msg, 0, 0},
        {"shake256", (abi_fn)shake256_32, buf, msg, 0, 0},
    };
    int failures = 0;

    if (__get_cpuid_count(0xd, 1, &eax, &ebx, &ecx, &edx) && (eax & 4))
        have_xinuse = 1;
    for (size_t i = 0; i < sizeof items / sizeof items[0]; i++) {
        for (uint64_t mis = 0; mis <= 16; mis += 16) {
            struct abi_call k;
            unsigned regs_bad, bad;
            int dirty;

            memset(&k, 0, sizeof k);
            k.fn = items[i].fn;
            k.a0 = (uint64_t)(uintptr_t)items[i].x;
            k.a1 = (uint64_t)(uintptr_t)items[i].y;
            k.a2 = (uint64_t)(uintptr_t)items[i].z;
            k.misalign = mis;
            k.have_xinuse = have_xinuse;
            abi_probe(&k);
            regs_bad = (k.rbx != 0x1111111111111111ULL) | (k.rbp != 0x2222222222222222ULL) << 1 |
                       (k.r12 != 0x3333333333333333ULL) << 2 | (k.r13 != 0x4444444444444444ULL) << 3 |
                       (k.r14 != 0x5555555555555555ULL) << 4 | (k.r15 != 0x6666666666666666ULL) << 5;
            dirty = have_xinuse ? (int)((k.xinuse >> 2) & 1) : -1;
            bad = regs_bad | (unsigned)k.rsp_changed << 6 |
                  (unsigned)(k.mxcsr_before != k.mxcsr_after) << 7 |
                  (unsigned)(k.fcw_before != k.fcw_after) << 8 |
                  (unsigned)((k.rflags >> 10) & 1) << 9 |
                  (unsigned)(items[i].api && dirty == 1) << 10;
            printf("%-24s rsp%%32=%-2u callee-saved=%s rsp=%s mxcsr/fcw/df=%s upper-ymm=%s%s\n",
                   items[i].name, (unsigned)mis, regs_bad ? "BAD" : "ok", k.rsp_changed ? "BAD" : "ok",
                   (bad >> 7) & 7 ? "BAD" : "ok",
                   dirty < 0 ? "n/a" : dirty ? "dirty" : "clean",
                   bad ? "  FAIL" : "");
            failures += bad != 0;
        }
    }
    if (crypto_kem_dec(ss2, ct, sk) || memcmp(ss, ss2, sizeof ss)) {
        printf("KEM round trip through the probe failed\n");
        return 1;
    }
    printf("abi: %s (XINUSE %s)\n", failures ? "FAIL" : "pass",
           have_xinuse ? "checked" : "not supported by this CPU; upper-YMM check skipped");
    return failures != 0;
}
