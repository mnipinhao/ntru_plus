#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>

// ARM64 cycle counter
static inline uint64_t get_cycles(void) {
    uint64_t cycles;
    __asm__ volatile("mrs %0, cntvct_el0" : "=r" (cycles));
    return cycles;
}

// Include AArch64 implementation
#include "../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768/api.h"
#include "../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768/params.h"
#include "../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768/poly.h"
#include "../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768/symmetric.h"

// Function declarations (will be linked from compiled object files)
extern int crypto_kem_keypair(unsigned char *pk, unsigned char *sk);
extern int crypto_kem_enc(unsigned char *ct, unsigned char *ss, const unsigned char *pk);
extern int crypto_kem_dec(unsigned char *ss, const unsigned char *ct, const unsigned char *sk);

// Individual function benchmarks for key optimized functions
extern void poly_cbd1(poly *r, const unsigned char *buf);
extern void poly_sotp_encode(poly *r, const unsigned char *msg, const unsigned char *buf);
extern int poly_sotp_decode(unsigned char *msg, const poly *r, const unsigned char *buf);
extern void poly_ntt(poly *r, const poly *a);
extern int poly_baseinv(poly *r, const poly *a);
extern void hash_f(unsigned char *buf, const unsigned char *msg);
extern void hash_g(unsigned char *buf, const unsigned char *msg);
extern void hash_h(unsigned char *buf, const unsigned char *msg);

#define TEST_ITERATIONS 1000

// Profile structure
typedef struct {
    char name[64];
    uint64_t total_cycles;
    uint64_t min_cycles;
    uint64_t max_cycles;
    int calls;
} profile_entry_t;

typedef struct {
    profile_entry_t entries[32];
    int count;
} profile_data_t;

static void add_profile(profile_data_t *profiles, const char *name, uint64_t cycles) {
    if (profiles->count >= 32) return;
    
    // Check if entry exists
    for (int i = 0; i < profiles->count; i++) {
        if (strcmp(profiles->entries[i].name, name) == 0) {
            profiles->entries[i].total_cycles += cycles;
            profiles->entries[i].calls++;
            if (cycles < profiles->entries[i].min_cycles) 
                profiles->entries[i].min_cycles = cycles;
            if (cycles > profiles->entries[i].max_cycles)
                profiles->entries[i].max_cycles = cycles;
            return;
        }
    }
    
    // Add new entry
    strncpy(profiles->entries[profiles->count].name, name, 63);
    profiles->entries[profiles->count].name[63] = '\0';
    profiles->entries[profiles->count].total_cycles = cycles;
    profiles->entries[profiles->count].min_cycles = cycles;
    profiles->entries[profiles->count].max_cycles = cycles;
    profiles->entries[profiles->count].calls = 1;
    profiles->count++;
}

static void print_profiles(const profile_data_t *profiles, const char *title) {
    printf("\n=== %s ===\n", title);
    printf("%-20s %12s %8s %12s %12s %12s\n", 
           "Function", "Total", "Calls", "Average", "Min", "Max");
    printf("%-20s %12s %8s %12s %12s %12s\n", 
           "--------", "-----", "-----", "-------", "---", "---");
    
    uint64_t grand_total = 0;
    for (int i = 0; i < profiles->count; i++) {
        grand_total += profiles->entries[i].total_cycles;
    }
    
    for (int i = 0; i < profiles->count; i++) {
        uint64_t avg = profiles->entries[i].total_cycles / profiles->entries[i].calls;
        double percentage = (double)profiles->entries[i].total_cycles / grand_total * 100.0;
        printf("%-20s %12lu %8d %12lu %12lu %12lu (%.1f%%)\n", 
               profiles->entries[i].name,
               profiles->entries[i].total_cycles,
               profiles->entries[i].calls,
               avg,
               profiles->entries[i].min_cycles,
               profiles->entries[i].max_cycles,
               percentage);
    }
    printf("\nGrand Total: %lu cycles\n", grand_total);
}

// Benchmark KEM operations
static void benchmark_kem_operations(profile_data_t *profiles) {
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES]; 
    unsigned char ct[CRYPTO_CIPHERTEXTBYTES];
    unsigned char ss1[CRYPTO_BYTES];
    unsigned char ss2[CRYPTO_BYTES];
    
    printf("Running AArch64 KEM operations benchmark (%d iterations)...\n", TEST_ITERATIONS);
    
    for (int i = 0; i < TEST_ITERATIONS; i++) {
        // KeyGen
        uint64_t start = get_cycles();
        int ret = crypto_kem_keypair(pk, sk);
        uint64_t end = get_cycles();
        assert(ret == 0);
        add_profile(profiles, "KeyGen", end - start);
        
        // Encapsulation  
        start = get_cycles();
        ret = crypto_kem_enc(ct, ss1, pk);
        end = get_cycles();
        assert(ret == 0);
        add_profile(profiles, "Encap", end - start);
        
        // Decapsulation
        start = get_cycles();
        ret = crypto_kem_dec(ss2, ct, sk);
        end = get_cycles();
        assert(ret == 0);
        add_profile(profiles, "Decap", end - start);
        
        // Verify shared secrets match
        assert(memcmp(ss1, ss2, CRYPTO_BYTES) == 0);
        
        if ((i + 1) % 100 == 0) {
            printf("  Completed %d/%d iterations\n", i + 1, TEST_ITERATIONS);
        }
    }
}

// Benchmark individual specialized functions
static void benchmark_specialized_functions(profile_data_t *profiles) {
    printf("Running specialized function benchmarks (%d iterations each)...\n", TEST_ITERATIONS);
    
    // Test data
    unsigned char buf[NTRUPLUS_N / 4];
    unsigned char msg[NTRUPLUS_N / 8];
    unsigned char hash_buf[NTRUPLUS_POLYBYTES];
    poly p1, p2, p3;
    
    // Initialize test data with some pattern
    for (int i = 0; i < sizeof(buf); i++) buf[i] = i & 0xFF;
    for (int i = 0; i < sizeof(msg); i++) msg[i] = (i * 3) & 0xFF;
    for (int i = 0; i < sizeof(hash_buf); i++) hash_buf[i] = (i * 7) & 0xFF;
    
    // poly_cbd1 benchmark
    for (int i = 0; i < TEST_ITERATIONS; i++) {
        uint64_t start = get_cycles();
        poly_cbd1(&p1, buf);
        uint64_t end = get_cycles();
        add_profile(profiles, "poly_cbd1", end - start);
    }
    
    // poly_sotp_encode benchmark
    for (int i = 0; i < TEST_ITERATIONS; i++) {
        uint64_t start = get_cycles();
        poly_sotp_encode(&p2, msg, buf);
        uint64_t end = get_cycles();
        add_profile(profiles, "poly_sotp_encode", end - start);
    }
    
    // poly_sotp_decode benchmark
    for (int i = 0; i < TEST_ITERATIONS; i++) {
        uint64_t start = get_cycles();
        poly_sotp_decode(msg, &p2, buf);
        uint64_t end = get_cycles();
        add_profile(profiles, "poly_sotp_decode", end - start);
    }
    
    // poly_ntt benchmark
    for (int i = 0; i < TEST_ITERATIONS; i++) {
        uint64_t start = get_cycles();
        poly_ntt(&p3, &p1);
        uint64_t end = get_cycles();
        add_profile(profiles, "poly_ntt", end - start);
    }
    
    // poly_baseinv benchmark (more expensive, fewer iterations)
    for (int i = 0; i < TEST_ITERATIONS / 10; i++) {
        uint64_t start = get_cycles();
        poly_baseinv(&p2, &p3);
        uint64_t end = get_cycles();
        add_profile(profiles, "poly_baseinv", end - start);
    }
    
    // Hash function benchmarks
    unsigned char hash_out[64];
    
    for (int i = 0; i < TEST_ITERATIONS; i++) {
        uint64_t start = get_cycles();
        hash_f(hash_out, hash_buf);
        uint64_t end = get_cycles();
        add_profile(profiles, "hash_f", end - start);
    }
    
    for (int i = 0; i < TEST_ITERATIONS; i++) {
        uint64_t start = get_cycles();
        hash_g(hash_out, hash_buf);
        uint64_t end = get_cycles();
        add_profile(profiles, "hash_g", end - start);
    }
    
    for (int i = 0; i < TEST_ITERATIONS; i++) {
        uint64_t start = get_cycles();
        hash_h(hash_out, hash_buf);
        uint64_t end = get_cycles();
        add_profile(profiles, "hash_h", end - start);
    }
}

int main() {
    printf("🚀 NTRU+ AArch64 Implementation Benchmark\n");
    printf("==========================================\n");
    printf("Implementation: Additional_Implementation/aarch64/NTRU+768\n");
    printf("Platform: ARM64 (Apple Silicon)\n");
    printf("Compiler: GCC -O3 with hand-optimized assembly\n");
    printf("Measurement: ARM64 CNTVCT_EL0 cycle counter\n");
    printf("Iterations: %d per operation\n\n", TEST_ITERATIONS);
    
    profile_data_t kem_profiles = {0};
    profile_data_t func_profiles = {0};
    
    // Benchmark full KEM operations
    benchmark_kem_operations(&kem_profiles);
    print_profiles(&kem_profiles, "KEM Operations (AArch64 Implementation)");
    
    // Benchmark individual specialized functions
    benchmark_specialized_functions(&func_profiles);
    print_profiles(&func_profiles, "Individual Functions (AArch64 Implementation)");
    
    printf("\n=== Implementation Details ===\n");
    printf("• Hand-optimized AArch64 assembly files:\n");
    printf("  - asm/cbd.s      (poly_cbd1, poly_sotp_*)\n");
    printf("  - asm/ntt.s      (poly_ntt)\n");
    printf("  - asm/base.s     (poly_basemul*)\n");
    printf("  - asm/crepmod3.s (poly_crepmod3)\n");
    printf("  - asm/pack.s     (poly packing/unpacking)\n");
    printf("  - asm/add.s      (polynomial addition)\n");
    printf("• NEON SIMD instructions for vectorized operations\n");
    printf("• Optimized register allocation and loop unrolling\n");
    printf("• SHAKE256 assembly optimization (if CE supported)\n\n");
    
    return 0;
}