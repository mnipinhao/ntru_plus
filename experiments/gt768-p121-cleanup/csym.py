"""P121: symbol hygiene for NTRU+768's assembly (behaviour-preserving).

- `.global X` + `.global _X` and `X:` + `_X:`  ->  `.global C_SYM(X)` / `C_SYM(X):`
  (ELF keeps X, Mach-O gets _X; the second, unused spelling disappears)
- drops the unreferenced aliases poly_ntt_loose_block_major, gt_decap_gt_poly_ntt
- makes the *_end markers and gt_fqinv15_asm file-local
usage: csym.py TREE
"""
import re, sys, pathlib
T = pathlib.Path(sys.argv[1])
DEFINE = """#ifndef C_SYM
#ifdef __APPLE__
#define C_SYM_1(sym) _##sym
#define C_SYM(sym) C_SYM_1(sym)
#else
#define C_SYM(sym) sym
#endif
#endif
"""
ALIASES = ('poly_ntt_loose_block_major', 'gt_decap_gt_poly_ntt')
for name in ('add.S', 'cbd.S', 'crepmod3.S', 'keccakf1600.S', 'keccakf1600_v84a.S', 'ntt.S', 'pack.S', 'base.S'):
    p = T / name; lines = p.read_text().split('\n'); out = []; changed = 0
    doubled = set()
    for l in lines:
        m = re.match(r'\s*\.global\s+_([A-Za-z][A-Za-z0-9_]*)\s*$', l)
        if m: doubled.add(m.group(1))
    for i, l in enumerate(lines):
        s = l.strip()
        m = re.match(r'\.global\s+_?([A-Za-z][A-Za-z0-9_]*)$', s)
        if m and m.group(1) in ALIASES: changed += 1; continue
        m = re.match(r'_?([A-Za-z][A-Za-z0-9_]*):$', s)
        if m and m.group(1) in ALIASES: changed += 1; continue
        m = re.match(r'(\s*)\.global\s+_([A-Za-z][A-Za-z0-9_]*)$', l)
        if m and m.group(2) in doubled: changed += 1; continue                     # drop _X spelling
        m = re.match(r'(\s*)\.global\s+([A-Za-z][A-Za-z0-9_]*)$', l)
        if m and m.group(2) in doubled:
            out.append(f'{m.group(1)}.global C_SYM({m.group(2)})'); changed += 1; continue
        m = re.match(r'(\s*)_([A-Za-z][A-Za-z0-9_]*):\s*$', l)
        if m and m.group(2) in doubled: changed += 1; continue
        m = re.match(r'(\s*)([A-Za-z][A-Za-z0-9_]*):\s*$', l)
        if m and m.group(2) in doubled:
            out.append(f'{m.group(1)}C_SYM({m.group(2)}):'); changed += 1; continue
        m = re.match(r'\s*\.global\s+(gt_internal_poly_ntt_loose_end|gt_decap_poly_ntt_end)$', l)
        if m: changed += 1; continue
        if re.match(r'\s*\.global\s+C_SYM\(gt_fqinv15_asm\)$', l): changed += 1; continue
        out.append(l)
    text = '\n'.join(out)
    if doubled:
        # a guarded definition before every converted global (sections of base.S #undef theirs)
        text = re.sub(r'(^[ \t]*\.global C_SYM\()', lambda mo: mo.group(1), text, flags=re.M)
        first = re.search(r'^[ \t]*\.global C_SYM\(', text, flags=re.M)
        if name == 'base.S':
            text = re.sub(r'(^[ \t]*\.global C_SYM\((?:%s)\))' % '|'.join(sorted(doubled)),
                          lambda mo: DEFINE + mo.group(1), text, flags=re.M)
        else:
            text = DEFINE + '\n' + text
    p.write_text(text)
    print(f'{name}: {changed} lines changed, {len(doubled)} doubled symbols')
