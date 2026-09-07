#!/usr/bin/env python3
"""Print an apply_patch proposal; never mutate the baseline or candidate files."""
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

baseline, target = map(Path, sys.argv[1:3])
files = {str(p.relative_to(baseline)): p.read_text() for p in baseline.rglob('*') if p.is_file()}
mapping = {p: ('ntt_internal.h' if p == 'internal/ntt.h' else Path(p).name)
           for p in files if p.startswith(('asm/', 'internal/', 'NO_CE/'))}
assert len(set(mapping.values())) == len(mapping)
assert not (set(mapping.values()) & (set(files) - set(mapping)))
result = {}
includes = []
for old, content in files.items():
    new = mapping.get(old, old)
    if Path(old).suffix in ('.c', '.h', '.S'):
        def rewrite(match):
            inc = match.group(1)
            for base in ((baseline / old).parent, baseline, baseline / 'internal'):
                resolved = (base / inc).resolve()
                if resolved.is_file() and resolved.is_relative_to(baseline.resolve()):
                    relative = str(resolved.relative_to(baseline.resolve()))
                    destination = mapping.get(relative, relative)
                    includes.append({'source': old, 'include': inc, 'resolved': relative,
                                     'new_source': new, 'new_target': destination})
                    # Root -I. covers every mapped production header; leave unmoved local headers.
                    replacement = destination if relative in mapping else inc
                    return match.group(0).replace('"' + inc + '"', '"' + replacement + '"')
            includes.append({'source': old, 'include': inc, 'resolved': None})
            return match.group(0)
        content = re.sub(r'#\s*include\s*"([^"]+)"', rewrite, content)
    elif old != 'SOURCE-MANIFEST.sha256':
        for src in sorted(mapping, key=len, reverse=True):
            content = content.replace(src, mapping[src])
        if old == 'Makefile':
            content = content.replace('-I. -Iinternal', '-I.')
        if old == 'scripts/check_zeroization.py':
            content = content.replace("(ROOT/'asm').rglob('*.S')", "ROOT.glob('*.S')")
    result[new] = content
result['SOURCE-MANIFEST.sha256'] = ''.join(
    hashlib.sha256(content.encode()).hexdigest() + '  ./' + name + '\n'
    for name, content in sorted(result.items()) if name != 'SOURCE-MANIFEST.sha256')
if len(sys.argv) > 3 and sys.argv[3] == '--inventory':
    print(json.dumps({'mapping': mapping, 'includes': includes}, indent=2))
    sys.exit()
print('*** Begin Patch')
for old, before in files.items():
    new = mapping.get(old, old)
    after = result[new]
    if old == new and before == after:
        continue
    print('*** Update File: ' + str(target / old))
    if old != new:
        print('*** Move to: ' + str(target / new))
    if before == after:
        print('@@')
        print(' ' + before.splitlines()[0])
    else:
        for line in list(difflib.unified_diff(before.splitlines(), after.splitlines(), n=3))[2:]:
            print('@@' if line.startswith('@@') else line)
print('*** End Patch')
