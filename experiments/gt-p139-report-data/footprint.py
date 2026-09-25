#!/usr/bin/env python3
"""P139: distinct instruction bytes one KEM operation executes, from a callgrind profile collected
only inside that entry point (--collect-atstart=no --toggle-collect=crypto_kem_<op>
--dump-instr=yes --dump-line=no --compress-pos=no --compress-strings=no).  AArch64 instructions
are 4 bytes.  Library code (libc's memcpy/memset/... linked statically) is counted apart.
(lackey's --trace-mem was the first choice; on the Pi it spins, so callgrind it is.)
usage: footprint.py CALLGRIND_OUT"""
import sys, re
LIB = re.compile(r'^(_?_?mem|_?_?bzero|explicit_bzero|__explicit|__libc|_dl|__GI|__stack_chk|strlen|__strlen)')
fn = None; own = set(); lib = set()
for line in open(sys.argv[1]):
    if line.startswith('fn='): fn = line[3:].strip(); continue
    if not line.startswith('0x'): continue
    p = line.split(); a = int(p[0], 16)
    (lib if LIB.match(fn or '') else own).add(a)
print(f'{4 * len(own)} bytes KEM code, {4 * len(lib)} bytes library code')
