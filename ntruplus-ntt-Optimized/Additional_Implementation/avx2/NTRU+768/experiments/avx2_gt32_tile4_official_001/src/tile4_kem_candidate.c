#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "poly.h"
#include "symmetric.h"
#include "util.h"

#include "tile4.h"
#include "tile4_dual_terminal.h"
#include "tile4_kem_candidate.h"
#include "gt32_native_rcheck_placement.h"
#include "../generated/tile4_serialized_mapping.h"

#define WORDS GT32_TILE4_POLY_WORDS

#if defined(GT32_TILE4_RECOVER_ALIGN64)
#define GT32_RECOVER_ALIGNMENT __attribute__((aligned(64)))
#else
#define GT32_RECOVER_ALIGNMENT
#endif

typedef struct {
	int16_t c[WORDS];
	/* f during decode; then Forward/check scratch or final rhat. */
	int16_t aux[WORDS];
	int16_t hinv[WORDS];
	/* First BM output, then coefficient-order recovered message. */
	int16_t m[WORDS];
	/* Inverse rows, Forward output, or Official pack input. */
	int16_t work[WORDS];
} gt32_decap_scratch_t __attribute__((aligned(64)));

static int verify_bytes(const uint8_t *a, const uint8_t *b, size_t length)
{
	uint8_t acc = 0;
	for (size_t i = 0; i < length; i++)
		acc |= (uint8_t)(a[i] ^ b[i]);
	return (int)((-(uint64_t)acc) >> 63);
}

#if defined(GT32_TILE4_KEM_TESTING)
/* Historical SA control and scalar codec retained only for differential tests. */
static uint16_t centered_to_nonnegative(int16_t value)
{
	int32_t reduced = (int32_t)value % GT32_TILE4_Q;
	reduced += (reduced >> 31) & GT32_TILE4_Q;
	return (uint16_t)reduced;
}

static void gt32_tile4_tobytes_candidate(
	uint8_t out[GT32_TILE4_SERIALIZED_BYTES],
	const int16_t in[GT32_TILE4_POLY_WORDS])
{
	for (size_t pair = 0; pair < 384; pair++) {
		const uint16_t first = centered_to_nonnegative(
			in[gt32_tile4_serialized_to_aos[2U * pair]]);
		const uint16_t second = centered_to_nonnegative(
			in[gt32_tile4_serialized_to_aos[2U * pair + 1U]]);
		out[3U * pair] = (uint8_t)first;
		out[3U * pair + 1U] = (uint8_t)((first >> 8)
			| (uint16_t)(second << 4));
		out[3U * pair + 2U] = (uint8_t)(second >> 4);
	}
}

static int recover_message_and_r_sa(uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	gt32_decap_scratch_t *scratch,
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	if (gt32_tile4_frombytes_aos_asm(scratch->c, ct) != 0
		|| gt32_tile4_frombytes_bm_soa_semantic_asm(scratch->aux, sk) != 0
		|| gt32_tile4_frombytes_aos_asm(scratch->hinv,
			sk + NTRUPLUS_POLYBYTES) != 0)
		return 1;

	/*
	 * c stays in AoS for the later c-m edge.  f has no second consumer, so
	 * Decodeq deposits it directly in BM-native coefficient planes.
	 */
	gt32_tile4_basemul_scale_soa_aos_to_aos_private_asm(scratch->m,
		scratch->aux, scratch->c);
	gt32_tile4_inverse_all_pair_asm(scratch->work, scratch->m);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(scratch->m,
		scratch->work);
	poly_crepmod3((poly *)(void *)scratch->m);

	gt32_tile4_forward_full_wide_raw_pair_align64_asm(scratch->aux,
		scratch->m);
	poly_sub((poly *)(void *)scratch->c,
		(const poly *)(const void *)scratch->c,
		(const poly *)(const void *)scratch->aux);
	gt32_tile4_basemul_general_b2_asm(scratch->aux, scratch->c,
		scratch->hinv);
	gt32_tile4_tobytes_candidate(recovered_r, scratch->aux);
	return 0;
}
#endif

/* Decoder-native NTT-domain island shared by the two serialization controls. */
static __attribute__((always_inline)) inline void
recover_message_and_r_soa_domain_arithmetic(gt32_decap_scratch_t *scratch)
{
	gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(scratch->m,
		scratch->c, scratch->aux);
	gt32_tile4_inverse_all_pair_asm(scratch->work, scratch->m);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(scratch->m,
		scratch->work);
	poly_crepmod3((poly *)(void *)scratch->m);

	gt32_tile4_frontend_wide_raw_asm(scratch->aux, scratch->m);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->work, scratch->aux);
	poly_sub((poly *)(void *)scratch->c,
		(const poly *)(const void *)scratch->c,
		(const poly *)(const void *)scratch->work);
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(scratch->aux,
		scratch->c, scratch->hinv);
}

#if defined(GT32_GLOBAL_PHYSICAL_KEM)
void gt32_global_inverse_core_asm(int16_t *, const int16_t *);
void gt32_tile4_basemul_scale_soa_soa_to_m_private_asm(
	int16_t *, const int16_t *, const int16_t *);

/*
 * KEM-specific consumer of the global physical ABI.  Q24 c/f remain in their
 * decoder-native private SoA representation.  Only the first product's
 * output/consumer edge changes from B3->AoS + I1 to B3->M + global inverse.
 */
static __attribute__((always_inline)) inline void
recover_message_and_r_global_inverse_arithmetic(
	gt32_decap_scratch_t *scratch)
{
	gt32_tile4_basemul_scale_soa_soa_to_m_private_asm(scratch->m,
		scratch->c, scratch->aux);
	gt32_global_inverse_core_asm(scratch->work, scratch->m);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(scratch->m,
		scratch->work);
	poly_crepmod3((poly *)(void *)scratch->m);

	gt32_tile4_frontend_wide_raw_asm(scratch->aux, scratch->m);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->work, scratch->aux);
	poly_sub((poly *)(void *)scratch->c,
		(const poly *)(const void *)scratch->c,
		(const poly *)(const void *)scratch->work);
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(scratch->aux,
		scratch->c, scratch->hinv);
}
#endif

static __attribute__((always_inline)) inline void
recover_message_and_r_soa_domain_arithmetic_sidecar(
	gt32_decap_scratch_t *scratch, gt32_sotp_sidecar_t *sidecar)
{
	gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(scratch->m,
		scratch->c, scratch->aux);
	gt32_tile4_inverse_all_pair_asm(scratch->work, scratch->m);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(scratch->m,
		scratch->work);
	/* Preserve full m for N5; tap only post-crep {-1,0,1} registers. */
	gt32_poly_crepmod3_sidecar_s1_asm(scratch->m, sidecar);

	gt32_tile4_frontend_wide_raw_asm(scratch->aux, scratch->m);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->work, scratch->aux);
	poly_sub((poly *)(void *)scratch->c,
		(const poly *)(const void *)scratch->c,
		(const poly *)(const void *)scratch->work);
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(scratch->aux,
		scratch->c, scratch->hinv);
}

static __attribute__((always_inline)) inline void
encode_recovered_r_soa_bridge(uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	gt32_decap_scratch_t *scratch)
{
	gt32_tile4_soa_to_official_words_grouped_asm(scratch->work,
		scratch->aux);
	poly_tobytes(recovered_r, (const poly *)(const void *)scratch->work);
}

static __attribute__((always_inline)) inline void
encode_recovered_r_q24_gt_pack(uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	gt32_decap_scratch_t *scratch)
{
	/* BMgeneral produces centered-canonical private SoA at exponent e=0. */
	gt32_q24_encode_soa_asm(recovered_r, scratch->aux);
}

static GT32_RECOVER_ALIGNMENT int recover_message_and_r_soa_domain(
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	gt32_decap_scratch_t *scratch,
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	if (gt32_tile4_frombytes3_bm_soa_semantic_asm(scratch->c,
		scratch->aux, scratch->hinv, ct, sk) != 0)
		return 1;
	recover_message_and_r_soa_domain_arithmetic(scratch);
	encode_recovered_r_soa_bridge(recovered_r, scratch);
	return 0;
}

static GT32_RECOVER_ALIGNMENT int
recover_message_and_r_soa_domain_q24_unpack_only(
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	gt32_decap_scratch_t *scratch,
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	if (gt32_q24_decode3_soa_asm(scratch->c, scratch->aux, scratch->hinv,
		ct, sk) != 0)
		return 1;
	recover_message_and_r_soa_domain_arithmetic(scratch);
	encode_recovered_r_soa_bridge(recovered_r, scratch);
	return 0;
}

/*
 * Production GT-native wire boundary for the GT32 decapsulation candidate:
 * Q24 GT-unpack3 -> persistent private SoA arithmetic -> Q24 GT-pack.
 */
static GT32_RECOVER_ALIGNMENT int recover_message_and_r_soa_domain_q24(
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	gt32_decap_scratch_t *scratch,
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	if (gt32_q24_decode3_soa_asm(scratch->c, scratch->aux, scratch->hinv,
		ct, sk) != 0)
		return 1;
	recover_message_and_r_soa_domain_arithmetic(scratch);
	encode_recovered_r_q24_gt_pack(recovered_r, scratch);
	return 0;
}

#if defined(GT32_GLOBAL_PHYSICAL_KEM)
static GT32_RECOVER_ALIGNMENT int recover_message_and_r_q24_global_inverse(
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	gt32_decap_scratch_t *scratch,
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	if (gt32_q24_decode3_soa_asm(scratch->c, scratch->aux, scratch->hinv,
		ct, sk) != 0)
		return 1;
	recover_message_and_r_global_inverse_arithmetic(scratch);
	encode_recovered_r_q24_gt_pack(recovered_r, scratch);
	return 0;
}
#endif

static GT32_RECOVER_ALIGNMENT int
recover_message_and_r_soa_domain_q24_sidecar(
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	gt32_decap_scratch_t *scratch, gt32_sotp_sidecar_t *sidecar,
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	if (gt32_q24_decode3_soa_asm(scratch->c, scratch->aux, scratch->hinv,
		ct, sk) != 0)
		return 1;
	recover_message_and_r_soa_domain_arithmetic_sidecar(scratch, sidecar);
	encode_recovered_r_q24_gt_pack(recovered_r, scratch);
	return 0;
}

typedef int (*recover_fn)(uint8_t *, gt32_decap_scratch_t *,
	const uint8_t *, const uint8_t *);
typedef void (*check_encode_fn)(uint8_t *, gt32_decap_scratch_t *);

static void encode_check_soa_bridge(uint8_t out[NTRUPLUS_POLYBYTES],
	gt32_decap_scratch_t *scratch)
{
	gt32_tile4_frontend_wide_raw_asm(scratch->c, scratch->aux);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->hinv, scratch->c);
	gt32_tile4_soa_to_official_words_grouped_asm(scratch->work,
		scratch->hinv);
	poly_tobytes(out, (const poly *)(const void *)scratch->work);
}

static void encode_check_q24_lazy10788(uint8_t out[NTRUPLUS_POLYBYTES],
	gt32_decap_scratch_t *scratch)
{
	gt32_tile4_frontend_wide_raw_asm(scratch->c, scratch->aux);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->hinv, scratch->c);
	/* N5 private-SoA output is e=0 with the proven |word| <= 10788. */
	gt32_q24_encode_soa_lazy10788_asm(out, scratch->hinv);
}

#if defined(GT32_TILE4_KEM_TESTING)
int gt32_tile4_decap_trace_sa_control(
	int16_t m[NTRUPLUS_N],
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	gt32_decap_scratch_t scratch;
	const int result = recover_message_and_r_sa(recovered_r, &scratch, ct, sk);
	memcpy(m, scratch.m, sizeof scratch.m);
	secure_clear(&scratch, sizeof scratch);
	return result;
}

int gt32_tile4_decap_trace_candidate(
	int16_t m[NTRUPLUS_N],
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	gt32_decap_scratch_t scratch;
	const int result = recover_message_and_r_soa_domain_q24(recovered_r,
		&scratch, ct, sk);
	memcpy(m, scratch.m, sizeof scratch.m);
	secure_clear(&scratch, sizeof scratch);
	return result;
}

int gt32_tile4_decap_trace_soa_domain_candidate(
	int16_t m[NTRUPLUS_N],
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	gt32_decap_scratch_t scratch;
	const int result = recover_message_and_r_soa_domain(recovered_r, &scratch,
		ct, sk);
	memcpy(m, scratch.m, sizeof scratch.m);
	secure_clear(&scratch, sizeof scratch);
	return result;
}

int gt32_tile4_decap_trace_q24_decode_candidate(
	int16_t m[NTRUPLUS_N],
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	gt32_decap_scratch_t scratch;
	const int result = recover_message_and_r_soa_domain_q24_unpack_only(
		recovered_r, &scratch, ct, sk);
	memcpy(m, scratch.m, sizeof scratch.m);
	secure_clear(&scratch, sizeof scratch);
	return result;
}

int gt32_tile4_decap_trace_q24_pack_candidate(
	int16_t m[NTRUPLUS_N],
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	gt32_decap_scratch_t scratch;
	const int result = recover_message_and_r_soa_domain_q24(recovered_r,
		&scratch, ct, sk);
	memcpy(m, scratch.m, sizeof scratch.m);
	secure_clear(&scratch, sizeof scratch);
	return result;
}

void gt32_tile4_tobytes_candidate_testing(
	uint8_t out[NTRUPLUS_POLYBYTES], const int16_t in[NTRUPLUS_N])
{
	gt32_tile4_tobytes_candidate(out, in);
}
#endif

static __attribute__((always_inline)) inline int crypto_kem_dec_gt32_core(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES], recover_fn recover,
	check_encode_fn encode_check, int initialize_buffers)
{
	/* These are fully defined by the same producers as Official before use. */
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t buf1[NTRUPLUS_POLYBYTES];
	uint8_t buf2[NTRUPLUS_POLYBYTES];
	uint8_t buf3[NTRUPLUS_POLYBYTES + NTRUPLUS_SYMBYTES];
	gt32_decap_scratch_t scratch;
	int fail = 1;

	/* G0 control: quantify initialization absent from Official Main. */
	if (initialize_buffers != 0) {
		memset(msg, 0, sizeof msg);
		memset(buf1, 0, sizeof buf1);
		memset(buf2, 0, sizeof buf2);
		memset(buf3, 0, sizeof buf3);
	}

	/*
	 * Private inverse-scale island.  The selected recover function owns the
	 * typed GT-unpack contract; the production GT32 candidate deposits c/f/hinv
	 * directly into private BM SoA e=0, then performs B3 e=-1 -> I1/T9
	 * coefficient order e=0 -> crepmod3.
	 * Official Main rejects non-canonical ciphertext or secret-key encodings
	 * before arithmetic and clears the shared secret.
	 */
	if (recover(buf1, &scratch, ct, sk) != 0) {
		secure_clear(ss, NTRUPLUS_SSBYTES);
		goto cleanup;
	}

	hash_g(buf2, buf1);
	fail = poly_sotp_decode(msg, (const poly *)(const void *)scratch.m, buf2);

	memcpy(msg + NTRUPLUS_N / 8,
		sk + 2 * NTRUPLUS_POLYBYTES, NTRUPLUS_SYMBYTES);
	hash_h(buf3, msg);

	poly_cbd1((poly *)(void *)scratch.aux, buf3 + NTRUPLUS_SSBYTES);
	encode_check(buf2, &scratch);
	fail |= verify_bytes(buf1, buf2, NTRUPLUS_POLYBYTES);

	for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
		ss[i] = (uint8_t)(buf3[i] & (uint8_t)~(uint8_t)(-fail));

cleanup:
	secure_clear(msg, sizeof msg);
	secure_clear(buf1, sizeof buf1);
	secure_clear(buf2, sizeof buf2);
	secure_clear(buf3, sizeof buf3);
	secure_clear(&scratch, sizeof scratch);
	return fail;
}

/* G1 control: retain the old noinline generic core and indirect dispatch. */
static __attribute__((noinline)) int crypto_kem_dec_gt32_core_indirect(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES], recover_fn recover,
	check_encode_fn encode_check)
{
	return crypto_kem_dec_gt32_core(ss, ct, sk, recover, encode_check, 0);
}

static __attribute__((always_inline)) inline int
crypto_kem_dec_gt32_sidecar_core(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t buf1[NTRUPLUS_POLYBYTES];
	uint8_t buf2[NTRUPLUS_POLYBYTES];
	uint8_t buf3[NTRUPLUS_POLYBYTES + NTRUPLUS_SYMBYTES];
	gt32_decap_scratch_t scratch;
	/* buf3 is dead until hash_h overwrites it after SOTP decode. */
	gt32_sotp_sidecar_t *const sidecar =
		(gt32_sotp_sidecar_t *)(void *)buf3;
	int fail = 1;

	if (recover_message_and_r_soa_domain_q24_sidecar(buf1, &scratch,
		sidecar, ct, sk) != 0) {
		secure_clear(ss, NTRUPLUS_SSBYTES);
		goto cleanup;
	}

	hash_g(buf2, buf1);
	fail = gt32_sotp_decode_sidecar(msg, sidecar, buf2);

	memcpy(msg + NTRUPLUS_N / 8,
		sk + 2 * NTRUPLUS_POLYBYTES, NTRUPLUS_SYMBYTES);
	hash_h(buf3, msg);

	poly_cbd1((poly *)(void *)scratch.aux, buf3 + NTRUPLUS_SSBYTES);
	encode_check_q24_lazy10788(buf2, &scratch);
	fail |= verify_bytes(buf1, buf2, NTRUPLUS_POLYBYTES);

	for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
		ss[i] = (uint8_t)(buf3[i] & (uint8_t)~(uint8_t)(-fail));

cleanup:
	secure_clear(msg, sizeof msg);
	secure_clear(buf1, sizeof buf1);
	secure_clear(buf2, sizeof buf2);
	secure_clear(buf3, sizeof buf3);
	secure_clear(&scratch, sizeof scratch);
	return fail;
}

int crypto_kem_dec_gt32_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	/*
	 * Keep the statistically qualified lazy10788 GT-pack implementation as an
	 * independent body.  If GCC folds that body into this earlier public
	 * selector, the promotion itself changes the measured code placement.
	 */
	return crypto_kem_dec_gt32_q24_lazy_pack_candidate(ss, ct, sk);
}

int crypto_kem_dec_gt32_soa_domain_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	return crypto_kem_dec_gt32_core_indirect(ss, ct, sk,
		recover_message_and_r_soa_domain, encode_check_soa_bridge);
}

int crypto_kem_dec_gt32_q24_decode_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	/* Decode-only control: Q24 GT-unpack with the former pack bridge. */
	return crypto_kem_dec_gt32_core(ss, ct, sk,
		recover_message_and_r_soa_domain_q24_unpack_only,
		encode_check_soa_bridge, 0);
}

__attribute__((noipa))
int crypto_kem_dec_gt32_q24_pack_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	/* Production output boundary: centered private SoA -> Q24 GT-pack. */
	return crypto_kem_dec_gt32_core(ss, ct, sk,
		recover_message_and_r_soa_domain_q24, encode_check_soa_bridge, 0);
}

__attribute__((noipa))
int crypto_kem_dec_gt32_q24_lazy_pack_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	/* Qualified final-check boundary: only N5-lazy Encodeq changes. */
	return crypto_kem_dec_gt32_core(ss, ct, sk,
		recover_message_and_r_soa_domain_q24,
		encode_check_q24_lazy10788, 0);
}

#if defined(GT32_GLOBAL_PHYSICAL_KEM)
__attribute__((noipa))
int crypto_kem_dec_gt32_global_inverse_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	return crypto_kem_dec_gt32_core(ss, ct, sk,
		recover_message_and_r_q24_global_inverse,
		encode_check_q24_lazy10788, 0);
}

__attribute__((noipa, aligned(GT32_NATIVE_RCHECK_ALIGN)))
int crypto_kem_dec_gt32_native_rcheck_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t buf1[NTRUPLUS_POLYBYTES];
	uint8_t buf2[NTRUPLUS_N / 4];
	uint8_t buf3[NTRUPLUS_POLYBYTES + NTRUPLUS_SYMBYTES];
	gt32_decap_scratch_t scratch;
	int fail = 1;

	if (recover_message_and_r_q24_global_inverse(buf1, &scratch, ct, sk)
		!= 0) {
		secure_clear(ss, NTRUPLUS_SSBYTES);
		goto cleanup;
	}
	hash_g(buf2, buf1);
	fail = poly_sotp_decode(msg,
		(const poly *)(const void *)scratch.m, buf2);
	memcpy(msg + NTRUPLUS_N / 8,
		sk + 2 * NTRUPLUS_POLYBYTES, NTRUPLUS_SYMBYTES);
	hash_h(buf3, msg);

	poly_cbd1((poly *)(void *)scratch.m, buf3 + NTRUPLUS_SSBYTES);
	gt32_tile4_frontend_wide_raw_asm(scratch.work, scratch.m);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch.hinv, scratch.work);
	fail |= gt32_tile4_soa_equal_modq_12699_asm(scratch.aux,
		scratch.hinv);
	for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
		ss[i] = (uint8_t)(buf3[i] & (uint8_t)~(uint8_t)(-fail));

cleanup:
	secure_clear(msg, sizeof msg);
	secure_clear(buf1, sizeof buf1);
	secure_clear(buf2, sizeof buf2);
	secure_clear(buf3, sizeof buf3);
	secure_clear(&scratch, sizeof scratch);
	return fail;
}
#endif

__attribute__((noipa))
int crypto_kem_dec_gt32_q24_sidecar_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	/* Benchmark control: full m/N5 stay unchanged; SOTP consumes the tap. */
	return crypto_kem_dec_gt32_sidecar_core(ss, ct, sk);
}

int crypto_kem_dec_gt32_soa_domain_zeroinit_control(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	return crypto_kem_dec_gt32_core(ss, ct, sk,
		recover_message_and_r_soa_domain, encode_check_soa_bridge, 1);
}

int crypto_kem_dec_gt32_soa_domain_direct_control(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	return crypto_kem_dec_gt32_core(ss, ct, sk,
		recover_message_and_r_soa_domain, encode_check_soa_bridge, 0);
}
