#include "pack_asm.h"
#include "gt_perm.h"

#define Q 3457
#define BARRETT_V 19412        /* ((1<<26) + Q/2) / Q */

/*
 * NTRU+1152 canonical serialization, Good-Thomas layout to the 12-bit wire
 * format.
 *
 * Deliberately not a port of NTRU+864's pack_full/small/compare, which are
 * 7,751 lines and 111 Slothy windows.  Those exist because 864's degree-3
 * leaves are 6 bytes stored and 4.5 bytes packed, so neither aligns and the
 * routing needs ST3 lane stores and TBL.  Degree 4 is 8 bytes stored -- one
 * `d` register -- and 6 whole bytes packed.  Decision D5: start from the
 * simple stock-shaped codec and let G9's profile say whether more is needed.
 *
 * The leaf scatter itself does NOT go away: gt1152-p03-gt-layout measured one
 * GT vector's eight leaves landing at natural starts 0, 64, 128, ..., 448,
 * structurally identical to 864.  Only the granularity improves.  Here the
 * scatter is a plain table lookup.
 */

/* Centered Barrett into {-(q+1)/2 .. (q+1)/2}, branch-free. */
static inline int16_t barrett_reduce(int16_t a)
{
    int16_t t = (int16_t)(((int32_t)BARRETT_V * a + (1 << 25)) >> 26);
    return (int16_t)(a - (int16_t)(t * Q));
}

/* (-q, q) -> [0, q), branch-free. */
static inline uint16_t to_canonical(int16_t a)
{
    return (uint16_t)(a + ((a >> 15) & Q));
}

static inline void emit_pair(uint8_t *out, uint16_t t0, uint16_t t1)
{
    out[0] = (uint8_t)(t0 >> 0);
    out[1] = (uint8_t)((t0 >> 8) | (t1 << 4));
    out[2] = (uint8_t)(t1 >> 4);
}

/*
 * Full accepts every signed int16.  It has to: kem.c calls it on raw forward
 * output, which gt1152-p04-forward-8bank measured at +/-14607.
 */
void tobytes_full_asm(uint8_t out[NTRUPLUS1152_POLYBYTES],
                  const int16_t in[NTRUPLUS1152_N])
{
    for (int i = 0; i < NTRUPLUS1152_N / 2; i++) {
        uint16_t t0 = to_canonical(barrett_reduce(in[gt_of_natural[2 * i]]));
        uint16_t t1 = to_canonical(barrett_reduce(in[gt_of_natural[2 * i + 1]]));
        emit_pair(out + 3 * i, t0, t1);
    }
}

/*
 * Small requires every coefficient strictly inside (-q, q), so it skips the
 * Barrett.  G2/G4 bound basemul and basemul_add at 1764 and 1768, and baseinv
 * at 1781, all comfortably inside.  Never valid on raw forward output.
 */
void tobytes_small_asm(uint8_t out[NTRUPLUS1152_POLYBYTES],
                        const int16_t in[NTRUPLUS1152_N])
{
    for (int i = 0; i < NTRUPLUS1152_N / 2; i++) {
        uint16_t t0 = to_canonical(in[gt_of_natural[2 * i]]);
        uint16_t t1 = to_canonical(in[gt_of_natural[2 * i + 1]]);
        emit_pair(out + 3 * i, t0, t1);
    }
}

/*
 * Constant-time equality against the Full serialization, without materializing
 * it.  No early exit: every byte position is folded into the accumulator.
 */
int tobytes_compare_asm(const uint8_t expected[NTRUPLUS1152_POLYBYTES],
                         const int16_t in[NTRUPLUS1152_N])
{
    uint8_t acc = 0;

    for (int i = 0; i < NTRUPLUS1152_N / 2; i++) {
        uint8_t bytes[3];
        uint16_t t0 = to_canonical(barrett_reduce(in[gt_of_natural[2 * i]]));
        uint16_t t1 = to_canonical(barrett_reduce(in[gt_of_natural[2 * i + 1]]));

        emit_pair(bytes, t0, t1);
        acc |= (uint8_t)(bytes[0] ^ expected[3 * i + 0]);
        acc |= (uint8_t)(bytes[1] ^ expected[3 * i + 1]);
        acc |= (uint8_t)(bytes[2] ^ expected[3 * i + 2]);
    }

    return (int)((-(uint32_t)acc) >> 31);
}

/*
 * Decode without reduction.  Returns 0 iff every decoded value is below q,
 * 1 otherwise.  On failure the output is still fully written and must not be
 * consumed -- this matches NTRU+864's unpack.h contract, and is what lets the
 * caller reject before use without a data-dependent early exit here.
 */
int frombytes_asm(int16_t out[NTRUPLUS1152_N],
                   const uint8_t in[NTRUPLUS1152_POLYBYTES])
{
    uint32_t bad = 0;

    for (int i = 0; i < NTRUPLUS1152_N / 2; i++) {
        uint16_t t0 = (uint16_t)((in[3 * i + 0] | ((uint16_t)in[3 * i + 1] << 8)) & 0xFFF);
        uint16_t t1 = (uint16_t)(((in[3 * i + 1] >> 4) | ((uint16_t)in[3 * i + 2] << 4)) & 0xFFF);

        /* (t - q) stays negative exactly while t < q; fold the sign bit. */
        bad |= (uint32_t)(((int32_t)t0 - Q) >> 31) ^ 1u;
        bad |= (uint32_t)(((int32_t)t1 - Q) >> 31) ^ 1u;

        out[gt_of_natural[2 * i]] = (int16_t)t0;
        out[gt_of_natural[2 * i + 1]] = (int16_t)t1;
    }

    return (int)(bad & 1u);
}
