#include <stddef.h>
#include <stdint.h>
#include "api.h"
#include "params.h"
#include "symmetric.h"
#include "poly.h"
#include "gt864_tobytes.h"
#include "gt864_native.h"
#include "gt864_frombytes.h"
#include "gt864_secure_clear.h"
#include "randombytes.h"

#ifdef DSUPPORTS_SHAKE256_ASM
#include "CE/fips202.h"
#else
#include "NO_CE/fips202.h"
#endif

#include <stdint.h>
uint64_t prof_start(void);
void prof_end(int,uint64_t);
#include "gt864_poly_api.h"
#define poly_ntt(...) do { uint64_t _pt=prof_start(); gt_d1_poly_ntt(__VA_ARGS__); prof_end(0,_pt); } while(0)
#define poly_baseinv(...) ({ uint64_t _pt=prof_start(); int _pr=gt864_native_poly_baseinv(__VA_ARGS__); prof_end(1,_pt); _pr; })
#define poly_basemul(...) do { uint64_t _pt=prof_start(); gt_d1_poly_basemul(__VA_ARGS__); prof_end(2,_pt); } while(0)
#define poly_basemul_add(...) do { uint64_t _pt=prof_start(); gt_d1_poly_basemul_add(__VA_ARGS__); prof_end(4,_pt); } while(0)
#define poly_cbd1(...) do { uint64_t _pt=prof_start(); poly_cbd1(__VA_ARGS__); prof_end(9,_pt); } while(0)
#define poly_sotp_encode(...) do { uint64_t _pt=prof_start(); poly_sotp_encode(__VA_ARGS__); prof_end(10,_pt); } while(0)
#define poly_sotp_decode(...) ({ uint64_t _pt=prof_start(); int _pr=poly_sotp_decode(__VA_ARGS__); prof_end(11,_pt); _pr; })
#define poly_triple(...) do { uint64_t _pt=prof_start(); poly_triple(__VA_ARGS__); prof_end(12,_pt); } while(0)
#define poly_sub(...) do { uint64_t _pt=prof_start(); poly_sub(__VA_ARGS__); prof_end(13,_pt); } while(0)
#define poly_crepmod3(...) do { uint64_t _pt=prof_start(); poly_crepmod3(__VA_ARGS__); prof_end(14,_pt); } while(0)
#define hash_f(...) do { uint64_t _pt=prof_start(); hash_f(__VA_ARGS__); prof_end(15,_pt); } while(0)
#define hash_g(...) do { uint64_t _pt=prof_start(); hash_g(__VA_ARGS__); prof_end(16,_pt); } while(0)
#define hash_h(...) do { uint64_t _pt=prof_start(); hash_h(__VA_ARGS__); prof_end(17,_pt); } while(0)
#define shake256(...) do { uint64_t _pt=prof_start(); shake256(__VA_ARGS__); prof_end(18,_pt); } while(0)
#define randombytes(...) do { uint64_t _pt=prof_start(); randombytes(__VA_ARGS__); prof_end(19,_pt); } while(0)
#define secure_clear(...) do { uint64_t _pt=prof_start(); secure_clear(__VA_ARGS__); prof_end(20,_pt); } while(0)
#define gt864_native_inverse_ternary(...) do { uint64_t _pt=prof_start(); gt864_native_inverse_ternary(__VA_ARGS__); prof_end(21,_pt); } while(0)
#define gt864_native_basemul_for_inverse(...) do { uint64_t _pt=prof_start(); gt864_native_basemul_for_inverse(__VA_ARGS__); prof_end(3,_pt); } while(0)
#define gt864_native_inverse(...) do { uint64_t _pt=prof_start(); gt864_native_inverse(__VA_ARGS__); prof_end(5,_pt); } while(0)
#define gt864_fr0_tobytes_full(...) do { uint64_t _pt=prof_start(); gt864_fr0_tobytes_full(__VA_ARGS__); prof_end(6,_pt); } while(0)
#define gt864_fr0_tobytes_small(...) do { uint64_t _pt=prof_start(); gt864_fr0_tobytes_small(__VA_ARGS__); prof_end(7,_pt); } while(0)
#define gt864_fr0_frombytes_checked(...) ({ uint64_t _pt=prof_start(); int _pr=gt864_fr0_frombytes_checked(__VA_ARGS__); prof_end(8,_pt); _pr; })

/*************************************************
* Name:        verify
*
* Description: Compares two byte arrays for equality in constant time.
*
* Arguments:   - const uint8_t *a: first byte array
*              - const uint8_t *b: second byte array
*              - size_t len:      length of the arrays
*
* Returns 0 if the arrays are equal, 1 otherwise.
**************************************************/
static inline int verify(const uint8_t *a, const uint8_t *b, size_t len)
{
    uint8_t acc = 0;

    for (size_t i = 0; i < len; i++)
        acc |= (uint8_t)(a[i] ^ b[i]);

    return (-(uint64_t)acc) >> 63;
}

/*************************************************
* Name:        genf_derand
*
* Description: Deterministically generates a secret polynomial f and its
*              multiplicative inverse finv in the NTT domain.
*
* Arguments:   - poly *f:     output polynomial f (NTT domain)
*              - poly *finv:  output multiplicative inverse of f
*                              in the NTT domain
*              - const uint8_t *coins: 32-byte deterministic seed
*
* Returns 0 on success; non-zero if f is not invertible in the NTT domain.
**************************************************/
static inline int genf_derand(poly *f, poly *finv, uint8_t buf[NTRUPLUS_N / 4], const uint8_t *coins)
{
    shake256(buf, NTRUPLUS_N / 4, coins, 32);

    poly_cbd1(f, buf);
    poly_triple(f, f);
    f->coeffs[0] += 1;

    poly_ntt(f, f);

    return poly_baseinv(finv, f);
}

/*************************************************
* Name:        geng_derand
*
* Description: Deterministically generates a secret polynomial g and its
*              multiplicative inverse ginv in the NTT domain.
*
* Arguments:   - poly *g:      output polynomial g (NTT domain)
*              - poly *ginv:   output multiplicative inverse of g
*                               in the NTT domain
*              - const uint8_t *coins: 32-byte deterministic seed
*
* Returns 0 on success; non-zero if g is not invertible in the NTT domain.
**************************************************/
static inline int geng_derand(poly *g, poly *ginv, uint8_t buf[NTRUPLUS_N / 4], const uint8_t *coins)
{
    shake256(buf, NTRUPLUS_N / 4, coins, 32);

    poly_cbd1(g, buf);
    poly_triple(g, g);

    poly_ntt(g, g);

    return poly_baseinv(ginv, g);
}

/*************************************************
* Name:        crypto_kem_keypair_derand
*
* Description: Computes the deterministic public and secret key pair from
*              the secret polynomials f and g and their multiplicative
*              inverses finv and ginv in the NTT domain.
*
* Arguments:   - uint8_t *pk:   output public key
*              - uint8_t *sk:   output secret key
*              - const poly *f:     secret polynomial f (NTT domain)
*              - const poly *finv:  multiplicative inverse of f (NTT domain)
*              - const poly *g:     secret polynomial g (NTT domain)
*              - const poly *ginv:  multiplicative inverse of g (NTT domain)
*
* Returns:     void
**************************************************/
static inline void crypto_kem_keypair_derand(uint8_t *pk, uint8_t *sk,
                                             const poly *f,  const poly *finv,
                                             const poly *g,  const poly *ginv)
{
    poly h;

    poly_basemul(&h, g, finv);
    gt864_fr0_tobytes_small(pk, &h);

    poly_basemul(&h, f, ginv);
    /* D1 outputs fit (-q,q); the direct Forward result f does not. */
    gt864_fr0_tobytes_full(sk, f);
    gt864_fr0_tobytes_small(sk + NTRUPLUS_POLYBYTES, &h);
    hash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);
    secure_clear(&h, sizeof h);
}

/*************************************************
* Name:        crypto_kem_keypair
*
* Description: Generates an NTRU+ public/secret key pair for the
*              CCA-secure key encapsulation mechanism. Secret
*              polynomials f and g and their NTT-domain inverses
*              are sampled internally using fresh randomness.
*
* Arguments:   - uint8_t *pk: output public key
*                (array of CRYPTO_PUBLICKEYBYTES bytes)
*              - uint8_t *sk: output secret key
*                (array of CRYPTO_SECRETKEYBYTES bytes)
*
* Returns 0 on success.
**************************************************/
int crypto_kem_keypair(uint8_t *pk, uint8_t *sk)
{
    uint8_t coins[NTRUPLUS_SYMBYTES];
    /* Shared across retries, fully overwritten by SHAKE, erased on exit. */
    uint8_t buf[NTRUPLUS_N / 4];

    poly f, finv;
    poly g, ginv;

    do {
        randombytes(coins, sizeof coins);
    } while (genf_derand(&f, &finv, buf, coins));

    do {
        randombytes(coins, sizeof coins);
    } while (geng_derand(&g, &ginv, buf, coins));

    crypto_kem_keypair_derand(pk, sk, &f, &finv, &g, &ginv);
    secure_clear(coins, sizeof coins);
    secure_clear(buf, sizeof buf);
    secure_clear(&f, sizeof f);
    secure_clear(&finv, sizeof finv);
    secure_clear(&g, sizeof g);
    secure_clear(&ginv, sizeof ginv);
    return 0;
}

/*************************************************
* Name:        crypto_kem_enc_derand
*
* Description: Deterministically performs NTRU+ KEM encapsulation using
*              the public key pk and the supplied randomness coins,
*              producing a ciphertext ct and shared secret ss.
*
* Arguments:   - uint8_t *ct:      output ciphertext
*              - uint8_t *ss:      output shared secret
*              - const uint8_t *pk:    input public key
*              - const uint8_t *coins: input randomness for
*                                      deterministic encapsulation
*
* Returns 0 on success.
**************************************************/
static inline int crypto_kem_enc_derand(uint8_t *ct, uint8_t *ss,
                                        const uint8_t *pk,
                                        const uint8_t *coins)
{
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t buf1[NTRUPLUS_SYMBYTES + NTRUPLUS_N / 4];
    poly c, h, r, m;

    if (gt864_fr0_frombytes_checked(&h,pk)) {
        memset(ct,0,NTRUPLUS_CIPHERTEXTBYTES);
        secure_clear(ss,NTRUPLUS_SSBYTES);
        return 1;
    }

    for (size_t i = 0; i < NTRUPLUS_N / 8; i++)
        msg[i] = coins[i];

    hash_f(msg + NTRUPLUS_N / 8, pk);
    hash_h(buf1, msg);

    poly_cbd1(&r, buf1 + NTRUPLUS_SYMBYTES);
    poly_ntt(&r, &r);

    /* ct is dead until the final complete ciphertext serialization. */
    gt864_fr0_tobytes_full(ct, &r);
    hash_g(ct, ct);
    poly_sotp_encode(&m, msg, ct);
    poly_ntt(&m, &m);

    poly_basemul_add(&c, &h, &r, &m);
    gt864_fr0_tobytes_small(ct, &c);

    for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
        ss[i] = buf1[i];

    secure_clear(msg,sizeof msg);
    secure_clear(buf1,sizeof buf1);
    secure_clear(&r,sizeof r);
    secure_clear(&m,sizeof m);
    return 0;
}

/*************************************************
* Name:        crypto_kem_enc
*
* Description: Generates an NTRU+ KEM ciphertext ct and shared secret ss
*              using the public key pk. Fresh randomness is internally
*              sampled and used for encapsulation.
*
* Arguments:   - uint8_t *ct: output ciphertext
*                (array of CRYPTO_CIPHERTEXTBYTES bytes)
*              - uint8_t *ss: output shared secret
*                (array of CRYPTO_BYTES bytes)
*              - const uint8_t *pk: input public key
*                (array of CRYPTO_PUBLICKEYBYTES bytes)
*
* Returns 0 on success.
**************************************************/
int crypto_kem_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk)
{
    uint8_t coins[NTRUPLUS_N / 8];

    randombytes(coins, sizeof coins);
    int ret=crypto_kem_enc_derand(ct, ss, pk, coins);
    secure_clear(coins,sizeof coins);
    return ret;
}

/*************************************************
* Name:        crypto_kem_dec
*
* Description: Performs NTRU+ KEM decapsulation. Given a ciphertext ct
*              and a secret key sk, computes the shared secret ss. If
*              decapsulation fails, ss is set to all zero bytes.
*
* Arguments:   - uint8_t *ss:  output shared secret
*                (array of CRYPTO_BYTES bytes)
*              - const uint8_t *ct: input ciphertext
*                (array of CRYPTO_CIPHERTEXTBYTES bytes)
*              - const uint8_t *sk: input secret key
*                (array of CRYPTO_SECRETKEYBYTES bytes)
*
* Returns 0 on success, 1 on failure.
**************************************************/
int crypto_kem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk)
{
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t buf1[NTRUPLUS_POLYBYTES];
	uint8_t buf2[NTRUPLUS_POLYBYTES];
	uint8_t buf3[NTRUPLUS_POLYBYTES + NTRUPLUS_SYMBYTES];

    int8_t fail=1;

    /* Four-slot lifetime ABI: c, reusable f/work, hinv, and natural m. */
    poly c, f, hinv, m;

    /* Same rejection order as the selected Official. Secret-key validity is
     * intentionally released as a status bit; do not claim this branch-free. */
    if (gt864_fr0_frombytes_checked(&c,ct) ||
        gt864_fr0_frombytes_checked(&f,sk) ||
        gt864_fr0_frombytes_checked(&hinv,sk+NTRUPLUS_POLYBYTES)) {
        secure_clear(ss,NTRUPLUS_SSBYTES);
        goto cleanup;
    }

    /* Only this product uses R^-1; the paired inverse restores natural R0. */
    gt864_native_basemul_for_inverse(m.coeffs, c.coeffs, f.coeffs);
    gt864_native_inverse_ternary(&m, &m);

    /* f is dead after the decrypting BaseMul and becomes the work slot. */
    poly_ntt(&f, &m);
    poly_sub(&c, &c, &f);
    poly_basemul(&f, &c, &hinv);

    gt864_fr0_tobytes_small(buf1, &f);
    hash_g(buf2, buf1);
    fail = poly_sotp_decode(msg, &m, buf2);

    for (size_t i = 0; i < NTRUPLUS_SYMBYTES; i++)
        msg[i + NTRUPLUS_N / 8] = sk[i + 2 * NTRUPLUS_POLYBYTES];

    hash_h(buf3, msg);

    poly_cbd1(&f, buf3 + NTRUPLUS_SSBYTES);
    poly_ntt(&f, &f);
    gt864_fr0_tobytes_full(buf2, &f);

    fail |= verify(buf1, buf2, NTRUPLUS_POLYBYTES);

    for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
        ss[i] = buf3[i] & ~(-fail);

cleanup:
    secure_clear(msg,sizeof msg);
    secure_clear(buf1,sizeof buf1);
    secure_clear(buf2,sizeof buf2);
    secure_clear(buf3,sizeof buf3);
    secure_clear(&c,sizeof c);
    secure_clear(&f,sizeof f);
    secure_clear(&hinv,sizeof hinv);
    secure_clear(&m,sizeof m);
    return fail;
}
