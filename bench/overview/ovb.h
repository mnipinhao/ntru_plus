/*
 * Same-ELF component profiler interface (2026-09-23 AVX2 overview).
 *
 * Every implementation tree is compiled with its own headers together with
 * one adapter translation unit, linked into one relocatable object and every
 * defined global symbol is prefixed with the implementation's role
 * (objcopy --redefine-syms; see scripts/run_overview_components.py).  The
 * adapter exports `ovb_impl_desc` (renamed to <role>_ovb_impl_desc); the
 * harness only calls through it.  Undefined symbols (randombytes,
 * crypto_declassify, ovb_rng_seed, libc) resolve to the single harness copy.
 */
#ifndef OVB_H
#define OVB_H

#include <stdint.h>

#define OVB_BANKS 16

typedef struct {
    const char *name;          /* component name, e.g. "forward", "pack_m_lazy" */
    void (*prep)(unsigned);    /* untimed per-call preparation (may be 0) */
    void (*run)(unsigned);     /* the timed call, bank 0..OVB_BANKS-1 */
} ovb_component;

typedef struct {
    const char *kind;          /* "official", "gt768", "exp017" */
    void (*setup)(void);       /* builds all bank fixtures (uses seeded randombytes) */
    /* KEM with the harness RNG seeded by the caller; returns 0 on success. */
    int (*keypair)(unsigned char *pk, unsigned char *sk);
    int (*enc)(unsigned char *ct, unsigned char *ss, const unsigned char *pk);
    int (*dec)(unsigned char *ss, const unsigned char *ct, const unsigned char *sk);
    /* hash outputs for the cross-implementation equality preflight */
    void (*hash_f)(uint8_t *out, const uint8_t *in);
    void (*hash_g)(uint8_t *out, const uint8_t *in);
    void (*hash_h)(uint8_t *out, const uint8_t *in);
    unsigned count;
    const ovb_component *components;
} ovb_impl;

void ovb_rng_seed(uint64_t seed);

#endif
