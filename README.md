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