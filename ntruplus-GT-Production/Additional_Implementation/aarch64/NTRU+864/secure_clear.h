#ifndef UTIL_H
#define UTIL_H

#if defined(__APPLE__) && !defined(__STDC_WANT_LIB_EXT1__)
#define __STDC_WANT_LIB_EXT1__ 1
#endif
#if defined(__linux__) && !defined(_DEFAULT_SOURCE)
#define _DEFAULT_SOURCE
#endif

#include <stddef.h>
#include <stdint.h>
#include <string.h>
#ifdef _WIN32
#include <windows.h>
#endif

#if defined(__APPLE__)
/*
 * macOS provides memset_s but does not define __STDC_LIB_EXT1__, and the
 * __STDC_WANT_LIB_EXT1__ above only exposes the declaration when this header is
 * included before <string.h>.  Translation units do not all do that, so declare
 * it here and make the include order irrelevant.
 */
extern int memset_s(void *address, size_t address_size, int value,
                    size_t length);
#endif

#ifdef SECURE_CLEAR_AUDIT_HOOK
void gt_secure_clear_audit_hook(const void *address, size_t length);
#endif

static inline void secure_clear(void *v, size_t len)
{
#ifdef SECURE_CLEAR_AUDIT_HOOK
    const size_t audit_len = len;
#endif
#if defined(_WIN32)
    SecureZeroMemory(v, len);
#elif defined(__APPLE__)
    (void)memset_s(v, len, 0, len);
#elif defined(__GLIBC__)
    explicit_bzero(v, len);
#else
    volatile uint8_t *p = v;

    while (len-- > 0)
        *p++ = 0;
#endif
#ifdef SECURE_CLEAR_AUDIT_HOOK
    gt_secure_clear_audit_hook(v, audit_len);
#endif
}

#endif /* UTIL_H */
