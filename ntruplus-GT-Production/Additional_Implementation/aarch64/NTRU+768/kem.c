#include <stddef.h>
#include <stdint.h>
#include "api.h"
#include "params.h"
#include "symmetric.h"

#include "poly.h"
#include "randombytes.h"
#include "decap_verify.h"
#include "keygen.h"
#include "ntt_internal.h"
#include "secure_clear.h"

typedef gt_cq_poly keygen_poly;

#include "fips202.h"

static inline void encap_basemul_add_tobytes(uint8_t *ct, const poly *h,
                                             const poly *r, poly *m)
{
    /*
     * The encap-only assembly contract loads each 64-byte m block before
     * overwriting that same output block.  Reuse m as the ciphertext
     * polynomial to avoid a separate 1,536-byte stack object and clear.
     */
    poly_basemul_add(m, h, r, m);
    poly_tobytes(ct, m);
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
                              const uint8_t *coins, uint8_t buf[NTRUPLUS_N / 4])
{
    int result;

    shake256(buf, NTRUPLUS_N / 4, coins, 32);

    poly_cbd1(&f->storage, buf);
    keygen_ntt_mul3_add1(f);

    result = gt_keygen_baseinv_cq_to_cq_scaled_r(finv, f);
    return result;
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
                              const uint8_t *coins, uint8_t buf[NTRUPLUS_N / 4])
{
    int result;

    shake256(buf, NTRUPLUS_N / 4, coins, 32);

    poly_cbd1(&g->storage, buf);
    keygen_ntt_mul3(g);

    result = gt_keygen_baseinv_cq_to_cq_scaled_r(ginv, g);
    return result;
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
    keygen_poly h;

    gt_keygen_basemul_cq_cq_to_cq_scaled_r(&h, g, finv);

    gt_keygen_tobytes_cq(pk, &h);
    gt_keygen_tobytes_cq(sk, f);
    gt_keygen_basemul_cq_cq_to_cq_scaled_r(&h, f, ginv);
    gt_keygen_tobytes_cq(sk + NTRUPLUS_POLYBYTES, &h);
    hash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);
    gt_secure_clear(&h, sizeof h);

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
    uint8_t buf[NTRUPLUS_N / 4];

    keygen_poly f, g;
    keygen_poly finv, ginv;

    for (;;) {
        randombytes(coins, sizeof coins);
        if (!genf_derand(&f, &finv, coins, buf))
            break;

    }

    for (;;) {
        randombytes(coins, sizeof coins);
        if (!geng_derand(&g, &ginv, coins, buf))
            break;

    }

    crypto_kem_keypair_derand(pk, sk, &f, &finv, &g, &ginv);
    gt_secure_clear(buf, sizeof buf);
    gt_secure_clear(coins, sizeof coins);
    gt_secure_clear(&f, sizeof f);
    gt_secure_clear(&g, sizeof g);
    gt_secure_clear(&finv, sizeof finv);
    gt_secure_clear(&ginv, sizeof ginv);
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

    poly h, r, m;

    if (poly_frombytes(&h, pk)) {
        for (size_t i = 0; i < NTRUPLUS_CIPHERTEXTBYTES; i++) ct[i] = 0;
        gt_secure_clear(ss, NTRUPLUS_SSBYTES);

        return 1;
    }

    for (size_t i = 0; i < NTRUPLUS_N / 8; i++)
        msg[i] = coins[i];

    hash_f(msg + NTRUPLUS_N / 8, pk);
    hash_h(buf1, msg);

    poly_cbd1(&r, buf1 + NTRUPLUS_SYMBYTES);
    gt_internal_poly_ntt_encap_small(&r, &r);

    gt_internal_poly_tobytes_from_loose(ct, &r);
    hash_g(ct, ct);
    poly_sotp_encode(&m, msg, ct);
    gt_internal_poly_ntt_encap_small(&m, &m);

    encap_basemul_add_tobytes(ct, &h, &r, &m);

    for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
        ss[i] = buf1[i];

    gt_secure_clear(msg, sizeof msg);
    gt_secure_clear(buf1, sizeof buf1);

    gt_secure_clear(&r, sizeof r);
    gt_secure_clear(&m, sizeof m);
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
    int result;

    randombytes(coins, sizeof coins);
    result = crypto_kem_enc_derand(ct, ss, pk, coins);
    gt_secure_clear(coins, sizeof coins);
    return result;
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
    struct {
        uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
        uint8_t buf1[NTRUPLUS_POLYBYTES];
        uint8_t buf2[NTRUPLUS_POLYBYTES];
        poly c;
        poly hinv;
        union {
            poly forward;
            uint8_t buf3[NTRUPLUS_N / 4 + NTRUPLUS_SYMBYTES];
        } slot;
        poly m_then_r;
    } scratch;
    poly *forward = &scratch.slot.forward;
    poly *m_r = &scratch.m_then_r;
    int8_t fail;

    /*
     * Decode and validate ct/f in one 64-coefficient/two-group pipeline.
     * ct is retained in Decap QSoA layout; packed f is consumed directly
     * and is never materialized in the scratch object.
     */
    fail = (int8_t)gt_decap_checked_ct_f_basemul_scale64(
        m_r, &scratch.c, ct, sk);
    fail |= (int8_t)gt_decap_poly_frombytes(
        &scratch.hinv, sk + NTRUPLUS_POLYBYTES);
    if (fail) {
        gt_secure_clear(ss, NTRUPLUS_SSBYTES);
        goto cleanup;
    }

    gt_decap_poly_invntt_scale(m_r);
    poly_crepmod3(m_r, m_r);

    gt_decap_poly_ntt(forward, m_r);
    gt_decap_poly_sub(&scratch.c, &scratch.c, forward);
    gt_decap_poly_basemul(
        forward, &scratch.c, &scratch.hinv);
    gt_decap_poly_tobytes(scratch.buf1, forward);

    hash_g(scratch.buf2, scratch.buf1);
    fail = (int8_t)poly_sotp_decode(scratch.msg, m_r, scratch.buf2);

    for (size_t i = 0; i < NTRUPLUS_SYMBYTES; i++)
        scratch.msg[i + NTRUPLUS_N / 8] =
            sk[i + 2 * NTRUPLUS_POLYBYTES];

    hash_h(scratch.slot.buf3, scratch.msg);

    poly_cbd1(m_r, scratch.slot.buf3 + NTRUPLUS_SSBYTES);
    gt_decap_poly_ntt(&scratch.c, m_r);
    gt_decap_poly_tobytes(scratch.buf2, &scratch.c);

    fail |= verify(scratch.buf1, scratch.buf2, NTRUPLUS_POLYBYTES);

    for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
        ss[i] = scratch.slot.buf3[i] & ~(-fail);

cleanup:
    gt_secure_clear(&scratch, sizeof scratch);
    return fail;
}
