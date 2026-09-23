"""P121: make every non-global named label assembler-local (.L prefix) and delete
unreferenced Slothy/boundary markers.  Behaviour-preserving (verified by comparing
disassembly).  usage: labels.py TREE"""
import re, sys, pathlib
T = pathlib.Path(sys.argv[1])
for name in ('ntt.S', 'pack.S', 'base.S', 'add.S', 'cbd.S', 'crepmod3.S'):
    p = T / name; s = p.read_text()
    globs = set(re.findall(r'^\s*\.global\s+C_SYM\(([A-Za-z0-9_]+)\)', s, flags=re.M))
    defs = re.findall(r'^[ \t]*([A-Za-z_][A-Za-z0-9_.]*):', s, flags=re.M)
    named = [d for d in dict.fromkeys(defs) if not d.startswith(('.L', 'L')) and d not in globs and d != 'C_SYM']
    deleted = renamed = 0
    for d in named:
        tok = r'(?<![A-Za-z0-9_.])' + re.escape(d) + r'(?![A-Za-z0-9_])'
        if len(re.findall(tok, s)) == 1:                       # defined, never referenced
            s = re.sub(r'^[ \t]*' + re.escape(d) + r':[ \t]*\n', '', s, count=1, flags=re.M); deleted += 1
        else:
            new = '.L' + d.replace('_.L', '_').lstrip('_')
            s = re.sub(tok, new, s); renamed += 1
    p.write_text(s)
    print(f'{name}: {renamed} labels made local, {deleted} unreferenced markers deleted')
