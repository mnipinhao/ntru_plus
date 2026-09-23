"""P121: Official-style Name/Description/Arguments/Returns headers for the NTRU+768
assembly entries that had none (comments only).  usage: headers.py TREE"""
import pathlib, sys, textwrap
T = pathlib.Path(sys.argv[1])
def block(name, desc, args, ret):
    L = ['/*************************************************', f'* Name:        {name}', '*']
    d = textwrap.wrap(desc, 62)
    L += [f'* Description: {d[0]}'] + [f'*              {x}' for x in d[1:]] + ['*']
    first = True
    for a in args:
        w = textwrap.wrap(a, 60)
        L += [f"* {'Arguments:  ' if first else '            '} - {w[0]}"] + [f'*                {x}' for x in w[1:]]
        first = False
    L += ['*']
    r = textwrap.wrap(ret, 62)
    L += [f'* Returns:     {r[0]}'] + [f'*              {x}' for x in r[1:]] + ['**************************************************/']
    return '\n'.join(L) + '\n'
H = {
 ('add.S', 'poly_sub'): block('poly_sub', 'Coefficient-wise subtraction out = a - b, without reduction. Saves no SIMD callee-saved registers because it uses none.',
    ['poly *out: output polynomial; may alias a or b exactly', 'const poly *a: minuend', 'const poly *b: subtrahend'], 'none. Coefficients are the int16 differences.'),
 ('add.S', 'poly_triple'): block('poly_triple', 'Coefficient-wise multiplication by 3, without reduction.',
    ['poly *out: output polynomial; may alias in exactly', 'const poly *in: input polynomial'], 'none. Coefficients are 3 * in (int16).'),
 ('cbd.S', 'poly_cbd1'): block('poly_cbd1', 'Samples a polynomial from the centered binomial distribution with parameter eta = 1.',
    ['poly *out: output polynomial', 'const uint8_t *buf: NTRUPLUS_N/4 input bytes'], 'none. Output coefficients lie in {-1,0,1}.'),
 ('cbd.S', 'poly_sotp_encode'): block('poly_sotp_encode', 'Encodes a message using a one-time pad and centered binomial sampling with parameter eta = 1.',
    ['poly *out: output polynomial', 'const uint8_t *msg: NTRUPLUS_N/8 message bytes', 'const uint8_t *buf: NTRUPLUS_N/4 pad bytes'], 'none. Output coefficients lie in {-1,0,1}.'),
 ('cbd.S', 'poly_sotp_decode'): block('poly_sotp_decode', 'Decodes a message using the inverse one-time-pad operation and checks that every recovered coefficient is valid.',
    ['uint8_t *msg: NTRUPLUS_N/8 output bytes', 'const poly *a: input polynomial', 'const uint8_t *buf: NTRUPLUS_N/4 pad bytes'], '0 on success and 1 on failure.'),
 ('base.S', 'poly_basemul_add_encap'): block('poly_basemul_add_encap', 'Encapsulation product out = a * b + c in the block-major NTT domain, with a Q31 final reduction.',
    ['poly *out: output polynomial; may alias c exactly (the KEM passes out == c), no other overlap',
     'const poly *a: decoded public key h, coefficients in [0,q)',
     'const poly *b: output of poly_ntt_encap_small_lazy, |coefficient| <= 21050',
     'const poly *c: output of poly_ntt_encap_small_lazy, |coefficient| <= 21050'],
    'none. Output coefficients lie in (-q,q), the input range of poly_tobytes_encap.'),
 ('base.S', 'gt_keygen_baseinv_cq_finish'): block('gt_keygen_baseinv_cq_finish', 'Completes the keygen base inversion: multiplies each CQ numerator by the inverse of its denominator.',
    ['x0 = int16_t out_cq[24][32]: base inverses, CQ layout', 'x1 = const int16_t numerator[24][32]', 'x2 = const int16_t den[24][8]: inverted denominators'], 'none.'),
 ('pack.S', 'poly_tobytes_encap'): block('poly_tobytes_encap / poly_tobytes_encap_loose', 'Canonical 12-bit encoding of a block-major (Encap) polynomial, applying the Good-Thomas permutation. poly_tobytes_encap expects reduced coefficients; poly_tobytes_encap_loose first Barrett-reduces arbitrary int16 representatives.',
    ['uint8_t *out: NTRUPLUS_POLYBYTES output bytes', 'const poly *a: block-major polynomial; coefficients in (-q,q) for poly_tobytes_encap, any int16 for the loose entry'], 'none.'),
 ('pack.S', 'poly_frombytes_encap'): block('poly_frombytes_encap', 'Checked decoding of canonical 12-bit bytes into the block-major (Encap) layout.',
    ['poly *out: output polynomial, block-major', 'const uint8_t *in: NTRUPLUS_POLYBYTES input bytes'], '0 on success, 1 if any coefficient is >= q. Output coefficients lie in [0,4095] and are complete on either return.'),
 ('pack.S', 'poly_tobytes_keygen_cq'): block('poly_tobytes_keygen_cq', 'Canonical 12-bit encoding of a key-generation CQ polynomial.',
    ['uint8_t *out: NTRUPLUS_POLYBYTES output bytes', 'const gt_cq_poly *in: CQ polynomial, coefficients in (-q,q)'], 'none.'),
 ('keccakf1600.S', 'ntruplus_keccak_f1600_x1_aarch64'): block('ntruplus_keccak_f1600_x1_aarch64', 'Keccak-f[1600] permutation of one state, scalar AArch64 backend (used when __ARM_FEATURE_SHA3 is not defined).',
    ['uint64_t *state: 25-lane state, permuted in place', 'const uint64_t *rc: the 24 round constants'], 'none.'),
 ('keccakf1600_v84a.S', 'ntruplus_keccak_f1600_x1_v84a_aarch64'): block('ntruplus_keccak_f1600_x1_v84a_aarch64', 'Keccak-f[1600] permutation of one state using the Armv8.4-A SHA3 instructions; assembled only when __ARM_FEATURE_SHA3 is defined. Saves and restores d8-d15.',
    ['uint64_t *state: 25-lane state, permuted in place', 'const uint64_t *rc: the 24 round constants'], 'none.'),
 ('decap_ntt.S', 'poly_ntt_decap'): block('poly_ntt_decap', 'Good-Thomas forward NTT for decapsulation re-encryption. Uses a 1,696-byte stack frame; [sp, #0] is a Slothy spill slot.',
    ['poly *out: output polynomial, Decap QSoA layout', 'const poly *in: input polynomial in coefficient order, signed coefficients in [-2,2]'], 'none.'),
 ('ntt.S', 'poly_ntt_loose'): block('poly_ntt_loose', 'Validation entry of the shared forward core (mode 0); the KEM does not call it.',
    ['poly *out: output polynomial, block-major, coefficients in [-27548,27548]', 'const poly *in: input polynomial in coefficient order'], 'none.'),
 ('ntt.S', 'poly_ntt_keygen_cq'): block('poly_ntt_keygen_cq', 'Key-generation forward NTT (mode 1) writing the CQ layout consumed by poly_baseinv_keygen_cq_scaled_r.',
    ['gt_cq_poly *out: output, key-generation CQ layout', 'const poly *in: 3f+1 or 3g in coefficient order'], 'none.'),
 ('ntt.S', 'poly_ntt_encap_small'): block('poly_ntt_encap_small', 'Validation entry (mode 2): small-input forward NTT bit-exact to poly_ntt_loose; the KEM uses poly_ntt_encap_small_lazy.',
    ['poly *out: output polynomial, block-major; may alias in exactly', 'const poly *in: signed coefficients in [-2,2]'], 'none.'),
 ('ntt.S', 'poly_ntt_encap_small_lazy'): block('poly_ntt_encap_small_lazy', 'Encapsulation forward NTT (mode 3) for r and m.',
    ['poly *out: output polynomial, block-major, coefficients in [-21050,21050]; may alias in exactly', 'const poly *in: signed coefficients in [-2,2]'], 'none.'),
}
for (f, sym), text in H.items():
    p = T / f; s = p.read_text(); anchor = f'.global C_SYM({sym})'
    assert s.count(anchor) == 1, (f, sym)
    s = s.replace(anchor, text + anchor); p.write_text(s)
# the one-line finish comment and the decap_ntt ABI line are now covered by the headers
for f, old in (('base.S', '/* x0=CQ output, x1=CQ numerator scratch, x2=inverted denominators. */\n'),
               ('decap_ntt.S', '/* ABI: x0=dst, x1=src. The 1536-byte row scratch is stack-local. */\n')):
    p = T / f; s = p.read_text(); assert s.count(old) == 1, old; p.write_text(s.replace(old, ''))
print(f'{len(H)} headers added')
