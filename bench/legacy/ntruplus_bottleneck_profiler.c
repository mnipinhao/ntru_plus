#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

// Include actual NTRU+ headers
#include "params.h"
#include "api.h" 
#include "poly.h"
#include "randombytes.h"

// ARM64 cycle counter
static inline uint64_t get_cycles(void) {
    uint64_t cycles;
    __asm__ volatile("mrs %0, cntvct_el0" : "=r" (cycles));
    return cycles;
}

// Amdahl's Law calculation
double calculate_amdahl_speedup(double fraction_optimized, double speedup_factor) {
    if (fraction_optimized >= 1.0) return speedup_factor;
    return 1.0 / ((1.0 - fraction_optimized) + (fraction_optimized / speedup_factor));
}

void analyze_bottlenecks(uint64_t avg_keygen, uint64_t avg_encap, uint64_t avg_decap, int iterations) {
    printf("=== COST-BENEFIT ANALYSIS ===\n");
    
    // Measure specialized functions precisely
    uint8_t buf[NTRUPLUS_N/4];
    uint8_t msg[NTRUPLUS_N/8];
    poly poly_result;
    uint8_t msg_result[NTRUPLUS_N/8];
    
    randombytes(buf, sizeof(buf));
    randombytes(msg, sizeof(msg));
    for (int i = 0; i < NTRUPLUS_N; i++) {
        poly_result.coeffs[i] = rand() % NTRUPLUS_Q;
    }
    
    uint64_t start, end, total;
    
    // Measure poly_cbd1
    total = 0;
    for (int i = 0; i < iterations; i++) {
        start = get_cycles();
        poly_cbd1(&poly_result, buf);
        end = get_cycles();
        total += (end - start);
    }
    uint64_t cbd1_avg = total / iterations;
    
    // Measure poly_sotp_encode
    total = 0;
    for (int i = 0; i < iterations; i++) {
        start = get_cycles();
        poly_sotp_encode(&poly_result, msg, buf);
        end = get_cycles();
        total += (end - start);
    }
    uint64_t encode_avg = total / iterations;
    
    // Measure poly_sotp_decode
    total = 0;
    for (int i = 0; i < iterations; i++) {
        start = get_cycles();
        poly_sotp_decode(msg_result, &poly_result, buf);
        end = get_cycles();
        total += (end - start);
    }
    uint64_t decode_avg = total / iterations;
    
    // Analysis: KeyGen=2×cbd1, Encap=cbd1+encode, Decap=cbd1+decode
    uint64_t keygen_specialized = 2 * cbd1_avg;
    uint64_t encap_specialized = cbd1_avg + encode_avg; 
    uint64_t decap_specialized = cbd1_avg + decode_avg;
    
    printf("\n**PROFILING DATA FOR SENIOR PERFORMANCE ENGINEER:**\n\n");
    
    // Detailed breakdown
    double keygen_pct = (double)keygen_specialized / avg_keygen * 100.0;
    double encap_pct = (double)encap_specialized / avg_encap * 100.0;
    double decap_pct = (double)decap_specialized / avg_decap * 100.0;
    
    printf("**1. KeyGen (Total: %llu cycles)**\n", avg_keygen);
    printf("- poly_cbd1: %llu cycles (2× calls = %llu total, %.1f%%)\n", 
           cbd1_avg, keygen_specialized, keygen_pct);
    printf("- Other ops: %llu cycles (%.1f%%) [NTT, baseinv, basemul]\n\n",
           avg_keygen - keygen_specialized, 100.0 - keygen_pct);
    
    printf("**2. Encap (Total: %llu cycles)**\n", avg_encap);
    printf("- poly_cbd1: %llu cycles (%.1f%%)\n", cbd1_avg, (double)cbd1_avg/avg_encap*100.0);
    printf("- poly_sotp_encode: %llu cycles (%.1f%%)\n", encode_avg, (double)encode_avg/avg_encap*100.0);
    printf("- Combined: %llu cycles (%.1f%%)\n", encap_specialized, encap_pct);
    printf("- Other ops: %llu cycles (%.1f%%) [hashing, NTT, basemul]\n\n",
           avg_encap - encap_specialized, 100.0 - encap_pct);
    
    printf("**3. Decap (Total: %llu cycles)**\n", avg_decap);
    printf("- poly_cbd1: %llu cycles (%.1f%%)\n", cbd1_avg, (double)cbd1_avg/avg_decap*100.0);
    printf("- poly_sotp_decode: %llu cycles (%.1f%%)\n", decode_avg, (double)decode_avg/avg_decap*100.0);
    printf("- Combined: %llu cycles (%.1f%%)\n", decap_specialized, decap_pct);
    printf("- Other ops: %llu cycles (%.1f%%) [NTT, basemul, crepmod3, hashing]\n\n",
           avg_decap - decap_specialized, 100.0 - decap_pct);
    
    printf("=== AMDAHL'S LAW ANALYSIS ===\n");
    const double speedups[] = {2.0, 4.0, 6.0, INFINITY};
    const char* names[] = {"2×", "4×", "6×", "∞× (max)"};
    
    for (int i = 0; i < 4; i++) {
        printf("%s -> KeyGen: %.2fx, Encap: %.2fx, Decap: %.2fx\n", names[i],
               calculate_amdahl_speedup(keygen_pct/100.0, speedups[i]),
               calculate_amdahl_speedup(encap_pct/100.0, speedups[i]),
               calculate_amdahl_speedup(decap_pct/100.0, speedups[i]));
    }
    
    printf("\n=== RECOMMENDATION ===\n");
    double max_pct = (keygen_pct > encap_pct) ? keygen_pct : encap_pct;
    max_pct = (max_pct > decap_pct) ? max_pct : decap_pct;
    
    if (max_pct > 15.0) {
        printf("HIGH PRIORITY - Significant gains expected\n");
    } else if (max_pct > 8.0) {
        printf("MODERATE PRIORITY - Limited but measurable gains\n"); 
    } else {
        printf("LOW PRIORITY - Focus on NTT/basemul instead\n");
    }
}

int main() {
    printf("=== NTRU+ Specialized Function Bottleneck Analysis ===\n\n");
    
    const int iterations = 1000;
    uint8_t pk[CRYPTO_PUBLICKEYBYTES];
    uint8_t sk[CRYPTO_SECRETKEYBYTES]; 
    uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
    uint8_t ss1[CRYPTO_BYTES], ss2[CRYPTO_BYTES];
    
    // Warmup
    for (int i = 0; i < 10; i++) {
        crypto_kem_keypair(pk, sk);
        crypto_kem_enc(ct, ss1, pk);
        crypto_kem_dec(ss2, ct, sk);
    }
    
    // Measure KEM operations
    uint64_t start, end, total;
    
    total = 0;
    for (int i = 0; i < iterations; i++) {
        start = get_cycles();
        crypto_kem_keypair(pk, sk);
        end = get_cycles();
        total += (end - start);
    }
    uint64_t avg_keygen = total / iterations;
    
    total = 0;
    for (int i = 0; i < iterations; i++) {
        start = get_cycles();
        crypto_kem_enc(ct, ss1, pk);
        end = get_cycles(); 
        total += (end - start);
    }
    uint64_t avg_encap = total / iterations;
    
    total = 0;
    for (int i = 0; i < iterations; i++) {
        start = get_cycles();
        crypto_kem_dec(ss2, ct, sk);
        end = get_cycles();
        total += (end - start);
    }
    uint64_t avg_decap = total / iterations;
    
    printf("KeyGen: %llu cycles\n", avg_keygen);
    printf("Encap:  %llu cycles\n", avg_encap);
    printf("Decap:  %llu cycles\n\n", avg_decap);
    
    analyze_bottlenecks(avg_keygen, avg_encap, avg_decap, iterations);
    return 0;
}