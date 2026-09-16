"""Generate explicit caller selection, not coefficient-dependent dispatch.

Print apply_patch; freezes native timed KEM source as the surrounding path.
"""
from pathlib import Path
p=Path(__file__).resolve().parent
text=(p.parent/'gt864-decaps-scale/kem.c').read_text()
assert text.count('poly_tobytes(')==7
text=text.replace('poly_tobytes(', 'gt864_fr0_tobytes_full(')
for args in ['pk, &h','sk + NTRUPLUS_POLYBYTES, &hinv','ct, &c','buf1, &r2']:
 old=f'gt864_fr0_tobytes_full({args});';assert text.count(old)==1
 text=text.replace(old,f'gt864_fr0_tobytes_small({args});')
text=text.replace('#include "poly.h"','#include "poly.h"\nvoid gt864_fr0_tobytes_small(uint8_t*,const poly*);\nvoid gt864_fr0_tobytes_full(uint8_t*,const poly*);')
print('*** Begin Patch\n*** Add File: experiments/gt864-native-asm/build/kem-bytes.c')
for line in text.splitlines():print('+'+line)
print('*** End Patch')
