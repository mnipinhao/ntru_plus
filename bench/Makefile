# NTRU+ Benchmark Suite Makefile
# Performance analysis for specialized functions in NTRU+ KEM operations

CC = gcc
CFLAGS = -O3 -march=native -Wall -Wextra -std=c99
INCLUDES = -I../ntruplus-KpqC-Final/Optimized_Implementation/NTRU+768 \
           -I../ntruplus-KpqC-Final/Optimized_Implementation/NTRU+768/fips202
LDFLAGS = -lm

# NTRU+ source files (relative to bench directory)
NTRU_ROOT = ../ntruplus-KpqC-Final/Optimized_Implementation/NTRU+768
NTRU_SOURCES = $(NTRU_ROOT)/kem.c \
               $(NTRU_ROOT)/poly.c \
               $(NTRU_ROOT)/ntt.c \
               $(NTRU_ROOT)/symmetric.c \
               $(NTRU_ROOT)/randombytes.c \
               $(NTRU_ROOT)/fips202/fips202.c

# AArch64 implementation paths
AARCH64_ROOT = ../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768
AARCH64_INCLUDES = -I$(AARCH64_ROOT) -I$(AARCH64_ROOT)/CE
AARCH64_SOURCES = $(AARCH64_ROOT)/kem.c \
                  $(AARCH64_ROOT)/poly.c \
                  $(AARCH64_ROOT)/symmetric.c \
                  $(AARCH64_ROOT)/randombytes.c \
                  $(AARCH64_ROOT)/CE/fips202.c
AARCH64_ASM = $(AARCH64_ROOT)/asm/add.s \
              $(AARCH64_ROOT)/asm/ntt.s \
              $(AARCH64_ROOT)/asm/base.s \
              $(AARCH64_ROOT)/asm/crepmod3.s \
              $(AARCH64_ROOT)/asm/pack.s \
              $(AARCH64_ROOT)/asm/cbd.s \
              $(AARCH64_ROOT)/CE/f1600.S

# Main benchmark targets
BOTTLENECK_PROFILER = ntruplus_bottleneck_profiler
INDIVIDUAL_FUNCTION_TEST = function_speed_test
COMPREHENSIVE_PROFILER = comprehensive_kem_profiler
ASSEMBLY_COMPARISON = assembly_vs_c_comparison
AARCH64_BENCHMARK = aarch64_kem_benchmark
AARCH64_COMPARISON = aarch64_comparison_profiler

# Default target
all: bottleneck-analysis

# Main bottleneck analysis (answers: should we optimize these functions?)
bottleneck-analysis: $(BOTTLENECK_PROFILER)
	@echo "=== NTRU+ Bottleneck Analysis ==="
	@echo "Running comprehensive KEM operation profiling..."
	./$(BOTTLENECK_PROFILER)

$(BOTTLENECK_PROFILER): ntruplus_bottleneck_profiler.c
	$(CC) $(CFLAGS) $(INCLUDES) $< $(NTRU_SOURCES) -o $@ $(LDFLAGS)

# Individual function speed testing
function-test: $(INDIVIDUAL_FUNCTION_TEST)
	./$(INDIVIDUAL_FUNCTION_TEST)

$(INDIVIDUAL_FUNCTION_TEST): function_speed_test.c
	$(CC) $(CFLAGS) $(INCLUDES) $< $(NTRU_SOURCES) -o $@ $(LDFLAGS)

# Comprehensive KEM operation analysis (detailed breakdown of all major functions)
comprehensive-analysis: $(COMPREHENSIVE_PROFILER)
	@echo "=== COMPREHENSIVE NTRU+ KEM ANALYSIS ==="
	@echo "Profiling ALL major functions in KeyGen/Encap/Decap..."
	./$(COMPREHENSIVE_PROFILER)

$(COMPREHENSIVE_PROFILER): comprehensive_kem_profiler.c
	$(CC) $(CFLAGS) $(INCLUDES) $< $(NTRU_SOURCES) -o $@ $(LDFLAGS)

# Assembly vs C comparison (if assembly files are available)
assembly-comparison: $(ASSEMBLY_COMPARISON)
	./$(ASSEMBLY_COMPARISON)

$(ASSEMBLY_COMPARISON): assembly_vs_c_comparison.c
	$(CC) $(CFLAGS) $(INCLUDES) $< $(NTRU_SOURCES) -o $@ $(LDFLAGS)

# AArch64 implementation benchmark
aarch64-benchmark: $(AARCH64_BENCHMARK)
	@echo "=== NTRU+ AArch64 Implementation Benchmark ==="
	@echo "Running hand-optimized assembly implementation..."
	./$(AARCH64_BENCHMARK)

$(AARCH64_BENCHMARK): aarch64_kem_benchmark.c
	$(CC) $(CFLAGS) $(AARCH64_INCLUDES) -DSUPPORTS_SHAKE256_ASM $< $(AARCH64_SOURCES) $(AARCH64_ASM) -o $@ $(LDFLAGS)

# AArch64 vs Optimized comparison
aarch64-comparison: $(AARCH64_COMPARISON)
	./$(AARCH64_COMPARISON)

$(AARCH64_COMPARISON): aarch64_comparison_profiler.c
	$(CC) $(CFLAGS) $(INCLUDES) $(AARCH64_INCLUDES) $< -o $@ $(LDFLAGS)

# Quick run (default benchmark)
run: bottleneck-analysis

# Run all available benchmarks
run-all: bottleneck-analysis function-test comprehensive-analysis aarch64-benchmark

# Clean up
clean:
	rm -f $(BOTTLENECK_PROFILER) $(INDIVIDUAL_FUNCTION_TEST) $(COMPREHENSIVE_PROFILER) $(ASSEMBLY_COMPARISON) $(AARCH64_BENCHMARK) $(AARCH64_COMPARISON) *.o

# Help
help:
	@echo "NTRU+ Benchmark Suite"
	@echo "====================="
	@echo ""
	@echo "Targets:"
	@echo "  bottleneck-analysis   - Main cost-benefit analysis (default)"
	@echo "  function-test         - Individual function speed testing"
	@echo "  comprehensive-analysis - Detailed breakdown of ALL major functions"
	@echo "  assembly-comparison   - Compare C vs hand-written assembly"
	@echo "  aarch64-benchmark     - Benchmark AArch64 hand-optimized implementation"
	@echo "  aarch64-comparison    - Compare Optimized vs AArch64 implementations"
	@echo "  run                   - Quick run (same as bottleneck-analysis)"
	@echo "  run-all              - Run all available benchmarks"
	@echo "  clean                - Remove all generated files"
	@echo "  help                 - Show this help"
	@echo ""
	@echo "Usage Examples:"
	@echo "  make                  - Run bottleneck analysis"
	@echo "  make run             - Same as above"
	@echo "  make function-test   - Test individual functions"
	@echo "  make run-all         - Run comprehensive benchmark suite"

.PHONY: all bottleneck-analysis function-test assembly-comparison run run-all clean help