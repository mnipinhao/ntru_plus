/*
 * Namespacing for the mlkem-native-Keccak NTRU+ hash wrappers, so the
 * candidate hash_f/g/h coexist with the Official ones (global hash_f/g/h
 * from symmetric.c) in one diagnostic ELF:
 *   hash_f -> ntruplus{N}_keccak_hash_f   (likewise hash_g, hash_h)
 * with N = NTRUPLUS_N from the including parameter set's params.h.
 * NTRUPLUS_KECCAK_TAG (default keccak) lets a diagnostic build link a second
 * copy (e.g. compiled at -O2) under another tag.  Repo builds only; a flat
 * SUPERCOP tree uses the Official names unchanged.
 */
#ifndef NTRUPLUS_KECCAK_NAMES_H
#define NTRUPLUS_KECCAK_NAMES_H

#include "params.h"

#ifndef NTRUPLUS_KECCAK_TAG
#define NTRUPLUS_KECCAK_TAG keccak
#endif

#define NTRUPLUS_KECCAK_CAT5_(a, b, c, d, e) a##b##c##d##e
#define NTRUPLUS_KECCAK_CAT5(a, b, c, d, e) NTRUPLUS_KECCAK_CAT5_(a, b, c, d, e)
#define NTRUPLUS_KECCAK_NAME(s) \
    NTRUPLUS_KECCAK_CAT5(ntruplus, NTRUPLUS_N, _, NTRUPLUS_KECCAK_TAG, _##s)

#define hash_f NTRUPLUS_KECCAK_NAME(hash_f)
#define hash_g NTRUPLUS_KECCAK_NAME(hash_g)
#define hash_h NTRUPLUS_KECCAK_NAME(hash_h)

#endif /* NTRUPLUS_KECCAK_NAMES_H */
