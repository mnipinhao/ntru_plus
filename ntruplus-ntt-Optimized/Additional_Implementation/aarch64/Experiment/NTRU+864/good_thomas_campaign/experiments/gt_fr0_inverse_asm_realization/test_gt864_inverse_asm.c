#include "gt864_fr0_inverse_asm.h"
#include "../gt_fr0_inverse_consumer/gt864_fr0_inverse.h"

#include <stdint.h>
#include <stdio.h>

static uint32_t random_state = 0x5eU;
static int pass1_mismatches;
static int pass2_mismatches;
static int padding_writes;
static int cases;

static void check_case(const int16_t fr0[864], const char *label)
{
    int16_t intrinsic_p8[896] = {0};
    int16_t assembly_p8[896] = {0};
    int16_t intrinsic_out[864];
    int16_t assembly_out[864];

    for (int i = 768; i < 896; i++)
        if (i % 8 >= 6)
            assembly_p8[i] = (int16_t)0x5a5a;

    gt864_fr0_inverse_ntt9_neon(intrinsic_p8, fr0);
    gt864_fr0_inverse_ntt9_asm(assembly_p8, fr0);
    for (int i = 0; i < 896; i++) {
        if (i >= 768 && i % 8 >= 6) {
            if (assembly_p8[i] != (int16_t)0x5a5a)
                padding_writes++;
            continue;
        }
        if (assembly_p8[i] != intrinsic_p8[i]) {
            if (pass1_mismatches < 8)
                fprintf(stderr, "%s pass1 mismatch i=%d asm=%d ref=%d\n",
                        label, i, assembly_p8[i], intrinsic_p8[i]);
            pass1_mismatches++;
        }
    }

    gt864_fr0_inverse_finish_neon(intrinsic_out, intrinsic_p8);
    gt864_fr0_inverse_finish_asm(assembly_out, assembly_p8);
    for (int i = 0; i < 864; i++) {
        if (assembly_out[i] != intrinsic_out[i]) {
            if (pass2_mismatches < 8)
                fprintf(stderr, "%s pass2 mismatch i=%d asm=%d ref=%d\n",
                        label, i, assembly_out[i], intrinsic_out[i]);
            pass2_mismatches++;
        }
    }
    cases++;
}

int main(void)
{
    int16_t fr0[864];
    static const int16_t boundaries[] = {-2168,2168,-1,0,1};

    for (unsigned k = 0; k < sizeof(boundaries) / sizeof(boundaries[0]); k++) {
        for (int i = 0; i < 864; i++)
            fr0[i] = boundaries[k];
        check_case(fr0, "boundary");
    }
    for (int impulse = 0; impulse < 12; impulse++) {
        static const int positions[12] = {
            0,7,8,23,24,431,432,575,576,839,862,863
        };
        for (int i = 0; i < 864; i++)
            fr0[i] = 0;
        fr0[positions[impulse]] = (int16_t)(impulse & 1 ? -2168 : 2168);
        check_case(fr0, "impulse");
    }
    for (int trial = 0; trial < 32; trial++) {
        for (int i = 0; i < 864; i++) {
            random_state = random_state * 1664525u + 1013904223u;
            fr0[i] = (int16_t)((int32_t)(random_state % 4337U) - 2168);
        }
        check_case(fr0, "random");
    }

    printf("gt864_inverse_asm_gate=%s\n",
           pass1_mismatches + pass2_mismatches == 0 ? "pass" : "fail");
    printf("cases=%d\n", cases);
    printf("pass1_exact_mismatches=%d\n", pass1_mismatches);
    printf("pass2_exact_mismatches=%d\n", pass2_mismatches);
    printf("padding_writes=%d\n", padding_writes);
    printf("production_linked=0\n");
    return pass1_mismatches + pass2_mismatches + padding_writes != 0;
}
