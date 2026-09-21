#!/usr/bin/env python3
"""Run the refinement generator, then test its constants against AVX2 hardware."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    subprocess.run([sys.executable, str(ROOT/'tools/refine_encap_range.py')], check=True)
    report = ROOT/'generated/tile4_encap_range_refined.json'
    model = json.loads(report.read_text())
    build = ROOT/'build/range-refinement'
    build.mkdir(parents=True, exist_ok=True)
    source = ROOT/'tests/test_range_word_semantics.c'
    binary = build/'word-semantics'
    flags = ['-O2', '-mavx2', '-std=c11', '-Wall', '-Wextra', '-Werror',
             '-fsanitize=undefined', '-fno-sanitize-recover=all']
    subprocess.run(['cc', *flags, str(source), '-o', str(binary)], check=True)
    result = json.loads(subprocess.check_output(
        [str(binary), *sorted(model['constants_QINV'], key=int)], text=True))
    assert result['montgomery_cases'] == model['full_domain_constant_checks']
    result.update(compiler=subprocess.check_output(['cc','--version'], text=True).splitlines()[0],
                  flags=flags, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  elf_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                  model_sha256=hashlib.sha256(report.read_bytes()).hexdigest(),
                  scope='AVX2 arithmetic macro conformance only; not whole NTT binary proof')
    (ROOT/'generated/tile4_encap_range_word_conformance.json').write_text(
        json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
