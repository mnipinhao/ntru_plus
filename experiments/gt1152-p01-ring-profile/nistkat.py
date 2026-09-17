"""NIST KAT deterministic RNG: AES-256-ECB plus CTR_DRBG.

Transcribed from Reference_Implementation/NTRU+768/kat/rng.c so that the KAT
transcript can be reproduced without a C toolchain.  Encryption only; this is
test scaffolding, never a production primitive.
"""

SBOX = bytes.fromhex(
    "637c777bf26b6fc53001672bfed7ab76"
    "ca82c97dfa5947f0add4a2af9ca472c0"
    "b7fd9326363ff7cc34a5e5f171d83115"
    "04c723c31896059a071280e2eb27b275"
    "09832c1a1b6e5aa0523bd6b329e32f84"
    "53d100ed20fcb15b6acbbe394a4c58cf"
    "d0efaafb434d338545f9027f503c9fa8"
    "51a3408f929d38f5bcb6da2110fff3d2"
    "cd0c13ec5f974417c4a77e3d645d1973"
    "60814fdc222a908846eeb814de5e0bdb"
    "e0323a0a4906245cc2d3ac629195e479"
    "e7c8376d8dd54ea96c56f4ea657aae08"
    "ba78252e1ca6b4c6e8dd741f4bbd8b8a"
    "703eb5664803f60e613557b986c11d9e"
    "e1f8981169d98e949b1e87e9ce5528df"
    "8ca1890dbfe6426841992d0fb054bb16"
)

RCON = (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36)


def _xtime(a):
    a <<= 1
    if a & 0x100:
        a = (a ^ 0x1B) & 0xFF
    return a


def _mul(a, b):
    """Multiply in GF(2^8) with the AES reduction polynomial."""
    out = 0
    for _ in range(8):
        if b & 1:
            out ^= a
        b >>= 1
        a = _xtime(a)
    return out


def _expand_key_256(key):
    """AES-256 key schedule: 60 words, returned as 15 round keys of 16 bytes."""
    assert len(key) == 32
    words = [list(key[4 * i:4 * i + 4]) for i in range(8)]
    for i in range(8, 60):
        temp = list(words[i - 1])
        if i % 8 == 0:
            temp = temp[1:] + temp[:1]
            temp = [SBOX[b] for b in temp]
            temp[0] ^= RCON[i // 8 - 1]
        elif i % 8 == 4:
            temp = [SBOX[b] for b in temp]
        words.append([words[i - 8][j] ^ temp[j] for j in range(4)])
    return [bytes(b for w in words[4 * r:4 * r + 4] for b in w) for r in range(15)]


def _add_round_key(state, rk):
    return [state[i] ^ rk[i] for i in range(16)]


def _sub_bytes(state):
    return [SBOX[b] for b in state]


def _shift_rows(state):
    # State is column-major: index = 4*col + row.
    out = [0] * 16
    for row in range(4):
        for col in range(4):
            out[4 * col + row] = state[4 * ((col + row) % 4) + row]
    return out


def _mix_columns(state):
    out = [0] * 16
    for col in range(4):
        a = state[4 * col:4 * col + 4]
        out[4 * col + 0] = _mul(a[0], 2) ^ _mul(a[1], 3) ^ a[2] ^ a[3]
        out[4 * col + 1] = a[0] ^ _mul(a[1], 2) ^ _mul(a[2], 3) ^ a[3]
        out[4 * col + 2] = a[0] ^ a[1] ^ _mul(a[2], 2) ^ _mul(a[3], 3)
        out[4 * col + 3] = _mul(a[0], 3) ^ a[1] ^ a[2] ^ _mul(a[3], 2)
    return out


def aes256_ecb_block(key, block):
    """Encrypt one 16-byte block under a 32-byte key."""
    assert len(block) == 16
    round_keys = _expand_key_256(key)
    state = _add_round_key(list(block), round_keys[0])
    for rnd in range(1, 14):
        state = _mix_columns(_shift_rows(_sub_bytes(state)))
        state = _add_round_key(state, round_keys[rnd])
    state = _shift_rows(_sub_bytes(state))
    state = _add_round_key(state, round_keys[14])
    return bytes(state)


class CtrDrbg:
    """NIST SP 800-90A CTR_DRBG(AES-256) as used by the PQC KAT harness."""

    def __init__(self, entropy_input, personalization_string=None):
        seed_material = bytearray(entropy_input)
        assert len(seed_material) == 48
        if personalization_string is not None:
            for i in range(48):
                seed_material[i] ^= personalization_string[i]
        self.key = bytearray(32)
        self.v = bytearray(16)
        self._update(bytes(seed_material))
        self.reseed_counter = 1

    def _increment_v(self):
        for j in range(15, -1, -1):
            if self.v[j] == 0xFF:
                self.v[j] = 0x00
            else:
                self.v[j] += 1
                break

    def _update(self, provided_data):
        temp = bytearray()
        for _ in range(3):
            self._increment_v()
            temp += aes256_ecb_block(bytes(self.key), bytes(self.v))
        if provided_data is not None:
            for i in range(48):
                temp[i] ^= provided_data[i]
        self.key = bytearray(temp[:32])
        self.v = bytearray(temp[32:48])

    def randombytes(self, xlen):
        out = bytearray()
        remaining = xlen
        while remaining > 0:
            self._increment_v()
            block = aes256_ecb_block(bytes(self.key), bytes(self.v))
            take = 16 if remaining > 15 else remaining
            out += block[:take]
            remaining -= take
        self._update(None)
        self.reseed_counter += 1
        return bytes(out)


def self_test():
    """FIPS-197 C.3 AES-256 known-answer vector."""
    key = bytes(range(32))
    plaintext = bytes.fromhex("00112233445566778899aabbccddeeff")
    expected = bytes.fromhex("8ea2b7ca516745bfeafc49904b496089")
    got = aes256_ecb_block(key, plaintext)
    assert got == expected, f"AES-256 self-test failed: {got.hex()} != {expected.hex()}"
    return True


if __name__ == "__main__":
    self_test()
    print("nistkat: AES-256 FIPS-197 C.3 vector OK")
