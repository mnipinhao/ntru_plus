#include "d4_aos_f32x3_ref.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum {
    D4AOS_LANES = 768,
    CT_RANDOM_CASES = 10000
};

typedef struct {
    uint64_t before[4];
    d4aos_f32x3_state state;
    uint64_t after[4];
} guarded_state __attribute__((aligned(32)));

static uint32_t random_state = 1;

static uint32_t deterministic_random(void)
{
    random_state = 1664525U * random_state + 1013904223U;
    return random_state;
}

static void set_canaries(guarded_state *guarded)
{
    for (int index = 0; index < 4; ++index) {
        guarded->before[index] = UINT64_C(0x8e9274b16d35ca40) ^ (uint64_t)index;
        guarded->after[index] = UINT64_C(0x47d1ac639b8025fe) ^ (uint64_t)index;
    }
}

static int canaries_are_valid(const guarded_state *guarded)
{
    for (int index = 0; index < 4; ++index) {
        if (guarded->before[index] !=
                (UINT64_C(0x8e9274b16d35ca40) ^ (uint64_t)index) ||
            guarded->after[index] !=
                (UINT64_C(0x47d1ac639b8025fe) ^ (uint64_t)index)) {
            return 0;
        }
    }

    return 1;
}

static int compare_state(
    const d4aos_f32x3_state *expected,
    const d4aos_f32x3_state *actual,
    const char *layer,
    const char *kind,
    int test_id)
{
    for (int lane = 0; lane < D4AOS_LANES; ++lane) {
        if (actual->lane[lane] != expected->lane[lane]) {
            const int vector = lane / 16;
            const int physical_lane = lane % 16;
            const int row = vector / 16;
            const int block = vector % 16;
            const int branch = physical_lane / 8;
            const int packed_u = (physical_lane % 8) / 4;
            const int coefficient = physical_lane % 4;

            fprintf(stderr,
                "%s mismatch kind=%s test=%d row=%d block=%d lane=%d "
                "branch=%d u=%d coefficient=%d expected=%d actual=%d\n",
                layer, kind, test_id, row, block, physical_lane, branch,
                packed_u, coefficient, expected->lane[lane], actual->lane[lane]);
            return 0;
        }
    }

    return 1;
}

static int check_case(const d4aos_f32x3_state *input, const char *kind, int test_id)
{
    d4aos_f32x3_state checkpoint_l0;
    d4aos_f32x3_state checkpoint_l1;
    d4aos_f32x3_state checkpoint_l2;
    d4aos_f32x3_state checkpoint_l3;
    d4aos_f32x3_state checkpoint_l4;
    guarded_state actual_l0;
    guarded_state actual_l1;
    guarded_state actual_l2;
    guarded_state release_l2;

    set_canaries(&actual_l0);
    set_canaries(&actual_l1);
    set_canaries(&actual_l2);
    set_canaries(&release_l2);
    memset(&actual_l0.state, 0xa5, sizeof(actual_l0.state));
    memset(&actual_l1.state, 0xa5, sizeof(actual_l1.state));
    memset(&actual_l2.state, 0xa5, sizeof(actual_l2.state));
    memset(&release_l2.state, 0xa5, sizeof(release_l2.state));
    d4aos_f32x3_ref_inverse_ntt32_checkpoints(
        &checkpoint_l0, &checkpoint_l1, &checkpoint_l2,
        &checkpoint_l3, &checkpoint_l4, input);
    gt_d4aos_f32x3_invntt32_ct_l0_l2_checkpoints_asm(
        &actual_l0.state, &actual_l1.state, &actual_l2.state, input);
    gt_d4aos_f32x3_invntt32_ct_merged_l0_l2_asm(&release_l2.state, input);

    if (!canaries_are_valid(&actual_l0) || !canaries_are_valid(&actual_l1) ||
        !canaries_are_valid(&actual_l2) || !canaries_are_valid(&release_l2)) {
        fprintf(stderr, "canary mismatch kind=%s test=%d\n", kind, test_id);
        return 0;
    }

    return compare_state(&checkpoint_l0, &actual_l0.state, "L0", kind, test_id) &&
        compare_state(&checkpoint_l1, &actual_l1.state, "L1", kind, test_id) &&
        compare_state(&checkpoint_l2, &actual_l2.state, "L2", kind, test_id) &&
        compare_state(&checkpoint_l2, &release_l2.state, "release-L2", kind, test_id);
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

        for (int lane = 0; lane < D4AOS_LANES; ++lane) {
            input.lane[lane] = value;
        }
        if (!check_case(&input, "boundary", boundary)) {
            return 1;
        }
    }

    for (int basis = 0; basis < D4AOS_LANES; ++basis) {
        memset(&input, 0, sizeof(input));
        input.lane[basis] = 1;
        if (!check_case(&input, "basis", basis)) {
            return 1;
        }
    }

    for (int test_id = 0; test_id < CT_RANDOM_CASES; ++test_id) {
        for (int lane = 0; lane < D4AOS_LANES; ++lane) {
            input.lane[lane] = (int16_t)(deterministic_random() % D4AOS_Q);
        }
        if (!check_case(&input, "random", test_id)) {
            return 1;
        }
    }

    puts("f32x3-ct-merged-l0-l2-asm=passed checkpoints=L0,L1,L2 "
         "basis=768 random=10000 canaries=passed");
    return 0;
}
