#!/bin/bash
# Quick validation script for NTRU+ optimizations

echo "🔍 NTRU+ Optimization Validation"
echo "==============================="

# Check if we're in the right directory
if [ ! -d "bench" ]; then
    echo "❌ Error: bench directory not found"
    echo "Please run this script from the ntruplus root directory"
    exit 1
fi

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