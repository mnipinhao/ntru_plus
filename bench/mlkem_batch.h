#ifndef NTRUPLUS_MLKEM_BATCH_H
#define NTRUPLUS_MLKEM_BATCH_H

#include <stdint.h>

/* Matches mlkem-native's component-benchmark defaults. */
#define NTRUPLUS_BATCH_WARMUP 50U
#define NTRUPLUS_BATCH_ITERATIONS 300U
#define NTRUPLUS_BATCH_TESTS 20U
#define NTRUPLUS_BATCH_MAX_TESTS 64U

typedef uint64_t (*ntruplus_batch_counter)(void);
typedef void (*ntruplus_batch_prepare)(void *context, unsigned test);
typedef void (*ntruplus_batch_operation)(void *context, unsigned iteration);

typedef struct {
    unsigned warmup;
    unsigned iterations;
    unsigned tests;
} ntruplus_batch_config;

typedef struct {
    uint64_t control_totals[NTRUPLUS_BATCH_MAX_TESTS];
    uint64_t candidate_totals[NTRUPLUS_BATCH_MAX_TESTS];
    uint64_t control_median_total;
    uint64_t candidate_median_total;
    uint64_t control_cycles_per_operation;
    uint64_t candidate_cycles_per_operation;
} ntruplus_batch_result;

typedef struct {
    uint64_t totals[NTRUPLUS_BATCH_MAX_TESTS];
    uint64_t median_total;
    uint64_t cycles_per_operation;
} ntruplus_batch_absolute_result;

int ntruplus_batch_absolute(const ntruplus_batch_config *config,
                            ntruplus_batch_counter counter,
                            ntruplus_batch_prepare prepare,
                            ntruplus_batch_operation operation,
                            void *context,
                            ntruplus_batch_absolute_result *result);

/* Returns zero on success. The caller must preflight operation correctness.
 * A destructive operation must restore its input inside the timed callback;
 * that restoration is then part of the reported operation contract.
 */
int ntruplus_batch_pair(const ntruplus_batch_config *config,
                        ntruplus_batch_counter counter,
                        ntruplus_batch_prepare prepare_control,
                        ntruplus_batch_operation run_control,
                        void *control_context,
                        ntruplus_batch_prepare prepare_candidate,
                        ntruplus_batch_operation run_candidate,
                        void *candidate_context,
                        ntruplus_batch_result *result);

#endif
