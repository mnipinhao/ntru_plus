# ENCAP-MA2-CT-EGRESS-H4-M3B-ASM

## Outcome

One namespaced AVX2 implementation now lowers the H3 caller-wide scale-1
terminal through canonical Natural-Q scratch and directly emits the exact
1728-byte pinned-Official ciphertext representation:

```text
ntruplus1152_exp001_encap_h4_m3b_exact_egress
```

The implementation is generated in
`asm/encap_h4_m3b_exact_egress.S`.  Its entry and retained constant tables are
32-byte aligned.  It has no call, branch, stack frame, vector spill, or
`vzeroupper`.

## Ownership correction found by the ASM hard gate

The first live packed24 implementation followed the M2D/M2E assumption that
Official physical coefficient `k` is ciphertext wire coefficient `k`.  Its
packed scratch matched that assumption exactly, but the full ciphertext gate
failed against pinned Official `poly_tobytes`.

The failure was not hidden with modular comparison.  A 1152-basis probe was
run against the already qualified Natural-Q H1 machine object.  It establishes
an exact bijection from every Natural-Q MA2 source cell to its serialized wire
coefficient.  The results reject both speculative ownership revisions:

```text
M2C direct-map model mismatches: 1008 / 1152
M2D physical-index model mismatches: 1141 / 1152
```

The actual topology remains useful: all 576 wire pairs join the same lane in
adjacent terminal vectors.  However, each 64-coefficient tile has its own
machine-probed lane permutation.  M3B therefore forms plane-adjacent pair32
values, sorts the four eight-pair streams with exact per-tile indices,
interleaves parity companions, and packs four ordered 24-byte groups into
three 32-byte ciphertext stores.

## Linked ledger

Relative to the unchanged H3 object, M3B adds 1,488 linked instructions:

```text
terminal Barrett/sign canonicalization: 432
exact canonical scratch-to-wire egress: 1056
```

The egress ledger is:

```text
canonical scratch loads: 72
pair unpack routes:       72
pair vpmaddwd:            72
vpermd index loads:       30
vpermd routes:            72
parity routes:           144
pack routes:             486
pack-state saves:         54
ciphertext stores:        54
total:                  1056
```

The complete symbol is 5,075 instructions and 31,348 text bytes.  Its retained
rodata is 5,728 bytes.  Whole-function peak YMM usage remains the inherited
16/16; the new egress itself peaks at 14.

## Correctness and ABI closure

The following gates pass:

- 1,003 random-small plus fixed zero/alternating valid cases;
- caller-wide scale-1 semantic differential;
- canonical scratch differential against standalone H3;
- exact pinned-Official ciphertext bytes;
- Official invalid-PK accept/reject differential;
- `pk == ct`, `ct = pk + 16`, and `ct = pk - 16` overlap cases;
- input immutability and scratch/ciphertext canaries;
- ASan and UBSan;
- exact linked opcode delta and 32-byte entry/text/rodata alignment.

Run the reproducible closure with:

```sh
make h4-m3b-check
make h4-m3b-sanitize
```

## Decision

The M3B ASM correctness and machine-structure checkpoint is complete.  M2D
and M2E remain historical rejected hypotheses and must not be used as wire
ownership sources.  No benchmark or native KEM integration is authorized by
this checkpoint; the next decision is whether to price this qualified exact
egress against the H4-M3 Natural-Q H1 fallback.
