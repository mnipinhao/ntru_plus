#include <stddef.h>
#include <stdint.h>
#include "api.h"
#include "params.h"
#include "symmetric.h"

#include "poly.h"
#include "randombytes.h"
#include "internal/decap_verify.h"
#include "internal/keygen.h"

typedef gt_cq_poly keygen_poly;

#include "NO_CE/fips202.h"

static inline void encap_basemul_add_tobytes(uint8_t *ct, const poly *h,
                                             const poly *r, const poly *m)
{
    poly c;

    poly_basemul_add(&c, h, r, m);
    poly_tobytes(ct, &c);
}

static inline void keygen_ntt_mul3_add1(keygen_poly *out)
{
    poly_triple(&out->storage, &out->storage);
    out->storage.coeffs[0] += 1;
    gt_keygen_poly_ntt_to_cq(out, &out->storage);
}

static inline void keygen_ntt_mul3(keygen_poly *out)
{
    poly_triple(&out->storage, &out->storage);
    gt_keygen_poly_ntt_to_cq(out, &out->storage);
}

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
static inline int genf_derand(keygen_poly *f,
                              keygen_poly *finv,
                              const uint8_t *coins)
{
    uint8_t buf[NTRUPLUS_N / 4];

    shake256(buf, sizeof buf, coins, 32);

    poly_cbd1(&f->storage, buf);
    keygen_ntt_mul3_add1(f);

    return gt_keygen_baseinv_cq_to_cq_scaled_r(finv, f);
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
static inline int geng_derand(keygen_poly *g,
                              keygen_poly *ginv,
                              const uint8_t *coins)
{
    uint8_t buf[NTRUPLUS_N / 4];

    shake256(buf, sizeof buf, coins, 32);

    poly_cbd1(&g->storage, buf);
    keygen_ntt_mul3(g);

    return gt_keygen_baseinv_cq_to_cq_scaled_r(ginv, g);
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
                                             const keygen_poly *f,
                                             const keygen_poly *finv,
                                             const keygen_poly *g,
                                             const keygen_poly *ginv)
{
    keygen_poly h, hinv;

    gt_keygen_basemul_cq_cq_to_cq_scaled_r(&h, g, finv);
    gt_keygen_basemul_cq_cq_to_cq_scaled_r(&hinv, f, ginv);

    gt_keygen_tobytes_cq(pk, &h);
    gt_keygen_tobytes_cq(sk, f);
    gt_keygen_tobytes_cq(sk + NTRUPLUS_POLYBYTES, &hinv);
    hash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);
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
int crypto_kem_keypair_internal(uint8_t *pk, uint8_t *sk)
{
    uint8_t coins[NTRUPLUS_SYMBYTES];

    keygen_poly f, g;
    keygen_poly finv, ginv;

    do {
        randombytes(coins, sizeof coins);
    } while (genf_derand(&f, &finv, coins));

    do {
        randombytes(coins, sizeof coins);
    } while (geng_derand(&g, &ginv, coins));

    crypto_kem_keypair_derand(pk, sk, &f, &finv, &g, &ginv);
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
	uint8_t buf2[NTRUPLUS_POLYBYTES];

    poly h, r, m;

    for (size_t i = 0; i < NTRUPLUS_N / 8; i++)
        msg[i] = coins[i];

    hash_f(msg + NTRUPLUS_N / 8, pk);
    hash_h(buf1, msg);

    poly_cbd1(&r, buf1 + NTRUPLUS_SYMBYTES);
    poly_ntt(&r, &r);

    poly_tobytes(buf2, &r);
    hash_g(buf2, buf2);
    poly_sotp_encode(&m, msg, buf2);
    poly_ntt(&m, &m);

    poly_frombytes(&h, pk);
    encap_basemul_add_tobytes(ct, &h, &r, &m);

    for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
        ss[i] = buf1[i];

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
int crypto_kem_enc_internal(uint8_t *ct, uint8_t *ss, const uint8_t *pk)
{
    uint8_t coins[NTRUPLUS_N / 8];

    randombytes(coins, sizeof coins);
    return crypto_kem_enc_derand(ct, ss, pk, coins);
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
int crypto_kem_dec_internal(uint8_t *ss, const uint8_t *ct,
                            const uint8_t *sk)
{
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t buf1[NTRUPLUS_POLYBYTES];
	uint8_t buf2[NTRUPLUS_POLYBYTES];
	uint8_t buf3[NTRUPLUS_POLYBYTES + NTRUPLUS_SYMBYTES];

    int8_t fail;

    poly c, f;
    poly r1;
    poly m1, m2;

    poly_frombytes(&c, ct);
    poly_frombytes(&f, sk);

    /* Production poly API: basemul leaves R^-1; invntt absorbs it. */
    poly_basemul(&m1, &c, &f);
    poly_invntt(&m1, &m1);
    poly_crepmod3(&m1, &m1);

    poly_ntt(&m2, &m1);
    poly_sub(&c, &c, &m2);
    gt_decap_verify_to_bytes(buf1, &c, sk + NTRUPLUS_POLYBYTES);
    hash_g(buf2, buf1);
    fail = poly_sotp_decode(msg, &m1, buf2);

    for (size_t i = 0; i < NTRUPLUS_SYMBYTES; i++)
        msg[i + NTRUPLUS_N / 8] = sk[i + 2 * NTRUPLUS_POLYBYTES];

    hash_h(buf3, msg);

    poly_cbd1(&r1, buf3 + NTRUPLUS_SSBYTES);
    poly_ntt(&r1, &r1);
    poly_tobytes(buf2, &r1);

    fail |= verify(buf1, buf2, NTRUPLUS_POLYBYTES);

    for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
        ss[i] = buf3[i] & ~(-fail);

    return fail;
}
