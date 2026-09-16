# ToBytes producer-selected Barrett deletion — correctness gate

Date: 2026-09-08. Experimental only; production unchanged. No new cycle result.

## Contract and caller selection

`tobytes_small/candidate.alloc.S` requires R0 coefficients strictly inside
(-3457,3457). It retains sign-based canonicalization, routing and byte packing.
The full entry accepts every signed-int16 value and retains Barrett reduction.
See `tobytes-producer-audit/README.md` for the producer proof and Forward witnesses.

| KEM caller | Entry | Reason |
| --- | --- | --- |
| Keygen h -> pk | small | D1 final output in [-3023,3023] |
| Keygen hinv -> sk | small | D1 final output in [-3023,3023] |
| Encaps c -> ct | small | D1 final output in [-3023,3023] |
| Decaps r2 -> hash bytes | small | D1 final output in [-3023,3023] |
| Keygen f -> sk | full | K1 Forward is not bounded by (-q,q) |
| Encaps r -> hash bytes | full | K1 Forward is not bounded by (-q,q) |
| Decaps r1 -> hash bytes | full | K1 Forward is not bounded by (-q,q) |

Selection is fixed by caller, not by inspecting secret coefficients.
`prepare_bytes_kem.py` generates the isolated KEM source; it checks exactly seven
serialization sites and replaces exactly four with the small entry.

## Static savings

One pair producer: 337 -> 299 instructions excluding RET. Each full ToBytes
calls six pair producers: deletion of 108 SQRDMULH + 108 MLS, and 12 dead
reciprocal-constant setup instructions, totals **228 instructions/call**.
This is relative to the matching new full-range implementation, not production.
Keygen uses two small calls; Encaps and Decaps use one each.

Slothy allocation used /Users/chenpinhao/slothy, with no coefficient spills.
Allocated sources assemble as AArch64 ELF and contain no residual symbolic
registers or hidden calls. No timing scheduling was performed for the small core.
The existing byte-scratch architecture remains: 648 bytes used, 656 allocated
and wiped, 2592 bytes of scratch traffic per complete serialization. These costs
mean instruction savings do not establish a speedup over production ToBytes.

## Native correctness

Mac ARM64 and Pi 5 both passed `integration/build_bytes.py` using real allocated
assembly, not C substitute cores:

- 66048 full cases: all 65536 uniform signed-int16 values plus 512 random cases.
- 7425 small cases: all 6913 uniform values in [-3456,3456] plus 512 mixed cases.
- 512 shared-domain comparisons, exact 1296-byte scalar-oracle output.
- AAPCS preservation, input immutability, output canaries, 656-byte scratch wipe.

Uniform exhaustive cases are not an exhaustive proof over all 864-element inputs.
Canaries check output overwrite, not inaccessible-page input overread.

Pi 5 `pi-bytes.py` passed three full-KEM comparisons:

1. Frozen opt -> new all-full ToBytes control.
2. Frozen opt -> caller-selected full/small ToBytes.
3. All-full control -> selected full/small.

Each reported 32 valid/tampered cases, zero cross-version pk/ct differences,
instrumentation equivalence, and 32 malformed-ciphertext equivalence cases.
The other arithmetic objects were reused from the frozen tested opt candidate.

Remote artifacts:
`/home/pi/ntruplus-experiments/gt864-native-timing-20260908.X8u5QV/experiments/gt864-native-asm/build`

| Binary | SHA256 |
| --- | --- |
| opt.so | 9104e4fd65e7f71bafa92565f5fc47d9825a641b01f77db14ddfb304b503d0f0 |
| bytes-allfull.so | 805dd9ad2c9d7d0f45d22a2c34857730a7631ee673f9cfa4e79e4953d9ff9dfa |
| bytes-selected.so | 92e555e7fb34f882e22a1e6f1a496c2053a3660608a3e2076c020fcf3b67ed8c |

The three `check-*-*.log` files are alongside those binaries.

## Next gate

Schedule the full/small pair cores with the same timing policy, then measure
complete ToBytes and paired full KEM against frozen opt and the all-full control.
Keep production unchanged until complete-boundary cycle results justify promotion.
