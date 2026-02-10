# NTRU vs NTRU+ Implementation Comparison

This repository contains both the original NTRU implementation and the NTRU+ implementation, allowing for direct comparison and analysis of these post-quantum cryptographic schemes.

## Repository Structure

```
ntru-vs-ntruplus/
├── README.md                        # This file - comparison documentation
├── CLAUDE.md                        # AI assistant configuration
│
├── ntru/                            # Original NTRU Implementation
│   └── NIST-PQ-Submission-NTRU-20201016/
│       └── Reference_Implementation, Optimized_Implementation, etc.
│
└── ntruplus/                        # NTRU+ Implementation
    ├── Reference_Implementation/    # Reference C implementation
    ├── Optimized_Implementation/    # Optimized C implementation
    ├── Additional_Implementation/   # AVX2 optimized implementation
    ├── KAT/                         # Known Answer Tests
    ├── scripts/                     # Build and test utilities
    ├── impl-diff.md                 # Detailed implementation differences
    └── NTRU+_License.txt           # License information
```

## Overview

This document compares the NIST-PQ-Submission-NTRU-20201016 implementation (ntruhps2048677) with the NTRU+ implementation (NTRU+KEM768), highlighting their fundamental differences in cryptographic design and implementation approach.

## Algorithm Overview

| Aspect | NTRU HPS (ntruhps2048677) | NTRU+ (NTRU+KEM768) |
|--------|-------------------------|---------------------|
| **Scheme Type** | Classical NTRU with HPS variant | NTRU+ (Enhanced NTRU) |
| **Ring Structure** | Z[X]/(X^N - 1) | Z_q[X]/(X^N - X^{N/2} + 1) |
| **Submission** | NIST PQC Round 3 Finalist | Independent research/newer variant |
| **Design Philosophy** | Conservative, well-studied | Modern optimizations |

## Cryptographic Parameters Comparison

### NTRU HPS (ntruhps2048677)
```c
#define NTRU_N 677                    // Ring dimension
#define NTRU_LOGQ 11                  // log₂(q) = 11
#define NTRU_Q (1 << NTRU_LOGQ)      // q = 2048
#define NTRU_WEIGHT (NTRU_Q/8 - 2)   // Weight = 254

// Key and ciphertext sizes
#define CRYPTO_SECRETKEYBYTES 1234    // Secret key: 1,234 bytes
#define CRYPTO_PUBLICKEYBYTES 930     // Public key: 930 bytes
#define CRYPTO_CIPHERTEXTBYTES 930    // Ciphertext: 930 bytes
#define CRYPTO_BYTES 32               // Shared secret: 32 bytes
```

### NTRU+ (NTRU+KEM768)
```c
#define NTRUPLUS_N 768                // Ring dimension
#define NTRUPLUS_Q 3457              // Modulus q = 3457

// Key and ciphertext sizes
#define NTRUPLUS_SECRETKEYBYTES 2336  // Secret key: 2,336 bytes
#define NTRUPLUS_PUBLICKEYBYTES 1152  // Public key: 1,152 bytes
#define NTRUPLUS_CIPHERTEXTBYTES 1152 // Ciphertext: 1,152 bytes
#define NTRUPLUS_SSBYTES 32          // Shared secret: 32 bytes
```

### Key Differences in Parameters
1. **Ring Dimension**: NTRU uses N=677, NTRU+ uses N=768 (power-of-2 friendly)
2. **Modulus**: NTRU uses q=2048 (power-of-2), NTRU+ uses q=3457 (prime)
3. **Ring Polynomial**: Different irreducible polynomials
4. **Key Sizes**: NTRU+ has larger keys but more structured parameters

## File Structure and Implementation Architecture

### NTRU HPS Implementation (32 files)
**Core Algorithm Files:**
- `owcpa.c/owcpa.h` - One-Way CPA-secure PKE
- `poly.c/poly.h` - Polynomial operations
- `sample.c/sample.h` - Sampling algorithms
- `kem.c/kem.h` - KEM wrapper

**Specialized Components:**
- `pack3.c`, `packq.c` - Coefficient packing/unpacking
- `poly_lift.c` - Polynomial lifting operations
- `poly_mod.c` - Modular reduction
- `poly_r2_inv.c` - R₂ inversion
- `poly_s3_inv.c` - S₃ inversion
- `poly_rq_mul.c` - Ring multiplication

**Cryptographic Primitives:**
- `fips202.c/fips202.h` - SHA-3/SHAKE implementation
- `crypto_sort_int32.c` - Constant-time sorting
- `cmov.c/cmov.h` - Conditional move operations

### NTRU+ Implementation (27 files)
**Core Algorithm Files:**
- `kem.c/kem.h` - Direct KEM implementation
- `poly.c/poly.h` - Polynomial operations with NTT
- `ntt.c/ntt.h` - Number Theoretic Transform

**Optimized Components:**
- `reduce.c/reduce.h` - Modular reduction
- `symmetric.c/symmetric.h` - Symmetric operations
- `verify.c/verify.h` - Verification operations

**Cryptographic Primitives:**
- `aes256ctr.c/aes256ctr.h` - AES-256 in CTR mode
- `sha256.c`, `sha512.c` - SHA-2 family
- `randombytes.c/randombytes.h` - Random number generation

## Algorithmic Differences

### Polynomial Coefficient Types
- **NTRU HPS**: `uint16_t coeffs[NTRU_N]` - Unsigned 16-bit integers
- **NTRU+**: `int16_t coeffs[NTRUPLUS_N]` - Signed 16-bit integers

### Mathematical Operations

#### NTRU HPS Operations
```c
void poly_mod_3_Phi_n(poly *r);      // Reduction mod 3
void poly_mod_q_Phi_n(poly *r);      // Reduction mod q
void poly_S3_tobytes(...);           // Ternary packing
void poly_Sq_tobytes(...);           // Coefficient packing
```

#### NTRU+ Operations
```c
void poly_ntt(poly *r, const poly *a);     // Forward NTT
void poly_invntt(poly *r, const poly *a);  // Inverse NTT
void poly_basemul(...);                    // NTT domain multiplication
int poly_baseinv(...);                     // NTT domain inversion
void poly_crepmod3(...);                   // Centered mod 3 reduction
```

### Key Generation Approaches

#### NTRU HPS Key Generation
- Uses specialized sampling for different coefficient sets
- Separate handling of f, g, and h polynomials
- Multiple polynomial lifting and inversion steps
- Direct polynomial arithmetic

#### NTRU+ Key Generation
- Centered Binomial Distribution (CBD) sampling
- NTT-based polynomial operations
- Uses `poly_cbd1()` for generating f and g
- Multiplication and inversion in NTT domain

### Build System Comparison

#### NTRU HPS Makefile
```makefile
CC=/usr/bin/cc
LDFLAGS=-lcrypto
CFLAGS = -DCRYPTO_NAMESPACE\(s\)=ntru_\#\#s

SOURCES = cmov.c crypto_sort_int32.c fips202.c kem.c owcpa.c pack3.c packq.c \
          poly.c poly_lift.c poly_mod.c poly_r2_inv.c poly_rq_mul.c poly_s3_inv.c \
          PQCgenKAT_kem.c rng.c sample.c sample_iid.c
```

#### NTRU+ Makefile
```makefile
CC =gcc
CFLAGS += -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls \
  -Wshadow -Wpointer-arith -O3 -fomit-frame-pointer
LDFLAGS=-lcrypto

SOURCES= kem.c poly.c ntt.c aes256ctr.c sha256.c sha512.c symmetric.c reduce.c verify.c
```

**Key Differences:**
- NTRU+ has more aggressive compiler optimizations
- NTRU HPS uses namespace macros for symbol management
- NTRU+ has cleaner, more modular source organization

## Security and Performance Considerations

### NTRU HPS Advantages
- **Mature Design**: Extensively analyzed in NIST PQC process
- **Conservative Parameters**: Well-studied security margins
- **Smaller Keys**: More compact key sizes
- **NIST Standardized**: Official post-quantum standard

### NTRU+ Advantages  
- **NTT Optimization**: Fast polynomial multiplication
- **Power-of-2 Friendly**: N=768 enables efficient implementations
- **Modern Optimizations**: Updated design principles
- **Structured Parameters**: Better suited for hardware implementations

### Performance Characteristics
- **NTRU HPS**: Optimized for space efficiency, direct polynomial operations
- **NTRU+**: Optimized for speed via NTT, larger memory footprint

## Implementation Complexity

### NTRU HPS Complexity
- **Higher Code Complexity**: 32 files with specialized operations
- **Multiple Polynomial Formats**: Different packing schemes
- **Direct Arithmetic**: No transform domain optimizations
- **Extensive Validation**: Complex parameter checking

### NTRU+ Complexity
- **Streamlined Design**: 27 files with cleaner architecture
- **Transform-Based**: Heavy reliance on NTT for efficiency
- **Unified Polynomial Type**: Single coefficient representation
- **Modern C Practices**: Better code organization

## Conclusion

The comparison reveals two different evolutionary paths for NTRU-based cryptography:

- **NTRU HPS** represents a conservative, thoroughly-analyzed approach optimized for the NIST standardization process
- **NTRU+** represents modern algorithmic optimizations with NTT-based acceleration and updated parameter choices

**Choose NTRU HPS when:**
- NIST compliance is required
- Smaller key sizes are critical  
- Maximum security assurance is needed
- Legacy compatibility is important

**Choose NTRU+ when:**
- Maximum performance is required
- Modern optimization techniques are preferred
- Power-of-2 dimensions fit the architecture
- Research flexibility is desired

Both implementations maintain constant-time operations and provide post-quantum security, but serve different optimization goals and use cases.