#include "mlkem_batch.h"
#include <assert.h>
#include <stdio.h>

static uint64_t fake_clock;
static uint64_t read_clock(void) { return fake_clock; }
struct sample { unsigned calls; unsigned prepare_calls; unsigned weight; };
static void prepare(void *opaque, unsigned test) {
    struct sample *state = opaque;
    state->prepare_calls++;
    state->calls = test;
}
static void operation(void *opaque, unsigned iteration) {
    struct sample *state = opaque;
    state->calls += iteration + 1U;
    fake_clock += state->weight;
}
int main(void) {
    ntruplus_batch_config config = { 2U, 4U, 4U };
    ntruplus_batch_result result;
    struct sample control = { 0U, 0U, 7U }, candidate = { 0U, 0U, 5U };
    assert(ntruplus_batch_pair(&config, read_clock, prepare, operation, &control,
                              prepare, operation, &candidate, &result) == 0);
    assert(control.prepare_calls == candidate.prepare_calls && control.prepare_calls == 4U);
    assert(result.control_median_total == 28U && result.candidate_median_total == 20U);
    assert(result.control_cycles_per_operation == 7U && result.candidate_cycles_per_operation == 5U);
    for (unsigned i = 0; i < config.tests; i++) {
        assert(result.control_totals[i] == 28U && result.candidate_totals[i] == 20U);
    }
    ntruplus_batch_absolute_result absolute;
    assert(ntruplus_batch_absolute(&config, read_clock, prepare, operation,
                                   &control, &absolute) == 0);
    assert(absolute.median_total == 28U && absolute.cycles_per_operation == 7U);
    puts("mlkem-style batch engine test passed");
    return 0;
}
