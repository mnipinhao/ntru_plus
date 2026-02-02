# Implementation Differences: Reference vs Optimized vs Additional (AVX2)

This document compares the three NTRU+ implementations in this repository, highlighting their key differences in terms of performance, architecture, and implementation approach.

## High-Level Overview

| Aspect | Reference Implementation | Optimized Implementation | Additional Implementation (AVX2) |
|--------|-------------------------|---------------------------|----------------------------------|
| **Purpose** | Clean, readable reference | Performance-optimized C code | Hardware-accelerated assembly |
| **Target Audience** | Academic research, verification | Production use, balanced performance | High-performance computing |
| **Hardware Requirements** | Standard C compiler | Standard C compiler | x86-64 with AVX2, BMI2, POPCNT, AES |
| **Code Complexity** | Simple, straightforward | Moderately optimized | Highly complex, hand-optimized |

## File Structure Comparison

### Common Files (All Implementations)
All three implementations share these core files:
- `api.h` - NIST API interface
- `params.h` - Cryptographic parameters
- `kem.c/kem.h` - Key encapsulation mechanism
- `test.c` - Testing framework
- `PQCgenKAT_kem.c` - NIST KAT generator
- `randombytes.c/randombytes.h` - Random number generation
- `rng.c/rng.h` - RNG for KAT generation
- `aes256ctr.c/aes256ctr.h` - AES-256 counter mode
- `symmetric.c/symmetric.h` - Symmetric cryptography
- `verify.c/verify.h` - Constant-time verification
- `cpucycles.c/cpucycles.h` - Performance measurement

### Reference vs Optimized Implementation
**Files Present in Both:**
- `poly.c/poly.h` (371 lines each) - Polynomial operations
- `ntt.c/ntt.h` - Number Theoretic Transform
- `reduce.c/reduce.h` - Modular reduction
- `sha256.c`, `sha512.c`, `sha2.h` - SHA hash functions

**Key Observation:** Reference and Optimized implementations have **identical file structure and sizes**, suggesting they may be the same codebase or very similar optimizations.

### Additional Implementation (AVX2) - Major Differences

**Significantly Different Files:**
- `poly.c` - **Only 42 lines** (vs 371 in others)
  - Most polynomial operations moved to assembly
  - Contains only high-level wrapper functions like `poly_crepmod3`
- `consts.c` - **New file** containing pre-computed constants
  - 1,628 NTT twiddle factors (`zetas`)
  - 1,632 inverse NTT factors (`zetas_inv`)
  - Aligned vector constants for AVX2 operations

**Missing Files (moved to assembly):**
- No `ntt.c`, `reduce.c`, `sha256.c`, `sha512.c` files
- Functionality implemented in assembly files

**New Assembly Directory (`asm/`):**
- `ntt.s` (9,702 bytes) - Forward NTT transform
- `invntt.s` (9,609 bytes) - Inverse NTT transform
- `basemul.s` (2,832 bytes) - Base multiplication
- `baseinv.s` (9,653 bytes) - Base inversion
- `reduce.s` (4,367 bytes) - Modular reduction
- `add.s` (1,808 bytes) - Addition operations
- `pack.s` (4,217 bytes) - Packing/unpacking
- `cbd.s` (2,869 bytes) - Centered binomial distribution

## Build System Differences

### Compiler Flags
**Reference & Optimized:**
```makefile
CFLAGS += -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls \
  -Wshadow -Wpointer-arith -O3 -fomit-frame-pointer
```

**AVX2 Implementation:**
```makefile
CFLAGS += -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls \
  -Wshadow -Wpointer-arith -mavx2 -mbmi2 -mpopcnt -maes \
  -march=native -mtune=native -O3 -fomit-frame-pointer
```

**Key AVX2 Additions:**
- `-mavx2` - Enable AVX2 instructions
- `-mbmi2` - Bit manipulation instructions 2
- `-mpopcnt` - Population count instruction
- `-maes` - AES instruction set
- `-march=native -mtune=native` - Target specific CPU architecture

### Source File Lists
**Reference & Optimized:**
```makefile
SOURCES= kem.c poly.c ntt.c aes256ctr.c sha256.c sha512.c symmetric.c reduce.c verify.c
```

**AVX2:**
```makefile
SOURCES= asm/add.s asm/baseinv.s asm/basemul.s asm/cbd.s asm/invntt.s asm/ntt.s \
         asm/pack.s asm/reduce.s aes256ctr.c consts.c kem.c poly.c symmetric.c \
         verify.c cpucycles.c
```

## Performance Architecture

### Reference/Optimized Implementation
- **Pure C implementation** with standard optimizations
- **Readable code structure** for algorithm understanding
- **Portable across architectures**
- **Moderate performance** suitable for most applications

### AVX2 Implementation
- **Hand-optimized assembly** for critical operations
- **Vectorized operations** using 256-bit AVX2 registers
- **Pre-computed constants** to minimize runtime calculations
- **Memory alignment** (`__attribute__((aligned(32)))`) for optimal vector loads
- **Specialized instructions** (BMI2 for bit manipulation, AES for cryptographic operations)

## Algorithm Implementation Differences

### Polynomial Operations
- **Reference/Optimized:** Complete C implementations in `poly.c`
- **AVX2:** Minimal C wrapper functions, core operations in assembly

### NTT (Number Theoretic Transform)
- **Reference/Optimized:** C implementation with standard optimizations
- **AVX2:** Hand-written assembly using AVX2 vector instructions for parallel processing

### Constants and Precomputation
- **Reference/Optimized:** Constants defined in header files
- **AVX2:** Large precomputed tables in `consts.c` with vector-friendly layouts

## Security Considerations

All implementations maintain:
- **Constant-time operations** to prevent timing attacks
- **Same cryptographic parameters** across all variants
- **Identical API interface** for seamless replacement
- **NIST compliance** with standard test vectors

## Development Notes

- **Reference/Optimized** appear to be nearly identical, suggesting the "optimized" version may use compiler-level optimizations rather than algorithmic changes
- **AVX2 implementation** represents a complete architectural redesign for maximum performance
- **Assembly code quality** in AVX2 version suggests professional optimization work
- **Memory alignment requirements** in AVX2 version require careful integration considerations