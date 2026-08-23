#ifndef GT32_ENCAP_CONSUMER_ABI_069_H
#define GT32_ENCAP_CONSUMER_ABI_069_H

#include "../../gt32_encap_consumer_abi_068/src/gate_068.h"

void gt32_069_cluster2_normal(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *);
void gt32_069_cluster3_normal(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *);
void gt32_069_cluster4_normal(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *);
void gt32_069_cluster6_normal(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *);
void gt32_069_cluster3_reversed(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *);
void gt32_069_cluster4_reversed(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *);

#endif
