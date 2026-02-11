#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

#include "params.h"
#include "api.h"
#include "poly.h"
#include "ntt.h"
#include "symmetric.h"
#include "randombytes.h"
#include "fips202/fips202.h"

// ARM64 cycle counter
static inline uint64_t get_cycles(void) {
    uint64_t cycles;
    __asm__ volatile("mrs %0, cntvct_el0" : "=r" (cycles));
    return cycles;
}

// Profiling infrastructure
typedef struct {
    uint64_t total_cycles;
    uint32_t call_count;
    const char* name;
} function_profile_t;

// Global profiling data for each KEM operation
static function_profile_t keygen_profiles[10];
static function_profile_t encap_profiles[10]; 
static function_profile_t decap_profiles[10];
static int keygen_profile_count = 0;
static int encap_profile_count = 0;
static int decap_profile_count = 0;

// Add profile entry
void add_profile(function_profile_t* profiles, int* count, const char* name, uint64_t cycles) {
    // Find existing profile or create new one
    for (int i = 0; i < *count; i++) {
        if (strcmp(profiles[i].name, name) == 0) {
            profiles[i].total_cycles += cycles;
            profiles[i].call_count++;
            return;
        }
    }
    
    // Create new profile entry
    if (*count < 10) {
        profiles[*count].name = name;
        profiles[*count].total_cycles = cycles;
        profiles[*count].call_count = 1;
        (*count)++;
    }
}

// Instrumented wrappers for major bottleneck functions
static function_profile_t* current_profiles = NULL;
static int* current_count = NULL;

void poly_ntt_profiled(poly *r, const poly *a) {
    uint64_t start = get_cycles();
    poly_ntt(r, a);
    uint64_t end = get_cycles();
    if (current_profiles) add_profile(current_profiles, current_count, "poly_ntt", end - start);
}

void poly_invntt_profiled(poly *r, const poly *a) {
    uint64_t start = get_cycles();
    poly_invntt(r, a);
    uint64_t end = get_cycles();
    if (current_profiles) add_profile(current_profiles, current_count, "poly_invntt", end - start);
}

int poly_baseinv_profiled(poly *r, const poly *a) {
    uint64_t start = get_cycles();
    int result = poly_baseinv(r, a);
    uint64_t end = get_cycles();
    if (current_profiles) add_profile(current_profiles, current_count, "poly_baseinv", end - start);
    return result;
}

void poly_basemul_profiled(poly *r, const poly *a, const poly *b) {
    uint64_t start = get_cycles();
    poly_basemul(r, a, b);
    uint64_t end = get_cycles();
    if (current_profiles) add_profile(current_profiles, current_count, "poly_basemul", end - start);
}

void poly_basemul_add_profiled(poly *r, const poly *a, const poly *b, const poly *c) {
    uint64_t start = get_cycles();
    poly_basemul_add(r, a, b, c);
    uint64_t end = get_cycles();
    if (current_profiles) add_profile(current_profiles, current_count, "poly_basemul_add", end - start);
}

void poly_crepmod3_profiled(poly *r, const poly *a) {
    uint64_t start = get_cycles();
    poly_crepmod3(r, a);
    uint64_t end = get_cycles();
    if (current_profiles) add_profile(current_profiles, current_count, "poly_crepmod3", end - start);
}

void hash_f_profiled(uint8_t *out, const uint8_t *in) {
    uint64_t start = get_cycles();
    hash_f(out, in);
    uint64_t end = get_cycles();
    if (current_profiles) add_profile(current_profiles, current_count, "hash_f", end - start);
}

void hash_h_profiled(uint8_t *out, const uint8_t *in) {
    uint64_t start = get_cycles();
    hash_h(out, in);
    uint64_t end = get_cycles();
    if (current_profiles) add_profile(current_profiles, current_count, "hash_h", end - start);
}

void hash_g_profiled(uint8_t *out, const uint8_t *in) {
    uint64_t start = get_cycles();
    hash_g(out, in);
    uint64_t end = get_cycles();
    if (current_profiles) add_profile(current_profiles, current_count, "hash_g", end - start);
}

void shake256_profiled(uint8_t *out, size_t outlen, const uint8_t *in, size_t inlen) {
    uint64_t start = get_cycles();
    shake256(out, outlen, in, inlen);
    uint64_t end = get_cycles();
    if (current_profiles) add_profile(current_profiles, current_count, "shake256", end - start);
}

void poly_cbd1_profiled(poly *r, const uint8_t *buf) {
    uint64_t start = get_cycles();
    poly_cbd1(r, buf);
    uint64_t end = get_cycles();
    if (current_profiles) add_profile(current_profiles, current_count, "poly_cbd1", end - start);
}

void poly_sotp_encode_profiled(poly *r, const uint8_t *msg, const uint8_t *buf) {
    uint64_t start = get_cycles();
    poly_sotp_encode(r, msg, buf);
    uint64_t end = get_cycles();
    if (current_profiles) add_profile(current_profiles, current_count, "poly_sotp_encode", end - start);
}

int poly_sotp_decode_profiled(uint8_t *msg, const poly *a, const uint8_t *buf) {
    uint64_t start = get_cycles();
    int result = poly_sotp_decode(msg, a, buf);
    uint64_t end = get_cycles();
    if (current_profiles) add_profile(current_profiles, current_count, "poly_sotp_decode", end - start);
    return result;
}

// Instrumented KEM operations (simplified versions to capture major functions)
int crypto_kem_keypair_profiled(uint8_t *pk, uint8_t *sk) {
    current_profiles = keygen_profiles;
    current_count = &keygen_profile_count;
    
    uint8_t coins[NTRUPLUS_SYMBYTES];
    poly f, finv, g, ginv;
    uint8_t buf[NTRUPLUS_N / 4];
    
    // Generate f polynomial
    randombytes(coins, sizeof(coins));
    shake256_profiled(buf, sizeof(buf), coins, 32);
    poly_cbd1_profiled(&f, buf);
    poly_triple(&f, &f);
    f.coeffs[0] += 1;
    poly_ntt_profiled(&f, &f);
    poly_baseinv_profiled(&finv, &f);
    
    // Generate g polynomial  
    randombytes(coins, sizeof(coins));
    shake256_profiled(buf, sizeof(buf), coins, 32);
    poly_cbd1_profiled(&g, buf);
    poly_triple(&g, &g);
    poly_ntt_profiled(&g, &g);
    poly_baseinv_profiled(&ginv, &g);
    
    // Compute public key
    poly h, hinv;
    poly_basemul_profiled(&h, &g, &finv);
    poly_basemul_profiled(&hinv, &f, &ginv);
    
    poly_tobytes(pk, &h);
    poly_tobytes(sk, &f);
    poly_tobytes(sk + NTRUPLUS_POLYBYTES, &hinv);
    hash_f_profiled(sk + 2 * NTRUPLUS_POLYBYTES, pk);
    
    current_profiles = NULL;
    current_count = NULL;
    return 0;
}

int crypto_kem_enc_profiled(uint8_t *ct, uint8_t *ss, const uint8_t *pk) {
    current_profiles = encap_profiles;
    current_count = &encap_profile_count;
    
    uint8_t coins[NTRUPLUS_N / 8];
    uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
    uint8_t buf1[NTRUPLUS_SYMBYTES + NTRUPLUS_N / 4];
    uint8_t buf2[NTRUPLUS_POLYBYTES];
    poly c, h, r, m;
    
    randombytes(coins, sizeof(coins));
    for (size_t i = 0; i < NTRUPLUS_N / 8; i++)
        msg[i] = coins[i];
    
    hash_f_profiled(msg + NTRUPLUS_N / 8, pk);
    hash_h_profiled(buf1, msg);
    
    poly_cbd1_profiled(&r, buf1 + NTRUPLUS_SYMBYTES);
    poly_ntt_profiled(&r, &r);
    
    poly_tobytes(buf2, &r);
    hash_g_profiled(buf2, buf2);
    poly_sotp_encode_profiled(&m, msg, buf2);
    poly_ntt_profiled(&m, &m);
    
    poly_frombytes(&h, pk);
    poly_basemul_add_profiled(&c, &h, &r, &m);
    poly_tobytes(ct, &c);
    
    for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
        ss[i] = buf1[i];
    
    current_profiles = NULL;
    current_count = NULL;
    return 0;
}

int crypto_kem_dec_profiled(uint8_t *ss, const uint8_t *ct, const uint8_t *sk) {
    current_profiles = decap_profiles;
    current_count = &decap_profile_count;
    
    uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
    uint8_t buf1[NTRUPLUS_POLYBYTES];
    uint8_t buf2[NTRUPLUS_POLYBYTES];
    uint8_t buf3[NTRUPLUS_POLYBYTES + NTRUPLUS_SYMBYTES];
    
    int8_t fail;
    poly c, f, hinv;
    poly r1, r2;
    poly m1, m2;
    
    poly_frombytes(&c, ct);
    poly_frombytes(&f, sk);
    poly_frombytes(&hinv, sk + NTRUPLUS_POLYBYTES);
    
    poly_basemul_profiled(&m1, &c, &f);
    poly_invntt_profiled(&m1, &m1);
    poly_crepmod3_profiled(&m1, &m1);
    
    poly_ntt_profiled(&m2, &m1);
    poly_sub(&c, &c, &m2);
    poly_basemul_profiled(&r2, &c, &hinv);
    
    poly_tobytes(buf1, &r2);
    hash_g_profiled(buf2, buf1);
    fail = poly_sotp_decode_profiled(msg, &m1, buf2);
    
    for (size_t i = 0; i < NTRUPLUS_SYMBYTES; i++)
        msg[i + NTRUPLUS_N / 8] = sk[i + 2 * NTRUPLUS_POLYBYTES];
    
    hash_h_profiled(buf3, msg);
    
    poly_cbd1_profiled(&r1, buf3 + NTRUPLUS_SSBYTES);
    poly_ntt_profiled(&r1, &r1);
    poly_tobytes(buf2, &r1);
    
    // verify() is small, skip for this analysis
    
    for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
        ss[i] = buf3[i] & ~(-fail);
    
    current_profiles = NULL;
    current_count = NULL;
    return fail;
}

void print_operation_profile(const char* operation, function_profile_t* profiles, int count, uint64_t total_cycles) {
    printf("\n=== %s DETAILED BREAKDOWN ===\n", operation);
    printf("Total Operation: %llu cycles\n\n", total_cycles);
    
    // Sort profiles by total cycles (descending)
    for (int i = 0; i < count - 1; i++) {
        for (int j = i + 1; j < count; j++) {
            if (profiles[i].total_cycles < profiles[j].total_cycles) {
                function_profile_t temp = profiles[i];
                profiles[i] = profiles[j];
                profiles[j] = temp;
            }
        }
    }
    
    printf("%-20s %12s %8s %10s %8s\n", "Function", "Total Cycles", "Calls", "Avg/Call", "% Total");
    printf("%-20s %12s %8s %10s %8s\n", "--------", "------------", "-----", "--------", "-------");
    
    uint64_t accounted_cycles = 0;
    for (int i = 0; i < count; i++) {
        uint64_t avg = profiles[i].total_cycles / profiles[i].call_count;
        double percentage = (double)profiles[i].total_cycles / total_cycles * 100.0;
        
        printf("%-20s %12llu %8u %10llu %7.1f%%\n", 
               profiles[i].name,
               profiles[i].total_cycles,
               profiles[i].call_count,
               avg,
               percentage);
        
        accounted_cycles += profiles[i].total_cycles;
    }
    
    uint64_t unaccounted = total_cycles - accounted_cycles;
    double unaccounted_pct = (double)unaccounted / total_cycles * 100.0;
    printf("%-20s %12llu %8s %10s %7.1f%%\n", 
           "Other/Overhead", unaccounted, "-", "-", unaccounted_pct);
}

void analyze_optimization_priorities(void) {
    printf("\n=== OPTIMIZATION PRIORITY ANALYSIS ===\n");
    
    // Collect all function data across operations
    struct {
        const char* name;
        uint64_t total_cycles;
        uint32_t total_calls;
        const char* operations;
    } global_functions[20];
    int global_count = 0;
    
    // Aggregate function calls across all operations
    function_profile_t all_profiles[30];
    int all_count = 0;
    
    // Copy all profiles
    for (int i = 0; i < keygen_profile_count; i++) {
        all_profiles[all_count++] = keygen_profiles[i];
    }
    for (int i = 0; i < encap_profile_count; i++) {
        all_profiles[all_count++] = encap_profiles[i];
    }
    for (int i = 0; i < decap_profile_count; i++) {
        all_profiles[all_count++] = decap_profiles[i];
    }
    
    // Merge duplicates
    for (int i = 0; i < all_count; i++) {
        int found = -1;
        for (int j = 0; j < global_count; j++) {
            if (strcmp(global_functions[j].name, all_profiles[i].name) == 0) {
                found = j;
                break;
            }
        }
        
        if (found >= 0) {
            global_functions[found].total_cycles += all_profiles[i].total_cycles;
            global_functions[found].total_calls += all_profiles[i].call_count;
        } else if (global_count < 20) {
            global_functions[global_count].name = all_profiles[i].name;
            global_functions[global_count].total_cycles = all_profiles[i].total_cycles;
            global_functions[global_count].total_calls = all_profiles[i].call_count;
            global_count++;
        }
    }
    
    // Sort by total cycles
    for (int i = 0; i < global_count - 1; i++) {
        for (int j = i + 1; j < global_count; j++) {
            if (global_functions[i].total_cycles < global_functions[j].total_cycles) {
                // Swap structures
                const char* temp_name = global_functions[i].name;
                uint64_t temp_cycles = global_functions[i].total_cycles;
                uint32_t temp_calls = global_functions[i].total_calls;
                
                global_functions[i].name = global_functions[j].name;
                global_functions[i].total_cycles = global_functions[j].total_cycles;
                global_functions[i].total_calls = global_functions[j].total_calls;
                
                global_functions[j].name = temp_name;
                global_functions[j].total_cycles = temp_cycles;
                global_functions[j].total_calls = temp_calls;
            }
        }
    }
    
    printf("**OPTIMIZATION PRIORITY RANKING** (across all KEM operations):\n\n");
    printf("%-20s %12s %8s %12s\n", "Function", "Total Cycles", "Calls", "Priority");
    printf("%-20s %12s %8s %12s\n", "--------", "------------", "-----", "--------");
    
    for (int i = 0; i < global_count && i < 10; i++) {
        const char* priority;
        if (i < 3) priority = "🔥 HIGH";
        else if (i < 6) priority = "⚡ MEDIUM"; 
        else priority = "🔧 LOW";
        
        printf("%-20s %12llu %8u %12s\n",
               global_functions[i].name,
               global_functions[i].total_cycles,
               global_functions[i].total_calls,
               priority);
    }
    
    printf("\n**ENGINEERING RECOMMENDATIONS:**\n");
    printf("1. 🔥 Focus on top 3 functions for maximum impact\n");
    printf("2. ⚡ Consider medium priority if top 3 are already optimized\n");
    printf("3. 🔧 Low priority functions: optimize only in comprehensive passes\n");
}

int main() {
    printf("=== COMPREHENSIVE NTRU+ KEM BOTTLENECK ANALYSIS ===\n");
    printf("Profiling all major functions in KeyGen, Encap, and Decap operations\n\n");
    
    const int iterations = 100; // Fewer iterations due to comprehensive profiling
    
    uint8_t pk[CRYPTO_PUBLICKEYBYTES];
    uint8_t sk[CRYPTO_SECRETKEYBYTES];
    uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
    uint8_t ss1[CRYPTO_BYTES], ss2[CRYPTO_BYTES];
    
    // Warmup
    printf("Warming up...\n");
    for (int i = 0; i < 10; i++) {
        crypto_kem_keypair(pk, sk);
        crypto_kem_enc(ct, ss1, pk);
        crypto_kem_dec(ss2, ct, sk);
    }
    
    printf("Running %d iterations of comprehensive profiling...\n", iterations);
    
    // Clear profiles
    keygen_profile_count = encap_profile_count = decap_profile_count = 0;
    
    // Measure total times
    uint64_t total_keygen = 0, total_encap = 0, total_decap = 0;
    
    for (int i = 0; i < iterations; i++) {
        uint64_t start, end;
        
        // KeyGen
        start = get_cycles();
        crypto_kem_keypair_profiled(pk, sk);
        end = get_cycles();
        total_keygen += (end - start);
        
        // Encap
        start = get_cycles();
        crypto_kem_enc_profiled(ct, ss1, pk);
        end = get_cycles();
        total_encap += (end - start);
        
        // Decap
        start = get_cycles();
        crypto_kem_dec_profiled(ss2, ct, sk);
        end = get_cycles();
        total_decap += (end - start);
    }
    
    // Average the results
    total_keygen /= iterations;
    total_encap /= iterations;
    total_decap /= iterations;
    
    // Average profile data
    for (int i = 0; i < keygen_profile_count; i++) {
        keygen_profiles[i].total_cycles /= iterations;
    }
    for (int i = 0; i < encap_profile_count; i++) {
        encap_profiles[i].total_cycles /= iterations;
    }
    for (int i = 0; i < decap_profile_count; i++) {
        decap_profiles[i].total_cycles /= iterations;
    }
    
    // Print detailed breakdowns
    print_operation_profile("KEYGEN", keygen_profiles, keygen_profile_count, total_keygen);
    print_operation_profile("ENCAP", encap_profiles, encap_profile_count, total_encap);
    print_operation_profile("DECAP", decap_profiles, decap_profile_count, total_decap);
    
    analyze_optimization_priorities();
    
    printf("\n=== SUMMARY FOR ENGINEERING DECISION ===\n");
    printf("This data shows the REAL bottlenecks in NTRU+ KEM operations.\n");
    printf("Use this to make data-driven optimization decisions.\n");
    printf("Focus engineering effort on the highest-cycle functions first.\n");
    
    return 0;
}