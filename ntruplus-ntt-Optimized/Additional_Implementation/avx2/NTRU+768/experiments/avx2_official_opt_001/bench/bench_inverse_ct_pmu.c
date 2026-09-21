/* Isolated, repeated inverse work for external perf-stat diagnosis.
 * This is not a cycle headline: reset and process startup are counted too.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "poly.h"

void ntruplus768_officialopt_invntt_ct_cohort(poly *);
void ntruplus768_officialopt_invntt_ct_wresident(poly *);
void ntruplus768_officialopt_invntt_ct_earlynorm(poly *);

int main(int argc, char **argv) {
    enum { REPEATS = 1000000 };
    void (*run)(poly *) = NULL;
    if (argc != 2) return 2;
    if (!strcmp(argv[1], "cohort")) run = ntruplus768_officialopt_invntt_ct_cohort;
    if (!strcmp(argv[1], "wresident")) run = ntruplus768_officialopt_invntt_ct_wresident;
    if (!strcmp(argv[1], "earlynorm")) run = ntruplus768_officialopt_invntt_ct_earlynorm;
    if (!run) return 2;
    poly input, output;
    for (unsigned i = 0; i < NTRUPLUS_N; i++)
        input.coeffs[i] = (int16_t)((int)((i * 113U + 29U) % 15289U) - 7644);
    volatile uint32_t sink = 0;
    for (unsigned iteration = 0; iteration < REPEATS; iteration++) {
        output = input;
        run(&output);
        sink ^= (uint16_t)output.coeffs[iteration % NTRUPLUS_N];
    }
    printf("variant=%s repeats=%u sink=%u\n", argv[1], REPEATS, sink);
    return 0;
}
