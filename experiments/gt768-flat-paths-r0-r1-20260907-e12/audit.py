#!/usr/bin/env python3
"""Build paired objects, capture symbol references, and check path-only equivalence.

Generated objects, preprocess output, nm/relocation logs and JSON belong in .build.
This is a conservative object-level reference inventory, not a dead-code proof.
"""
import argparse
import hashlib
import json
import platform
import subprocess
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('baseline', type=Path)
p.add_argument('candidate', type=Path)
p.add_argument('output', type=Path)
p.add_argument('--cc', default='cc')
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=True)

def run(args, cwd=None, **kw):
    return subprocess.check_output(args, cwd=cwd, **kw)

def sources(root):
    return run(['make', '-s', '--no-print-directory', '-f', 'Makefile', '-f', '-', 'audit_sources'],
               cwd=root, input=b'audit_sources:\n\t@echo $(KEM_SOURCES)\n').decode().split()

old, new = sources(a.baseline), sources(a.candidate)
assert len(old) == len(new) == 28
flags = ['-O3', '-fomit-frame-pointer', '-std=c99', '-Wall', '-Wextra', '-Wpedantic',
         '-ffunction-sections', '-fdata-sections']
records = []
for i, (src0, src1) in enumerate(zip(old, new)):
    record = {'old': src0, 'new': src1}
    for kind, root, source in [('baseline', a.baseline, src0), ('candidate', a.candidate, src1)]:
        out = a.output / kind
        out.mkdir(exist_ok=True)
        stem = out / f'{i:02d}-{Path(source).name}'
        includes = ['-I.'] + (['-Iinternal'] if kind == 'baseline' else [])
        command = [a.cc] + includes + flags
        pp = run(command + ['-E', '-P', source], cwd=root)
        stem.with_suffix(stem.suffix + '.pp').write_bytes(pp)
        obj = str(stem) + '.o'
        run(command + ['-c', source, '-o', obj], cwd=root)
        nm = run(['nm', '-a', obj]).decode()
        Path(obj + '.nm').write_text(nm)
        undefined = run(['nm', '-u', obj]).decode()
        reloc = None
        if platform.system() == 'Linux':
            reloc = run(['objdump', '-r', obj]).decode()
            Path(obj + '.reloc').write_text(reloc)
        record[kind] = {
            'source_sha256': hashlib.sha256((root / source).read_bytes()).hexdigest(),
            'preprocessed_sha256': hashlib.sha256(pp).hexdigest(),
            'object_sha256': hashlib.sha256(Path(obj).read_bytes()).hexdigest(),
            'definitions': [line for line in nm.splitlines() if len(line.split()) >= 3 and line.split()[-2] != 'U'],
            'undefined': undefined.splitlines(),
            'command': command + ['-c', source, '-o', obj],
        }
    record['preprocessed_equal'] = record['baseline']['preprocessed_sha256'] == record['candidate']['preprocessed_sha256']
    record['object_equal'] = record['baseline']['object_sha256'] == record['candidate']['object_sha256']
    records.append(record)
    print(f'{i:02d} {src0} -> {src1}: pp={record["preprocessed_equal"]} object={record["object_equal"]}', flush=True)

# Capture all explicit labels/directives and their same-file textual reference lines.
# Assembly local label references may not survive as relocations. Do not interpret
# this list or nm -u as exact intra-object function reachability.
import re
labels = []
for source in old:
    lines = (a.baseline / source).read_text().splitlines()
    for n, line in enumerate(lines, 1):
        match = re.match(r'^\s*([A-Za-z_.$][\w.$]*):', line)
        if not match:
            continue
        name = match.group(1)
        refs = [j for j, text in enumerate(lines, 1) if j != n and
                re.search(r'(?<![\w.$])' + re.escape(name) + r'(?![\w.$])', text)]
        labels.append({'source': source, 'line': n, 'label': name, 'same_file_text_refs': refs})
summary = {'host': platform.platform(), 'compiler': run([a.cc, '--version']).decode().splitlines()[0],
           'units': records, 'local_label_reference_index': labels,
           'preprocessed_equal': all(r['preprocessed_equal'] for r in records),
           'objects_equal': all(r['object_equal'] for r in records)}
(a.output / 'audit.json').write_text(json.dumps(summary, indent=2) + '\n')
assert summary['preprocessed_equal'], 'Preprocessor behavior changed'
assert summary['objects_equal'], 'Object mismatch: inspect before accepting path-only equivalence'
