#ifndef NTRUPLUS768_SECURE_CLEAR_H
#define NTRUPLUS768_SECURE_CLEAR_H

#include <stddef.h>
#include <stdint.h>
#include <string.h>
#ifdef _WIN32
#include <windows.h>
#endif

#if defined(__GLIBC__)
/*
 * Some translation units include libc headers before this private header, so
 * feature-test macros cannot reliably expose the declaration under -std=c99.
 */
extern void explicit_bzero(void *address, size_t length);
#endif

#ifdef GT_SECURE_CLEAR_AUDIT_HOOK
void gt_secure_clear_audit_hook(const void *address, size_t length);
#endif

static inline void gt_secure_clear(void *address, size_t length)
{
#ifdef GT_SECURE_CLEAR_AUDIT_HOOK
    const size_t audit_length = length;
#endif
#if defined(_WIN32)
    SecureZeroMemory(address, length);
#elif defined(__STDC_LIB_EXT1__)
    (void)memset_s(address, length, 0, length);
#elif defined(__GLIBC__)
    explicit_bzero(address, length);
#else
    volatile uint8_t *cursor = address;

    while (length-- > 0)
        *cursor++ = 0;
#endif
#ifdef GT_SECURE_CLEAR_AUDIT_HOOK
    gt_secure_clear_audit_hook(address, audit_length);
#endif
}

#endif
