# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an implementation package for NTRU+, a post-quantum cryptographic scheme that provides both Key Encapsulation Mechanism (KEM) and Public Key Encryption (PKE) variants. The repository contains multiple implementations optimized for different use cases and security levels.

## Repository Structure

The codebase is organized into four main implementation categories:

- **Reference_Implementation/**: Clean, readable implementations for understanding the algorithm
- **Optimized_Implementation/**: Performance-optimized C implementations 
- **Additional_Implementation/avx2/**: AVX2-optimized implementations using assembly code
- **KAT/**: Known Answer Tests for validation
- **scripts/**: Security analysis and testing scripts

Each implementation directory contains both `crypto_kem/` (Key Encapsulation) and `crypto_pke/` (Public Key Encryption) variants with parameter sets: 576, 768, 864, and 1152.

## Build Commands

Each implementation variant has its own Makefile. Navigate to the specific parameter directory to build:

### Reference and Optimized Implementations
```bash
# Navigate to desired implementation (example: Reference KEM with 768-bit security)
cd Reference_Implementation/crypto_kem/NTRU+KEM768/

# Build all targets
make all

# Build individual targets
make test          # Build test executable
make PQCgenKAT_kem # Build NIST KAT generator
make clean         # Clean build artifacts
```

### AVX2 Implementation
```bash
cd Additional_Implementation/avx2/crypto_kem/NTRU+KEM768/
make all
```

Note: AVX2 implementation requires compatible hardware and uses additional compiler flags (`-mavx2 -mbmi2 -mpopcnt -maes -march=native`).

## Key Files and Architecture

### Core Algorithm Files
- `kem.c/kem.h`: Key encapsulation mechanism implementation
- `poly.c/poly.h`: Polynomial arithmetic operations
- `ntt.c/ntt.h`: Number Theoretic Transform for efficient multiplication
- `params.h`: Cryptographic parameters (N, Q, key/ciphertext sizes)
- `api.h`: Standard NIST API interface

### Cryptographic Primitives
- `aes256ctr.c`: AES-256 in counter mode
- `sha256.c/sha512.c`: SHA hash functions  
- `symmetric.c`: Symmetric cryptographic operations
- `verify.c`: Constant-time comparison functions
- `reduce.c`: Modular reduction operations

### Testing and Validation
- `test.c`: Basic functionality tests
- `PQCgenKAT_kem.c`: NIST Known Answer Test generator
- `randombytes.c`: Random number generation for tests

### AVX2 Optimizations
The AVX2 implementation replaces C polynomial operations with assembly:
- `asm/ntt.s`, `asm/invntt.s`: Optimized NTT transforms
- `asm/basemul.s`: Fast base multiplication
- `asm/reduce.s`: Optimized modular reduction

## Parameter Sets

Each variant (576, 768, 864, 1152) represents different security levels and performance trade-offs:
- Higher numbers indicate stronger security but larger key/ciphertext sizes
- Parameter set 768 is commonly used for benchmarking

## Development Notes

- All Makefiles use gcc with strict warning flags and -O3 optimization
- The codebase follows NIST PQC submission standards
- Constant-time implementations prevent timing attacks
- AVX2 variants require x86-64 processors with AVX2 support