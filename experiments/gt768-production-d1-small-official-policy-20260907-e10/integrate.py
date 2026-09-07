"""Emit a reviewed apply_patch patch, never edit production implicitly."""
from pathlib import Path
import difflib, re
R = Path(__file__).resolve().parent
W = R.parents[1]
BASE = W.parent
REL = 'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768'
P = W / REL
E08 = BASE / 'gt768-production-policy-threeway-20260907-e08/ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/experiments/gt768-production-policy-threeway-20260907-e08/.build/production-policy'
E03 = BASE / 'gt768-decap-basemul-d1-q31-stagger-20260904-e03' / REL
changes = {}
def put(rel, text): changes[rel] = text
def strip(s):
    def sub(m):
        keep = []
        for line in m[0].splitlines():
            t = line.strip()
            if t.startswith(('/*','*')) or not t: continue
            if re.match(r'(ldp|ldr)\s',t) or re.match(r'add\s+sp\s*,',t) or t == 'ret':
                keep.append(line); continue
            assert re.match(r'(movi|mov|str|stp|subs|b\.ne|ins)\s',t) or t.endswith(':'), t
        return '\n'.join(keep)
    return re.sub(r'[ \t]*/\* P0-B:.*?\*/.*?^[ \t]*ret\b',sub,s,flags=re.S|re.M)
for p in (P/'asm').rglob('*.S'):
    put(str(p.relative_to(P)),strip(p.read_text()))
put('asm/internal/decap_base.S',strip((E03/'asm/internal/decap_base.S').read_text()))
s = changes['asm/ntt.S']
assert 'gt_internal_poly_ntt_encap_small' not in s, 'one-time pristine-base patch builder only'
start = s.index('    add x1, x20, #0'); end = s.index('    ldr w2, [sp, #8]',start)
front = s[start:end]; dead = {}; out = []; removed = 0
for line in front.splitlines(True):
    code = line.split('//')[0].strip()
    m = re.match(r'sqrdmulh v(\d+)\.8H, v(\d+)\.8H, v0\.H\[5\]',code)
    if m:
        assert int(m[1]) not in dead
        dead[int(m[1])] = int(m[2]); removed += 1; continue
    m = re.match(r'mls v(\d+)\.8H, v(\d+)\.8H, v0\.H\[0\]',code)
    if m and int(m[2]) in dead:
        del dead[int(m[2])]; removed += 1; continue
    assert not set(map(int,re.findall(r'\bv(\d+)\.',code))).intersection(dead)
    out.append(line)
assert removed == 96 and not dead
s = s[:start] + '    ldr w2, [sp, #8]\n    cmp w2, #2\n    b.eq .Lencap_small_front\n' + s[start:end] + '.Lntt_endpoint_suffix:\n' + s[end:]
s = s.replace('    cbnz w2, .Lgt_shared_core_cq_suffix','    cmp w2, #1\n    b.eq .Lgt_shared_core_cq_suffix',1)
s += '''
.text
.align 4
/* Encap-only signed [-2,2] input: round(-6844*b/32768) is exactly zero.
 * Delete only that top-split quotient/correction; all subsequent instructions
 * and the block-major loose output contract are identical to generic NTT.
 * Mode 2 is saved before x2 is reused as a table pointer above.
 */
.global gt_internal_poly_ntt_encap_small
.global _gt_internal_poly_ntt_encap_small
#ifndef __APPLE__
.type gt_internal_poly_ntt_encap_small, %function
#endif
gt_internal_poly_ntt_encap_small:
_gt_internal_poly_ntt_encap_small:
    mov w2, #2
    b .Lgt_shared_core_entry
.Lencap_small_front:
''' + ''.join(out) + '    b .Lntt_endpoint_suffix\n'
put('asm/ntt.S',s)
c = (E08/'kem.c').read_text()
assert c.count('gt_internal_poly_ntt_loose(&') == 2
c = c.replace('gt_internal_poly_ntt_loose(&','gt_internal_poly_ntt_encap_small(&')
c = re.sub(r'\n(?:[ \t]*\n){2,}', '\n\n', c)
put('kem.c',c)
put('internal/ntt.h',(P/'internal/ntt.h').read_text().replace('void gt_internal_poly_ntt_loose(poly *out, const poly *in);','''void gt_internal_poly_ntt_loose(poly *out, const poly *in);

/* Encap CBD/SOTP input only: each signed coefficient must be in [-2,2].
 * Bit-exact to generic loose NTT, including in-place operation.
 * Not a replacement for arbitrary/keygen inputs. */
void gt_internal_poly_ntt_encap_small(poly *out, const poly *in);'''))
s = (P/'symmetric.c').read_text(); s=s.replace('    gt_secure_clear(data, sizeof data);','    /* hash_f input is public; follow the Official cleanup policy. */',1)
put('symmetric.c',s)
put('NO_CE/fips202.c',(R/'.build/official/fips202.c').read_text().replace('#include "util.h"','#include "../internal/secure_clear.h"').replace('secure_clear(', 'gt_secure_clear('))
put('NO_CE/fips202.h',(R/'.build/official/fips202.h').read_text())
s=(P/'scripts/check_release.py').read_text().replace('"gt_internal_poly_ntt_loose",','"gt_internal_poly_ntt_encap_small",')
put('scripts/check_release.py',s)
print('*** Begin Patch')
for rel, text in changes.items():
    old=(P/rel).read_text()
    if text == old: continue
    print('*** Update File: '+str(P/rel))
    diff=list(difflib.unified_diff(old.splitlines(True),text.splitlines(True),n=3))[2:]
    for line in diff:
        print('@@' if line.startswith('@@') else line.rstrip('\n'))
print('*** End Patch')
