#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re

HERE=Path(__file__).resolve(); EXP=HERE.parents[1]; ROOT=HERE.parents[3]; OUT=EXP/'generated'
OUT.mkdir(exist_ok=True)
def rd(n):return (ROOT/n).read_text()
def sha(n):return hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
def macro(src,name):
 m=re.search(rf'^\s*\.macro\s+{re.escape(name)}\b[^\n]*\n(.*?)^\s*\.endm\s*$',src,re.M|re.S)
 if not m:raise RuntimeError(f'missing macro {name}')
 return m.group(1)

ntt=rd('ntt_m.s')+r'''
.macro GT103_STORE_QL2 v0,v1,v2,v3,outoff
 vmovdqu \v0, \outoff+0(%rdi)
 vmovdqu \v2, \outoff+32(%rdi)
 vmovdqu \v1, \outoff+64(%rdi)
 vmovdqu \v3, \outoff+96(%rdi)
.endm
.section .text.gt103_ntt_ql2,"ax",@progbits
FR_TRANSPOSE_CUT_FORWARD_FUNCTION gt103_ntt_ql2_avx2,GT103_STORE_QL2
'''
(OUT/'ntt_ql2.s').write_text(ntt)

b3=rd('basemul.s')+r'''
.macro GT103_OUTPUT_QL2
 vmovdqu 0(%rdi), %ymm5
 vmovdqu 32(%rdi), %ymm6
 vmovdqu 64(%rdi), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm5, %ymm5
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm6, %ymm6
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm7, %ymm7
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpunpcklwd %ymm6, %ymm5, %ymm1
 vpunpckhwd %ymm6, %ymm5, %ymm2
 vpunpcklwd %ymm8, %ymm7, %ymm3
 vpunpckhwd %ymm8, %ymm7, %ymm4
 vpunpckldq %ymm3, %ymm1, %ymm5
 vpunpckhdq %ymm3, %ymm1, %ymm6
 vpunpckldq %ymm4, %ymm2, %ymm7
 vpunpckhdq %ymm4, %ymm2, %ymm8
 vmovdqu %ymm5, 0(%rdi)
 vmovdqu %ymm6, 32(%rdi)
 vmovdqu %ymm7, 64(%rdi)
 vmovdqu %ymm8, 96(%rdi)
.endm
.section .text.gt103_b3_ql2,"ax",@progbits
TILE4_BASEMUL_B3_FUNCTION gt103_basemul_general_ql2_avx2,GT103_OUTPUT_QL2,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA
'''
(OUT/'basemul_ql2.s').write_text(b3)

pack_src=rd('pack.s')
sum_body=macro(pack_src,'Q24_ENCODE_SOA_SUM_BODY')
if sum_body.count('Q24_TRANSPOSE')!=12:raise RuntimeError('unexpected sum body')
ql2_body=sum_body.replace('Q24_TRANSPOSE','GT103_Q24_Q_ONLY')
# pack.s redefines Q24_ENCODE_REG_PACKET again for later verification kernels.
# Use a private copy of the high-range reducer active at the production E0V
# instantiation point rather than whichever definition is last in the file.
ql2_body=ql2_body.replace('Q24_ENCODE_REG_PACKET','GT103_Q24_ENCODE_HR')
pack=pack_src+r'''
.macro GT103_Q24_Q_ONLY s0,s1,s2,s3,t0,t1,t2,t3
 vpunpcklqdq %\s2, %\s0, %\t0
 vpunpckhqdq %\s2, %\s0, %\t1
 vpunpcklqdq %\s3, %\s1, %\t2
 vpunpckhqdq %\s3, %\s1, %\t3
.endm
.macro GT103_Q24_ENCODE_HR src,srcx,perm,offset,safe
 vpmulhrsw %ymm13, \src, %ymm14
 vpmullw %ymm15, %ymm14, %ymm14
 vpsubw %ymm14, \src, \src
 Q24_ENCODE_CANONICAL_REG_PACKET \src,\srcx,\perm,\offset,\safe
.endm
.macro GT103_Q24_QL2_SUM_BODY
'''+ql2_body+r'''
.endm
.section .text.gt103_pack_ql2_sum,"ax",@progbits
.p2align 5
.globl gt103_pack_ql2_sum_avx2
.type gt103_pack_ql2_sum_avx2,@function
gt103_pack_ql2_sum_avx2:
 vmovdqa .Lq24_q(%rip), %ymm15
 vmovdqa .Lq24_v(%rip), %ymm13
 GT103_Q24_QL2_SUM_BODY
 vzeroupper
 ret
.size gt103_pack_ql2_sum_avx2,.-gt103_pack_ql2_sum_avx2
'''
(OUT/'pack_ql2.s').write_text(pack)

static={'experiment':'GT32-QL2-SHARED-CONVERGENCE-103','baseline':'b2a4bea','production_modified':False,
'sha256':{n:sha(n) for n in ('ntt_m.s','basemul.s','pack.s','encap.c')},
'dynamic_route_ledger':{'forward':-144,'b3':96,'serializer':-96,'net':-144},
'loads_delta':0,'stores_delta':0,'materialized_bytes_delta':0,
'contracts':{'Forward_m_QL2':'store ownership [t0,t2,t1,t3], zero routes','B3_output_QL2':'W+D after finalizer','QL2_add_Q24':'memory-source add plus Q only'}}
(OUT/'static.json').write_text(json.dumps(static,indent=2)+'\n')
print(json.dumps(static['dynamic_route_ledger'],indent=2))
