#!/usr/bin/env python3
"""Generate the isolated P5 kem.c candidate from the recorded production baseline."""

import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "60b74b054a773efc77595bd90424cb8c26f18931"
SOURCE_PATH = "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/kem.c"
EXPECTED_SHA256 = "717bb40d760360e1c7aee380f2ac22bca67e83df8aa9b3a4d1d5ad4a949c6a21"
OUT = Path(__file__).resolve().parent / "build/candidate/kem.c"


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"expected one replacement, found {text.count(old)}: {old[:60]!r}")
    return text.replace(old, new)


text = subprocess.check_output(
    ["git", "show", f"{BASE}:{SOURCE_PATH}"], cwd=ROOT, text=True
)
if hashlib.sha256(text.encode()).hexdigest() != EXPECTED_SHA256:
    raise SystemExit("recorded baseline kem.c hash mismatch")

text = replace_once(text, """    poly h, hinv;

    poly_basemul(&h, g, finv);
    poly_basemul(&hinv, f, ginv);

    /* D1 outputs fit (-q,q); the direct Forward result f does not. */
    gt864_fr0_tobytes_small(pk, &h);
    gt864_fr0_tobytes_full(sk, f);
    gt864_fr0_tobytes_small(sk + NTRUPLUS_POLYBYTES, &hinv);
    hash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);
    secure_clear(&h, sizeof h);
    secure_clear(&hinv, sizeof hinv);
""", """    poly h;

    poly_basemul(&h, g, finv);
    gt864_fr0_tobytes_small(pk, &h);

    poly_basemul(&h, f, ginv);
    /* D1 outputs fit (-q,q); the direct Forward result f does not. */
    gt864_fr0_tobytes_full(sk, f);
    gt864_fr0_tobytes_small(sk + NTRUPLUS_POLYBYTES, &h);
    hash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);
    secure_clear(&h, sizeof h);
""")

text = replace_once(text, "\tuint8_t buf2[NTRUPLUS_POLYBYTES];\n\n    poly c, h, r, m;", "    poly c, h, r, m;")
text = replace_once(text, """    gt864_fr0_tobytes_full(buf2, &r);
    hash_g(buf2, buf2);
    poly_sotp_encode(&m, msg, buf2);
""", """    /* ct is dead until the final complete ciphertext serialization. */
    gt864_fr0_tobytes_full(ct, &r);
    hash_g(ct, ct);
    poly_sotp_encode(&m, msg, ct);
""")
text = replace_once(text, """    secure_clear(msg,sizeof msg);
    secure_clear(buf1,sizeof buf1);
    secure_clear(buf2,sizeof buf2);
    secure_clear(&r,sizeof r);
""", """    secure_clear(msg,sizeof msg);
    secure_clear(buf1,sizeof buf1);
    secure_clear(&r,sizeof r);
""")

text = replace_once(text, """    poly c, f, hinv;
    poly r1, r2;
    poly m1, m2;
""", """    /* Four-slot lifetime ABI: c, reusable f/work, hinv, and natural m. */
    poly c, f, hinv, m;
""")
text = replace_once(text, """    gt864_native_basemul_for_inverse(m1.coeffs, c.coeffs, f.coeffs);
    gt864_native_inverse(&m1, &m1);
    poly_crepmod3(&m1, &m1);

    poly_ntt(&m2, &m1);
    poly_sub(&c, &c, &m2);
    poly_basemul(&r2, &c, &hinv);

    gt864_fr0_tobytes_small(buf1, &r2);
    hash_g(buf2, buf1);
    fail = poly_sotp_decode(msg, &m1, buf2);
""", """    gt864_native_basemul_for_inverse(m.coeffs, c.coeffs, f.coeffs);
    gt864_native_inverse(&m, &m);
    poly_crepmod3(&m, &m);

    /* f is dead after the decrypting BaseMul and becomes the work slot. */
    poly_ntt(&f, &m);
    poly_sub(&c, &c, &f);
    poly_basemul(&f, &c, &hinv);

    gt864_fr0_tobytes_small(buf1, &f);
    hash_g(buf2, buf1);
    fail = poly_sotp_decode(msg, &m, buf2);
""")
text = replace_once(text, """    poly_cbd1(&r1, buf3 + NTRUPLUS_SSBYTES);
    poly_ntt(&r1, &r1);
    gt864_fr0_tobytes_full(buf2, &r1);
""", """    poly_cbd1(&f, buf3 + NTRUPLUS_SSBYTES);
    poly_ntt(&f, &f);
    gt864_fr0_tobytes_full(buf2, &f);
""")
text = replace_once(text, """    secure_clear(&r1,sizeof r1);
    secure_clear(&r2,sizeof r2);
    secure_clear(&m1,sizeof m1);
    secure_clear(&m2,sizeof m2);
""", """    secure_clear(&m,sizeof m);
""")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(text)
print(OUT)
