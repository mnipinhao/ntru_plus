# NTRU+1152 Official AVX2 caller-bounded lazy Forward, Phase A (correctness only).
# All rules live in the shared, parameterised common/official_opt_lazy/lazy.mk.
PARAM := 1152
include ../../../common/official_opt_lazy/lazy.mk
# 2-op freeze in poly_tobytes stacked on the lazy Forward (candidate
# avx2-officialopt-lazy-freeze-1152-exp001) + freeze-only control: see freeze2op.mk.
include ../../../common/official_opt_lazy/freeze2op.mk
# SCRATCH direct-codec decision-gate measurement (no candidate): see codec8_scratch.mk.
include ../../../common/official_opt_lazy/codec8_scratch.mk
