#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

#include "params.h"
#include "poly.h"
#include "randombytes.h"

// ARM64 cycle counter
static inline uint64_t get_cycles(void) {
    uint64_t cycles;
    __asm__ volatile("mrs %0, cntvct_el0" : "=r" (cycles));
    return cycles;
}

// Statistical analysis structure
typedef struct {
    uint64_t min;
    uint64_t max; 
    uint64_t avg;
    double median;
    double std_dev;
} perf_stats_t;

void calculate_stats(uint64_t *measurements, int count, perf_stats_t *stats) {
    // Sort measurements
    for (int i = 0; i < count - 1; i++) {
        for (int j = i + 1; j < count; j++) {
            if (measurements[i] > measurements[j]) {
                uint64_t temp = measurements[i];
                measurements[i] = measurements[j];
                measurements[j] = temp;
            }
        }
    }
    
    stats->min = measurements[0];
    stats->max = measurements[count - 1];
    
    uint64_t total = 0;
    for (int i = 0; i < count; i++) {
        total += measurements[i];
    }
    stats->avg = total / count;
    
    stats->median = (count % 2 == 0) ? 
        (measurements[count/2 - 1] + measurements[count/2]) / 2.0 :
        measurements[count/2];
        
    // Standard deviation
    double sum_sq_diff = 0.0;
    double avg_double = (double)stats->avg;
    for (int i = 0; i < count; i++) {
        double diff = (double)measurements[i] - avg_double;
        sum_sq_diff += diff * diff;
    }
    stats->std_dev = sqrt(sum_sq_diff / (double)count);
}

void benchmark_function(void (*func)(void), const char *name, int iterations) {
    printf("=== %s Performance ===\n", name);
    
    uint64_t *measurements = malloc(iterations * sizeof(uint64_t));
    
    // Warmup
    for (int i = 0; i < 100; i++) {
        func();
    }
    
    // Actual measurements
    for (int i = 0; i < iterations; i++) {
        uint64_t start = get_cycles();
        func();
        uint64_t end = get_cycles();
        measurements[i] = end - start;
    }
    
    perf_stats_t stats;
    calculate_stats(measurements, iterations, &stats);
    
    printf("Iterations: %d\n", iterations);
    printf("Min:        %llu cycles\n", stats.min);
    printf("Max:        %llu cycles\n", stats.max);
    printf("Average:    %llu cycles\n", stats.avg);
    printf("Median:     %.1f cycles\n", stats.median);
    printf("Std Dev:    %.1f cycles\n", stats.std_dev);
    printf("Variance:   %.1f%%\n", (stats.std_dev / stats.avg) * 100.0);
    printf("\n");
    
    free(measurements);
}

// Global test data for consistent benchmarking
static poly test_poly;
static uint8_t test_buf[NTRUPLUS_N/4];
static uint8_t test_msg[NTRUPLUS_N/8];
static uint8_t test_result[NTRUPLUS_N/8];

void test_poly_cbd1(void) {
    poly_cbd1(&test_poly, test_buf);
}

void test_poly_sotp_encode(void) {
    poly_sotp_encode(&test_poly, test_msg, test_buf);
}

void test_poly_sotp_decode(void) {
    poly_sotp_decode(test_result, &test_poly, test_buf);
}

// Additional functions for comparison
void test_poly_ntt(void) {
    poly temp;
    memcpy(&temp, &test_poly, sizeof(poly));
    poly_ntt(&temp, &test_poly);
}

void test_poly_invntt(void) {
    poly temp;
    memcpy(&temp, &test_poly, sizeof(poly));
    poly_invntt(&temp, &test_poly);
}

void test_poly_basemul(void) {
    poly temp;
    poly_basemul(&temp, &test_poly, &test_poly);
}

int main() {
    printf("=== NTRU+ Individual Function Speed Test ===\n");
    printf("Testing specialized functions and comparison with core operations\n\n");
    
    const int iterations = 10000;
    
    // Initialize test data
    randombytes(test_buf, sizeof(test_buf));
    randombytes(test_msg, sizeof(test_msg));
    for (int i = 0; i < NTRUPLUS_N; i++) {
        test_poly.coeffs[i] = rand() % NTRUPLUS_Q;
    }
    
    printf("System Info:\n");
    uint32_t freq;
    __asm__ volatile("mrs %0, cntfrq_el0" : "=r" (freq));
    printf("ARM Counter Frequency: %u Hz\n", freq);
    printf("Test iterations: %d\n\n", iterations);
    
    // Test our target specialized functions
    printf("=== TARGET SPECIALIZED FUNCTIONS ===\n");
    benchmark_function(test_poly_cbd1, "poly_cbd1", iterations);
    benchmark_function(test_poly_sotp_encode, "poly_sotp_encode", iterations);
    benchmark_function(test_poly_sotp_decode, "poly_sotp_decode", iterations);
    
    // Test core NTRU+ operations for comparison
    printf("=== CORE NTRU+ OPERATIONS (for comparison) ===\n");
    benchmark_function(test_poly_ntt, "poly_ntt", iterations);
    benchmark_function(test_poly_invntt, "poly_invntt", iterations); 
    benchmark_function(test_poly_basemul, "poly_basemul", iterations);
    
    printf("=== ANALYSIS ===\n");
    printf("Compare the specialized function performance against core operations.\n");
    printf("If NTT/basemul are significantly more expensive, focus optimization there.\n");
    printf("This data helps validate the bottleneck analysis from the main profiler.\n");
    
    return 0;
}