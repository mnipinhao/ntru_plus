#include <stdint.h>
#include "tail_map.h"

#define Q 3457
#define BARRETT_RECIP 621199

/*
 * NTRU+1152 invntt16 tail, in C.
 *
 * NTRU+864's assembly version cannot be carried over by remapping immediates:
 * it is called once and covers every component, so its output count grows with
 * the component count, from 96 to 128.  G6a established that; G6b's decision
 * (D8) is to write it in C for Milestone 1 with assembly still the target.
 *
 * The kernel is three copies of one 2-banks x 16-t -> 32-outputs map at 864,
 * and four copies of the same map at 1152.  tail_map.h holds that map, measured
 * from the 864 kernel rather than read out of 1205 lines of solver output.
 *
 * Signature matches the assembly it replaces so the driver calls it unchanged;
 * the table pointers are unused because the map is compiled in.
 *
 * Cost: 4096 multiply-accumulates against 589 assembly instructions.  Correct
 * and directly derived from the validated kernel, which is what Milestone 1
 * needs, but materially slower.
 */
void invntt16_tail_asm(int16_t *out, const int16_t *scratch, long unused_z,
                       const int16_t *unused_stage, const int16_t *unused_terminal)
{
    (void)unused_z;
    (void)unused_stage;
    (void)unused_terminal;

    for (int branch = 0; branch < 4; branch++) {
        for (int k = 0; k < TAIL_OUTPUTS; k++) {
            int32_t acc = 0;

            for (int top = 0; top < 2; top++)
                for (int t = 0; t < 16; t++)
                    acc += (int32_t)tail_map[top][t][k]
                         * (int32_t)scratch[8 * t + top * 4 + branch];

            /* Branch-free Barrett, the same reciprocal G4 re-proved for
             * degree 4: |out| <= 3024, inside the consumer's contract. */
            int32_t qhat = (int32_t)(((int64_t)acc * BARRETT_RECIP + (1 << 30)) >> 31);
            out[4 * TAIL_M_STRIDE * k + branch] = (int16_t)(acc - qhat * Q);
        }
    }
}
