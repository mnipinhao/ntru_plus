#include "gt864_friso2_basemul_neon.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define N 864
#define Q 3457
#define B0 26306
#define B12 5185

static uint32_t rng_state = 0x864b51u;
static int mismatches;

static uint32_t random_u32(void)
{
    uint32_t x = rng_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    return rng_state = x;
}

static int canonical(int64_t value)
{
    value %= Q;
    return value < 0 ? (int)(value + Q) : (int)value;
}

static int component_for_index(int index)
{
    return index % 24 / 8;
}

static int z0_for_index(int index)
{
    return index / 432 == 0 ? 9 : 3;
}

static int bounded_random(int bound)
{
    return (int)(random_u32() % (uint32_t)(2 * bound + 1)) - bound;
}

static void scalar_basemul(int16_t out[N], const int16_t a[N],
                           const int16_t b[N], const int16_t *c)
{
    for (int group = 0; group < 36; ++group) {
        int z0 = group < 18 ? 9 : 3;
        for (int lane = 0; lane < 8; ++lane) {
            int base = 24 * group + lane;
            int64_t av[3] = {a[base], a[base + 8], a[base + 16]};
            int64_t bv[3] = {b[base], b[base + 8], b[base + 16]};
            int64_t product[3] = {
                av[0] * bv[0] + z0 * (av[1] * bv[2] + av[2] * bv[1]),
                av[0] * bv[1] + av[1] * bv[0] + z0 * av[2] * bv[2],
                av[0] * bv[2] + av[1] * bv[1] + av[2] * bv[0],
            };
            for (int component = 0; component < 3; ++component) {
                int index = base + 8 * component;
                out[index] = (int16_t)canonical(
                    product[component] + (c == NULL ? 0 : c[index]));
            }
        }
    }
}

static void compare_mod_q(const int16_t got[N], const int16_t want[N],
                          const char *label)
{
    for (int i = 0; i < N; ++i) {
        if (canonical(got[i]) != canonical(want[i])) {
            if (mismatches < 8)
                fprintf(stderr, "%s[%d]: got=%d want=%d\n",
                        label, i, got[i], want[i]);
            ++mismatches;
        }
    }
}

static void fill_case(int16_t a[N], int16_t b[N], int16_t c[N], int kind)
{
    static const int boundary[] = {0, 1, -1, B12 - 1, 1 - B12,
                                   B12, -B12, 1728, -1728};
    for (int i = 0; i < N; ++i) {
        int component = component_for_index(i);
        int bound = component == 0 ? B0 : B12;
        if (kind < (int)(sizeof(boundary) / sizeof(boundary[0]))) {
            int value = boundary[(kind + i + z0_for_index(i)) %
                                 (int)(sizeof(boundary) / sizeof(boundary[0]))];
            if (value > bound) value = bound;
            if (value < -bound) value = -bound;
            a[i] = (int16_t)value;
            b[i] = (int16_t)((i & 1) ? -value : value);
            c[i] = (int16_t)((i % 3 == 0) ? bound : -bound);
        } else {
            a[i] = (int16_t)bounded_random(bound);
            b[i] = (int16_t)bounded_random(bound);
            c[i] = (int16_t)bounded_random(bound);
        }
    }
}

static void run_case(int kind)
{
    int16_t a[N], b[N], c[N], want[N], staged[N], direct[N], alias[N];
    char label[80];
    fill_case(a, b, c, kind);

    scalar_basemul(want, a, b, NULL);
    gt864_friso2_basemul_staged(staged, a, b);
    gt864_friso2_basemul_direct(direct, a, b);
    snprintf(label, sizeof(label), "staged-case-%d", kind);
    compare_mod_q(staged, want, label);
    snprintf(label, sizeof(label), "direct-case-%d", kind);
    compare_mod_q(direct, want, label);
    compare_mod_q(direct, staged, "direct-vs-staged");

    memcpy(alias, a, sizeof(alias));
    gt864_friso2_basemul_direct(alias, alias, b);
    compare_mod_q(alias, want, "direct-out-equals-a");
    memcpy(alias, b, sizeof(alias));
    gt864_friso2_basemul_direct(alias, a, alias);
    compare_mod_q(alias, want, "direct-out-equals-b");

    scalar_basemul(want, a, b, c);
    gt864_friso2_basemul_add_staged(staged, a, b, c);
    gt864_friso2_basemul_add_direct(direct, a, b, c);
    compare_mod_q(staged, want, "staged-add");
    compare_mod_q(direct, want, "direct-add");
    compare_mod_q(direct, staged, "direct-add-vs-staged");
    memcpy(alias, c, sizeof(alias));
    gt864_friso2_basemul_add_direct(alias, a, b, alias);
    compare_mod_q(alias, want, "direct-add-out-equals-c");
    memcpy(alias, a, sizeof(alias));
    gt864_friso2_basemul_add_direct(alias, alias, b, c);
    compare_mod_q(alias, want, "direct-add-out-equals-a");
    memcpy(alias, b, sizeof(alias));
    gt864_friso2_basemul_add_direct(alias, a, alias, c);
    compare_mod_q(alias, want, "direct-add-out-equals-b");
}

int main(void)
{
    for (int kind = 0; kind < 73; ++kind)
        run_case(kind);
    printf("gt864_friso2_basemul_cycle_correctness=%s\n",
           mismatches == 0 ? "pass" : "fail");
    printf("cases=73\n");
    printf("mod_q_mismatches=%d\n", mismatches);
    return mismatches != 0;
}
