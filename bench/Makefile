# NTRU+ Benchmark Suite Makefile
# Performance analysis for specialized functions in NTRU+ KEM operations

CC = gcc
CFLAGS = -O3 -march=native -Wall -Wextra -std=c99
INCLUDES = -I../../ntruplus-KpqC-Final/Optimized_Implementation/NTRU+768 \
           -I../../ntruplus-KpqC-Final/Optimized_Implementation/NTRU+768/fips202
LDFLAGS = -lm

# NTRU+ source files (relative to bench directory)
NTRU_ROOT = ../../ntruplus-KpqC-Final/Optimized_Implementation/NTRU+768
NTRU_SOURCES = $(NTRU_ROOT)/kem.c \
               $(NTRU_ROOT)/poly.c \
               $(NTRU_ROOT)/ntt.c \
               $(NTRU_ROOT)/symmetric.c \
               $(NTRU_ROOT)/randombytes.c \
               $(NTRU_ROOT)/fips202/fips202.c

# Main benchmark targets
BOTTLENECK_PROFILER = ntruplus_bottleneck_profiler
INDIVIDUAL_FUNCTION_TEST = function_speed_test
ASSEMBLY_COMPARISON = assembly_vs_c_comparison

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

# Assembly vs C comparison (if assembly files are available)
assembly-comparison: $(ASSEMBLY_COMPARISON)
	./$(ASSEMBLY_COMPARISON)

$(ASSEMBLY_COMPARISON): assembly_vs_c_comparison.c
	$(CC) $(CFLAGS) $(INCLUDES) $< $(NTRU_SOURCES) -o $@ $(LDFLAGS)

# Quick run (default benchmark)
run: bottleneck-analysis

# Run all available benchmarks
run-all: bottleneck-analysis function-test

# Clean up
clean:
	rm -f $(BOTTLENECK_PROFILER) $(INDIVIDUAL_FUNCTION_TEST) $(ASSEMBLY_COMPARISON) *.o

# Help
help:
	@echo "NTRU+ Benchmark Suite"
	@echo "====================="
	@echo ""
	@echo "Targets:"
	@echo "  bottleneck-analysis   - Main cost-benefit analysis (default)"
	@echo "  function-test         - Individual function speed testing"
	@echo "  assembly-comparison   - Compare C vs hand-written assembly"
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