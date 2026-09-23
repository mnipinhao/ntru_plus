/*
 * Dynamic instruction count helper for the SCRATCH direct-codec gate
 * (docs/ntruplus768-1152-direct-codec.md).  `count_codec8_scratch V N` calls
 * variant V N times; per-call instructions = (count(V) - count(0)) / N from
 *   taskset -c 1 perf stat -x, -e instructions:u build/count_codec8_scratch V N
 * (read-only perf counting of this process only).  The difference includes the
 * call and switch dispatch (about 3 instructions per call).
 *   0 empty loop  1 Official poly_tobytes  2 freeze2op tobytes  3 scratch pack
 *   4 scratch madd  5 Official poly_frombytes  6 scratch frombytes
 */
#include <stdint.h>
#include <stdlib.h>

#include "params.h"
#include "poly.h"

void FREEZE_TOBYTES(uint8_t *, const poly *);
void codec8_scratch_tobytes_pack(uint8_t *, const poly *);
void codec8_scratch_tobytes_madd(uint8_t *, const poly *);
int codec8_scratch_frombytes(poly *, const uint8_t *);
static volatile int sink;

int main(int argc, char **argv) {
    static poly p;
    static uint8_t b[NTRUPLUS_POLYBYTES];
    if (argc != 3) return 2;
    int v = atoi(argv[1]);
    long n = atol(argv[2]);
    for (unsigned i = 0; i < NTRUPLUS_N; i++) p.coeffs[i] = (int16_t)(i * 7 % NTRUPLUS_Q);
    poly_tobytes(b, &p);
    for (long k = 0; k < n; k++) switch (v) {
        case 0: break;
        case 1: poly_tobytes(b, &p); break;
        case 2: FREEZE_TOBYTES(b, &p); break;
        case 3: codec8_scratch_tobytes_pack(b, &p); break;
        case 4: codec8_scratch_tobytes_madd(b, &p); break;
        case 5: sink = poly_frombytes(&p, b); break;
        case 6: sink = codec8_scratch_frombytes(&p, b); break;
        default: return 2;
    }
    return 0;
}
