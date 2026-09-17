"""Pure-Python NTRU+1152 reference implementation.

Declared oracle for the GT1152 campaign.  Transcribed from
  ntruplus-ntt-Optimized/Reference_Implementation/NTRU+1152/{ntt.c,poly.c}
  ntruplus-ntt-Optimized/Reference_Implementation/NTRU+768/{kem.c,symmetric.c}
with C integer semantics (int16_t wrap-around, arithmetic shifts) preserved
exactly, because several reductions here depend on them.

The zeta table is parsed from the C source rather than copied, so this module
cannot silently drift from the implementation it is supposed to check.
"""

import hashlib
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REF1152 = REPO / "ntruplus-ntt-Optimized/Reference_Implementation/NTRU+1152"
REF864 = REPO / "ntruplus-ntt-Optimized/Reference_Implementation/NTRU+864"

N = 1152
Q = 3457
SYMBYTES = 32
SSBYTES = 32
POLYBYTES = 1728
PUBLICKEYBYTES = POLYBYTES
SECRETKEYBYTES = 2 * POLYBYTES + SYMBYTES
CIPHERTEXTBYTES = POLYBYTES

R = -147          # 2^16 mod q
RINV = -682       # R^-1 mod q
RSQ = 867         # R^2 mod q
QINV = 12929      # q^-1 mod 2^16
OMEGA = -886      # omega * R mod q
ZMINUSZ5INV = -1665
NINV = -1693
TWO_NINV = 71


def s16(x):
    """Truncate to int16_t with C's two's-complement wrap."""
    x &= 0xFFFF
    return x - 0x10000 if x >= 0x8000 else x


def parse_zetas(source=None):
    """Extract `const int16_t zetas[288]` from a reference ntt.c."""
    path = Path(source) if source else REF1152 / "ntt.c"
    text = path.read_text()
    match = re.search(r"const int16_t zetas\[288\]\s*=\s*\{(.*?)\};", text, re.S)
    if not match:
        raise ValueError(f"zetas[288] not found in {path}")
    values = [int(tok) for tok in re.findall(r"-?\d+", match.group(1))]
    if len(values) != 288:
        raise ValueError(f"expected 288 zetas in {path}, got {len(values)}")
    return values


ZETAS = parse_zetas()


# --------------------------------------------------------------------------
# Field arithmetic
# --------------------------------------------------------------------------

def montgomery_reduce(a):
    """int32 -> int16 congruent to a * R^-1 mod q."""
    t = s16(s16(a) * QINV)
    return s16((a - t * Q) >> 16)


_BARRETT_V = ((1 << 26) + Q // 2) // Q


def barrett_reduce(a):
    """int16 -> centered representative in {-(q+1)/2 .. (q+1)/2}."""
    t = s16((_BARRETT_V * a + (1 << 25)) >> 26)
    t = s16(t * Q)
    return s16(a - t)


def fqmul(a, b):
    return montgomery_reduce(a * b)


def fqinv(a):
    """Inverse in Z_q via the reference addition chain (exponent 3455)."""
    t1 = fqmul(a, a)
    t2 = fqmul(t1, t1)
    t2 = fqmul(t2, t2)
    t3 = fqmul(t2, t2)
    t1 = fqmul(t1, t2)
    t2 = fqmul(t1, t3)
    t2 = fqmul(t2, t2)
    t2 = fqmul(t2, a)
    t1 = fqmul(t1, t2)
    t2 = fqmul(t2, t2)
    t2 = fqmul(t2, t2)
    t2 = fqmul(t2, t2)
    t2 = fqmul(t2, t2)
    t2 = fqmul(t2, t2)
    t2 = fqmul(t2, t2)
    t2 = fqmul(t2, t1)
    return fqmul(RINV, t2)


_CREP_V = ((1 << 15) + 3 // 2) // 3


def crepmod3(a):
    """int16 -> {-1,0,1} congruent to a mod 3."""
    a = s16(a + ((a >> 15) & Q))
    a = s16(a - (Q + 1) // 2)
    a = s16(a + ((a >> 15) & Q))
    a = s16(a - (Q - 1) // 2)
    t = s16((_CREP_V * a + (1 << 14)) >> 15)
    t = s16(t * 3)
    return s16(a - t)


# --------------------------------------------------------------------------
# Transform:  2 (alpha/beta CRT) x 9 (two radix-3) x 16 (four radix-2)
#             = 288 leaves of degree 4
# --------------------------------------------------------------------------

def ntt(a):
    r = [0] * N
    k = 1
    zeta1 = ZETAS[k]
    k += 1

    for i in range(N // 2):
        t1 = fqmul(zeta1, a[i + N // 2])
        r[i + N // 2] = s16(a[i] + a[i + N // 2] - t1)
        r[i] = s16(a[i] + t1)

    step = N // 6
    while step >= 64:                      # radix-3 levels: 192, 64
        for start in range(0, N, 3 * step):
            zeta1 = ZETAS[k]
            k += 1
            zeta2 = ZETAS[k]
            k += 1
            for i in range(start, start + step):
                t1 = fqmul(zeta1, r[i + step])
                t2 = fqmul(zeta2, r[i + 2 * step])
                t3 = fqmul(OMEGA, s16(t1 - t2))
                r[i + 2 * step] = s16(r[i] - t1 - t3)
                r[i + step] = s16(r[i] - t2 + t3)
                r[i] = s16(r[i] + t1 + t2)
        step //= 3

    step = 32
    while step >= 4:                       # radix-2 levels: 32, 16, 8, 4
        for start in range(0, N, step << 1):
            zeta1 = ZETAS[k]
            k += 1
            for i in range(start, start + step):
                t1 = fqmul(zeta1, r[i + step])
                r[i + step] = barrett_reduce(s16(r[i] - t1))
                r[i] = barrett_reduce(s16(r[i] + t1))
        step >>= 1

    return r


def invntt(a):
    r = list(a)
    k = 287

    step = 4
    while step <= 32:
        for start in range(0, N, step << 1):
            zeta1 = ZETAS[k]
            k -= 1
            for i in range(start, start + step):
                t1 = r[i + step]
                r[i + step] = fqmul(zeta1, s16(t1 - r[i]))
                r[i] = barrett_reduce(s16(r[i] + t1))
        step <<= 1

    step = 64
    while step <= N // 6:
        for start in range(0, N, 3 * step):
            zeta2 = ZETAS[k]
            k -= 1
            zeta1 = ZETAS[k]
            k -= 1
            for i in range(start, start + step):
                t1 = fqmul(OMEGA, s16(r[i + step] - r[i]))
                t2 = fqmul(zeta1, s16(r[i + 2 * step] - r[i] + t1))
                t3 = fqmul(zeta2, s16(r[i + 2 * step] - r[i + step] - t1))
                r[i] = barrett_reduce(s16(r[i] + r[i + step] + r[i + 2 * step]))
                r[i + step] = t2
                r[i + 2 * step] = t3
        step *= 3

    for i in range(N // 2):
        t1 = s16(r[i] + r[i + N // 2])
        t2 = fqmul(ZMINUSZ5INV, s16(r[i] - r[i + N // 2]))
        r[i] = fqmul(NINV, s16(t1 - t2))
        r[i + N // 2] = fqmul(TWO_NINV, t2)

    return r


# --------------------------------------------------------------------------
# Degree-4 leaf arithmetic in Z_q[X]/(X^4 - zeta)
# --------------------------------------------------------------------------

def basemul(a, b, zeta):
    r = [0] * 4
    r[0] = montgomery_reduce(a[1] * b[3] + a[2] * b[2] + a[3] * b[1])
    r[1] = montgomery_reduce(a[2] * b[3] + a[3] * b[2])
    r[2] = montgomery_reduce(a[3] * b[3])

    r[0] = montgomery_reduce(r[0] * zeta + a[0] * b[0])
    r[1] = montgomery_reduce(r[1] * zeta + a[0] * b[1] + a[1] * b[0])
    r[2] = montgomery_reduce(r[2] * zeta + a[0] * b[2] + a[1] * b[1] + a[2] * b[0])
    r[3] = montgomery_reduce(a[0] * b[3] + a[1] * b[2] + a[2] * b[1] + a[3] * b[0])

    return [montgomery_reduce(x * RSQ) for x in r]


def basemul_add(a, b, c, zeta):
    r = [0] * 4
    r[0] = montgomery_reduce(a[1] * b[3] + a[2] * b[2] + a[3] * b[1])
    r[1] = montgomery_reduce(a[2] * b[3] + a[3] * b[2])
    r[2] = montgomery_reduce(a[3] * b[3])

    r[0] = montgomery_reduce(r[0] * zeta + a[0] * b[0])
    r[1] = montgomery_reduce(r[1] * zeta + a[0] * b[1] + a[1] * b[0])
    r[2] = montgomery_reduce(r[2] * zeta + a[0] * b[2] + a[1] * b[1] + a[2] * b[0])
    r[3] = montgomery_reduce(a[0] * b[3] + a[1] * b[2] + a[2] * b[1] + a[3] * b[0])

    return [montgomery_reduce(c[i] * R + r[i] * RSQ) for i in range(4)]


def baseinv(a, zeta):
    """Quadratic-tower inversion.  Returns (fail, r[4])."""
    t0 = montgomery_reduce(a[2] * a[2] - 2 * a[1] * a[3])
    t1 = montgomery_reduce(a[3] * a[3])
    t0 = montgomery_reduce(a[0] * a[0] + t0 * zeta)
    t1 = montgomery_reduce(a[1] * a[1] + t1 * zeta - 2 * a[0] * a[2])
    t2 = montgomery_reduce(t1 * zeta)

    t3 = montgomery_reduce(t0 * t0 - t1 * t2)
    if t3 == 0:
        return 1, [0, 0, 0, 0]

    r = [
        montgomery_reduce(a[0] * t0 + a[2] * t2),
        montgomery_reduce(a[3] * t2 + a[1] * t0),
        montgomery_reduce(a[2] * t0 + a[0] * t1),
        montgomery_reduce(a[1] * t1 + a[3] * t0),
    ]

    t3 = fqinv(t3)
    signs = (1, -1, 1, -1)
    return 0, [s16(signs[i] * montgomery_reduce(r[i] * t3)) for i in range(4)]


# --------------------------------------------------------------------------
# Polynomial layer
# --------------------------------------------------------------------------

def poly_tobytes(a):
    out = bytearray(POLYBYTES)
    for i in range(N // 2):
        t0 = a[2 * i]
        t0 = s16(t0 + ((t0 >> 15) & Q))
        t1 = a[2 * i + 1]
        t1 = s16(t1 + ((t1 >> 15) & Q))
        out[3 * i + 0] = (t0 >> 0) & 0xFF
        out[3 * i + 1] = ((t0 >> 8) | (t1 << 4)) & 0xFF
        out[3 * i + 2] = (t1 >> 4) & 0xFF
    return bytes(out)


def poly_frombytes(data):
    r = [0] * N
    for i in range(N // 2):
        r[2 * i] = (data[3 * i + 0] | (data[3 * i + 1] << 8)) & 0xFFF
        r[2 * i + 1] = ((data[3 * i + 1] >> 4) | (data[3 * i + 2] << 4)) & 0xFFF
    return r


def poly_cbd1(buf):
    r = [0] * N
    for i in range(N // 8):
        t1 = buf[i]
        t2 = buf[i + N // 8]
        for j in range(8):
            r[8 * i + j] = (t1 & 1) - (t2 & 1)
            t1 >>= 1
            t2 >>= 1
    return r


def poly_sotp_encode(msg, buf):
    tmp = bytearray(N // 4)
    for i in range(N // 8):
        tmp[i] = buf[i] ^ msg[i]
    for i in range(N // 8, N // 4):
        tmp[i] = buf[i]
    return poly_cbd1(tmp)


def poly_sotp_decode(a, buf):
    """Returns (fail, msg).  Mirrors the reference masking exactly."""
    msg = bytearray(N // 8)
    r = 0
    for i in range(N // 8):
        t1 = buf[i]
        t2 = buf[i + N // 8]
        t3 = 0
        for j in range(8):
            t4 = t2 & 1
            t4 = (t4 + a[8 * i + j]) & 0xFFFF
            r |= t4
            t4 = (t4 ^ t1) & 1
            t3 ^= t4 << j
            t1 >>= 1
            t2 >>= 1
        msg[i] = t3 & 0xFF
    r >>= 1
    r = ((-r) & 0xFFFFFFFF) >> 31
    mask = (r - 1) & 0xFF
    for i in range(N // 8):
        msg[i] &= mask
    return r, bytes(msg)


def poly_baseinv(a):
    """Returns (fail, r).  Leaf zeta comes from zetas[144 + i], sign-alternated."""
    r = [0] * N
    for i in range(N // 8):
        zeta = ZETAS[144 + i]
        fail, block = baseinv(a[8 * i:8 * i + 4], zeta)
        if fail:
            return 1, [0] * N
        r[8 * i:8 * i + 4] = block
        fail, block = baseinv(a[8 * i + 4:8 * i + 8], s16(-zeta))
        if fail:
            return 1, [0] * N
        r[8 * i + 4:8 * i + 8] = block
    return 0, r


def poly_basemul(a, b):
    r = [0] * N
    for i in range(N // 8):
        zeta = ZETAS[144 + i]
        r[8 * i:8 * i + 4] = basemul(a[8 * i:8 * i + 4], b[8 * i:8 * i + 4], zeta)
        r[8 * i + 4:8 * i + 8] = basemul(
            a[8 * i + 4:8 * i + 8], b[8 * i + 4:8 * i + 8], s16(-zeta))
    return r


def poly_basemul_add(a, b, c):
    r = [0] * N
    for i in range(N // 8):
        zeta = ZETAS[144 + i]
        r[8 * i:8 * i + 4] = basemul_add(
            a[8 * i:8 * i + 4], b[8 * i:8 * i + 4], c[8 * i:8 * i + 4], zeta)
        r[8 * i + 4:8 * i + 8] = basemul_add(
            a[8 * i + 4:8 * i + 8], b[8 * i + 4:8 * i + 8],
            c[8 * i + 4:8 * i + 8], s16(-zeta))
    return r


def poly_sub(a, b):
    return [s16(a[i] - b[i]) for i in range(N)]


def poly_triple(a):
    return [s16(3 * a[i]) for i in range(N)]


def poly_crepmod3(a):
    return [crepmod3(x) for x in a]


# --------------------------------------------------------------------------
# Symmetric primitives
# --------------------------------------------------------------------------

def shake256(data, outlen):
    return hashlib.shake_256(data).digest(outlen)


def hash_f(msg):
    return shake256(b"\x00" + msg[:POLYBYTES], 32)


def hash_g(msg):
    return shake256(b"\x01" + msg[:POLYBYTES], N // 4)


def hash_h(msg):
    return shake256(b"\x02" + msg[:N // 8 + SYMBYTES], SSBYTES + N // 4)


# --------------------------------------------------------------------------
# KEM
# --------------------------------------------------------------------------

def genf_derand(coins):
    buf = shake256(coins, N // 4)
    f = poly_cbd1(buf)
    f = poly_triple(f)
    f[0] = s16(f[0] + 1)
    f = ntt(f)
    fail, finv = poly_baseinv(f)
    return fail, f, finv


def geng_derand(coins):
    buf = shake256(coins, N // 4)
    g = poly_cbd1(buf)
    g = poly_triple(g)
    g = ntt(g)
    fail, ginv = poly_baseinv(g)
    return fail, g, ginv


def crypto_kem_keypair(rng):
    while True:
        fail, f, finv = genf_derand(rng.randombytes(SYMBYTES))
        if not fail:
            break
    while True:
        fail, g, ginv = geng_derand(rng.randombytes(SYMBYTES))
        if not fail:
            break

    h = poly_basemul(g, finv)
    hinv = poly_basemul(f, ginv)

    pk = poly_tobytes(h)
    sk = poly_tobytes(f) + poly_tobytes(hinv) + hash_f(pk)
    return pk, sk


def crypto_kem_enc_derand(pk, coins):
    msg = bytearray(N // 8 + SYMBYTES)
    msg[:N // 8] = coins[:N // 8]
    msg[N // 8:] = hash_f(pk)

    buf1 = hash_h(bytes(msg))

    r = poly_cbd1(buf1[SYMBYTES:])
    r = ntt(r)

    buf2 = hash_g(poly_tobytes(r))
    m = poly_sotp_encode(msg, buf2)
    m = ntt(m)

    h = poly_frombytes(pk)
    c = poly_basemul_add(h, r, m)
    return poly_tobytes(c), bytes(buf1[:SSBYTES])


def crypto_kem_enc(pk, rng):
    return crypto_kem_enc_derand(pk, rng.randombytes(N // 8))


def crypto_kem_dec(ct, sk):
    c = poly_frombytes(ct)
    f = poly_frombytes(sk)
    hinv = poly_frombytes(sk[POLYBYTES:])

    m1 = poly_basemul(c, f)
    m1 = invntt(m1)
    m1 = poly_crepmod3(m1)

    m2 = ntt(m1)
    c = poly_sub(c, m2)
    r2 = poly_basemul(c, hinv)

    buf1 = poly_tobytes(r2)
    buf2 = hash_g(buf1)
    fail, msg = poly_sotp_decode(m1, buf2)

    msg = bytearray(msg) + bytearray(sk[2 * POLYBYTES:2 * POLYBYTES + SYMBYTES])
    buf3 = hash_h(bytes(msg))

    r1 = poly_cbd1(buf3[SSBYTES:])
    r1 = ntt(r1)
    buf2 = poly_tobytes(r1)

    fail |= 0 if buf1 == buf2 else 1
    mask = 0 if fail else 0xFF
    return fail, bytes(b & mask for b in buf3[:SSBYTES])
