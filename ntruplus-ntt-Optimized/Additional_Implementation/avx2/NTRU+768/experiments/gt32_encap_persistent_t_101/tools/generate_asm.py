#!/usr/bin/env python3
from pathlib import Path
import json, hashlib

HERE=Path(__file__).resolve(); EXP=HERE.parents[1]; ROOT=HERE.parents[3]; OUT=EXP/'generated'
OUT.mkdir(exist_ok=True)

def rd(n): return (ROOT/n).read_text()
def sha(n): return hashlib.sha256((ROOT/n).read_bytes()).hexdigest()

ntt=rd('ntt_m.s')+r'''
.macro GT101_STORE_T v0,v1,v2,v3,outoff
 vmovdqu \v0, \outoff+0(%rdi)
 vmovdqu \v1, \outoff+32(%rdi)
 vmovdqu \v2, \outoff+64(%rdi)
 vmovdqu \v3, \outoff+96(%rdi)
.endm
.section .text.gt101_ntt_t,"ax",@progbits
FR_TRANSPOSE_CUT_FORWARD_FUNCTION gt101_ntt_t_avx2,GT101_STORE_T
'''
(OUT/'ntt_t.s').write_text(ntt)

b3=rd('basemul.s')+r'''
.macro GT101_INPUT_B_T
 vmovdqu 0(%rdx), %ymm9
 vmovdqu 32(%rdx), %ymm10
 vmovdqu 64(%rdx), %ymm11
 vmovdqu 96(%rdx), %ymm12
 vpshufb .Lgt101_plane_mask(%rip), %ymm9, %ymm9
 vpshufb .Lgt101_plane_mask(%rip), %ymm10, %ymm10
 vpshufb .Lgt101_plane_mask(%rip), %ymm11, %ymm11
 vpshufb .Lgt101_plane_mask(%rip), %ymm12, %ymm12
 vpunpckldq %ymm11, %ymm9, %ymm1
 vpunpckhdq %ymm11, %ymm9, %ymm2
 vpunpckldq %ymm12, %ymm10, %ymm3
 vpunpckhdq %ymm12, %ymm10, %ymm4
 vpunpcklqdq %ymm3, %ymm1, %ymm9
 vpunpckhqdq %ymm3, %ymm1, %ymm10
 vpunpcklqdq %ymm4, %ymm2, %ymm11
 vpunpckhqdq %ymm4, %ymm2, %ymm12
.endm
.section .text.gt101_b3_m_t,"ax",@progbits
TILE4_BASEMUL_B3_FUNCTION gt101_basemul_general_m_t_avx2,TILE4_OUTPUT_SOA_LATE_RSQ,TILE4_INPUT_A_SOA,GT101_INPUT_B_T
.section .rodata.gt101_plane_mask,"a",@progbits
.p2align 5
.Lgt101_plane_mask:
 .byte 0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15
 .byte 0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15
'''
(OUT/'basemul_t.s').write_text(b3)

specs={
0:[(0,3,177,0),(0,2,75,24),(0,0,75,48),(0,1,75,72),(1,3,177,96),(1,2,75,120),(1,0,75,144),(1,1,75,168)],
1:[(0,2,228,1056),(0,3,228,1080),(0,1,228,1104),(0,0,30,1128),(1,0,228,960),(1,1,228,984),(1,2,228,1008),(1,3,228,1032)],
2:[(0,1,30,384),(0,0,177,408),(0,3,30,432),(0,2,177,456),(1,1,30,480),(1,0,177,504),(1,3,30,528),(1,2,177,552)],
3:[(0,3,177,768),(0,2,75,792),(0,0,75,816),(0,1,75,840),(1,3,177,864),(1,2,75,888),(1,0,75,912),(1,1,75,936)],
4:[(0,2,228,288),(0,3,228,312),(0,1,228,336),(0,0,30,360),(1,0,228,192),(1,1,228,216),(1,2,228,240),(1,3,228,264)],
5:[(0,1,30,672),(0,0,177,696),(0,3,30,720),(0,2,177,744),(1,2,30,576),(1,3,30,600),(1,1,30,624),(1,0,177,648)]}

def packet(half,idx,perm,off):
    base=4 if half else 0
    a=base+(0 if idx<2 else 2); b=a+1; op='l' if idx%2==0 else 'h'
    safe=off==1128
    lines=[f' vpunpck{op}qdq %ymm{b}, %ymm{a}, %ymm8',
      ' vpmulhrsw .Lgt101_v(%rip), %ymm8, %ymm12',' vpmullw %ymm15, %ymm12, %ymm12',
      ' vpsubw %ymm12, %ymm8, %ymm8',f' vpermq ${perm}, %ymm8, %ymm8',
      ' vpsraw $15, %ymm8, %ymm12',' vpand %ymm15, %ymm12, %ymm12',' vpaddw %ymm12, %ymm8, %ymm8',
      ' vpmaddwd .Lgt101_pair_factor(%rip), %ymm8, %ymm8',' vpshufb .Lgt101_pack_mask(%rip), %ymm8, %ymm8',
      f' vmovdqu %xmm8, {off}(%rdi)',' vextracti128 $1, %ymm8, %xmm12']
    if safe: lines += [f' vmovq %xmm12, {off+12}(%rdi)',f' vpextrd $2, %xmm12, {off+20}(%rdi)']
    else: lines += [f' vmovdqu %xmm12, {off+12}(%rdi)']
    return '\n'.join(lines)

body=['''
.section .text.gt101_pack_t,"ax",@progbits
.p2align 5
.globl gt101_pack_t_avx2
.type gt101_pack_t_avx2,@function
gt101_pack_t_avx2:
 vmovdqa .Lgt101_q(%rip), %ymm15
''']
# Emit tiles in increasing wire-region order.  PACK1's ordinary 16-byte
# high-half store intentionally overlaps the next packet by four bytes; the
# next packet must therefore be written later.  Logical tile order is not
# wire order, so range(6) corrupts an already-written region at boundaries.
for tile in (0, 4, 2, 5, 3, 1):
    for j in range(8): body.append(f' vmovdqu {tile*256+j*32}(%rsi), %ymm{j}')
    # The source-half order in the symbolic map is not always wire order.
    # Sort packets by destination so each intentional four-byte over-store is
    # repaired by the following packet rather than corrupting an earlier one.
    for s in sorted(specs[tile], key=lambda x: x[3]): body.append(packet(*s))
body.append(''' vzeroupper
 ret
.size gt101_pack_t_avx2,.-gt101_pack_t_avx2
.section .rodata.gt101_pack_constants,"a",@progbits
.p2align 5
.Lgt101_q: .rept 16; .short 3457; .endr
.Lgt101_v: .rept 16; .short 9; .endr
.Lgt101_pair_factor: .rept 8; .short 1,4096; .endr
.Lgt101_pack_mask:
 .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128
 .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128
''')
(OUT/'pack_t.s').write_text(rd('pack.s')+'\n'.join(body))

static={'experiment':'GT32-ENCAP-PERSISTENT-T-101','source_sha256':{n:sha(n) for n in ['ntt_m.s','basemul.s','pack.s','encap.c']},
'ledger':{'ntt_T_routes_delta':-144,'pack_T_routes_delta':-96,'B3_M_T_routes_delta':144,'net_routes':-96,'loads_delta':0,'stores_delta':0},
'pack_store_geometry':{'ordinary_16B_tail_stores':47,'safe_final_packet_stores':2,'extra_fragmented_tile_tails':0},
'production_modified':False}
(OUT/'static.json').write_text(json.dumps(static,indent=2)+'\n')
print(json.dumps(static['ledger'],indent=2))
