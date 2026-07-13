#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <stddef.h>
#include <assert.h>

// ARM64 cycle counter
static inline uint64_t get_cycles(void) {
    uint64_t cycles;
    __asm__ volatile("mrs %0, cntvct_el0" : "=r" (cycles));
    return cycles;
}

// Include headers from both implementations
#define OPTIMIZED_IMPL 1
#define AARCH64_IMPL 2

// Function pointer types for dynamic loading
typedef int (*kem_keypair_func_t)(unsigned char *, unsigned char *);
typedef int (*kem_enc_func_t)(unsigned char *, unsigned char *, const unsigned char *);
typedef int (*kem_dec_func_t)(unsigned char *, const unsigned char *, const unsigned char *);

// Profile structure
typedef struct {
    char name[64];
    uint64_t cycles;
    int calls;
} profile_entry_t;

typedef struct {
    profile_entry_t entries[32];
    int count;
} profile_data_t;

// Performance comparison data
typedef struct {
    char operation[32];
    uint64_t optimized_cycles;
    uint64_t aarch64_cycles;
    double speedup;
    int iterations;
} comparison_t;

// Add profile entry
static void add_profile(profile_data_t *profiles, const char *name, uint64_t cycles) {
    if (profiles->count >= 32) return;
    
    // Check if entry exists
    for (int i = 0; i < profiles->count; i++) {
        if (strcmp(profiles->entries[i].name, name) == 0) {
            profiles->entries[i].cycles += cycles;
            profiles->entries[i].calls++;
            return;
        }
    }
    
    // Add new entry
    strncpy(profiles->entries[profiles->count].name, name, 63);
    profiles->entries[profiles->count].name[63] = '\0';
    profiles->entries[profiles->count].cycles = cycles;
    profiles->entries[profiles->count].calls = 1;
    profiles->count++;
}

// Print profile results
static void print_profiles(const profile_data_t *profiles, const char *title) {
    printf("\n=== %s ===\n", title);
    printf("%-20s %12s %8s %12s\n", "Function", "Total Cycles", "Calls", "Avg Cycles");
    printf("%-20s %12s %8s %12s\n", "--------", "------------", "-----", "----------");
    
    uint64_t total_cycles = 0;
    for (int i = 0; i < profiles->count; i++) {
        total_cycles += profiles->entries[i].cycles;
    }
    
    for (int i = 0; i < profiles->count; i++) {
        uint64_t avg = profiles->entries[i].cycles / profiles->entries[i].calls;
        double percentage = (double)profiles->entries[i].cycles / total_cycles * 100.0;
        printf("%-20s %12lu %8d %12lu (%.1f%%)\n", 
               profiles->entries[i].name, 
               profiles->entries[i].cycles,
               profiles->entries[i].calls,
               avg,
               percentage);
    }
    printf("Total: %lu cycles\n", total_cycles);
}

// Individual operation benchmarks using includes
#define TEST_ITERATIONS 1000

// Optimized Implementation functions
#include "../ntruplus-KpqC-Final/Optimized_Implementation/NTRU+768/api.h"
#include "../ntruplus-KpqC-Final/Optimized_Implementation/NTRU+768/params.h"

// Rename optimized functions to avoid conflicts
#define crypto_kem_keypair crypto_kem_keypair_opt
#define crypto_kem_enc crypto_kem_enc_opt  
#define crypto_kem_dec crypto_kem_dec_opt
#define poly_cbd1 poly_cbd1_opt
#define poly_sotp_encode poly_sotp_encode_opt
#define poly_sotp_decode poly_sotp_decode_opt
#define poly_ntt poly_ntt_opt
#define poly_baseinv poly_baseinv_opt
#define hash_f hash_f_opt
#define hash_g hash_g_opt
#define hash_h hash_h_opt
#define shake256 shake256_opt

#include "../ntruplus-KpqC-Final/Optimized_Implementation/NTRU+768/kem.c"
#include "../ntruplus-KpqC-Final/Optimized_Implementation/NTRU+768/poly.c"
#include "../ntruplus-KpqC-Final/Optimized_Implementation/NTRU+768/symmetric.c"
#include "../ntruplus-KpqC-Final/Optimized_Implementation/NTRU+768/fips202/fips202.c"

#undef crypto_kem_keypair
#undef crypto_kem_enc
#undef crypto_kem_dec
#undef poly_cbd1
#undef poly_sotp_encode
#undef poly_sotp_decode
#undef poly_ntt
#undef poly_baseinv
#undef hash_f
#undef hash_g
#undef hash_h
#undef shake256

// AArch64 Implementation functions
#define crypto_kem_keypair crypto_kem_keypair_aarch64
#define crypto_kem_enc crypto_kem_enc_aarch64
#define crypto_kem_dec crypto_kem_dec_aarch64
#define poly_cbd1 poly_cbd1_aarch64
#define poly_sotp_encode poly_sotp_encode_aarch64
#define poly_sotp_decode poly_sotp_decode_aarch64
#define poly_ntt poly_ntt_aarch64
#define poly_baseinv poly_baseinv_aarch64
#define hash_f hash_f_aarch64
#define hash_g hash_g_aarch64
#define hash_h hash_h_aarch64
#define shake256 shake256_aarch64

// We need to include aarch64 implementation - this is complex due to assembly
// Let's create a simpler approach using external compilation

static void benchmark_kem_operations_optimized(profile_data_t *profiles) {
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES]; 
    unsigned char ct[CRYPTO_CIPHERTEXTBYTES];
    unsigned char ss1[CRYPTO_BYTES];
    unsigned char ss2[CRYPTO_BYTES];
    
    printf("Benchmarking Optimized Implementation (C-only)...\n");
    
    for (int i = 0; i < TEST_ITERATIONS; i++) {
        // KeyGen
        uint64_t start = get_cycles();
        crypto_kem_keypair_opt(pk, sk);
        uint64_t end = get_cycles();
        add_profile(profiles, "KeyGen", end - start);
        
        // Encapsulation
        start = get_cycles();
        crypto_kem_enc_opt(ct, ss1, pk);
        end = get_cycles();
        add_profile(profiles, "Encap", end - start);
        
        // Decapsulation
        start = get_cycles();
        crypto_kem_dec_opt(ss2, ct, sk);
        end = get_cycles();
        add_profile(profiles, "Decap", end - start);
        
        // Verify shared secret matches
        assert(memcmp(ss1, ss2, CRYPTO_BYTES) == 0);
    }
}

// For aarch64 benchmark, we'll use external compilation approach
static void run_aarch64_benchmark_external(const char *output_file) {
    printf("Running AArch64 benchmark via external compilation...\n");
    
    // Create temporary C file for aarch64 benchmark
    FILE *f = fopen("/tmp/aarch64_bench.c", "w");
    if (!f) {
        printf("Error: Cannot create temporary benchmark file\n");
        return;
    }
    
    fprintf(f, "#include <stdio.h>\n");
    fprintf(f, "#include <stdint.h>\n");
    fprintf(f, "#include <string.h>\n");
    fprintf(f, "#include <assert.h>\n\n");
    
    // ARM64 cycle counter
    fprintf(f, "static inline uint64_t get_cycles(void) {\n");
    fprintf(f, "    uint64_t cycles;\n");
    fprintf(f, "    __asm__ volatile(\"mrs %%0, cntvct_el0\" : \"=r\" (cycles));\n");
    fprintf(f, "    return cycles;\n");
    fprintf(f, "}\n\n");
    
    // Include aarch64 headers and implementation
    fprintf(f, "#include \"../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768/api.h\"\n");
    fprintf(f, "#include \"../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768/params.h\"\n");
    fprintf(f, "#include \"../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768/kem.c\"\n");
    fprintf(f, "#include \"../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768/poly.c\"\n");
    fprintf(f, "#include \"../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768/symmetric.c\"\n");
    fprintf(f, "#ifdef SUPPORTS_SHAKE256_ASM\n");
    fprintf(f, "#include \"../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768/CE/fips202.c\"\n");
    fprintf(f, "#else\n");
    fprintf(f, "#include \"../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768/NO_CE/fips202.c\"\n");
    fprintf(f, "#endif\n\n");
    
    fprintf(f, "#define TEST_ITERATIONS 1000\n\n");
    
    fprintf(f, "int main() {\n");
    fprintf(f, "    unsigned char pk[CRYPTO_PUBLICKEYBYTES];\n");
    fprintf(f, "    unsigned char sk[CRYPTO_SECRETKEYBYTES];\n"); 
    fprintf(f, "    unsigned char ct[CRYPTO_CIPHERTEXTBYTES];\n");
    fprintf(f, "    unsigned char ss1[CRYPTO_BYTES];\n");
    fprintf(f, "    unsigned char ss2[CRYPTO_BYTES];\n");
    fprintf(f, "    \n");
    fprintf(f, "    uint64_t keygen_total = 0, encap_total = 0, decap_total = 0;\n");
    fprintf(f, "    \n");
    fprintf(f, "    for (int i = 0; i < TEST_ITERATIONS; i++) {\n");
    fprintf(f, "        uint64_t start, end;\n");
    fprintf(f, "        \n");
    fprintf(f, "        // KeyGen\n");
    fprintf(f, "        start = get_cycles();\n");
    fprintf(f, "        crypto_kem_keypair(pk, sk);\n");
    fprintf(f, "        end = get_cycles();\n");
    fprintf(f, "        keygen_total += (end - start);\n");
    fprintf(f, "        \n");
    fprintf(f, "        // Encapsulation\n");
    fprintf(f, "        start = get_cycles();\n");
    fprintf(f, "        crypto_kem_enc(ct, ss1, pk);\n");
    fprintf(f, "        end = get_cycles();\n");
    fprintf(f, "        encap_total += (end - start);\n");
    fprintf(f, "        \n");
    fprintf(f, "        // Decapsulation\n");
    fprintf(f, "        start = get_cycles();\n");
    fprintf(f, "        crypto_kem_dec(ss2, ct, sk);\n");
    fprintf(f, "        end = get_cycles();\n");
    fprintf(f, "        decap_total += (end - start);\n");
    fprintf(f, "        \n");
    fprintf(f, "        assert(memcmp(ss1, ss2, CRYPTO_BYTES) == 0);\n");
    fprintf(f, "    }\n");
    fprintf(f, "    \n");
    fprintf(f, "    printf(\"AArch64 Implementation Results:\\\\n\");\n");
    fprintf(f, "    printf(\"KeyGen: %%lu cycles (avg: %%lu)\\\\n\", keygen_total, keygen_total / TEST_ITERATIONS);\n");
    fprintf(f, "    printf(\"Encap: %%lu cycles (avg: %%lu)\\\\n\", encap_total, encap_total / TEST_ITERATIONS);\n");
    fprintf(f, "    printf(\"Decap: %%lu cycles (avg: %%lu)\\\\n\", decap_total, decap_total / TEST_ITERATIONS);\n");
    fprintf(f, "    \n");
    fprintf(f, "    return 0;\n");
    fprintf(f, "}\n");
    
    fclose(f);
    
    // Compile and run aarch64 benchmark
    printf("Compiling AArch64 benchmark...\n");
    system("cd /Users/chenpinhao/ntruplus && gcc -O3 -I. -o /tmp/aarch64_bench /tmp/aarch64_bench.c ../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768/asm/*.s -DSUPPORTS_SHAKE256_ASM ../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768/CE/f1600.S 2>/tmp/aarch64_compile_log.txt");
    
    printf("Running AArch64 benchmark...\n");
    system("/tmp/aarch64_bench > /tmp/aarch64_results.txt 2>&1");
    
    // Read and display results
    FILE *results = fopen("/tmp/aarch64_results.txt", "r");
    if (results) {
        char line[256];
        while (fgets(line, sizeof(line), results)) {
            printf("%s", line);
        }
        fclose(results);
    } else {
        printf("Error reading AArch64 results. Check compilation log:\n");
        system("cat /tmp/aarch64_compile_log.txt");
    }
}

int main() {
    printf("🎯 NTRU+ Implementation Comparison: Optimized (C) vs AArch64 (ASM)\n");
    printf("====================================================================\n");
    printf("Platform: ARM64 (Apple Silicon)\n");
    printf("Iterations: %d per measurement\n", TEST_ITERATIONS);
    printf("Measurement: ARM64 CNTVCT_EL0 cycle counter\n\n");
    
    profile_data_t opt_profiles = {0};
    
    // Benchmark optimized implementation
    benchmark_kem_operations_optimized(&opt_profiles);
    print_profiles(&opt_profiles, "Optimized Implementation (C-only)");
    
    // Run AArch64 benchmark externally due to assembly complexity
    run_aarch64_benchmark_external("/tmp/aarch64_results.txt");
    
    printf("\n=== Analysis Notes ===\n");
    printf("• Optimized Implementation: Pure C with compiler optimization (-O3)\n");
    printf("• AArch64 Implementation: C + hand-optimized AArch64 assembly\n");
    printf("• Assembly files: cbd.s, ntt.s, base.s, crepmod3.s, pack.s, add.s\n");
    printf("• Target functions: poly_cbd1, poly_sotp_encode/decode, poly_ntt, poly_basemul\n");
    printf("• Expected improvements in specialized polynomial operations\n");
    
    return 0;
}