"""P116 E2b: E2 with interleaved lanes [c0.b0, c0.b1, c1.b0, ...] so the post branch merge is one addp."""
import re
s = open('invntt_e2t.S').read()
s = re.sub(r'e2t_(invntt_|poly_invntt|gt_block)', r'e2b_\1', s)

old_vec = """    ldr d\\dst, [x3, #\\srcoff]
    ldr d12, [x4, #\\srcoff]
    mov v\\dst\\().d[1], v12.d[0]
"""
new_vec = """    /* P116 E2b: interleave branch halves lane by lane, [c0.b0, c0.b1, ...]. */
    ldr d\\dst, [x3, #\\srcoff]
    ldr d12, [x4, #\\srcoff]
    zip1 v\\dst\\().8h, v\\dst\\().8h, v12.8h
"""
assert s.count(old_vec) == 1; s = s.replace(old_vec, new_vec)

old_merge = """    zip1     v19.2d, v18.2d, v23.2d
    zip2     v24.2d, v18.2d, v23.2d
    add      v21.8h, v19.8h, v24.8h
"""
new_merge = """    /* P116 E2b: branch lanes are adjacent, so one pairwise add merges
     * both products: [lo.c0..c3 | hi.c0..c3]. */
    addp     v21.8h, v18.8h, v23.8h
"""
assert s.count(old_merge) == 1; s = s.replace(old_merge, new_merge)

head, tail = s.split('e2b_invntt_inv_branchfold_vecs:', 1)
lines = tail.split('\n'); n = 0
for i, l in enumerate(lines):
    m = re.match(r'(\s*\.hword\s+)(.*)$', l)
    if not m: continue
    v = [int(x) for x in re.findall(r'-?\d+', m.group(2))]
    assert len(v) == 8
    lines[i] = m.group(1) + ', '.join(str(v[4 * (j % 2) + j // 2]) for j in range(8))
    n += 1
assert n == 384, n
open('invntt_e2b.S', 'w').write(head + 'e2b_invntt_inv_branchfold_vecs:' + '\n'.join(lines))
print('ok', n)
