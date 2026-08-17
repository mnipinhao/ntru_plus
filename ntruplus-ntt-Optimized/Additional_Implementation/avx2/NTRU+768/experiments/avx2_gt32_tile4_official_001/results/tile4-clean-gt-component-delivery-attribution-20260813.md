# Clean GT component and delivery attribution (2026-08-13)

## Scope

- Whole-operation control: physically-pruned `avx2-gt-fastest-clean` versus
  Official Main under the SUPERcop cycle harness.
- Encap attribution: exact semantic cumulative prefixes, not a sum of isolated
  E1--E5 microbenchmarks.
- Sign convention: `GT - Official`; negative is favorable to GT.

## Whole SUPERcop result

| Operation | Official | Clean GT | Delta cycles | Favorable ABBA blocks |
| --- | ---: | ---: | ---: | ---: |
| Keypair | 21453.385 | 21402.161 | -51.224 | 3/4 |
| Encap | 28094.948 | 28132.995 | +38.047 | 1/4 |
| Decap | 19410.990 | 19351.188 | -59.802 | 2/4 |

## Encap cumulative-prefix result

The prefixes execute the real caller order:

1. `P1`: decode `h`, hash `msg`, CBD `r`
2. `P2`: Forward `r`
3. `P3`: pack `rhat`, `hash_g`, SOTP-produce `m`
4. `P4`: Forward `m`
5. `P5`: general BaseMul
6. `P6`: add `m`
7. `P7`: ciphertext pack, shared-secret delivery and cleanup

Every checkpoint passed byte-exact differential comparison.

Four-pair region-scoped PMU medians:

| Prefix | Normal cumulative core-cycle delta | Reversed cumulative core-cycle delta | Normal cumulative instruction delta | Reversed cumulative instruction delta |
| --- | ---: | ---: | ---: | ---: |
| P1 | +53 | +33 | +78 | +71 |
| P2 | -143 | +26 | -359 | -116 |
| P3 | +83 | +20 | -190 | -224 |
| P4 | +153 | -109 | -230 | -724 |
| P5 | +183 | +92 | -698 | -494 |
| P6 | -183 | +10 | -859 | -562 |
| P7 | +93 | +226 | -745 | -563 |

The exact cycle magnitude remains placement/runtime sensitive, but three facts
are stable:

1. From P2 onward GT retires fewer instructions.
2. GT performs roughly 0.75--0.78K more retired loads at P7 while performing
   roughly 76--81 fewer stores.
3. The final P7 delivery boundary adds about 217--276 core cycles relative to
   the preceding prefix in both layouts.  This is the first stable
   caller-context debt large enough to explain why isolated arithmetic wins do
   not close at the whole Encap boundary.

P3 (`rhat` pack + `hash_g` + SOTP handoff) is the earlier transition where TSC
often changes sign, but its core-cycle effect is not placement-stable enough to
name a single arithmetic culprit.

## Operation-to-GT-family reachability

| Family | Keypair | Encap | Decap | Raw object text+rodata bytes |
| --- | :---: | :---: | :---: | ---: |
| TILE4 frontend/core | yes | yes | yes | 15136 |
| P physical Forward | yes | no | no | 12288 |
| M/private-SoA Forward | no | yes | yes | 16736 |
| native F0xJ1 BaseMul | yes | no | no | 736 |
| private B3 variants | no | yes | yes | 3724 |
| global inverse | no | no | yes | 5108 |
| inverse T9 family | no | no | yes | 16714 |
| Q24 codec family | yes | yes | yes | 56037 |

Raw object sizes are family upper bounds before linked section GC, not additive
ELF contributions.  They identify the main footprint owners: Q24, the two
Forward families, inverse-tail tables and the common TILE4 core.

## Decision

- Do not reopen N5/B3/I1 local arithmetic from this result.
- Encap's missing local-to-whole closure is real; it is not explained by the
  isolated E2/E3 arithmetic.
- The next bounded experiment should target the P7 output/cleanup delivery
  shape while keeping the qualified Q24 packet mathematics unchanged.
- In parallel, build K-min/E-min/D-min linked images to measure the executable
  footprint delivery debt without interpreting a padding winner as an
  algorithmic win.
