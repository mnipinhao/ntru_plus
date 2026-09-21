#ifndef NTRUPLUS768_SECURE_CLEAR_H
#define NTRUPLUS768_SECURE_CLEAR_H

#include <stddef.h>
#include <stdint.h>
#include <string.h>
#ifdef _WIN32
#include <windows.h>
#endif

#ifdef GT_SECURE_CLEAR_AUDIT_HOOK
void gt_secure_clear_audit_hook(const void *address, size_t length);
#endif

static inline void gt_secure_clear(void *address, size_t length)
{
#ifdef GT_SECURE_CLEAR_AUDIT_HOOK
    const size_t audit_length = length;
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
    SecureZeroMemory(address, length);
#elif defined(__GNUC__) || defined(__clang__)
    memset(address, 0, length);
    __asm__ volatile("" : : "r"(address) : "memory");
#else
    {
        volatile uint8_t *cursor = address;

        while (length-- > 0)
            *cursor++ = 0;
    }
#endif
#ifdef GT_SECURE_CLEAR_AUDIT_HOOK
    gt_secure_clear_audit_hook(address, audit_length);
#endif
}

#endif
