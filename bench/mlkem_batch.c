#include "mlkem_batch.h"

#include <stdlib.h>
#include <string.h>

static int compare_u64(const void *left, const void *right) {
    uint64_t a = *(const uint64_t *)left;
    uint64_t b = *(const uint64_t *)right;
    return (a > b) - (a < b);
}

static int measure(const ntruplus_batch_config *config,
                   ntruplus_batch_counter counter,
                   ntruplus_batch_prepare prepare,
                   ntruplus_batch_operation operation,
                   void *context, unsigned test, uint64_t *total) {
    unsigned j;
    uint64_t start, end;
    prepare(context, test);
    for (j = 0; j < config->warmup; j++) operation(context, j);
    start = counter();
    for (j = 0; j < config->iterations; j++) operation(context, j);
    end = counter();
    if (end < start) return -1;
    *total = end - start;
    return 0;
}

int ntruplus_batch_absolute(const ntruplus_batch_config *config,
                            ntruplus_batch_counter counter,
                            ntruplus_batch_prepare prepare,
                            ntruplus_batch_operation operation,
                            void *context,
                            ntruplus_batch_absolute_result *result) {
    uint64_t sorted[NTRUPLUS_BATCH_MAX_TESTS];
    unsigned test;
    if (!config || !counter || !prepare || !operation || !result ||
        !config->iterations || !config->tests ||
        config->tests > NTRUPLUS_BATCH_MAX_TESTS) return -1;
    memset(result, 0, sizeof(*result));
    for (test = 0; test < config->tests; test++) {
        if (measure(config, counter, prepare, operation, context, test,
                    &result->totals[test])) return -1;
    }
    memcpy(sorted, result->totals, config->tests * sizeof(uint64_t));
    qsort(sorted, config->tests, sizeof(uint64_t), compare_u64);
    result->median_total = sorted[config->tests >> 1];
    result->cycles_per_operation = result->median_total / config->iterations;
    return 0;
}

int ntruplus_batch_pair(const ntruplus_batch_config *config,
                        ntruplus_batch_counter counter,
                        ntruplus_batch_prepare prepare_control,
                        ntruplus_batch_operation run_control,
                        void *control_context,
                        ntruplus_batch_prepare prepare_candidate,
                        ntruplus_batch_operation run_candidate,
                        void *candidate_context,
                        ntruplus_batch_result *result) {
    uint64_t sorted[NTRUPLUS_BATCH_MAX_TESTS];
    unsigned test;
    if (!config || !counter || !prepare_control || !run_control ||
        !prepare_candidate || !run_candidate || !result ||
        !config->iterations || !config->tests ||
        config->tests > NTRUPLUS_BATCH_MAX_TESTS) return -1;
    memset(result, 0, sizeof(*result));
    for (test = 0; test < config->tests; test++) {
        /* AB/BA counterbalances long-term drift without altering the source
         * method's warmup/batch/median estimator for either arm. */
        if ((test & 1U) == 0) {
            if (measure(config, counter, prepare_control, run_control,
                        control_context, test, &result->control_totals[test]) ||
                measure(config, counter, prepare_candidate, run_candidate,
                        candidate_context, test, &result->candidate_totals[test]))
                return -1;
        } else {
            if (measure(config, counter, prepare_candidate, run_candidate,
                        candidate_context, test, &result->candidate_totals[test]) ||
                measure(config, counter, prepare_control, run_control,
                        control_context, test, &result->control_totals[test]))
                return -1;
        }
    }
    memcpy(sorted, result->control_totals, config->tests * sizeof(uint64_t));
    qsort(sorted, config->tests, sizeof(uint64_t), compare_u64);
    result->control_median_total = sorted[config->tests >> 1];
    memcpy(sorted, result->candidate_totals, config->tests * sizeof(uint64_t));
    qsort(sorted, config->tests, sizeof(uint64_t), compare_u64);
    result->candidate_median_total = sorted[config->tests >> 1];
    result->control_cycles_per_operation = result->control_median_total / config->iterations;
    result->candidate_cycles_per_operation = result->candidate_median_total / config->iterations;
    return 0;
}
