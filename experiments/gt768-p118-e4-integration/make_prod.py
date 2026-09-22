"""P118: turn P117's invntt_e4.S into the production decap_invntt.S section.

ABI: void poly_invntt_ternary_decap(poly *inout, uint8_t scratch[2048])
  - in place on x0; x0 and x1 are never written by the body;
  - the 2,048-byte working area (three 512-byte row buffers + one 512-byte
    stage123 stripe) is caller-owned at x1, so the caller's existing clear
    covers it; the frame keeps only x30 and d8-d15 (80 bytes).
"""
import re, sys

src, out = sys.argv[1], sys.argv[2]
s = open(src).read()

# names
s = s.replace('e4_invntt_', 'module_decap_invntt_')
s = re.sub(r'#ifndef __APPLE__\n\t\.weak e4_poly_invntt\n\t\.weak _e4_poly_invntt\n#endif\n', '', s)
s = re.sub(r'\t\t\.global _?e4_gt_block_major_poly_invntt\n', '', s)
s = re.sub(r'_?e4_gt_block_major_poly_invntt:\n', '', s)
s = s.replace('_e4_poly_invntt', '_poly_invntt_ternary_decap').replace('e4_poly_invntt', 'poly_invntt_ternary_decap')
s = s.replace('.section .text.module_decap_invntt_body', '.section .text.module_decap_invntt_body')
assert 'e4_' not in s, [l for l in s.splitlines() if 'e4_' in l][:3]

# header
head_end = s.index('.macro module_decap_invntt_BARRETT_REDUCE')
head = '''/* Section: decap_invntt.S; private namespace module_decap_invntt_ */
#ifdef __APPLE__
.text
#else
.section .text.module_decap_invntt_body,"ax",%progbits
#endif
/*************************************************
* Name:        poly_invntt_ternary_decap
*
* Description: Good-Thomas inverse NTT of the first decapsulation product,
*              fused with the centered mod-3 map (poly_crepmod3).
*
* Arguments:   - poly *inout: product of poly_frombytes_basemul_decap_scale,
*                             which stores each 8-element group as eight
*                             4-coefficient elements (st4) and retains one
*                             R^-1 factor; |coefficients| <= 2458
*              - uint8_t scratch[2048]: caller-owned working area; holds
*                             secret intermediates on return
*
* Returns:     none.  inout holds coefficients in {-1, 0, 1} in natural order,
*              identical to poly_crepmod3 applied to the exact inverse.
*
* Structure: stage123 (lane-interleaved branches, 30 proof-placed Barretts)
* -> stripe scratch -> Slothy stage45 -> row buffers -> fused DFT3/branchfold
* post with one pairwise branch merge, one Barrett and the mod-3 step per
* output vector.  Overflow-free for every input with |x| <= 2458
* (experiments/gt768-p117-frontend-barrett-loads/range_interp.py).
**************************************************/

'''
s = head + s[head_end:]

# frame: x30 + d8-d15 only
s = re.sub(r'\.equ module_decap_invntt_INVNTT_SIMD_SAVE_OFFSET, 2080\n\.equ module_decap_invntt_INVNTT_STACK_SIZE, 2144\n\.equ module_decap_invntt_INVNTT_SAVED_X0_OFFSET, .*\n',
           '.equ module_decap_invntt_INVNTT_SIMD_SAVE_OFFSET, 0\n.equ module_decap_invntt_INVNTT_STACK_SIZE, 80\n', s)
s = s.replace('''    stp x30, x0, [sp, #-16]!
    sub sp, sp, #module_decap_invntt_INVNTT_STACK_SIZE
''', '''    sub sp, sp, #module_decap_invntt_INVNTT_STACK_SIZE
    str x30, [sp, #64]
''')
s = s.replace('''    add sp, sp, #module_decap_invntt_INVNTT_STACK_SIZE
    ldp x30, x0, [sp]
    add sp, sp, #16
    ret''', '''    ldr x30, [sp, #64]
    add sp, sp, #module_decap_invntt_INVNTT_STACK_SIZE
    ret''')

# working area -> caller scratch at x1; input base -> x0
n = s.count('    add x3, x1, #0\n    add x4, x1, #768\n'); assert n == 3, n
s = s.replace('    add x3, x1, #0\n    add x4, x1, #768\n', '    mov x3, x0\n')
for old, new in (('sp, #32', 'x1, #0'), ('sp, #544', 'x1, #512'), ('sp, #1056', 'x1, #1024')):
    assert s.count(f'add x2, {old}') == 1 and s.count(f'add x{8 if old=="sp, #32" else 9 if old=="sp, #544" else 10}, {old}') == 1
    s = s.replace(f'add x2, {old}', f'add x2, {new}')
    s = re.sub(rf'add (x8|x9|x10), {old}\b', rf'add \1, {new}', s)
assert s.count('add x14, sp, #1568') == 3
s = s.replace('add x14, sp, #1568', 'add x14, x1, #1536')
s = s.replace('    ldr x0, [sp, #module_decap_invntt_INVNTT_SAVED_X0_OFFSET]\n', '')
s = re.sub(r'stage123 stripe scratch at sp\+1568', 'stage123 stripe scratch at x1+1536', s)
s = re.sub(r'row(\d) row-buffer base at sp\+\d+', lambda m: f'row{m.group(1)} row-buffer base at x1+{512*int(m.group(1))}', s)
assert 'sp, #32' not in s and 'sp, #544' not in s and 'sp, #1056' not in s and 'x4' not in s.split('.macro module_decap_invntt_DIRECT_STAGE123_VEC')[1].split('.endm')[0]
s = s.replace('/* End section: invntt.S */', '/* End section: decap_invntt.S */')
if '/* End section: decap_invntt.S */' not in s:
    s = s.rstrip() + '\n\n/* End section: decap_invntt.S */\n'
open(out, 'w').write(s)
s = re.sub(r"P11[67] E[0-9a-z]+: ", "", s)
open(out, "w").write(s)
print("ok")
