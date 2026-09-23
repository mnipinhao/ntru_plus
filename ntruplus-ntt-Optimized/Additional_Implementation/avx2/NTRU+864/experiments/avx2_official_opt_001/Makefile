# NTRU+864 Official AVX2 caller-bounded lazy Forward, Phase A (correctness only).
# All rules live in the shared, parameterised common/official_opt_lazy/lazy.mk.
PARAM := 864
include ../../../common/official_opt_lazy/lazy.mk
# NTRU+864-only layout-fused codec candidates (Option A): see codec.mk.
include codec.mk
# NTRU+864-only direct 12-bit codec candidate exp002 (+ 2-op freeze): see codec_direct.mk.
include codec_direct.mk
# mlkem-native x1 Keccak (all SHAKE256) stacked on the exp002 candidate
# (avx2-officialopt-lazy-codec-keccak-864-exp001) + keccak-only control: see keccak.mk.
KECCAK_BASE := kem_lazy_codec_direct
KECCAK_BASE_ASM = $(LAZY_ASM) $(DIRECT_ASM)
KECCAK_BASE_CHECKS := check-generate check-codec-generate check-codec-direct-generate
KECCAK_BASE_QUAL := qualification/avx2-officialopt-lazy-codec-qual002
include ../../../common/official_opt_keccak/keccak.mk
