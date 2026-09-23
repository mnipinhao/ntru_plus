#!/bin/sh
# usage: build.sh GT_TREE OUT  -- executable holding the inverse and its tables
set -e; G=$1; O=$2
case $G in *864*) S="inverse_api.c inverse.S inverse16_paired.S inverse_tail_direct.S inverse_route.S crepmod3_raw.S basemul_rinv.S inverse9.S baseinv_num.S baseinv_prefix.S baseinv_inverse.S baseinv_recover.S baseinv_finish.S"; X="";;
  *) S="api_glue.c inverse.c rebase.S basemul_rinv.S baseinv_num.S baseinv_finish.S inverse_ntt.S inverse9.S inverse16.S inverse16_tail.S crepmod3_raw.S ntt.S ntt_top.S ntt_tail.S ntt9.S pack.c support.c base.c"; X="-DNTRUPLUS1152_ASM_BASEMUL_RINV -DNTRUPLUS1152_ASM_BASEINV_NUM -DNTRUPLUS1152_ASM_BASEINV_FINISH";;
esac
SS=""; for s in $S; do SS="$SS $G/$s"; done
cc -O2 -std=c11 $X -I$G -o $O driver.c $SS -Wl,-dead_strip
