"""P122: deduplicate the forward-NTT frontend iterations into per-class subroutines.

Each frontend iteration is five base-pointer `add`s followed by a body that is
textually identical for every iteration of the same scheduling class.  Every
iteration becomes `5 x add; bl <class body>`, and each distinct body is emitted
once, after the function, ending in `ret`.  x30 is saved in the prologue and
restored before the epilogue's `ret`.

The executed instruction stream is the original one plus the bl/ret pairs and
the x30 save/restore; the script refuses to run if any assumption fails.

usage: dedupe.py FILE ITER_MARKER END_MARKER NS PROLOGUE_ANCHOR EPILOGUE_ANCHOR [--no-x30] [--begin=TEXT]
Only classes with at least two iterations are converted; the others stay inline.
--no-x30 skips the x30 save/restore when a previous run already added it.
"""
import re, sys

path, iter_marker, end_marker, ns, pro_anchor, epi_anchor = sys.argv[1:7]
add_x30 = '--no-x30' not in sys.argv
# [sp, #0] is the Slothy spill slot (STACK_LOC_0) of these transforms; #56 lies
# between the x23 and d8 saves and is referenced by nothing else.
X30_SLOT = '[sp, #56]'
L = open(path).read().split('\n')

def is_insn(line):
    s = line.split('//')[0].strip()
    return bool(s) and not s.endswith(':') and not s.startswith(('.', '#', '/*', '*'))

begin_arg = [a[len('--begin='):] for a in sys.argv if a.startswith('--begin=')]
begin = [i for i, l in enumerate(L) if begin_arg and begin_arg[0] in l][0] if begin_arg else 0
first = [i for i, l in enumerate(L) if i >= begin and iter_marker in l][0]
end = [i for i, l in enumerate(L) if i > first and end_marker in l][0]
starts = [i for i, l in enumerate(L) if first <= i < end and iter_marker in l]
assert starts, 'markers not found'
bounds = starts + [end]

def body_text(body):
    return '\n'.join(l.split('//')[0].rstrip() for l in body if is_insn(l))

blocks = []
for k, s in enumerate(starts):
    block = L[s:bounds[k + 1]]
    idx = [j for j, l in enumerate(block) if is_insn(l)]
    is_add = [bool(re.match(r'\s*add x\d+, x\d+, #\d+\s*$', block[j].split('//')[0])) for j in idx]
    run = next(n for n in range(len(idx) - 4) if all(is_add[n:n + 5]))   # first five consecutive base adds
    last_add = idx[run + 4]
    blocks.append((s, bounds[k + 1], block, last_add, body_text(block[last_add + 1:])))
count = {}
for b in blocks: count[b[4]] = count.get(b[4], 0) + 1

classes = {}          # body text -> label
emitted = []          # (label, body lines)
replacement = {}      # start index -> (stop index, new lines)
for s, stop, block, last_add, text in blocks:
    if count[text] < 2:
        continue                                   # a unique body stays inline
    idx = [j for j, l in enumerate(block) if is_insn(l) and j <= last_add][-5:]
    for j in idx:
        assert re.match(r'\s*add x\d+, x\d+, #\d+\s*$', block[j].split('//')[0]), block[j]
    body = block[last_add + 1:]
    assert 'x30' not in text and not re.search(r'\bbl\b|\bret\b', text), 'body uses x30 or calls'
    assert not any(re.match(r'\s*[.A-Za-z_][A-Za-z0-9_.]*:\s*$', l) for l in body), 'label inside body'
    if text not in classes:
        named = [re.search(r'Frontend group (\d+)', l) for l in block]
        named = [m.group(1) for m in named if m]
        label = f'.L{ns}_frontend_group{named[0] if named else len(classes)}'
        assert label not in classes.values(), 'two bodies claim one class'
        classes[text] = label
        emitted.append((label, [l for l in body if l.strip()]))
    replacement[s] = (stop, block[:last_add + 1] + [f'    bl {classes[text]}', ''])

out = []; i = 0
while i < len(L):
    if i in replacement:
        stop, lines = replacement[i]; out.extend(lines); i = stop; continue
    out.append(L[i]); i += 1

text = '\n'.join(out)
assert text.count(pro_anchor) == 1 and text.count(epi_anchor) == 1, 'anchors'
if add_x30:
    text = text.replace(pro_anchor, pro_anchor + f'\n    str x30, {X30_SLOT}  // frontend class bodies are called with bl; [sp] is a spill slot')
    text = text.replace(epi_anchor, f'    ldr x30, {X30_SLOT}\n' + epi_anchor)
else:
    assert f'str x30, {X30_SLOT}' in text, 'x30 save expected from a previous run'

# emit the class bodies right after the function's epilogue ret
epi_at = text.index(epi_anchor) + len(epi_anchor)
ret_at = text.index('\n    ret', epi_at) + len('\n    ret')
subs = ['', f'    /* Frontend class bodies of this transform; each iteration sets its five',
        f'     * base pointers and calls the body of its scheduling class. */']
for label, body in emitted:
    subs += ['.p2align 6', f'{label}:'] + body + ['    ret', '']
text = text[:ret_at] + '\n' + '\n'.join(subs) + text[ret_at:]
open(path, 'w').write(text)
print(f'{path}: {len(replacement)} of {len(starts)} iterations -> {len(classes)} class bodies')
