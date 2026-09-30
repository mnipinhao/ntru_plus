// The official CE sponge calls f1600(state, round_constants).  This routes the
// call to GT's FEAT_SHA3 permutation (keccakf1600_v84a.S of the package being
// measured), which reads the round constants from the second argument; the
// sponge passes the standard table, so the effect on the state is the same:
// the "same Keccak permutation" builds on M2.
#ifdef __APPLE__
#define F1600 _f1600
#define GT_PERMUTATION _ntruplus_keccak_f1600_x1_v84a_aarch64
#else
#define F1600 f1600
#define GT_PERMUTATION ntruplus_keccak_f1600_x1_v84a_aarch64
#endif
.text
.p2align 2
.global F1600
F1600:
    b GT_PERMUTATION
