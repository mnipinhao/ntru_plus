#ifndef GT32_ENCAP_CONSUMER_ABI_068_H
#define GT32_ENCAP_CONSUMER_ABI_068_H

#include <stdint.h>

typedef void (*gt32_068_fn)(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *, int16_t *);

void gt32_068_control_normal(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *, int16_t *);
void gt32_068_reference_normal(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *, int16_t *);
void gt32_068_candidate_normal(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *, int16_t *);
void gt32_068_inline_normal(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *, int16_t *);
void gt32_068_control_reversed(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *, int16_t *);
void gt32_068_reference_reversed(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *, int16_t *);
void gt32_068_candidate_reversed(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *, int16_t *);
void gt32_068_inline_reversed(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *, int16_t *);

#endif
