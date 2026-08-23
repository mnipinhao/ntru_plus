#include "gate_068.h"

#include "internal.h"
#include "poly.h"

void gt32_032_b3_addm_normal(int16_t *, const int16_t *, const int16_t *,
	const int16_t *);
void gt32_032_b3_addm_reversed(int16_t *, const int16_t *, const int16_t *,
	const int16_t *);
void gt32_068_b3_pack_normal(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *);
void gt32_068_b3_pack_reversed(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *);
void gt32_068_b3_pack_inline_normal(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *);
void gt32_068_b3_pack_inline_reversed(uint8_t *, const int16_t *, const int16_t *,
	const int16_t *);

static void control(uint8_t *out, const int16_t *a, const int16_t *b,
	const int16_t *m, int16_t *scratch)
{
	ntruplus768_basemul_general_m_avx2(scratch, a, b);
	poly_add((poly *)(void *)scratch, (const poly *)(const void *)scratch,
		(const poly *)(const void *)m);
	ntruplus768_pack_m_highrange12699_avx2(out, scratch);
}

void gt32_068_control_normal(uint8_t *out, const int16_t *a,
	const int16_t *b, const int16_t *m, int16_t *scratch)
{
	control(out, a, b, m, scratch);
}

void gt32_068_reference_normal(uint8_t *out, const int16_t *a,
	const int16_t *b, const int16_t *m, int16_t *scratch)
{
	gt32_032_b3_addm_normal(scratch, a, b, m);
	ntruplus768_pack_m_highrange12699_avx2(out, scratch);
}

void gt32_068_candidate_normal(uint8_t *out, const int16_t *a,
	const int16_t *b, const int16_t *m, int16_t *scratch)
{
	(void)scratch;
	gt32_068_b3_pack_normal(out, a, b, m);
}

void gt32_068_inline_normal(uint8_t *out, const int16_t *a,
	const int16_t *b, const int16_t *m, int16_t *scratch)
{
	(void)scratch;
	gt32_068_b3_pack_inline_normal(out, a, b, m);
}

void gt32_068_candidate_reversed(uint8_t *out, const int16_t *a,
	const int16_t *b, const int16_t *m, int16_t *scratch)
{
	(void)scratch;
	gt32_068_b3_pack_reversed(out, a, b, m);
}

void gt32_068_inline_reversed(uint8_t *out, const int16_t *a,
	const int16_t *b, const int16_t *m, int16_t *scratch)
{
	(void)scratch;
	gt32_068_b3_pack_inline_reversed(out, a, b, m);
}

void gt32_068_reference_reversed(uint8_t *out, const int16_t *a,
	const int16_t *b, const int16_t *m, int16_t *scratch)
{
	gt32_032_b3_addm_reversed(scratch, a, b, m);
	ntruplus768_pack_m_highrange12699_avx2(out, scratch);
}

void gt32_068_control_reversed(uint8_t *out, const int16_t *a,
	const int16_t *b, const int16_t *m, int16_t *scratch)
{
	control(out, a, b, m, scratch);
}
