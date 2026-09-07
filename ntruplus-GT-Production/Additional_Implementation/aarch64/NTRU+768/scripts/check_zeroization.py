#!/usr/bin/env python3
"""Static gate for Official-aligned C cleanup, not the retired P0-B policy."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def require(relative, needles):
    text = (ROOT / relative).read_text()
    for needle in needles:
        if needle not in text:
            raise SystemExit(f'{relative}: missing {needle!r}')
require('secure_clear.h', ('GT_SECURE_CLEAR_AUDIT_HOOK', 'volatile uint8_t *cursor'))
require('kem.c', (
    'if (!genf_derand(&f, &finv, coins, buf))',
    'if (!geng_derand(&g, &ginv, coins, buf))',
    'gt_secure_clear(buf, sizeof buf);', 'gt_secure_clear(coins, sizeof coins);',
    'gt_secure_clear(&f, sizeof f);', 'gt_secure_clear(&finv, sizeof finv);',
    'gt_secure_clear(&g, sizeof g);', 'gt_secure_clear(&ginv, sizeof ginv);',
    'gt_secure_clear(&h, sizeof h);', 'gt_secure_clear(msg, sizeof msg);',
    'gt_secure_clear(buf1, sizeof buf1);', 'gt_secure_clear(&r, sizeof r);',
    'gt_secure_clear(&m, sizeof m);', 'gt_secure_clear(&scratch, sizeof scratch);',
    'gt_secure_clear(ss, NTRUPLUS_SSBYTES);',
    'gt_internal_poly_tobytes_from_loose(ct, &r);', 'hash_g(ct, ct);'))
require('keygen.c', ('gt_secure_clear(numerator, sizeof numerator);',
                            'gt_secure_clear(den, sizeof den);'))
require('fips202.c', ('gt_secure_clear(state->ctx, PQC_SHAKECTX_BYTES);',
    'gt_secure_clear(state->ctx, PQC_SHAKEINCCTX_BYTES);',
    'gt_secure_clear(t, sizeof t);', 'gt_secure_clear(t, sizeof(t));'))
s = (ROOT/'symmetric.c').read_text()
assert 'gt_secure_clear' not in s[s.index('void hash_f'):s.index('void hash_g')]
for start, end in [('void hash_g', 'void hash_h'), ('void hash_h', None)]:
    section = s[s.index(start):s.index(end) if end else len(s)]
    assert 'gt_secure_clear(data, sizeof data);' in section
for p in ROOT.glob('*.S'):
    assert 'P0-B:' not in p.read_text(), p
# Existing small keygen register cleanups remain; no full-frame wipe promise.
require('keygen_baseinv_prepare.S', ('movi v31.16b, #0',))
require('fqinv.S', ('movi v21.16b, #0',))
print('Official-aligned cleanup source coverage: ok (no full-frame wipe claim)')
