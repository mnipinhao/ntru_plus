#include "gt864_montgomery.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

extern const int16_t zetas[GT864_N / GT864_LEAF_DEGREE];
void ntt(int16_t out[GT864_N], const int16_t in[GT864_N]);
void invntt(int16_t out[GT864_N], const int16_t in[GT864_N]);
void basemul(int16_t out[3], const int16_t a[3], const int16_t b[3],
             int16_t zeta);

static uint32_t random_state = 0x8644dU;
static int failures;
static int exact_forward_cases;
static int exact_basemul_cases;
static int inverse_modq_cases;
static int roundtrip_cases;
static int full_product_cases;
static int alias_cases;

static uint32_t next_u32(void)
{
    uint32_t x = random_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    random_state = x;
    return x;
}

static int16_t canonical(int32_t value)
{
    value %= GT864_Q;
    if (value < 0)
        value += GT864_Q;
    return (int16_t)value;
}

static int16_t centered(int32_t value)
{
    int16_t result = canonical(value);
    if (result > GT864_Q / 2)
        result = (int16_t)(result - GT864_Q);
    return result;
}

static void compare_exact(const char *label, int case_id,
                          const int16_t got[GT864_N],
                          const int16_t expected[GT864_N])
{
    for (int i = 0; i < GT864_N; i++) {
        if (got[i] != expected[i]) {
            fprintf(stderr,
                    "mismatch,%s,case=%d,index=%d,got=%d,expected=%d\n",
                    label, case_id, i, got[i], expected[i]);
            failures++;
            return;
        }
    }
}

static void compare_modq(const char *label, int case_id,
                         const int16_t got[GT864_N],
                         const int16_t expected[GT864_N])
{
    for (int i = 0; i < GT864_N; i++) {
        if (canonical(got[i]) != canonical(expected[i])) {
            fprintf(stderr,
                    "mismatch_modq,%s,case=%d,index=%d,got=%d,expected=%d\n",
                    label, case_id, i, got[i], expected[i]);
            failures++;
            return;
        }
    }
}

static void fill_case(int16_t value[GT864_N], int kind)
{
    for (int i = 0; i < GT864_N; i++) {
        switch (kind) {
        case 0:
            value[i] = 0;
            break;
        case 1:
            value[i] = 1;
            break;
        case 2:
            value[i] = (int16_t)(i & 1 ? -1 : 1);
            break;
        case 3:
            value[i] = 1728;
            break;
        case 4:
            value[i] = -1728;
            break;
        default:
            value[i] = centered((int32_t)(next_u32() % GT864_Q));
            break;
        }
    }
}

static void current_basemul_poly(int16_t out[GT864_N],
                                 const int16_t a[GT864_N],
                                 const int16_t b[GT864_N])
{
    for (int pair = 0; pair < GT864_N / 6; pair++) {
        basemul(out + 6 * pair, a + 6 * pair, b + 6 * pair,
                zetas[GT864_N / 6 + pair]);
        basemul(out + 6 * pair + 3, a + 6 * pair + 3, b + 6 * pair + 3,
                (int16_t)-zetas[GT864_N / 6 + pair]);
    }
}

static void check_transform_case(const int16_t input[GT864_N], int case_id)
{
    int16_t grid[GT864_N];
    int16_t legacy[GT864_N];
    int16_t current[GT864_N];
    int16_t inverse_candidate[GT864_N];
    int16_t inverse_current[GT864_N];
    int16_t expected[GT864_N];
    int16_t alias[GT864_N];

    for (int i = 0; i < GT864_N; i++)
        expected[i] = centered(input[i]);

    gt864_mont_forward(grid, input);
    gt864_grid_to_legacy(legacy, grid);
    ntt(current, input);
    compare_exact("current_forward", case_id, legacy, current);
    exact_forward_cases++;

    gt864_mont_inverse(inverse_candidate, grid);
    invntt(inverse_current, legacy);
    compare_modq("current_inverse", case_id, inverse_candidate, inverse_current);
    inverse_modq_cases++;
    compare_exact("roundtrip", case_id, inverse_candidate, expected);
    roundtrip_cases++;

    memcpy(alias, input, sizeof alias);
    gt864_mont_forward(alias, alias);
    compare_exact("forward_alias", case_id, alias, grid);
    gt864_mont_inverse(alias, alias);
    compare_exact("inverse_alias", case_id, alias, expected);
    alias_cases += 2;
}

static void check_product_case(const int16_t a[GT864_N],
                               const int16_t b[GT864_N], int case_id)
{
    int16_t grid_a[GT864_N];
    int16_t grid_b[GT864_N];
    int16_t grid_product[GT864_N];
    int16_t legacy_a[GT864_N];
    int16_t legacy_b[GT864_N];
    int16_t legacy_product[GT864_N];
    int16_t mapped_product[GT864_N];
    int16_t got[GT864_N];
    int16_t scalar[GT864_N];
    int16_t schoolbook[GT864_N];
    int16_t alias[GT864_N];

    gt864_mont_forward(grid_a, a);
    gt864_mont_forward(grid_b, b);
    gt864_mont_basemul(grid_product, grid_a, grid_b);
    gt864_grid_to_legacy(legacy_a, grid_a);
    gt864_grid_to_legacy(legacy_b, grid_b);
    current_basemul_poly(legacy_product, legacy_a, legacy_b);
    gt864_grid_to_legacy(mapped_product, grid_product);
    compare_exact("current_basemul", case_id, mapped_product, legacy_product);
    exact_basemul_cases++;

    gt864_mont_inverse(got, grid_product);
    gt864_mul(scalar, a, b);
    gt864_schoolbook_mul(schoolbook, a, b);
    compare_modq("canonical_gt_product", case_id, got, scalar);
    compare_modq("schoolbook_product", case_id, got, schoolbook);
    full_product_cases++;

    memcpy(alias, a, sizeof alias);
    gt864_mont_mul(alias, alias, b);
    compare_modq("product_alias", case_id, alias, schoolbook);
    alias_cases++;
}

int main(void)
{
    int16_t a[GT864_N];
    int16_t b[GT864_N];
    const int impulses[] = {0, 1, 2, 3, 431, 432, 863};
    int case_id = 0;

    for (int kind = 0; kind < 5; kind++) {
        fill_case(a, kind);
        check_transform_case(a, case_id++);
    }
    for (size_t i = 0; i < sizeof impulses / sizeof impulses[0]; i++) {
        memset(a, 0, sizeof a);
        a[impulses[i]] = 1;
        check_transform_case(a, case_id++);
    }
    for (int i = 0; i < 20; i++) {
        fill_case(a, 5);
        check_transform_case(a, case_id++);
    }

    for (int kind = 0; kind < 5; kind++) {
        fill_case(a, kind);
        fill_case(b, 4 - kind);
        check_product_case(a, b, case_id++);
    }
    for (int i = 0; i < 12; i++) {
        fill_case(a, 5);
        fill_case(b, 5);
        check_product_case(a, b, case_id++);
    }

    printf("gt864_montgomery_reference,total_mismatches=%d\n", failures);
    printf("exact_current_forward_cases=%d\n", exact_forward_cases);
    printf("exact_current_basemul_cases=%d\n", exact_basemul_cases);
    printf("current_inverse_modq_cases=%d\n", inverse_modq_cases);
    printf("centered_roundtrip_cases=%d\n", roundtrip_cases);
    printf("full_product_cases=%d\n", full_product_cases);
    printf("alias_cases=%d\n", alias_cases);
    return failures != 0;
}
