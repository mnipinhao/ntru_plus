"""P116 E3: E2b reading Official's fused product stored as AoS elements (st4 per QSoA group).

qsoa_map.txt line i = QSoA position of GT block-major coefficient i (derived in P115).
Element (group g, lane l) of the st4 product sits at byte 64*g + 8*l, its four
coefficients contiguous, so each stage123 half stays one ldr d; only offsets change."""
import re
m = [int(x) for x in open('qsoa_map.txt')]
def off(gt_block):
    p = m[4 * gt_block]
    assert m[4*gt_block+1:4*gt_block+4] == [p + 8, p + 16, p + 24]
    return 64 * (p // 32) + 8 * (p % 8)

s = open('invntt_e2b.S').read()
s = re.sub(r'e2b_(invntt_|poly_invntt|gt_block)', r'e3_\1', s)

old_vec = """    ldr d\\dst, [x3, #\\srcoff]
    ldr d12, [x4, #\\srcoff]
    zip1 v\\dst\\().8h, v\\dst\\().8h, v12.8h
"""
new_vec = """    /* P116 E3: both branch elements from the st4 product, at their own offsets. */
    ldr d\\dst, [x3, #\\off0]
    ldr d12, [x3, #\\off1]
    zip1 v\\dst\\().8h, v\\dst\\().8h, v12.8h
"""
assert s.count(old_vec) == 1
s = s.replace(old_vec, new_vec).replace('_DIRECT_STAGE123_VEC dst, srcoff', '_DIRECT_STAGE123_VEC dst, off0, off1')

old_blk = '.macro e3_invntt_DIRECT_STAGE123_BLOCK_TO_SCRATCH group, off0, off1, off2, off3, off4, off5, off6, off7'
assert s.count(old_blk) == 1
s = s.replace(old_blk, '.macro e3_invntt_DIRECT_STAGE123_BLOCK_TO_SCRATCH group, ' +
              ', '.join(f'a{j}, b{j}' for j in range(8)))
for j, reg in enumerate(range(3, 11)):
    o = f'    e3_invntt_DIRECT_STAGE123_VEC {reg}, \\off{j}\n'
    assert s.count(o) == 1, o
    s = s.replace(o, f'    e3_invntt_DIRECT_STAGE123_VEC {reg}, \\a{j}, \\b{j}\n')

def repl(mo):
    offs = [int(x) for x in mo.group(3).split(',')]
    args = ', '.join(f'{off(o // 8)}, {off(96 + o // 8)}' for o in offs)
    return f'{mo.group(1)}e3_invntt_DIRECT_STAGE123_BLOCK_TO_SCRATCH {mo.group(2)}, {args}'
s, n = re.subn(r'^(\s*)e3_invntt_DIRECT_STAGE123_BLOCK_TO_SCRATCH (\d),\s*([-\d, ]+)$', repl, s, flags=re.M)
assert n == 12, n
open('invntt_e3.S', 'w').write(s)
print('ok')
