# NTRU+768 Official AVX2: caller-bounded lazy Forward (common generator; its
# instruction stream equals the NTRU+768 qual001 lazy Forward) plus the 2-op
# freeze in poly_tobytes, Phase A + same-ELF diagnostic.
# All rules live in the shared, parameterised common/official_opt_lazy/*.mk.
PARAM := 768
# Read-only reference for the lazy-stream-equality gate: the NTRU+768 qual001
# caller-lazy Forward (another experiment; never written from here).
LAZY_REFERENCE := ../avx2_official_opt_001/asm/ntruplus768_officialopt_ntt_caller_lazy.s
include ../../../common/official_opt_lazy/lazy.mk
include ../../../common/official_opt_lazy/freeze2op.mk
