#include <stddef.h>
#include <stdint.h>
#include "api.h"
#include "params.h"
#include "symmetric.h"
#include "poly.h"
#include "randombytes.h"

#ifdef GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
void poly_basemul_add_encap_direct32_q31_tobytes_contract(
    poly *r, const poly *a, const poly *b, const poly *c);
#endif

#if defined(GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT) && \
    defined(GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_C)
#error "select only one decap verify basemul->tobytes contract helper"
#endif

#if defined(GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_DIRECT) && \
    (defined(GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT) || \
     defined(GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_C))
#error "select only one decap verify basemul->tobytes contract helper"
#endif

#ifdef GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT
void gt_decap_verify_basemul_tobytes_contract_ref(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const poly *hinv);
#endif

#ifdef GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_C
void gt_decap_verify_basemul_tobytes_contract_c_candidate(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const poly *hinv);
#endif

#ifdef GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_DIRECT
void gt_decap_verify_basemul_tobytes_direct_candidate(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const poly *hinv);
#endif

#ifdef GT_PRODUCTION_USE_RMINUS1_DECAP
void poly_basemul_rminus1(poly *r, const poly *a, const poly *b);
void poly_invntt_from_rminus1(poly *r, const poly *a);
#endif

#ifdef GT_PRODUCTION_USE_RMINUS1_STAGE123SCRATCH_DECAP
void poly_basemul_rminus1_to_stage123scratch(int16_t *scratch,
                                             const poly *a,
                                             const poly *b);
void poly_invntt_from_rminus1_stage45scratch(poly *r,
                                             const int16_t *scratch);
#endif

#ifdef GT_PRODUCTION_USE_TUPLE_DECAP
void poly_basemul_to_tuple(poly *r, const poly *a, const poly *b);
void gt_tuple_poly_invntt(poly *r, const poly *a);
#endif

#ifdef GT_PRODUCTION_USE_PACK_TUPLE_DECAP
void gt_tuple_poly_invntt(poly *r, const poly *a);

static int gt_pack_block_major_index(int branch, int physical_j, int lane)
{
    return branch * 384 + 4 * physical_j + lane;
}

static int gt_pack_tuple_index(int branch, int row, int k32, int lane)
{
    return branch * 384 + row * 128 + 4 * k32 + lane;
}

static int gt_pack_tuple_physical_j(int row, int k32)
{
    return (32 * row + 3 * k32) % 96;
}

static void gt_block_major_to_tuple_c(poly *tuple,
                                      const poly *block_major)
{
    for (int branch = 0; branch < 2; branch++)
        for (int row = 0; row < 3; row++)
            for (int k32 = 0; k32 < 32; k32++) {
                const int physical_j = gt_pack_tuple_physical_j(row, k32);

                for (int lane = 0; lane < 4; lane++) {
                    const int tuple_idx =
                        gt_pack_tuple_index(branch, row, k32, lane);
                    const int block_idx =
                        gt_pack_block_major_index(branch, physical_j, lane);

                    tuple->coeffs[tuple_idx] =
                        block_major->coeffs[block_idx];
                }
            }
}
#endif

#ifdef GT_PRODUCTION_USE_SCALED_KEYPAIR
int poly_baseinv_scaled_r(poly *r, const poly *a);
void poly_basemul_scaled_r_input(poly *r, const poly *a,
                                 const poly *b_scaled_r);
#define KEYPAIR_BASEINV poly_baseinv_scaled_r
#define KEYPAIR_BASEMUL poly_basemul_scaled_r_input
#else
#define KEYPAIR_BASEINV poly_baseinv
#define KEYPAIR_BASEMUL poly_basemul
#endif

#ifdef DSUPPORTS_SHAKE256_ASM
#include "CE/fips202.h"
#else
#include "NO_CE/fips202.h"
#endif

#ifdef GT_DIRECT32_Q31_RELEASE_GUARD_NOINLINE
#define GT_ENCAP_TOBYTES_CONTRACT_INLINE
#if defined(__GNUC__) || defined(__clang__)
#define GT_ENCAP_TOBYTES_CONTRACT_ATTR __attribute__((noinline))
#else
#define GT_ENCAP_TOBYTES_CONTRACT_ATTR
#endif
#else
#define GT_ENCAP_TOBYTES_CONTRACT_INLINE inline
#define GT_ENCAP_TOBYTES_CONTRACT_ATTR
#endif

static GT_ENCAP_TOBYTES_CONTRACT_INLINE GT_ENCAP_TOBYTES_CONTRACT_ATTR void
gt_encap_basemul_add_tobytes_contract(uint8_t *ct, const poly *h,
                                      const poly *r, const poly *m)
{
    poly c;

#ifdef GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
    poly_basemul_add_encap_direct32_q31_tobytes_contract(&c, h, r, m);
#else
    poly_basemul_add(&c, h, r, m);
#endif
    poly_tobytes(ct, &c);
}

#undef GT_ENCAP_TOBYTES_CONTRACT_INLINE
#undef GT_ENCAP_TOBYTES_CONTRACT_ATTR

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
static inline int genf_derand(poly *f, poly *finv, const uint8_t *coins)
{
    uint8_t buf[NTRUPLUS_N / 4];

    shake256(buf, sizeof buf, coins, 32);

    poly_cbd1(f, buf);
    poly_triple(f, f);
    f->coeffs[0] += 1;

    poly_ntt(f, f);

    return KEYPAIR_BASEINV(finv, f);
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
static inline int geng_derand(poly *g, poly *ginv, const uint8_t *coins)
{
    uint8_t buf[NTRUPLUS_N / 4];

    shake256(buf, sizeof buf, coins, 32);

    poly_cbd1(g, buf);
    poly_triple(g, g);

    poly_ntt(g, g);

    return KEYPAIR_BASEINV(ginv, g);
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
    poly h, hinv;

    KEYPAIR_BASEMUL(&h, g, finv);
    KEYPAIR_BASEMUL(&hinv, f, ginv);

    poly_tobytes(pk, &h);
    poly_tobytes(sk, f);
    poly_tobytes(sk + NTRUPLUS_POLYBYTES, &hinv);
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
int crypto_kem_keypair(uint8_t *pk, uint8_t *sk)
{
    uint8_t coins[NTRUPLUS_SYMBYTES];

    poly f, finv;
    poly g, ginv;

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
    gt_encap_basemul_add_tobytes_contract(ct, &h, &r, &m);
    
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
int crypto_kem_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk)
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
int crypto_kem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk)
{
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t buf1[NTRUPLUS_POLYBYTES];
	uint8_t buf2[NTRUPLUS_POLYBYTES];
	uint8_t buf3[NTRUPLUS_POLYBYTES + NTRUPLUS_SYMBYTES];
    
    int8_t fail;
    
    poly c, f, hinv;
    poly r1;
#if !defined(GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT) && \
    !defined(GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_C) && \
    !defined(GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_DIRECT)
    poly r2;
#endif
    poly m1, m2;
    
    poly_frombytes(&c, ct);
    poly_frombytes(&f, sk);
    poly_frombytes(&hinv, sk + NTRUPLUS_POLYBYTES);
    
#ifdef GT_PRODUCTION_USE_RMINUS1_STAGE123SCRATCH_DECAP
    poly_basemul_rminus1_to_stage123scratch(m1.coeffs, &c, &f);
    poly_invntt_from_rminus1_stage45scratch(&m1, m1.coeffs);
#elif defined(GT_PRODUCTION_USE_RMINUS1_DECAP)
    /* Paired ABI: basemul_rminus1 leaves an extra R^-1 for this invntt entry. */
    poly_basemul_rminus1(&m1, &c, &f);
    poly_invntt_from_rminus1(&m1, &m1);
#elif defined(GT_PRODUCTION_USE_TUPLE_DECAP)
    poly_basemul_to_tuple(&m1, &c, &f);
    gt_tuple_poly_invntt(&m1, &m1);
#elif defined(GT_PRODUCTION_USE_PACK_TUPLE_DECAP)
    poly_basemul(&m1, &c, &f);
    gt_block_major_to_tuple_c(&m2, &m1);
    gt_tuple_poly_invntt(&m1, &m2);
#else
    poly_basemul(&m1, &c, &f);
    poly_invntt(&m1, &m1);
#endif
#if !defined(GT_PRODUCTION_USE_RMINUS1_CREP3_DECAP) && \
    !defined(GT_PRODUCTION_USE_RMINUS1_STAGE123SCRATCH_CREP3_DECAP)
    poly_crepmod3(&m1, &m1);
#endif
    
    poly_ntt(&m2, &m1);
    poly_sub(&c, &c, &m2);
#ifdef GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT
    gt_decap_verify_basemul_tobytes_contract_ref(buf1, &c, &hinv);
#elif defined(GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_C)
    gt_decap_verify_basemul_tobytes_contract_c_candidate(buf1, &c, &hinv);
#elif defined(GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_DIRECT)
    gt_decap_verify_basemul_tobytes_direct_candidate(buf1, &c, &hinv);
#else
    poly_basemul(&r2, &c, &hinv);
    poly_tobytes(buf1, &r2);
#endif
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
