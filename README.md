# NTRU+ (Implementation + Profiling)
NTRU+: Compact Construction of NTRU
Using Simple Encoding Method

# Practical Optimization Priority
Based on current profiling docs:
1. NTT / inverse NTT
2. base multiplication / inversion
3. hashing path (SHAKE/Keccak)
4. micro-kernels like poly_cbd1 / poly_sotp_* last

That is: optimize the dominant path first, then polish specialized helpers.

# Directory Policy
- `ntruplus-KpqC-Final`: frozen clean baseline
- `ntruplus-ntt-Optimized/Reference_Implementation`: local baseline inside the optimization workspace
- `ntruplus-ntt-Optimized/Optimized_Implementation`: main scalar optimization lane
- `ntruplus-ntt-Optimized/Cortex-M_Optimized_Implementation`: preserved older optimized/Cortex-M-oriented lane
- `ntruplus-ntt-Optimized/Additional_Implementation`: architecture-specific AVX2/AArch64 implementations
