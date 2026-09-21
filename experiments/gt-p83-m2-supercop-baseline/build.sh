#!/bin/zsh
set -e
S="$1"
SC=$S/supercop; SH_=$S/shim
CEROOT=/Users/chenpinhao/ntruplus/ntruplus-ntt-Optimized/Additional_Implementation/aarch64
G=/Users/chenpinhao/ntruplus/ntruplus-GT-Production/Additional_Implementation/aarch64
P=$S/bench/perop3.c
rm -rf $S/bin && mkdir -p $S/bin
for s in 768 864 1152; do
  d=$SC/ntruplus$s/aarch64
  (cd $d && cc -O3 -fomit-frame-pointer -Wno-unused-result -I. -I$SH_/inc -o $S/bin/off${s}_noce \
     $P $SH_/rb.c kem.c symmetric.c poly.c fips202.c add.s ntt.s base.s crepmod3.s pack.s cbd.s)
  (cd $d && cc -O3 -fomit-frame-pointer -Wno-unused-result -DSUPPORTS_SHAKE256_ASM \
     -I$CEROOT/NTRU+768/CE -I. -I$SH_/inc -o $S/bin/off${s}_ce \
     $P $SH_/rb.c kem.c symmetric.c poly.c $CEROOT/NTRU+768/CE/fips202.c $CEROOT/NTRU+768/CE/f1600.S \
     add.s ntt.s base.s crepmod3.s pack.s cbd.s)
done
(cd $G/NTRU+768 && cc -I. -I$SH_/inc -O3 -fomit-frame-pointer -std=c99 -Wno-unused-result -o $S/bin/gt768 \
  $P $SH_/rb.c kem.c symmetric.c fips202.c keygen.c keygen_lambda.c basemul_lambda.c ntt.S base.S pack.S \
  cbd.S crepmod3.S kem_api.S add.S keccakf1600.S keccakf1600_v84a.S)
(cd $G/NTRU+864 && cc -I. -I$SH_/inc -O3 -std=c11 -D_DEFAULT_SOURCE -Wno-unused-result -o $S/bin/gt864 \
  $P $SH_/rb.c symmetric.c fips202.c ntt_api.c base.c add.S crepmod3.S cbd.S ntt.S ntt9.S ntt_top.S \
  unpack.c unpack_api.c kem.c ntt_tail.S pack_compare.S pack_full.S pack_small.S pack.c inverse_api.c \
  inverse.S baseinv_num.S baseinv_prefix.S baseinv_inverse.S baseinv_recover.S baseinv_finish.S inverse16.S \
  inverse16_tail.S crepmod3_raw.S basemul_rinv.S inverse9.S support_abi.S hash_fixed.c keccakf1600.S keccakf1600_v84a.S)
(cd $G/NTRU+1152 && cc -I. -I$SH_/inc -O3 -std=c11 -D_DEFAULT_SOURCE -Wno-unused-result \
  -DNTRUPLUS1152_ASM_BASEMUL_RINV -DNTRUPLUS1152_ASM_BASEINV_NUM -DNTRUPLUS1152_ASM_BASEINV_FINISH \
  -o $S/bin/gt1152 $P $SH_/rb.c kem.c symmetric.c fips202.c hash_fixed.c base.c inverse.c pack.c support.c \
  api_glue.c rebase.S keccakf1600.S keccakf1600_v84a.S basemul_rinv.S baseinv_num.S baseinv_finish.S ntt.S \
  inverse16_tail.S ntt_top.S ntt_tail.S ntt9.S inverse_ntt.S inverse9.S inverse16.S crepmod3_raw.S)
ls $S/bin
