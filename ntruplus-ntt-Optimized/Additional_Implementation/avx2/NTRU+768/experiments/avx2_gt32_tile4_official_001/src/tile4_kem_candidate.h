#ifndef NTRUPLUS_GT32_TILE4_KEM_CANDIDATE_H
#define NTRUPLUS_GT32_TILE4_KEM_CANDIDATE_H

#include <stdint.h>

#include "params.h"

/*
 * Opt-in GT32 production candidate.  Q24 GT-unpack maps wire bytes directly
 * to private BM SoA; centered Q24 GT-pack emits recovered-r; and the qualified
 * lazy10788 Q24 GT-pack emits the final reencryption check.  The symbol remains
 * distinct from public crypto_kem_dec until all KEM gates pass.
 */
int crypto_kem_dec_gt32_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

/* Benchmark-only c-persistent-SoA decapsulation candidate. */
int crypto_kem_dec_gt32_soa_domain_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

/* Q24 GT-unpack-only control retaining the former recovered-r pack bridge. */
int crypto_kem_dec_gt32_q24_decode_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

/*
 * Statistically qualified recovered-r Q24 GT-pack implementation.  The
 * independent body is retained as the centered control after the final-check
 * lazy10788 boundary was added to the production candidate.
 */
int crypto_kem_dec_gt32_q24_pack_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

/* Qualified final-check lazy10788 private-SoA Q24 GT-pack body. */
int crypto_kem_dec_gt32_q24_lazy_pack_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

/* Opt-in KEM gate: Q24/B3-M/global-inverse for the first decap product. */
int crypto_kem_dec_gt32_global_inverse_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

int crypto_kem_dec_gt32_native_rcheck_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

/* Benchmark-only crepmod3 sidecar tap with production full-m/N5 semantics. */
int crypto_kem_dec_gt32_q24_sidecar_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

/* Benchmark-only G0 control with the old unnecessary stack-buffer memset. */
int crypto_kem_dec_gt32_soa_domain_zeroinit_control(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

/* Benchmark-only G1 control with a specialized direct-call core. */
int crypto_kem_dec_gt32_soa_domain_direct_control(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

#if defined(GT32_TILE4_KEM_TESTING)
int gt32_tile4_decap_trace_sa_control(
	int16_t m[NTRUPLUS_N],
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);
int gt32_tile4_decap_trace_candidate(
	int16_t m[NTRUPLUS_N],
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);
int gt32_tile4_decap_trace_soa_domain_candidate(
	int16_t m[NTRUPLUS_N],
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);
int gt32_tile4_decap_trace_q24_decode_candidate(
	int16_t m[NTRUPLUS_N],
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);
int gt32_tile4_decap_trace_q24_pack_candidate(
	int16_t m[NTRUPLUS_N],
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);
void gt32_tile4_tobytes_candidate_testing(
	uint8_t out[NTRUPLUS_POLYBYTES], const int16_t in[NTRUPLUS_N]);
#endif

#endif
