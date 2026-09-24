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
# SCRATCH direct-codec decision-gate measurement (no candidate): see codec8_scratch.mk.
include ../../../common/official_opt_lazy/codec8_scratch.mk
# mlkem-native x1 Keccak (all SHAKE256) stacked on the lazy+freeze2op candidate
# (avx2-officialopt-lazy-freeze-keccak-768-exp001) + keccak-only control: see keccak.mk.
KECCAK_BASE := kem_lazy_freeze2op
KECCAK_BASE_ASM = $(LAZY_ASM) $(FREEZE_ASM)
KECCAK_BASE_CHECKS := check-generate check-freeze-generate
KECCAK_BASE_QUAL := qualification/avx2-officialopt-lazy-freeze-qual001
include ../../../common/official_opt_keccak/keccak.mk
# HT Forward (Hwang-style data movement) + keygen R^2 fold stacked on the Keccak
# candidate (avx2-officialopt-lazy-freeze-keccak-ht-768-exp001) + ht_only /
# r2fold_only controls: see common/official_opt_ht/ht.mk.
include ../../../common/official_opt_ht/ht.mk
