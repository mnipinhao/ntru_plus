#ifndef GT_OPTIMIZED_PERF_COUNTER_H
#define GT_OPTIMIZED_PERF_COUNTER_H

#include <stdint.h>

int perf_counter_open(void);
void perf_counter_close(void);
int perf_counter_start(void);
uint64_t perf_counter_stop(void);

#endif
