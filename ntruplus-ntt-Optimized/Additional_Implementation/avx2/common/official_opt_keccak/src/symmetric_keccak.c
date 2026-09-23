/*
 * NTRU+ hash wrappers on mlkem-native's x1 SHAKE256 (repo builds).
 *
 * This translation unit is the pinned Official symmetric.c, unmodified,
 * compiled against fips202_mlkem.h (shake256 -> mlk_shake256) with its three
 * functions namespaced by keccak_names.h (hash_f -> ntruplus{N}_keccak_hash_f,
 * ...).  The wrappers' semantics therefore stay the Official ones exactly:
 *   hash_f: SHAKE256(0x00 || msg[POLYBYTES])          -> 32 bytes
 *   hash_g: SHAKE256(0x01 || msg[POLYBYTES])          -> N/4 bytes, stack copy cleared
 *   hash_h: SHAKE256(0x02 || msg[N/8 + 32])            -> 32 + N/4 bytes, stack copy cleared
 * (the input is copied into a stack buffer first, so hash_g(ct, ct) in kem.c
 * never aliases the SHAKE256 input and output).
 *
 * Include path order: the parameter set's upstream/supercop-avx2 before
 * common/official_opt_keccak/{src,config} and third_party/mlkem-native-*.
 * util.h comes first, as in symmetric.c, so its feature-test macros precede
 * the <string.h> that mlkem-native's common.h pulls in (explicit_bzero).
 */
#include "util.h"
#include "params.h"
#include "fips202_mlkem.h"
#include "keccak_names.h"
#include "symmetric.c"
