/*
 * Drop-in replacement for the Official NTRU+ AVX2 fips202.h (SUPERCOP
 * 20260831 crypto_kem/ntruplus{768,864,1152}/avx2/fips202.h, sha256
 * c843fef6...): the only SHAKE256 entry point the Official kem.c and
 * symmetric.c use, shake256(output, outlen, input, inlen), is bound to
 * mlkem-native's x1 one-shot mlk_shake256 (C Keccak-f[1600], vendored in
 * third_party/mlkem-native-fips202-b3ba7b32).
 *
 * The header claims the Official include guard FIPS202_H, so a translation
 * unit that includes it first never reads the Official fips202.h (whose
 * shake256 macro would name fips202avx_shake256).  The Official incremental
 * API (shake256_init/absorb/finalize/squeeze, keccak_state) is not used by
 * kem.c or symmetric.c and is deliberately not provided.
 *
 * Contract inherited from mlk_shake256: input and output must not overlap
 * (Official symmetric.c always hashes a stack copy, and kem.c's keypair
 * calls hash a separate coins buffer); inlen, outlen <= MLK_MAX_BUFFER_SIZE.
 *
 * In a flat SUPERCOP implementation directory this file is installed as
 * fips202.h and its include below is rewritten to "mlk_fips202.h" (see
 * tools/export_keccak_flat.py).
 */
#ifndef FIPS202_H
#define FIPS202_H

#include <stddef.h>
#include <stdint.h>

#include "mlkem/src/fips202/fips202.h"

#define shake256 mlk_shake256

#endif /* FIPS202_H */
