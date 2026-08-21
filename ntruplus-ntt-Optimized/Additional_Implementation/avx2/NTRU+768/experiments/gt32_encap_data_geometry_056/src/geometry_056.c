#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "cpucycles.h"
#include "geometry_056.h"
#include "internal.h"
#include "poly.h"
#include "symmetric.h"
#include "util.h"

enum role { ROLE_H, ROLE_R, ROLE_M, ROLE_C, ROLE_WORK, ROLE_COUNT };

typedef struct __attribute__((aligned(64))) {
	int16_t slot[5][NTRUPLUS_N];
} geometry_scratch;

typedef struct {
	int16_t *role[ROLE_COUNT];
} geometry_roles;

static const uint8_t placements[GEOMETRY_056_PROFILES][ROLE_COUNT] = {
	/* Current production: h, r, m, c, work. */
	{ 0, 1, 2, 3, 4 },
	/* Same frame and traffic; only c and work exchange slots. */
	{ 0, 1, 2, 4, 3 },
	/* Preserve cyclic role spacing while changing page-relative offsets. */
	{ 1, 2, 3, 4, 0 },
};

static volatile uint64_t geometry_sink;

static geometry_roles bind_roles(geometry_scratch *scratch,
	enum geometry_056_profile profile)
{
	geometry_roles result;
	for (size_t role = 0; role < ROLE_COUNT; role++)
		result.role[role] = scratch->slot[placements[profile][role]];
	return result;
}

static void forward_m(int16_t out[NTRUPLUS_N],
	int16_t frontend[NTRUPLUS_N], const int16_t in[NTRUPLUS_N])
{
	ntruplus768_ntt_frontend_avx2(frontend, in);
	ntruplus768_ntt_m_avx2(out, frontend);
}

static int common_prefix(geometry_roles roles, uint8_t msg[HASH_H_INBYTES],
	uint8_t hashbuf[HASH_H_OUTBYTES],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	if (ntruplus768_unpack_m_avx2(roles.role[ROLE_H], pk) != 0)
		return 1;
	memcpy(msg, coins, NTRUPLUS_N / 8);
	hash_f(msg + NTRUPLUS_N / 8, pk);
	hash_h(hashbuf, msg);
	return 0;
}

static void prepare_b3(geometry_roles roles, uint8_t msg[HASH_H_INBYTES],
	uint8_t hashbuf[HASH_H_OUTBYTES], uint8_t encoded[NTRUPLUS_POLYBYTES])
{
	poly_cbd1((poly *)(void *)roles.role[ROLE_WORK],
		hashbuf + NTRUPLUS_SYMBYTES);
	forward_m(roles.role[ROLE_R], roles.role[ROLE_C],
		roles.role[ROLE_WORK]);
	ntruplus768_pack_m_lazy10788_avx2(encoded, roles.role[ROLE_R]);
	hash_g(encoded, encoded);
	poly_sotp_encode((poly *)(void *)roles.role[ROLE_WORK], msg, encoded);
	forward_m(roles.role[ROLE_M], roles.role[ROLE_C],
		roles.role[ROLE_WORK]);
}

int geometry_056_encap(enum geometry_056_profile profile,
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES], uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t hashbuf[HASH_H_OUTBYTES];
	geometry_scratch scratch;
	geometry_roles roles;

	if ((unsigned)profile >= GEOMETRY_056_PROFILES)
		return 1;
	roles = bind_roles(&scratch, profile);
	if (common_prefix(roles, msg, hashbuf, pk, coins) != 0) {
		memset(ct, 0, NTRUPLUS_CIPHERTEXTBYTES);
		secure_clear(ss, NTRUPLUS_SSBYTES);
		return 1;
	}
	prepare_b3(roles, msg, hashbuf, ct);
	ntruplus768_basemul_general_m_avx2(roles.role[ROLE_C],
		roles.role[ROLE_H], roles.role[ROLE_R]);
	poly_add((poly *)(void *)roles.role[ROLE_C],
		(const poly *)(const void *)roles.role[ROLE_C],
		(const poly *)(const void *)roles.role[ROLE_M]);
	ntruplus768_pack_m_highrange12699_avx2(ct, roles.role[ROLE_C]);
	memcpy(ss, hashbuf, NTRUPLUS_SSBYTES);
	secure_clear(msg, sizeof msg);
	secure_clear(hashbuf, sizeof hashbuf);
	secure_clear(roles.role[ROLE_R], NTRUPLUS_N * sizeof(int16_t));
	secure_clear(roles.role[ROLE_M], NTRUPLUS_N * sizeof(int16_t));
	return 0;
}

long long geometry_056_measure_region(enum geometry_056_profile profile,
	enum geometry_056_region region,
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t hashbuf[HASH_H_OUTBYTES];
	uint8_t encoded[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
	geometry_scratch scratch;
	geometry_roles roles;
	long long start, end;

	if ((unsigned)profile >= GEOMETRY_056_PROFILES
		|| (unsigned)region >= GEOMETRY_056_REGIONS)
		return -1;
	roles = bind_roles(&scratch, profile);
	if (common_prefix(roles, msg, hashbuf, pk, coins) != 0)
		return -1;

	if (region == GEOMETRY_056_CBD) {
		start = cpucycles();
		poly_cbd1((poly *)(void *)roles.role[ROLE_WORK],
			hashbuf + NTRUPLUS_SYMBYTES);
		end = cpucycles();
		geometry_sink ^= (uint16_t)roles.role[ROLE_WORK][0];
		return end - start;
	}
	if (region == GEOMETRY_056_R_PRODUCER) {
		start = cpucycles();
		poly_cbd1((poly *)(void *)roles.role[ROLE_WORK],
			hashbuf + NTRUPLUS_SYMBYTES);
		forward_m(roles.role[ROLE_R], roles.role[ROLE_C],
			roles.role[ROLE_WORK]);
		end = cpucycles();
		geometry_sink ^= (uint16_t)roles.role[ROLE_R][0];
		return end - start;
	}
	prepare_b3(roles, msg, hashbuf, encoded);
	start = cpucycles();
	ntruplus768_basemul_general_m_avx2(roles.role[ROLE_C],
		roles.role[ROLE_H], roles.role[ROLE_R]);
	end = cpucycles();
	geometry_sink ^= (uint16_t)roles.role[ROLE_C][0];
	return end - start;
}
