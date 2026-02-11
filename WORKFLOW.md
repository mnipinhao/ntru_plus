# 🚀 NTRU+ Optimization Workflow Guide

## Overview

This guide provides a step-by-step workflow for optimizing NTRU+ implementation functions while maintaining correctness and measuring performance improvements systematically.

**Target Audience**: Performance Engineers, Cryptographic Developers  
**Prerequisites**: Basic knowledge of C, cryptography, and command-line tools

---

## 🎯 Quick Start Checklist

- [ ] Set up repository structure
- [ ] Verify baseline functionality  
- [ ] Test benchmarking framework
- [ ] Create your first optimization
- [ ] Validate correctness with KAT
- [ ] Measure performance improvement

---

## 📋 Phase 1: Initial Setup

### Step 1.1: Repository Initialization

```bash
# Navigate to your project root (where ntruplus-KpqC-Final exists)
cd /path/to/your/ntruplus

# Run the setup script (creates complete workspace)
./scripts/setup_workspace.sh

# This creates:
# - optimized/ntruplus/ (complete copy for modification)
# - baseline -> ntruplus-KpqC-Final (symlink, no duplication)
# - bench/ (working benchmarking infrastructure)
# - Complete KAT files and test data
```

### Step 1.2: Verify Setup Works

```bash
# Quick validation of the entire setup
./scripts/validate_optimization.sh

# Expected output:
# 🔍 NTRU+ Optimization Validation
# 1. 🏗️  Building implementations...
# 2. 🧪 Testing functionality...
# 3. 📋 Validating correctness with KAT...
# 🎉 Validation SUCCESSFUL!
```

### Step 1.3: Understand the Structure

```bash
# Your baseline (symlink to original, no duplication)
ls -la baseline  # -> ntruplus-KpqC-Final

# Your workspace (complete copy for modification)
ls optimized/ntruplus/
# ├── Optimized_Implementation/
# │   ├── NTRU+576/, NTRU+768/, NTRU+864/, NTRU+1152/
# ├── Additional_Implementation/
# ├── Reference_Implementation/ 
# └── KAT/                    # ✅ Complete KAT files
#     └── crypto_kem/
#         └── NTRU+KEM768/    # ✅ All KAT files present

# Working benchmarking infrastructure
ls bench/
# ├── Makefile      # ✅ Ready-to-use, tests both implementations
# ├── build/        # Compiled binaries
# └── results/      # KAT comparison results
```

---

## 🔧 Phase 2: The Optimization Cycle

### Step 2.1: Navigate to Your Target

```bash
# Go to your optimization target (NTRU+768)
cd optimized/ntruplus/Optimized_Implementation/NTRU+768

# Verify the structure
ls -la
# ├── kem.c, poly.c, ntt.c, symmetric.c  # ✅ All source files
# ├── api.h, params.h, poly.h           # ✅ All headers  
# ├── fips202/                          # ✅ Hash functions
# ├── test/test.c                       # ✅ Test file
# └── Makefile                          # ✅ Build system
```

### Step 2.2: Select Optimization Target

Based on the profiling analysis, prioritize functions by impact:

**High Priority Targets** (from previous analysis):
1. `poly_ntt` (18.5% of runtime)
2. `poly_baseinv` (16.6% of runtime)  
3. `hash_g` (13.1% of runtime)

**Your Specialized Targets**:
4. `poly_cbd1`
5. `poly_sotp_encode`
6. `poly_sotp_decode`

### Step 2.3: Make Your Optimization

```bash
# Example: Optimize poly_cbd1 function
vim poly.c

# Make your changes to the target function
# Save and exit
```

### Step 2.4: Quick Build Test

```bash
# Optional: Quick local build test
make clean && make test
./build/test  # Should run without errors
```

---

## ✅ Phase 3: Correctness Verification

### Step 3.1: Automated KAT Validation

```bash
# Navigate to benchmark directory
cd ../../../../bench

# Compare baseline vs optimized KAT outputs  
make compare-kat

# Expected output:
# 📋 Generating baseline KAT...
# ✅ Baseline KAT saved to results/baseline_kat.rsp
# 📋 Generating optimized KAT...  
# ✅ Optimized KAT saved to results/optimized_kat.rsp
# 🔍 Comparing KAT files...
# ✅ KAT comparison PASSED - implementations are functionally identical
```

### Step 3.2: If KAT Validation Fails

```bash
# KAT validation failed - debug your optimization
echo "❌ KAT comparison FAILED - implementations differ"

# Check the differences
diff bench/results/baseline_kat.rsp bench/results/optimized_kat.rsp | head -20

# Common fixes:
# 1. Check for uninitialized variables
# 2. Verify array bounds  
# 3. Ensure deterministic behavior
# 4. Check for typos in your optimization
```

### Step 3.3: Extended Correctness Testing

```bash
# Run functionality tests on both implementations
make run-baseline    # Should complete without errors
make run-optimized   # Should complete without errors

# Both should produce identical behavior
```

---

## 📊 Phase 4: Performance Measurement

### Step 4.1: Individual Function Benchmark

Use your existing benchmark infrastructure in the `bench/` directory:

```bash
# Use your comprehensive benchmark suite
cd bench
make comprehensive-analysis  # Existing detailed profiler

# Use specialized function benchmarks
make aarch64-benchmark      # If testing assembly optimizations
```

### Step 4.2: Integration with Existing Tools

Your optimized implementation can be integrated with the existing benchmark tools:

```bash
# Navigate to your existing benchmark directory  
cd ../bench  # Your original comprehensive benchmark suite

# Update benchmark to point to optimized implementation
# Modify paths in Makefile or create new targets
```

---

## 📈 Phase 5: Results Analysis

### Step 5.1: Interpreting Benchmark Results

**Performance Metrics to Track**:
- **Cycle Count**: Raw CPU cycles (most accurate)
- **Speedup Factor**: `baseline_cycles / optimized_cycles`
- **Percentage Improvement**: `(baseline - optimized) / baseline * 100%`
- **Statistical Confidence**: Min/Max/Median across iterations

**Example Output**:
```
🚀 Optimization Results Summary
===============================

Function: poly_cbd1
├── Baseline:    15 cycles (avg)
├── Optimized:    5 cycles (avg)  
├── Speedup:     3.0x
└── Improvement: 66.7%

KEM Operations:
├── KeyGen:      2.1x speedup (450 → 214 cycles)
├── Encap:       1.8x speedup (280 → 156 cycles)
├── Decap:       2.3x speedup (270 → 117 cycles)
└── Overall:     2.1x speedup (1000 → 487 cycles)
```

### Step 5.2: Success Criteria

**Correctness Requirements** (Must Pass):
- [ ] KAT output identical to baseline
- [ ] Extended correctness tests pass
- [ ] No functional regressions

**Performance Targets** (Goals):
- [ ] Individual function speedup > 1.5x
- [ ] Overall KEM operation improvement > 10%
- [ ] No performance regressions in other functions

### Step 5.3: Documentation Updates

Update `OPTIMIZATION_LOG.md`:
```markdown
## Optimization Entry: poly_cbd1 SIMD Implementation

**Date**: 2026-02-11
**Target Function**: poly_cbd1
**Optimization Type**: SIMD vectorization
**Engineer**: [Your Name]

### Changes Made:
- Replaced scalar bit operations with NEON SIMD
- Vectorized 16-byte parallel processing
- Optimized register allocation

### Results:
- ✅ KAT validation: PASSED
- ⚡ Performance: 3.0x speedup (15 → 5 cycles)
- 📊 Overall impact: 2.1x KEM operation speedup

### Lessons Learned:
- SIMD vectorization highly effective for bit manipulation
- Register pressure requires careful optimization
- Compiler auto-vectorization was insufficient
```

---

## 🔄 Phase 6: Iteration and Scaling

### Step 6.1: Rapid Optimization Iteration

```bash
# Quick iteration loop:
# 1. Edit optimization
cd optimized/ntruplus/Optimized_Implementation/NTRU+768
vim poly.c

# 2. Validate correctness
cd ../../../../bench && make compare-kat

# 3. If passes, measure performance
# 4. If fails, debug and repeat
```

### Step 6.2: Multiple Function Optimization

```bash
# Work on different functions
cd optimized/ntruplus/Optimized_Implementation/NTRU+768

# Optimize poly_cbd1
vim poly.c  # Edit poly_cbd1 function
cd ../../../../bench && make compare-kat  # Validate

# Optimize poly_sotp_encode  
cd ../optimized/ntruplus/Optimized_Implementation/NTRU+768
vim poly.c  # Edit poly_sotp_encode function
cd ../../../../bench && make compare-kat  # Validate

# Each optimization can be validated independently
```

---

## 🛠️ Available Tools

### Benchmarking Makefile Targets

```bash
cd bench

# Build and test
make all                # Build both baseline and optimized
make run-baseline       # Test baseline functionality
make run-optimized      # Test optimized functionality

# Correctness validation
make kat-baseline       # Generate baseline KAT  
make kat-optimized      # Generate optimized KAT
make compare-kat        # Compare KATs (main validation)

# Maintenance
make clean              # Clean build artifacts
make help               # Show all available targets
```

### Validation Scripts

```bash
# Quick validation (from project root)
./scripts/validate_optimization.sh

# Expected workflow:
# 1. Builds both implementations
# 2. Tests functionality  
# 3. Compares KAT outputs
# 4. Reports success/failure
```

---

## 🚨 Troubleshooting

### Common Issues and Solutions

**Build Errors**:
```bash
# Check include paths
cd optimized/ntruplus/Optimized_Implementation/NTRU+768
make clean && make test

# Verify all source files present
ls -la *.c *.h fips202/
```

**KAT Generation Fails**:
```bash
# Check KAT dependencies
ls ../../KAT/crypto_kem/NTRU+KEM768/
# Should contain: PQCgenKAT_kem.c, aes.c, rng.c, aes.h, rng.h

# Manual KAT test
cd bench
make kat-baseline  # Should work without errors
```

**Validation Script Fails**:
```bash
# Run components individually
cd bench
make all           # Should build both implementations
make run-baseline  # Should run without errors  
make run-optimized # Should run without errors
make compare-kat   # Should pass for unmodified code
```

---

## 🎯 Success Checklist

Before starting optimization work, verify:

- [ ] `./scripts/setup_workspace.sh` completes successfully
- [ ] `./scripts/validate_optimization.sh` reports "Validation SUCCESSFUL"  
- [ ] `cd bench && make compare-kat` passes for unmodified code
- [ ] Both baseline and optimized tests run without errors
- [ ] KAT files are generated and compared correctly

**If all items pass**: ✅ You're ready to start optimizing!  
**If any item fails**: ❌ Debug the specific issue before proceeding

---

## 🚀 What's Ready

✅ **Clean directory structure** - No duplication, clear paths  
✅ **Complete copying** - All KAT files and dependencies included  
✅ **Working validation** - KAT comparison works correctly  
✅ **Automated setup** - One script creates entire workspace  
✅ **Clear workflow** - Step-by-step process from setup to optimization  
✅ **Professional infrastructure** - Ready for systematic optimization work

**Result**: You can now proceed with confidence to optimize your NTRU+ functions knowing that correctness validation works correctly!

---

**📝 Document Version**: 2.0  
**📅 Last Updated**: February 2026  
**🔄 Status**: Clean, updated, ready for use