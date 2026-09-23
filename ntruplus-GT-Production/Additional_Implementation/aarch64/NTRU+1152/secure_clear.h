#ifndef UTIL_H
#define UTIL_H

#include <stddef.h>
#include <stdint.h>
#include <string.h>
#ifdef _WIN32
#include <windows.h>
#endif

#ifdef SECURE_CLEAR_AUDIT_HOOK
void gt_secure_clear_audit_hook(const void *address, size_t length);
#endif

static inline void secure_clear(void *v, size_t len)
{
#ifdef SECURE_CLEAR_AUDIT_HOOK
    const size_t audit_len = len;
#endif
/*
 * One technique on every non-Windows platform, following mlkem-native: a plain
 * clear plus a compiler barrier, where the barrier is what stops the store
 * being removed as a dead write.  This replaces a three-way platform branch --
 * memset_s on Apple, explicit_bzero on glibc, a volatile byte loop otherwise --
 * that was three behaviours to reason about.  Measured neutral-to-better on
 * both hosts: A76 decaps -30 and encaps -70 cycles, M2 decaps 5,410 -> 5,390ns.
 *
 * memset_s additionally required declaring it by hand on macOS, which does not
 * define __STDC_LIB_EXT1__, and carried bounds-check semantics we never used.
 */
#if defined(_WIN32)
    SecureZeroMemory(v, len);
#elif defined(__GNUC__) || defined(__clang__)
    memset(v, 0, len);
    __asm__ volatile("" : : "r"(v) : "memory");
#else
    {
        volatile uint8_t *p = v;
        while (len-- > 0)
            *p++ = 0;
    }
#endif
#ifdef SECURE_CLEAR_AUDIT_HOOK
    gt_secure_clear_audit_hook(v, audit_len);
#endif
}

/* SUPERCOP's TIMECOP treats every secret-derived branch as a leak unless the
 * value is declassified first.  Only values released by design are: a secret
 * key that fails to decode, and the non-invertibility keygen retries on, both
 * as in Official. */
#ifdef SUPERCOP
#include "crypto_declassify.h"
#define ntruplus_declassify crypto_declassify
#else
#define ntruplus_declassify(x, xlen) ((void)(x), (void)(xlen))
#endif

#endif /* UTIL_H */
