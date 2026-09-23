"""P121: NTRU+768 file and header restructuring (behaviour-preserving).

- crepmod3.S -> test/reference/crepmod3.S (test oracle only)
- decap_verify.h -> decap.h; ntt.h -> encap.h, which also takes the Encap-only
  declarations from poly.h; validation-only declarations move to
  test/reference/poly_reference.h
- layout.h merged into keygen.h; keygen_lambda.c + basemul_lambda.c -> tables.c,
  with their tables declared in keygen.h / encap.h
- ntt.S split: ntt.S (shared forward core with all Encap/keygen/validation
  entries, the lazy entry now next to its core), decap_ntt.S, decap_invntt.S
- Makefile, check_release.py, export_supercop.py and includes follow
usage: structure.py TREE   (run inside a git work tree; uses git mv)
"""
import re, subprocess, sys, pathlib
T = pathlib.Path(sys.argv[1])
def rd(p): return (T / p).read_text()
def wr(p, s): (T / p).write_text(s)
def mv(a, b): subprocess.run(['git', 'mv', a, b], cwd=T, check=True)
def sub1(p, a, b):
    s = rd(p); assert s.count(a) == 1, (p, a[:60]); wr(p, s.replace(a, b))

CSYM = """#ifndef C_SYM
#ifdef __APPLE__
#define C_SYM_1(sym) _##sym
#define C_SYM(sym) C_SYM_1(sym)
#else
#define C_SYM(sym) sym
#endif
#endif
"""

# ---- 1. crepmod3.S becomes a test oracle
mv('crepmod3.S', 'test/reference/crepmod3.S')

# ---- 2. headers
mv('decap_verify.h', 'decap.h')
s = rd('decap.h').replace('NTRUPLUS768_INTERNAL_DECAP_VERIFY_H', 'NTRUPLUS768_DECAP_H')
s = s.replace('#include <stdint.h>\n', '#include <stdint.h>\n', 1)
s = re.sub(r'^(#define NTRUPLUS768_DECAP_H\n)', r'\1\n/* Decapsulation endpoints (private to kem.c); layouts in docs/IMPLEMENTATION.md. */\n', s, flags=re.M)
wr('decap.h', s)

mv('ntt.h', 'encap.h')
poly = rd('poly.h')
blk_tobytes = """/* Canonical encoding of a reduced block-major (Encap) polynomial: the
 * ciphertext boundary.  Key generation packs pk/sk with poly_tobytes_keygen_cq. */
void poly_tobytes_encap(uint8_t out[NTRUPLUS_POLYBYTES], const poly *a);
/*
 * Decode every coefficient and return 1 iff any decoded 12-bit value is
 * outside [0, NTRUPLUS_Q). The output is complete on both return paths.
 */
int poly_frombytes_encap(poly *out,
                   const uint8_t in[NTRUPLUS_POLYBYTES]);
"""
blk_muladd = """/* Encapsulation-only a*b+c endpoint; its result is packed immediately. */
void poly_basemul_add_encap(poly *out, const poly *a, const poly *b,
                      const poly *c);
"""
blk_crep = """/* Centers modulo q, then modulo 3; input [-3456,3456]. Exact alias allowed.
 * Test oracle: the KEM uses the mod 3 fused into poly_invntt_ternary_decap. */
void poly_crepmod3(poly *out, const poly *in);
"""
for b in (blk_tobytes, blk_muladd, blk_crep):
    assert poly.count(b) == 1, b[:40]; poly = poly.replace(b, '')
poly = re.sub(r'\n{3,}', '\n\n', poly)
poly = poly.replace('} poly __attribute__((aligned(16)));\n',
                    '} poly __attribute__((aligned(16)));\n\n/* Shared polynomial helpers; operation-specific endpoints are in encap.h,\n * keygen.h and decap.h. */\n')
wr('poly.h', poly)

enc = rd('encap.h')
enc = enc.replace('NTRUPLUS768_NTT_H', 'NTRUPLUS768_ENCAP_H')
loose = re.search(r'/\*\n \* Internal GT transform contracts;.*?\*/\nvoid poly_ntt_loose\(poly \*out, const poly \*in\);\n\n', enc, flags=re.S).group(0)
small = re.search(r'/\* Encap CBD/SOTP input only:.*?\*/\nvoid poly_ntt_encap_small\(poly \*out, const poly \*in\);\n\n', enc, flags=re.S).group(0)
enc = enc.replace(loose, '').replace(small, '')
enc = enc.replace('#include "poly.h"\n',
                  '#include "poly.h"\n\n/* Encapsulation endpoints (private to kem.c).  Block-major layout and the\n * loose range are described in docs/IMPLEMENTATION.md. */\n\n'
                  + blk_tobytes + '\n' + blk_muladd +
                  '\n/* Lambda table of the Encap basemul-add (tables.c; consumed by base.S). */\n'
                  'extern const int16_t gt_rowbitrev_lambda[2][96];\n')
wr('encap.h', re.sub(r'\n{3,}', '\n\n', enc))

ref = rd('test/reference/poly_reference.h')
ref = ref.replace('void poly_invntt(poly *out, const poly *in);\n',
                  'void poly_invntt(poly *out, const poly *in);\n\n'
                  + blk_crep.replace(' * Test oracle: the KEM uses', ' * Test oracle (test/reference/crepmod3.S): the KEM uses') +
                  '\n/* Validation entries of the shared forward core in ntt.S (not called by the\n'
                  ' * KEM).  poly_ntt_loose: generic input, block-major output in\n'
                  ' * [-27548,27548].  poly_ntt_encap_small: signed [-2,2] input, bit-exact to\n'
                  ' * poly_ntt_loose, in-place allowed. */\n'
                  'void poly_ntt_loose(poly *out, const poly *in);\n'
                  'void poly_ntt_encap_small(poly *out, const poly *in);\n')
wr('test/reference/poly_reference.h', ref)

# ---- 3. layout.h -> keygen.h; tables
lay = rd('layout.h')
body = lay[lay.index('/* Keygen-only CQ layout'):lay.rindex('#endif')]
kg = rd('keygen.h').replace('#include "layout.h"\n',
                            '#include <stdint.h>\n\n#include "poly.h"\n\n' + body +
                            '#define GT_KEYGEN_CQ_GROUPS 24\n\n'
                            '/* Quartic lambda table of the keygen CQ pipeline (tables.c). */\n'
                            'extern const int16_t gt_keygen_bpq_lambda8[GT_KEYGEN_CQ_GROUPS][8];\n\n')
wr('keygen.h', kg)
subprocess.run(['git', 'rm', '-q', 'layout.h'], cwd=T, check=True)
sub1('keygen.c', """#define GT_KEYGEN_CQ_GROUPS 24

extern const int16_t gt_keygen_bpq_lambda8[GT_KEYGEN_CQ_GROUPS][8];

""", '')
kl = rd('keygen_lambda.c'); bl = rd('basemul_lambda.c')
kl = kl.replace('#include "params.h"\n', '#include "params.h"\n#include "keygen.h"\n#include "encap.h"\n')
kl = kl.replace('#define GT_KEYGEN_CQ_GROUPS 24\n\n', '')
bl = bl.replace('#include <stdint.h>\n', '')
tables = ('/* Constant tables of the NTRU+768 GT pipeline: the keygen CQ quartic lambdas\n'
          ' * and the Encap basemul-add row lambdas. */\n' + kl.rstrip() + '\n\n/* Encap basemul-add row lambdas (row-bit-reversed order). */\n' + bl.lstrip())
wr('tables.c', tables)
subprocess.run(['git', 'rm', '-q', 'keygen_lambda.c', 'basemul_lambda.c'], cwd=T, check=True)
subprocess.run(['git', 'add', 'tables.c'], cwd=T, check=True)

# ---- 4. split ntt.S
L = rd('ntt.S').split('\n')
def at(p): return [i for i, l in enumerate(L) if p in l][0]
a = at('/* Section: decap_invntt.S'); b = at('/* End section: decap_invntt.S */')
c = at('/* Section: decap_forward.S'); d = at('/* End section: decap_forward.S */')
core, inv, fwd, tail = L[:a], L[a:b + 1], L[c:d + 1], L[d + 1:]
wr('decap_invntt.S', CSYM + '\n' + '\n'.join(inv) + '\n')
wr('decap_ntt.S', CSYM + '\n' + '\n'.join(fwd) + '\n')
subprocess.run(['git', 'add', 'decap_invntt.S', 'decap_ntt.S'], cwd=T, check=True)
new = '\n'.join(core).rstrip() + '\n\n' + '\n'.join(tail).lstrip('\n')
new = new.replace(""" *   module_ntt_            shared forward core with poly_ntt_loose (validation),
 *                          poly_ntt_keygen_cq and poly_ntt_encap_small; the
 *                          poly_ntt_encap_small_lazy entry, at the end of the file,
 *                          branches back into this core
 *   module_decap_invntt_   poly_invntt_ternary_decap (decapsulation inverse)
 *   module_decap_forward_  poly_ntt_decap (decapsulation forward)""",
""" *   poly_ntt_keygen_cq          keygen, CQ output
 *   poly_ntt_encap_small_lazy   Encap r and m (at the end of this file)
 *   poly_ntt_loose              validation: generic input
 *   poly_ntt_encap_small        validation: bit-exact small-input variant
 * The decapsulation transforms are in decap_ntt.S (forward) and
 * decap_invntt.S (inverse).""")
new = new.replace('/* NTRU+768 Good-Thomas transforms.  Sections, in file order:',
                  '/* NTRU+768 Good-Thomas forward NTT: one shared core (module_ntt_) with four\n * entries selected by a mode register:')
wr('ntt.S', new)

# ---- 5. build system and checks
mk = rd('Makefile')
old = mk[mk.index('PUBLIC_ASM := \\'):mk.index('KAT_REQ :=')]
mk = mk.replace(old, """KEM_ASM := \\
	ntt.S \\
	decap_ntt.S \\
	decap_invntt.S \\
	base.S \\
	pack.S \\
	cbd.S \\
	add.S \\
	keccakf1600.S \\
	keccakf1600_v84a.S \\
	kem_api.S

KEM_C := \\
	kem.c \\
	symmetric.c \\
	fips202.c \\
	keygen.c \\
	tables.c

REFERENCE_ASM := test/reference/basemul.S test/reference/invntt.S \\
	test/reference/crepmod3.S

KEM_SOURCES := $(KEM_C) $(KEM_ASM)

""")
mk = mk.replace('$(TEST_SUPPORT): test/test_support.c $(KEM_SOURCES) randombytes.c | $(BUILD_DIR)',
                '$(TEST_SUPPORT): test/test_support.c test/reference/crepmod3.S $(KEM_SOURCES) randombytes.c | $(BUILD_DIR)')
wr('Makefile', mk)

cr = rd('scripts/check_release.py')
cr = cr.replace("""headers = (ROOT / "poly.h").read_text(encoding="utf-8")
reference_header = (ROOT / "test/reference/poly_reference.h").read_text()
for symbol in ("poly_basemul", "poly_invntt"):
    if re.search(rf"\\b{symbol}\\s*\\(", headers):
        fail(f"test-only declaration in production header: {symbol}")
    if not re.search(rf"\\b{symbol}\\s*\\(", reference_header):
        fail(f"missing test-only declaration: {symbol}")
for symbol in REQUIRED_PUBLIC_SYMBOLS:
    if re.search(rf"\\b{re.escape(symbol)}\\s*\\(", headers) is None:
        fail(f"missing public declaration: {symbol}")

kem_source = (ROOT / "kem.c").read_text(encoding="utf-8")
internal_headers = (ROOT / "ntt.h").read_text(encoding="utf-8")""",
"""production_headers = "".join(
    path.read_text(encoding="utf-8") for path in sorted(ROOT.glob("*.h")))
reference_header = (ROOT / "test/reference/poly_reference.h").read_text()
for symbol in TEST_ONLY_SYMBOLS:
    if re.search(rf"\\b{symbol}\\s*\\(", production_headers):
        fail(f"test-only declaration in production header: {symbol}")
    if not re.search(rf"\\b{symbol}\\s*\\(", reference_header):
        fail(f"missing test-only declaration: {symbol}")
headers = (ROOT / "encap.h").read_text(encoding="utf-8")
for symbol in REQUIRED_PUBLIC_SYMBOLS:
    if re.search(rf"\\b{re.escape(symbol)}\\s*\\(", headers) is None:
        fail(f"missing Encap declaration: {symbol}")

kem_source = (ROOT / "kem.c").read_text(encoding="utf-8")
internal_headers = headers""")
cr = cr.replace('EXPECTED_KAT_RSP_SHA256 = (',
                'TEST_ONLY_SYMBOLS = (\n    "poly_basemul",\n    "poly_invntt",\n    "poly_crepmod3",\n'
                '    "poly_ntt_loose",\n    "poly_ntt_encap_small",\n)\nEXPECTED_KAT_RSP_SHA256 = (')
cr = cr.replace('    "ntt.S",\n', '    "ntt.S",\n    "decap_ntt.S",\n    "decap_invntt.S",\n')
cr = cr.replace('    "crepmod3.S",\n', '')
cr = cr.replace('    "ntt.h",\n', '    "encap.h",\n    "decap.h",\n    "keygen.h",\n    "tables.c",\n')
cr = cr.replace('    "test/reference/invntt.S",\n', '    "test/reference/invntt.S",\n    "test/reference/crepmod3.S",\n')
wr('scripts/check_release.py', cr)

ex = rd('scripts/export_supercop.py')
ex = ex.replace("assert not ({'poly_basemul', '_poly_basemul', 'poly_invntt', '_poly_invntt',",
                "assert not ({'poly_basemul', '_poly_basemul', 'poly_invntt', '_poly_invntt',\n             'poly_crepmod3', '_poly_crepmod3',")
wr('scripts/export_supercop.py', ex)

# ---- 6. includes
sub1('kem.c', '#include "decap_verify.h"\n', '#include "decap.h"\n')
sub1('kem.c', '#include "ntt.h"\n', '#include "encap.h"\n')
sub1('test/test_abi.c', '#include "decap_verify.h"\n', '#include "decap.h"\n#include "encap.h"\n')
sub1('test/test_ntt_small.c', '#include "ntt.h"\n', '#include "encap.h"\n#include "reference/poly_reference.h"\n')
sub1('test/test_support.c', '#include "poly.h"\n', '#include "poly.h"\n#include "reference/poly_reference.h"\n')
print('structure: done')
