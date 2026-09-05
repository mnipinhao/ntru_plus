#include "gt864_fr0_basemul.h"
#include "gt864_fr0_basemul_d1.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define N 864
#define Q 3457
#define BOUND 25569

static uint32_t random_state = 0xd100864u;
static int mismatches;
static int alias_mismatches;
static int maximum_abs;

static int centered(int value)
{
    value %= Q;
    if (value < 0)
        value += Q;
    if (value > Q / 2)
        value -= Q;
    return value;
}

static int16_t random_bound(void)
{
    random_state = random_state * 1664525u + 1013904223u;
    return (int16_t)((random_state % (2U * BOUND + 1U)) - BOUND);
}

static void compare_modq(const int16_t got[N], const int16_t expected[N],
                         const char *label, int *counter)
{
    for (int i = 0; i < N; i++) {
        int actual = got[i] < 0 ? -got[i] : got[i];
        if (actual > maximum_abs)
            maximum_abs = actual;
        if (centered(got[i]) != centered(expected[i])) {
            if (*counter < 8)
                fprintf(stderr, "%s mismatch i=%d got=%d expected=%d\n",
                        label, i, got[i], expected[i]);
            (*counter)++;
        }
    }
}

static void check_case(const int16_t a[N], const int16_t b[N],
                       const int16_t c[N], const char *label)
{
    int16_t baseline[N], candidate[N], alias[N];

    gt864_fr0_basemul_neon(baseline, a, b);
    gt864_fr0_basemul_d1_neon(candidate, a, b);
    compare_modq(candidate, baseline, label, &mismatches);

    memcpy(alias, a, sizeof(alias));
    gt864_fr0_basemul_d1_neon(alias, alias, b);
    compare_modq(alias, candidate, "alias-a", &alias_mismatches);
    memcpy(alias, b, sizeof(alias));
    gt864_fr0_basemul_d1_neon(alias, a, alias);
    compare_modq(alias, candidate, "alias-b", &alias_mismatches);

    gt864_fr0_basemul_add_neon(baseline, a, b, c);
    gt864_fr0_basemul_add_d1_neon(candidate, a, b, c);
    compare_modq(candidate, baseline, label, &mismatches);

    memcpy(alias, a, sizeof(alias));
    gt864_fr0_basemul_add_d1_neon(alias, alias, b, c);
    compare_modq(alias, candidate, "alias-add-a", &alias_mismatches);
    memcpy(alias, b, sizeof(alias));
    gt864_fr0_basemul_add_d1_neon(alias, a, alias, c);
    compare_modq(alias, candidate, "alias-add-b", &alias_mismatches);
    memcpy(alias, c, sizeof(alias));
    gt864_fr0_basemul_add_d1_neon(alias, a, b, alias);
    compare_modq(alias, candidate, "alias-add-c", &alias_mismatches);
}

int main(void)
{
    int16_t a[N], b[N], c[N];
    static const int16_t values[] = {-BOUND, BOUND, -1728, 1728, 0, 1, -1};
    int cases = 0;

    for (size_t k = 0; k < sizeof(values) / sizeof(values[0]); k++) {
        for (int i = 0; i < N; i++) {
            a[i] = values[k];
            b[i] = values[(k + 2) % 7];
            c[i] = values[(k + 4) % 7];
        }
        check_case(a, b, c, "boundary");
        cases++;
    }
    for (int trial = 0; trial < 64; trial++) {
        for (int i = 0; i < N; i++) {
            a[i] = random_bound();
            b[i] = random_bound();
            c[i] = random_bound();
        }
        check_case(a, b, c, "random");
        cases++;
    }

    printf("gt864_fr0_basemul_d1_gate=%s\n",
           mismatches + alias_mismatches == 0 ? "pass" : "fail");
    printf("cases=%d\n", cases);
    printf("mod_q_mismatches=%d\n", mismatches);
    printf("alias_mismatches=%d\n", alias_mismatches);
    printf("observed_maximum_abs=%d\n", maximum_abs);
    return mismatches + alias_mismatches != 0;
}
