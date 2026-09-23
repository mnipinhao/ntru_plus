"""P130 timing knockouts (outputs wrong, timing only), applied to a copy of a tree.
usage: knockouts.py TREE {A|B|store16}
  A        unpack8: one 16-byte load (over-reads 4 bytes past a group)
  B        unpack: drop the 64-bit half-inserts (o = b)
  store16  pack: every nine-byte run one 16-byte store (overwrites neighbours)"""
import re, sys
t, k = sys.argv[1], sys.argv[2]
if k == 'A':
    p = f'{t}/unpack.c'; s = open(p).read()
    old = 'uint32_t tail;memcpy(&tail,s+8,4);uint8x16_t b=vcombine_u8(vld1_u8(s),vdup_n_u8(0));b=vreinterpretq_u8_u32(vsetq_lane_u32(tail,vreinterpretq_u32_u8(b),2));'
    assert s.count(old) == 1; open(p, 'w').write(s.replace(old, 'uint8x16_t b=vld1q_u8(s);'))
elif k == 'B':
    p = f'{t}/unpack.c'; s = open(p).read()
    s, n = re.subn(r'vreinterpretq_s16_s64\(vsetq_lane_s64\(vgetq_lane_s64\(vreinterpretq_s64_s16\((b\d)\),\d\),vreinterpretq_s64_s16\((o\d+)\),\d\)\)', r'\1', s)
    open(p, 'w').write(s); print(n, 'inserts dropped')
elif k == 'store16':
    p = f'{t}/pack.c'; s = open(p).read()
    old = """    vst1_u8(out, vget_low_u8(b));
    vst1q_lane_u8(out + 8, b, 8);"""
    assert s.count(old) == 1; open(p, 'w').write(s.replace(old, '    vst1q_u8(out, b);'))
