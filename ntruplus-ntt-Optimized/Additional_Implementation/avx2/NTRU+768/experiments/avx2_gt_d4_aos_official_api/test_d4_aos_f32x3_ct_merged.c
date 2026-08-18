#include "d4_aos_f32x3_ref.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum { CT_LANES = 768, CT_RANDOM_CASES = 10000 };

typedef struct {
    uint64_t before[4];
    d4aos_f32x3_state state;
    uint64_t after[4];
} guarded_state __attribute__((aligned(32)));

static uint32_t random_word = 7;

static uint32_t next_random(void)
{
    random_word = 1664525U * random_word + 1013904223U;
    return random_word;
}

static void initialize_guard(guarded_state *guarded)
{
    for (int index = 0; index < 4; ++index) {
        guarded->before[index] = UINT64_C(0x91ac72ef340d865b) ^ (uint64_t)index;
        guarded->after[index] = UINT64_C(0x2f68bd095ec147a3) ^ (uint64_t)index;
    }
}

static int guard_is_valid(const guarded_state *guarded)
{
    for (int index = 0; index < 4; ++index) {
        if (guarded->before[index] !=
                (UINT64_C(0x91ac72ef340d865b) ^ (uint64_t)index) ||
            guarded->after[index] !=
                (UINT64_C(0x2f68bd095ec147a3) ^ (uint64_t)index)) {
            return 0;
        }
    }
    return 1;
}

static int compare_checkpoint(
    const d4aos_f32x3_state *expected,
    const d4aos_f32x3_state *actual,
    const char *layer,
    const char *kind,
    int test_id)
{
    for (int index = 0; index < CT_LANES; ++index) {
        if (expected->lane[index] != actual->lane[index]) {
            const int vector = index / 16;
            const int lane = index % 16;
            const int row = vector / 16;
            const int block = vector % 16;
            const int branch = lane / 8;
            const int packed_u = lane % 8 / 4;
            const int coefficient = lane % 4;
            const int tile = block & 3;
            const int exponent = layer[1] == '3' ? 4 * tile + 2 * packed_u :
                2 * tile + packed_u + ((block & 4) != 0 ? 8 : 0);

            fprintf(stderr,
                "%s mismatch kind=%s test=%d row=%d block=%d lane=%d branch=%d "
                "u=%d coefficient=%d expected=%d actual=%d exponent=%d "
                "metadata=f32x3_ct_l3_l4_tables.json\n",
                layer, kind, test_id, row, block, lane, branch, packed_u,
                coefficient, expected->lane[index], actual->lane[index], exponent);
            return 0;
        }
    }
    return 1;
}

static int check_case(const d4aos_f32x3_state *input, const char *kind, int test_id)
{
    d4aos_f32x3_state scalar_l0;
    d4aos_f32x3_state scalar_l1;
    d4aos_f32x3_state scalar_l2;
    d4aos_f32x3_state scalar_l3;
    d4aos_f32x3_state scalar_l4;
    d4aos_f32x3_state assembly_l2;
    d4aos_f32x3_state assembly_l3;
    d4aos_f32x3_state assembly_l4;
    d4aos_f32x3_state release_l4;
    guarded_state complete;
    guarded_state yang;
    guarded_state yang_compact;

    initialize_guard(&complete);
    initialize_guard(&yang);
    initialize_guard(&yang_compact);
    d4aos_f32x3_ref_inverse_ntt32_checkpoints(
        &scalar_l0, &scalar_l1, &scalar_l2, &scalar_l3, &scalar_l4, input);
    gt_d4aos_f32x3_invntt32_ct_merged_l0_l2_asm(&assembly_l2, input);
    gt_d4aos_f32x3_invntt32_ct_l3_l4_checkpoints_asm(
        &assembly_l3, &assembly_l4, &assembly_l2);
    gt_d4aos_f32x3_invntt32_ct_merged_l3_l4_asm(&release_l4, &assembly_l2);
    gt_d4aos_f32x3_invntt32_ct_merged_asm(&complete.state, input);
    gt_d4aos_f32x3_invntt32_ct_merged_yang_asm(&yang.state, input);
    gt_d4aos_f32x3_invntt32_ct_merged_yang_compact_asm(
        &yang_compact.state, input);

    return guard_is_valid(&complete) && guard_is_valid(&yang) &&
        guard_is_valid(&yang_compact) &&
        compare_checkpoint(&scalar_l2, &assembly_l2, "L2", kind, test_id) &&
        compare_checkpoint(&scalar_l3, &assembly_l3, "L3", kind, test_id) &&
        compare_checkpoint(&scalar_l4, &assembly_l4, "L4", kind, test_id) &&
        compare_checkpoint(&scalar_l4, &release_l4, "release-L4", kind, test_id) &&
        compare_checkpoint(&scalar_l4, &complete.state, "complete-L4", kind, test_id) &&
        compare_checkpoint(&scalar_l4, &yang.state, "yang-L4", kind, test_id) &&
        compare_checkpoint(
            &scalar_l4, &yang_compact.state, "yang-compact-L4", kind, test_id);
}

int main(void)
{
    d4aos_f32x3_state input;

    memset(&input, 0, sizeof(input));
    if (!check_case(&input, "zero", 0)) {
        return 1;
    }

    for (int boundary = 0; boundary < 3; ++boundary) {
        const int16_t value = (int16_t)(boundary == 0 ? 0 :
            (boundary == 1 ? 1 : D4AOS_Q - 1));
        for (int lane = 0; lane < CT_LANES; ++lane) {
            input.lane[lane] = value;
        }
        if (!check_case(&input, "boundary", boundary)) {
            return 1;
        }
    }

    for (int basis = 0; basis < CT_LANES; ++basis) {
        memset(&input, 0, sizeof(input));
        input.lane[basis] = 1;
        if (!check_case(&input, "basis-monomial", basis)) {
            return 1;
        }
    }

    for (int test_id = 0; test_id < CT_RANDOM_CASES; ++test_id) {
        for (int lane = 0; lane < CT_LANES; ++lane) {
            input.lane[lane] = (int16_t)(next_random() % D4AOS_Q);
        }
        if (!check_case(&input, "random", test_id)) {
            return 1;
        }
    }

    puts("f32x3-five-layer-ct=passed Y0=exact Y1=exact Y2=exact L3=exact "
         "L4=exact basis=768 random=10000 boundaries=passed canaries=passed");
    return 0;
}
