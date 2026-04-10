# NTRU+ (https://www.ntruplus.org/)

This website serves as the official repository for **NTRU+**, a key encapsulation mechanism (**KEM**) algorithm that was selected as one of the **final algorithms** in Round 2 of the [Korean Post-Quantum Cryptography Competition (KpqC)](https://www.kpqc.or.kr).

### Reference Implementation
- C-based implementation  
- Structured to reflect the NTRU+ specification as intuitively as possible  
- Focused on clarity, readability, and correctness
- Local scalar baseline for comparison against optimized variants

### Optimized Implementation
- Main scalar optimization lane for this workspace
- Intended for algorithmic NTT work, including schedule, zeta ordering, and layout changes
- Compared against `Reference_Implementation`, but not required to preserve the same internal transform contract

### Cortex-M Optimized Implementation
- Preserved pre-existing optimized C lane
- Kept separate from the new scalar optimization workflow so Cortex-M-oriented work does not block broader NTT restructuring

### Additional Implementation
- Architecture-specific, hand-tuned assembly implementations
  - Intel AVX2  
  - ARMv8-A NEON  
- Fully consistent with the reference implementation  

### Workspace Policy
- `Reference_Implementation`: keep stable and readable; use as the local baseline
- `Optimized_Implementation`: active development area for scalar optimization experiments
- `Cortex-M_Optimized_Implementation`: retained for Cortex-M-specific or legacy optimized C work
- `Additional_Implementation`: architecture-specific backends after the C-level algorithm/layout is settled
