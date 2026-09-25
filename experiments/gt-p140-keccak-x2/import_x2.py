#!/usr/bin/env python3
"""P140: turn mlkem-native's keccak_f1600_x2_v84a_aarch64_asm.S into a standalone GT source file:
the notice and attribution kept verbatim, the three mlkem-native macros replaced by C_SYM, guarded
by __ARM_FEATURE_SHA3 as keccakf1600_v84a.S is.  usage: import_x2.py MLKEM_FILE > keccakf1600_x2_v84a.S"""
import sys
src = open(sys.argv[1]).read().splitlines()
NAME = 'ntruplus_keccak_f1600_x2_v84a_aarch64'
yaml = next(i for i, l in enumerate(src) if l.startswith('/*yaml'))
notice = src[:yaml]
author = [l for l in src[yaml:] if l.startswith('// Author:') or l.startswith('// This implementation') or l.startswith('// The only difference') or l.startswith('// during load')]
a = next(i for i, l in enumerate(src) if 'MLK_ASM_FN_SYMBOL(' in l)
b = next(i for i, l in enumerate(src) if 'MLK_ASM_FN_SIZE(' in l)
body = src[a + 1:b]
assert not any('MLK_' in l for l in body)
out = notice + [''] + author + ['//', '// Imported from mlkem-native (github.com/pq-code-package/mlkem-native, b3ba7b3,',
    '// mlkem/src/fips202/native/aarch64/src/keccak_f1600_x2_v84a_aarch64_asm.S): the',
    '// mlkem-native symbol macros are replaced by C_SYM; the instructions are unchanged.',
    '// void ' + NAME + '(uint64_t state[50], const uint64_t rc[24]): two sequential states.',
    '', '#ifndef C_SYM', '#ifdef __APPLE__', '#define C_SYM_1(sym) _##sym', '#define C_SYM(sym) C_SYM_1(sym)',
    '#else', '#define C_SYM(sym) sym', '#endif', '#endif', '', '#if defined(__ARM_FEATURE_SHA3)', '',
    '.text', '.balign 4', f'.global C_SYM({NAME})', f'C_SYM({NAME}):'] + body + ['', '#endif /* __ARM_FEATURE_SHA3 */', '',
    '#if defined(__linux__) && defined(__ELF__)', '.section .note.GNU-stack,"",%progbits', '#endif']
print('\n'.join(out))
