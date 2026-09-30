#!/usr/bin/env python3
"""Distinct instruction bytes one KEM operation executes, from a callgrind profile collected
only inside that entry point (--collect-atstart=no --toggle-collect=crypto_kem_<op>
--dump-instr=yes --dump-line=no --compress-pos=no --compress-strings=no).  AArch64 instructions
are 4 bytes.  KEM code is the measured program's own code.  The C library's code (memcpy,
memset, malloc, free, ...) is counted apart, and the dynamic loader's is left out: it only binds
the program's calls into the C library the first time they are made.  Callgrind gives each
address relative to its object, so the object decides where an address counts.
(lackey's --trace-mem would record the addresses directly, but on the Pi it spins.)
usage: footprint.py CALLGRIND_OUT"""
import os, sys
program = obj = None; own = set(); lib = set()
for line in open(sys.argv[1]):
    if line.startswith('cmd:'): program = os.path.basename(line.split()[1]); continue
    if line.startswith('ob='): obj = os.path.basename(line[3:].strip()); continue
    if not line.startswith('0x') or obj is None: continue
    a = int(line.split()[0], 16)
    if obj == program: own.add(a)
    elif obj.startswith('libc.so'): lib.add(a)
print(f'{4 * len(own)} bytes KEM code, {4 * len(lib)} bytes library code')
