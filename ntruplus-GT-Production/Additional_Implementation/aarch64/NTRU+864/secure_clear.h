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
     * One technique on every non-Windows platform, following mlkem-native,
     * which uses a plain clear plus a compiler barrier throughout and cites
     * FIPS 203 Section 3.3, Destruction of intermediate values.  The barrier
     * is what stops the store being removed as a dead write.
     *
     * This replaces a three-way platform branch whose behaviour nobody could
     * predict without knowing which libc was in play.  The bounds-checked
     * variant is C11 Annex K, optional and unevenly provided, and on macOS
     * NTRU+768 fell through every branch to the byte loop -- the slowest of
     * the three.  The loop is kept for compilers without GNU inline asm.
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

#endif /* UTIL_H */
