# NTRU+864 / NTRU+1152 Official AVX2: caller-bounded lazy Forward (Phase A)

Branch `official-opt-lazy-864-1152`, forked from `avx2-official-opt` at
`e76ecdf`. This ports the NTRU+768 caller-lazy Forward
(`docs/ntruplus768-official-opt.md`, Rounds 4-6) to the two larger Official
parameter sets. **Phase A is only about correctness.** No timing, SUPERCOP
campaign, Native measurement or host-control change was made. Native KEM
timing is Phase B.

## Scope

| | NTRU+864 | NTRU+1152 |
|---|---|---|
| Experiment | `NTRU+864/experiments/avx2_official_opt_001` | `NTRU+1152/experiments/avx2_official_opt_001` |
| Upstream (SUPERCOP 20260831, imported once, never edited) | tree `13e0d983…7006` | tree `78daf6b9…5010` |
| Removed block | `ntt.s:365-383` (`#reduce2`), 6 regs/iter | `ntt.s:403-428` (`#reduce2`), 8 regs/iter |
| Removed per Forward | 54 each of `vpmulhrsw`/`vpmullw`/`vpsubw`, plus 1 `_16xv` load | 72 each, plus 1 `_16xv` load |
| Candidate symbol | `ntruplus864_officialopt_ntt_caller_lazy`, 1,329 B | `ntruplus1152_officialopt_ntt_caller_lazy`, 1,569 B |

Every other instruction of Official `poly_ntt` is kept in order. The
general-input `poly_ntt` stays linked and unchanged. The candidate KEM
(`src/kem_lazy.c`) is Official `kem.c`, which is byte-identical for 768, 864
and 1152, with its six `poly_ntt` calls redirected to the namespaced entry.
The entry is valid only for the Official caller domains (inputs in `[-3,4]`).
No general-input claim is made.

The shared, parameterised tooling is in
`ntruplus-ntt-Optimized/Additional_Implementation/avx2/common/official_opt_lazy/`:
`tools/` (generator, linked audit), `tests/` (Forward and KEM differentials),
`range_proof/` (the Phase-0 reduction-audit emulator and ledger, ported to
read the experiment's upstream copy and the generated ASM), and `lazy.mk`.

## Gates (all pass for both parameters)

1. **Generator** (`make check-generate`). It pins the `ntt.s` and `kem.c`
   hashes and asserts that exactly one `#reduce2…#store` block exists, with
   the exact opcode counts. It also checks that each `vpsubw` closes an
   `x -= q·round(x·v/2^15)` on a register that is later stored, that the
   terminal loop runs 9 times, and that `%ymm1` is used nowhere else. The
   derivation is run twice and must be byte-identical. `--check` confirms
   that the committed ASM and KEM equal a fresh regeneration.
2. **Forward differential**. 27,295 cases for 864 and 33,055 for 1152, over
   five caller domains. The patterns are constants, alternating values, 4N
   impulse patterns, 1000 random inputs and 1000 extreme-only inputs.
   - Checks per case: lazy ≡ Official (mod q) in every lane; Official Barrett
     applied to the lazy output equals the Official output bit-exactly; the
     output lies within the per-domain proven bound; the canaries are intact.
   - Extra checks: the producer domains of cbd1, triple and sotp_encode, and
     crepmod3 on every int16 (output `[-2,2]`). The real
     `poly_tobytes`/`poly_frombytes` canonicalise every int16, so the lazy
     representation never reaches the wire.
3. **KEM**. 100 deterministic vectors, with pk/sk/ct/ss byte-exact against
   Official. Invalid PK, bit-flipped CT, noncanonical CT and noncanonical SK
   all behave identically.
   - Forced *g*-retry: `CBD1(g)=0`, 3 draws.
   - Forced *f*-retry: `TEST_F_RETRY`. The keys must equal an uninjected
     keypair whose first coin draw was discarded, which is stronger than the
     fixed draw count used for 768.
   - Natural retries: NTRU+1152 hit 40 natural *f*-inversion and 45 natural
     *g*-inversion retries within the 100 vectors, all byte-exact. This closes
     the "actual f-retry" gap that 768 left open, for 1152 only. NTRU+864 had
     no natural retry, so only the injected *f* path is covered for 864.
4. **Sanitizers**. ASan + UBSan (`-fno-sanitize-recover=all`) + LeakSanitizer
   passed on the Forward test, the KEM test and the KEM f-retry test.
   LeakSanitizer worked on this host, so it was **not** disabled (768 had to
   disable it). `DETECT_LEAKS=0` exists only for hosts where it breaks.
5. **Linked audit** (`results/phase-a/linked-symbol-summary.json`).
   - The symbol is unique, sized and 32-byte aligned. It has one `ret`, no
     stack reference, no call and no `vzeroupper`, and no `vpmulhrsw` or
     `_16xv` remains.
   - Compared row by row against the Official `poly_ntt` in the same ELF,
     every row is identical (branch targets included) except the removed
     block and the `_16xv` load.
   - Call relocations: the lazy KEM object calls the candidate 6 times and
     `poly_ntt` 0 times. The reference KEM calls `poly_ntt` 6 times.
6. **Range proof** (`make range-proof`, `results/phase-a/range-proof-summary.json`).
   - Validation: the emulator matches the machine on `poly_ntt`, the lazy
     entry, `poly_basemul` and `poly_baseinv_1`.
   - Method: a per-lane interval replay of the *generated* lazy ASM. It must
     equal, lane by lane, the Official replay with the terminal Barrett
     skipped. Zero signed-word failures occurred.
   - Lazy output bounds: envelope `[-17961,17957]`; keygen f
     `[-17193,17194]`, g `[-17193,17193]`; decap m′ `[-16382,16385]`;
     encap r/m and re-encryption `[-15580,15580]`.
   - Consumers: BaseInv has no overflow and its zero check is exact. BaseMul
     outputs stay within ±1865. `poly_add` stays within ±17404 (864) or
     ±17436 (1152), and `poly_sub` within `[-16385,19838]`. `tobytes` is
     canonical for every int16.
   - Any drift from the Phase-0 audit bounds is treated as a failure. A
     tampered-ASM negative test failed both `--check` and the range proof,
     as intended.

## Reproduce

```sh
cd ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+864/experiments/avx2_official_opt_001   # or NTRU+1152
make phase-a      # check-upstream, check-generate, Forward+KEM tests, sanitize, audit, range-proof
make record       # phase-a, then refresh results/phase-a/{linked-symbol,range-proof}-summary.json
```

Headers are read (read-only) from the pristine SUPERCOP 20260831 tree
(`SUPERCOP_PRISTINE`, default `/home/nuc/src/supercop-pristine-20260831`).
The deterministic RNG is the NIST KAT DRBG from
`third_party/NTRUplus-official-main`.

## Not done (Phase B and later)

- No component, batch or Native SUPERCOP timing. `performance: not-measured`.
- No qualification export and no installer run.
- No `clean/` change and no promotion.
- No natural *f*-retry for 864; only the injection covers it.
