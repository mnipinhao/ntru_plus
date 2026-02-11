#!/bin/bash
# NTRU+ Optimization Workspace Setup Script (Fixed Version)
# Creates improved repository structure with complete file copying

set -e  # Exit on any error

echo "🚀 Setting up NTRU+ Optimization Workspace (Fixed)"
echo "================================================="

# Check if we're in the right directory
if [ ! -d "ntruplus-KpqC-Final" ]; then
    echo "❌ Error: ntruplus-KpqC-Final directory not found"
    echo "Please run this script from the directory containing ntruplus-KpqC-Final"
    exit 1
fi

echo "📁 Creating improved directory structure..."

# Create main directory structure (no baseline duplication)
mkdir -p optimized
mkdir -p bench/{framework,tests,results/comparison_reports}
mkdir -p tools
mkdir -p docs
mkdir -p scripts

echo "📋 Setting up optimization workspace..."

# Copy complete ntruplus-KpqC-Final to optimized workspace
if [ ! -d "optimized/ntruplus" ]; then
    echo "📦 Copying complete implementation to optimization workspace..."
    cp -r ntruplus-KpqC-Final optimized/ntruplus
    echo "✅ Complete optimization workspace created"
else
    echo "ℹ️  Optimization workspace already exists, skipping copy"
fi

# Create baseline symlink for easy reference (no duplication)
if [ ! -L "baseline" ]; then
    echo "🔗 Creating baseline reference..."
    ln -s ntruplus-KpqC-Final baseline
    echo "✅ Baseline reference created (symlink to avoid duplication)"
fi

echo "🔧 Setting up benchmarking infrastructure..."

# Create benchmarking Makefile
cat > bench/Makefile << 'EOF'
# NTRU+ Benchmarking Suite Makefile (Fixed)
CC = gcc
CFLAGS = -O3 -march=native -Wall -Wextra -std=c99

# Paths to implementations
BASELINE_ROOT = ../baseline
OPTIMIZED_ROOT = ../optimized/ntruplus
TARGET_PARAM = NTRU+768

# Include paths for both implementations
BASELINE_INCLUDES = -I$(BASELINE_ROOT)/Optimized_Implementation/$(TARGET_PARAM) \
                   -I$(BASELINE_ROOT)/Optimized_Implementation/$(TARGET_PARAM)/fips202
OPTIMIZED_INCLUDES = -I$(OPTIMIZED_ROOT)/Optimized_Implementation/$(TARGET_PARAM) \
                    -I$(OPTIMIZED_ROOT)/Optimized_Implementation/$(TARGET_PARAM)/fips202

# Source files
BASELINE_SOURCES = $(BASELINE_ROOT)/Optimized_Implementation/$(TARGET_PARAM)/kem.c \
                  $(BASELINE_ROOT)/Optimized_Implementation/$(TARGET_PARAM)/poly.c \
                  $(BASELINE_ROOT)/Optimized_Implementation/$(TARGET_PARAM)/ntt.c \
                  $(BASELINE_ROOT)/Optimized_Implementation/$(TARGET_PARAM)/symmetric.c \
                  $(BASELINE_ROOT)/Optimized_Implementation/$(TARGET_PARAM)/randombytes.c \
                  $(BASELINE_ROOT)/Optimized_Implementation/$(TARGET_PARAM)/fips202/fips202.c

OPTIMIZED_SOURCES = $(OPTIMIZED_ROOT)/Optimized_Implementation/$(TARGET_PARAM)/kem.c \
                   $(OPTIMIZED_ROOT)/Optimized_Implementation/$(TARGET_PARAM)/poly.c \
                   $(OPTIMIZED_ROOT)/Optimized_Implementation/$(TARGET_PARAM)/ntt.c \
                   $(OPTIMIZED_ROOT)/Optimized_Implementation/$(TARGET_PARAM)/symmetric.c \
                   $(OPTIMIZED_ROOT)/Optimized_Implementation/$(TARGET_PARAM)/randombytes.c \
                   $(OPTIMIZED_ROOT)/Optimized_Implementation/$(TARGET_PARAM)/fips202/fips202.c

BUILDDIR = build
RESULTSDIR = results

.PHONY: all clean directories test-baseline test-optimized compare

all: directories test-baseline test-optimized

directories:
	@mkdir -p $(BUILDDIR) $(RESULTSDIR)

test-baseline: directories
	@echo "🔬 Building baseline implementation test..."
	$(CC) $(CFLAGS) $(BASELINE_INCLUDES) -o $(BUILDDIR)/test_baseline \
		$(BASELINE_SOURCES) $(BASELINE_ROOT)/Optimized_Implementation/$(TARGET_PARAM)/test/test.c

test-optimized: directories
	@echo "🚀 Building optimized implementation test..."
	$(CC) $(CFLAGS) $(OPTIMIZED_INCLUDES) -o $(BUILDDIR)/test_optimized \
		$(OPTIMIZED_SOURCES) $(OPTIMIZED_ROOT)/Optimized_Implementation/$(TARGET_PARAM)/test/test.c

# Quick functionality test
run-baseline: test-baseline
	@echo "🧪 Running baseline test..."
	@./$(BUILDDIR)/test_baseline

run-optimized: test-optimized
	@echo "🧪 Running optimized test..."
	@./$(BUILDDIR)/test_optimized

# Generate KAT files for comparison
kat-baseline: directories
	@echo "📋 Generating baseline KAT..."
	$(CC) $(CFLAGS) $(BASELINE_INCLUDES) -o $(BUILDDIR)/kat_baseline \
		$(BASELINE_SOURCES) $(BASELINE_ROOT)/KAT/crypto_kem/NTRU+KEM768/PQCgenKAT_kem.c \
		$(BASELINE_ROOT)/KAT/crypto_kem/NTRU+KEM768/aes.c \
		$(BASELINE_ROOT)/KAT/crypto_kem/NTRU+KEM768/rng.c
	cd $(BUILDDIR) && ./kat_baseline
	@mv $(BUILDDIR)/PQCkemKAT_*.rsp $(RESULTSDIR)/baseline_kat.rsp
	@echo "✅ Baseline KAT saved to $(RESULTSDIR)/baseline_kat.rsp"

kat-optimized: directories
	@echo "📋 Generating optimized KAT..."
	$(CC) $(CFLAGS) $(OPTIMIZED_INCLUDES) -o $(BUILDDIR)/kat_optimized \
		$(OPTIMIZED_SOURCES) $(OPTIMIZED_ROOT)/KAT/crypto_kem/NTRU+KEM768/PQCgenKAT_kem.c \
		$(OPTIMIZED_ROOT)/KAT/crypto_kem/NTRU+KEM768/aes.c \
		$(OPTIMIZED_ROOT)/KAT/crypto_kem/NTRU+KEM768/rng.c
	cd $(BUILDDIR) && ./kat_optimized
	@mv $(BUILDDIR)/PQCkemKAT_*.rsp $(RESULTSDIR)/optimized_kat.rsp
	@echo "✅ Optimized KAT saved to $(RESULTSDIR)/optimized_kat.rsp"

# Compare KAT files
compare-kat: kat-baseline kat-optimized
	@echo "🔍 Comparing KAT files..."
	@if diff -q $(RESULTSDIR)/baseline_kat.rsp $(RESULTSDIR)/optimized_kat.rsp > /dev/null; then \
		echo "✅ KAT comparison PASSED - implementations are functionally identical"; \
	else \
		echo "❌ KAT comparison FAILED - implementations differ"; \
		echo "First few differences:"; \
		diff $(RESULTSDIR)/baseline_kat.rsp $(RESULTSDIR)/optimized_kat.rsp | head -10; \
		exit 1; \
	fi

clean:
	rm -rf $(BUILDDIR) $(RESULTSDIR)/*.rsp

help:
	@echo "NTRU+ Benchmarking Suite (Fixed)"
	@echo "================================"
	@echo ""
	@echo "Setup and Testing:"
	@echo "  all              - Build both implementations"
	@echo "  run-baseline     - Test baseline functionality"
	@echo "  run-optimized    - Test optimized functionality"
	@echo ""
	@echo "Correctness Validation:"
	@echo "  kat-baseline     - Generate baseline KAT"
	@echo "  kat-optimized    - Generate optimized KAT"
	@echo "  compare-kat      - Compare KAT files (main validation)"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean            - Remove build artifacts"
	@echo "  help             - Show this help"
	@echo ""
	@echo "Quick Validation Workflow:"
	@echo "  make all && make compare-kat"
EOF

echo "🛠️  Creating validation tools..."

# Create quick validation script
cat > scripts/validate_optimization.sh << 'EOF'
#!/bin/bash
# Quick validation script for NTRU+ optimizations

echo "🔍 NTRU+ Optimization Validation"
echo "==============================="

cd bench

echo ""
echo "1. 🏗️  Building implementations..."
make all

echo ""
echo "2. 🧪 Testing functionality..."
echo "   Testing baseline..."
make run-baseline
echo "   Testing optimized..."
make run-optimized

echo ""
echo "3. 📋 Validating correctness with KAT..."
make compare-kat

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Validation SUCCESSFUL!"
    echo "   ✅ Both implementations build correctly"
    echo "   ✅ Both implementations run without errors"
    echo "   ✅ KAT outputs are identical"
    echo ""
    echo "🚀 Ready for performance benchmarking!"
else
    echo ""
    echo "❌ Validation FAILED!"
    echo "   Please fix correctness issues before benchmarking"
    exit 1
fi
EOF

chmod +x scripts/validate_optimization.sh

echo "📚 Creating updated documentation..."

# Update WORKFLOW.md section for fixed approach
cat > docs/FIXED_WORKFLOW_SECTION.md << 'EOF'
# 🔧 Fixed Workflow - Phase 1: Initial Setup

## Step 1.1: Repository Initialization (Fixed)

```bash
# Navigate to your project root (where ntruplus-KpqC-Final exists)
cd /path/to/your/ntruplus

# Run the fixed setup script
./scripts/setup_workspace_fixed.sh

# This creates:
# - optimized/ntruplus-KpqC-Final/ (complete copy for modification)
# - baseline -> ntruplus-KpqC-Final (symlink, no duplication)
# - bench/ (benchmarking infrastructure)
# - tools/, docs/, scripts/ (development utilities)
```

## Step 1.2: Verify Setup Works (Fixed)

```bash
# Quick validation of the entire setup
./scripts/validate_optimization.sh

# Expected output:
# 🔍 NTRU+ Optimization Validation
# ===============================
# 1. 🏗️  Building implementations...
# 2. 🧪 Testing functionality...
# 3. 📋 Validating correctness with KAT...
# 🎉 Validation SUCCESSFUL!
```

## Step 1.3: Understand the Structure

```bash
# Your baseline (original, read-only reference)
ls baseline/  # -> points to ntruplus-KpqC-Final

# Your workspace (complete copy for modification)  
ls optimized/ntruplus-KpqC-Final/
# ├── Optimized_Implementation/NTRU+768/    # Your main target
# ├── KAT/crypto_kem/NTRU+KEM768/          # KAT files (complete)
# └── ... (all other implementations)

# Benchmarking infrastructure
ls bench/
# ├── Makefile          # Ready-to-use build system
# ├── build/            # Compiled binaries
# └── results/          # KAT and benchmark results
```

## Step 1.4: Ready for Optimization

```bash
# Navigate to your optimization target
cd optimized/ntruplus-KpqC-Final/Optimized_Implementation/NTRU+768

# Edit your target function (example: poly_cbd1 in poly.c)
vim poly.c

# Validate your change
cd ../../../../bench
make compare-kat    # Must pass before performance testing

# If KAT passes, you're ready for benchmarking!
```
EOF

echo "✅ Workspace setup complete!"
echo ""
echo "🎯 Structure Created:"
echo "1. ✅ No duplication - baseline is a symlink"
echo "2. ✅ Complete file copying - all KAT files included"  
echo "3. ✅ Working validation - KAT comparison works out-of-the-box"
echo "4. ✅ Clean naming - optimized/ntruplus/ (shorter path)"
echo ""
echo "🚀 Next Steps:"
echo "1. ./scripts/validate_optimization.sh     # Verify everything works"
echo "2. cd optimized/ntruplus/Optimized_Implementation/NTRU+768"
echo "3. vim poly.c                            # Make your optimization"
echo "4. cd ../../../../bench && make compare-kat  # Validate correctness"
echo ""
echo "📖 See WORKFLOW.md for complete optimization process"