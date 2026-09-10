# P5 KEM temporary lifetime ledger

Baseline is production commit `60b74b05`; the linked translation unit is
`kem.c -> kem-normal.o` with the symbol redirects recorded in its Makefile.

## Keygen

| Storage | Definition | Final consumer | Reuse proof |
|---|---|---|---|
| `h` | `g * finv` | public-key ToBytes | Dead before `f * ginv`; that call overwrites all 864 coefficients |
| `hinv` | `f * ginv` | secret-key ToBytes | May occupy the same `h` object after the first serialization |

The surviving object is still cleared once.  The former `h` value was public;
the second value is the same secret-derived `hinv` that the baseline cleared.

## Encaps

| Storage | Definition | Final consumer | Reuse proof |
|---|---|---|---|
| `buf2` | full serialization of NTT-domain `r` | in-place `hash_g`, then `poly_sotp_encode` | `ct` has no final value until the later ciphertext ToBytes, which overwrites all 1296 bytes |

The established `hash_g(out, in)` call already supports `out == in`.  No error
exit exists between the temporary write and the final complete ciphertext write.

## Decaps

| Phase | `c` | `f` | `hinv` | `m` |
|---|---|---|---|---|
| decode | ciphertext | secret f | inverse h | unused |
| decrypt | retained | final consumer as BaseMul input | retained | BaseMul output, then natural message polynomial |
| reencryption 1 | updated by subtract | `NTT(m)`, then `c*hinv` output | final consumer | retained for SOTP decode |
| reencryption 2 | dead | freshly sampled `r`, then `NTT(r)` | dead | retained until decode is complete |

`poly_sub(&c,&c,&f)` is explicitly in-place for its first input.  The D1 BaseMul
loads a complete 24-coefficient group before storing that group; this candidate
does not require its output to alias either input.  Every surviving object is
cleared on both the valid and early-rejection paths.
