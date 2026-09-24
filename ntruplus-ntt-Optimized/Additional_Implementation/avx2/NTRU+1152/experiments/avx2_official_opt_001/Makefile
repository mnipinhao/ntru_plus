# NTRU+1152 Official AVX2 caller-bounded lazy Forward, Phase A (correctness only).
# All rules live in the shared, parameterised common/official_opt_lazy/lazy.mk.
PARAM := 1152
include ../../../common/official_opt_lazy/lazy.mk
# 2-op freeze in poly_tobytes stacked on the lazy Forward (candidate
# avx2-officialopt-lazy-freeze-1152-exp001) + freeze-only control: see freeze2op.mk.
include ../../../common/official_opt_lazy/freeze2op.mk
# SCRATCH direct-codec decision-gate measurement (no candidate): see codec8_scratch.mk.
include ../../../common/official_opt_lazy/codec8_scratch.mk
# mlkem-native x1 Keccak (all SHAKE256) stacked on the lazy+freeze2op candidate
# (avx2-officialopt-lazy-freeze-keccak-1152-exp001) + keccak-only control: see keccak.mk.
KECCAK_BASE := kem_lazy_freeze2op
KECCAK_BASE_ASM = $(LAZY_ASM) $(FREEZE_ASM)
KECCAK_BASE_CHECKS := check-generate check-freeze-generate
KECCAK_BASE_QUAL := qualification/avx2-officialopt-lazy-freeze-qual001
include ../../../common/official_opt_keccak/keccak.mk
# HT Forward (Hwang-style data movement, the NTRU+768 block network) + keygen R^2
# fold stacked on the Keccak candidate (avx2-officialopt-lazy-freeze-keccak-ht-1152-exp001)
# + ht_only / r2fold_only controls; no HT inverse: see common/official_opt_ht/ht.mk.
include ../../../common/official_opt_ht/ht.mk
