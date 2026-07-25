#include <stddef.h>
#include <stdint.h>

#include "gt_native_pack.h"

#include "gt_native_pack_tables.inc"

#define GT_PACK_V 19412

static inline uint16_t canonicalize(int16_t value)
{
	int32_t reduced = value;
	const int32_t quotient =
		((int32_t)value * GT_PACK_V) >> 26;

	reduced -= quotient * NTRUPLUS_Q;
	reduced -= NTRUPLUS_Q;
	reduced += (reduced >> 31) & NTRUPLUS_Q;
	return (uint16_t)reduced;
}

uint16_t gt_native_pack_canonicalize_test(int16_t value)
{
	return canonicalize(value);
}

static inline int16_t native_coefficient(const poly *native,
	unsigned production_batch, unsigned coefficient, unsigned lane)
{
	const unsigned production_quartic = 16U * production_batch + lane;
	const unsigned native_quartic =
		gt_production_to_native_quartic[production_quartic];
	const unsigned native_batch = native_quartic >> 4;
	const unsigned native_lane = native_quartic & 15U;

	return native->coeffs[
		64U * native_batch + 16U * coefficient + native_lane];
}

void gt_poly_tobytes_native(uint8_t out[NTRUPLUS_POLYBYTES],
	const poly *native)
{
	uint8_t *destination = out;

	for (unsigned production_group = 0; production_group < 6;
	     production_group++) {
		for (unsigned lane = 0; lane < 16; lane++) {
			for (unsigned sign = 0; sign < 2; sign++) {
				const unsigned production_batch =
					2U * production_group + sign;

				for (unsigned coefficient = 0; coefficient < 4;
				     coefficient += 2) {
					const uint16_t first = canonicalize(
						native_coefficient(native,
							production_batch,
							coefficient, lane));
					const uint16_t second = canonicalize(
						native_coefficient(native,
							production_batch,
							coefficient + 1, lane));

					destination[0] = (uint8_t)first;
					destination[1] = (uint8_t)(
						(first >> 8) | (second << 4));
					destination[2] =
						(uint8_t)(second >> 4);
					destination += 3;
				}
			}
		}
	}
}
