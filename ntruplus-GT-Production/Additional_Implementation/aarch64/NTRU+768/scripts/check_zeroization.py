#!/usr/bin/env python3
"""Static gate for Official-aligned C cleanup, not the retired P0-B policy."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def require(relative, needles):
    text = (ROOT / relative).read_text()
    for needle in needles:
        if needle not in text:
            raise SystemExit(f'{relative}: missing {needle!r}')
require('util.h', ('GT_SECURE_CLEAR_AUDIT_HOOK', 'volatile uint8_t *cursor'))
require('kem.c', (
    'if (!genf_derand(&f, &finv, coins, buf))',
    'if (!geng_derand(&g, &ginv, coins, buf))',
    'secure_clear(buf, sizeof buf);', 'secure_clear(coins, sizeof coins);',
    'secure_clear(&f, sizeof f);', 'secure_clear(&finv, sizeof finv);',
    'secure_clear(&g, sizeof g);', 'secure_clear(&ginv, sizeof ginv);',
    'secure_clear(&h, sizeof h);', 'secure_clear(msg, sizeof msg);',
    'secure_clear(buf1, sizeof buf1);', 'secure_clear(&r, sizeof r);',
    'secure_clear(&m, sizeof m);', 'secure_clear(&scratch, sizeof scratch);',
    'secure_clear(ss, NTRUPLUS_SSBYTES);',
    'poly_tobytes_encap_loose(ct, &r);', 'hash_g(ct, ct);'))
require('keygen.c', ('secure_clear(numerator, sizeof numerator);',
                            'secure_clear(den, sizeof den);'))
require('fips202.c', ('secure_clear(state->ctx, PQC_SHAKECTX_BYTES);',
    'secure_clear(state->ctx, PQC_SHAKEINCCTX_BYTES);',
    'secure_clear(t, sizeof t);', 'secure_clear(t, sizeof(t));'))
s = (ROOT/'symmetric.c').read_text()
assert 'secure_clear' not in s[s.index('void hash_f'):s.index('void hash_g')]
g = s[s.index('void hash_g'):s.index('void hash_h')]
assert 'ntruplus_hash_g_fixed(buf, msg);' in g
assert 'uint8_t data[' not in g
require('fips202.c', ('void ntruplus_hash_g_fixed(', 'secure_clear(s, sizeof s);'))
# The fused hash_g kernels are gone: the sponge is portable C over the
# permutation, so the wipe that used to live at the end of each kernel now lives
# once in shake256_prefixed, checked above.  Assert the assembly is back to the
# permutation alone, with no fixed-size sponge left to audit separately.
for backend in ('keccakf1600.S', 'keccakf1600_v84a.S'):
    text = (ROOT / backend).read_text()
    if 'fused' in text:
        raise SystemExit(f'{backend}: a fused sponge is back; re-audit its wipe')
require('keccakf1600.S', ('C_SYM(ntruplus_keccak_f1600_x1_aarch64):',))
require('keccakf1600_v84a.S', ('C_SYM(ntruplus_keccak_f1600_x1_v84a_aarch64):',))
# hash_f and hash_h used to build 0x00||msg and 0x02||msg in a stack buffer and
# (for hash_h) wipe it afterwards.  They now absorb through shake256_prefixed,
# so there is no copy to wipe -- the same invariant hash_g already had above,
# which is strictly stronger than wiping one.
for start, end in [('void hash_f', 'void hash_g'), ('void hash_h', None)]:
    section = s[s.index(start):s.index(end) if end else len(s)]
    assert 'uint8_t data[' not in section, start
    assert 'memcpy(' not in section, start
    assert 'shake256_prefixed(' in section, start
require('fips202.c', ('void shake256_prefixed(', 'secure_clear(s, sizeof s);',
                      'secure_clear(tail, sizeof tail);'))
for p in ROOT.glob('*.S'):
    assert 'P0-B:' not in p.read_text(), p
# Existing small keygen register cleanups remain; no full-frame wipe promise.
require('base.S', ('movi v31.16b, #0',))
require('base.S', ('movi v21.16b, #0',))
print('Official-aligned cleanup source coverage: ok (no full-frame wipe claim)')
