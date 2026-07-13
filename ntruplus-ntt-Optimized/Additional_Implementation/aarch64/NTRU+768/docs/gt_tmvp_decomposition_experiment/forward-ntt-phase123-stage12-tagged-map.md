# Forward NTT Phase123 -> Stage12 Tagged Map

Date: 2026-07-08

Scope: production GT forward NTT Phase123 handoff into the NTT32 stage12 row
kernel.  This is a mapping document only; it does not change assembly.

Source files:

```text
asm/slothy/inputs/ntt768_gt_frontend.sym.S
asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S
```

## 1. Local terms

One GT row has 256 int16 coefficients.  One Neon Q vector contains eight int16
lanes, so one row is represented as:

```text
Q0, Q1, ..., Q31
```

The Phase123 symbolic source stores three row outputs at each local output site:

```text
q9  -> [x4, #offset] -> row0
q10 -> [x5, #offset] -> row1
q11 -> [x6, #offset] -> row2
```

Within Phase123 iteration `i`, the four store offsets are:

```text
#0, #16, #32, #48
```

They correspond to local slots:

```text
slot = offset / 16
Q index = 4 * i + slot
```

The row-local lane group for `Qk` is:

```text
h[8*k .. 8*k+7]
```

NTT32 stage12 consumes stripe `s` as:

```text
Q[s], Q[s+8], Q[s+16], Q[s+24]
```

Therefore:

```text
stage12 stripe = Q index mod 8
stage12 depth  = floor(Q index / 8)
```

The stage12 output is written back to the same Q slots.  Stage345 then consumes
contiguous post-stage12 blocks:

```text
stage345 block0 consumes post-stage12 Q0..Q7
stage345 block1 consumes post-stage12 Q8..Q15
stage345 block2 consumes post-stage12 Q16..Q23
stage345 block3 consumes post-stage12 Q24..Q31
```

Important: a raw input `Qk` is only one input of its stripe.  The four raw inputs
of that stripe jointly produce four post-stage12 outputs.  For example,
`Q0/Q8/Q16/Q24` jointly produce post-stage12 output slots `Q0`, `Q8`, `Q16`,
and `Q24`.

## 2. Where a rewrite should start

There are three possible cut points.

### A. From the top split

This is the most invasive route.  It may allow a cleaner global DAG, but it also
pulls in input loads, early splitting, twist/precompute values, and all three
row outputs at once.  The current Phase123 body already uses a very full vector
register set, so starting at the top risks making register allocation worse
before it solves the stage12 grouping problem.

This route is not the first prototype unless we decide to regenerate a complete
Phase123+stage12 symbolic DAG.

### B. After each local Phase123 output is formed

This is the best first structural cut.  Keep the existing Phase123 arithmetic
until `q9/q10/q11` are ready, but replace some of the stores with a tagged
producer/consumer handoff:

```text
q9/q10/q11 ready
  -> tag as row, Q index, stage12 stripe, stage12 depth
  -> either store to temporary holding scratch
  -> or feed a small stage12 direct prototype once the stripe is complete
```

This avoids rewriting the DFT3 arithmetic first.  It also makes it possible to
measure the cost of the stage12 handoff separately from the cost of the
Phase123 arithmetic.

### C. At the store edge only

This is the easiest route but probably too weak.  It can store raw Q values in a
stripe-major layout, but if stage12 still loads raw Q from memory later, the main
memory roundtrip remains.  This is a layout experiment, not the real direct
stage12 fuse.

## 3. Stage12 stripe groups

The key mismatch is that Phase123 emits consecutive Q vectors, while stage12
consumes stride-8 Q vectors.

| Stage12 stripe | Raw inputs | Producer iterations | Post-stage12 output slots | Stage345 consumers |
| --- | --- | --- | --- | --- |
| 0 | Q0, Q8, Q16, Q24 | iter0, iter2, iter4, iter6 | Q0, Q8, Q16, Q24 | block0, block1, block2, block3 |
| 1 | Q1, Q9, Q17, Q25 | iter0, iter2, iter4, iter6 | Q1, Q9, Q17, Q25 | block0, block1, block2, block3 |
| 2 | Q2, Q10, Q18, Q26 | iter0, iter2, iter4, iter6 | Q2, Q10, Q18, Q26 | block0, block1, block2, block3 |
| 3 | Q3, Q11, Q19, Q27 | iter0, iter2, iter4, iter6 | Q3, Q11, Q19, Q27 | block0, block1, block2, block3 |
| 4 | Q4, Q12, Q20, Q28 | iter1, iter3, iter5, iter7 | Q4, Q12, Q20, Q28 | block0, block1, block2, block3 |
| 5 | Q5, Q13, Q21, Q29 | iter1, iter3, iter5, iter7 | Q5, Q13, Q21, Q29 | block0, block1, block2, block3 |
| 6 | Q6, Q14, Q22, Q30 | iter1, iter3, iter5, iter7 | Q6, Q14, Q22, Q30 | block0, block1, block2, block3 |
| 7 | Q7, Q15, Q23, Q31 | iter1, iter3, iter5, iter7 | Q7, Q15, Q23, Q31 | block0, block1, block2, block3 |

## 4. Register pressure implications

The naive "keep Phase123 output live until stage12" plan is too large.

| Candidate live group | Raw Q vectors before stage12 | Practical status |
| --- | ---: | --- |
| one stripe, one row | 4 | plausible as a tiny prototype |
| one stripe, all three rows | 12 | maybe possible only with careful scheduling |
| stripes0-3, one row | 16 | high pressure once stage12 temps/twiddles are included |
| stripes0-3, all three rows | 48 | impossible in Neon registers |
| full row | 32 | impossible if Phase123 state is also live |
| full three-row Phase123 output | 96 | impossible |

This is why the first prototype should not try to carry an entire row.  It
should start with a small tagged stripe or a temporary holding scratch.

## 5. Full Phase123 store-site map

Columns:

```text
line        source line in asm/slothy/inputs/ntt768_gt_frontend.sym.S
iter        Phase123 iteration
reg         q9/q10/q11 producer register
row         GT row index
Q           row-local vector slot
stripe      NTT32 stage12 stripe
depth       input depth inside the stripe: Q[stripe + 8*depth]
lane group  row-local int16 lanes carried by this Q vector
slot block  post-stage12 slot block if stage12 stores back to the same address
offset      Phase123 row scratch offset within the current iteration base
```

| line | iter | reg | row | Q | stripe | depth | lane group | slot block | offset |
| ---: | ---: | --- | ---: | --- | ---: | ---: | --- | --- | ---: |
| 131 | 0 | q9 | 0 | Q0 | 0 | 0 | h0..h7 | block0 | 0 |
| 132 | 0 | q10 | 1 | Q0 | 0 | 0 | h0..h7 | block0 | 0 |
| 133 | 0 | q11 | 2 | Q0 | 0 | 0 | h0..h7 | block0 | 0 |
| 144 | 0 | q9 | 0 | Q1 | 1 | 0 | h8..h15 | block0 | 16 |
| 145 | 0 | q10 | 1 | Q1 | 1 | 0 | h8..h15 | block0 | 16 |
| 146 | 0 | q11 | 2 | Q1 | 1 | 0 | h8..h15 | block0 | 16 |
| 157 | 0 | q9 | 0 | Q2 | 2 | 0 | h16..h23 | block0 | 32 |
| 158 | 0 | q10 | 1 | Q2 | 2 | 0 | h16..h23 | block0 | 32 |
| 159 | 0 | q11 | 2 | Q2 | 2 | 0 | h16..h23 | block0 | 32 |
| 170 | 0 | q9 | 0 | Q3 | 3 | 0 | h24..h31 | block0 | 48 |
| 171 | 0 | q10 | 1 | Q3 | 3 | 0 | h24..h31 | block0 | 48 |
| 172 | 0 | q11 | 2 | Q3 | 3 | 0 | h24..h31 | block0 | 48 |
| 305 | 1 | q9 | 0 | Q4 | 4 | 0 | h32..h39 | block0 | 0 |
| 306 | 1 | q10 | 1 | Q4 | 4 | 0 | h32..h39 | block0 | 0 |
| 307 | 1 | q11 | 2 | Q4 | 4 | 0 | h32..h39 | block0 | 0 |
| 318 | 1 | q9 | 0 | Q5 | 5 | 0 | h40..h47 | block0 | 16 |
| 319 | 1 | q10 | 1 | Q5 | 5 | 0 | h40..h47 | block0 | 16 |
| 320 | 1 | q11 | 2 | Q5 | 5 | 0 | h40..h47 | block0 | 16 |
| 331 | 1 | q9 | 0 | Q6 | 6 | 0 | h48..h55 | block0 | 32 |
| 332 | 1 | q10 | 1 | Q6 | 6 | 0 | h48..h55 | block0 | 32 |
| 333 | 1 | q11 | 2 | Q6 | 6 | 0 | h48..h55 | block0 | 32 |
| 344 | 1 | q9 | 0 | Q7 | 7 | 0 | h56..h63 | block0 | 48 |
| 345 | 1 | q10 | 1 | Q7 | 7 | 0 | h56..h63 | block0 | 48 |
| 346 | 1 | q11 | 2 | Q7 | 7 | 0 | h56..h63 | block0 | 48 |
| 479 | 2 | q9 | 0 | Q8 | 0 | 1 | h64..h71 | block1 | 0 |
| 480 | 2 | q10 | 1 | Q8 | 0 | 1 | h64..h71 | block1 | 0 |
| 481 | 2 | q11 | 2 | Q8 | 0 | 1 | h64..h71 | block1 | 0 |
| 492 | 2 | q9 | 0 | Q9 | 1 | 1 | h72..h79 | block1 | 16 |
| 493 | 2 | q10 | 1 | Q9 | 1 | 1 | h72..h79 | block1 | 16 |
| 494 | 2 | q11 | 2 | Q9 | 1 | 1 | h72..h79 | block1 | 16 |
| 505 | 2 | q9 | 0 | Q10 | 2 | 1 | h80..h87 | block1 | 32 |
| 506 | 2 | q10 | 1 | Q10 | 2 | 1 | h80..h87 | block1 | 32 |
| 507 | 2 | q11 | 2 | Q10 | 2 | 1 | h80..h87 | block1 | 32 |
| 518 | 2 | q9 | 0 | Q11 | 3 | 1 | h88..h95 | block1 | 48 |
| 519 | 2 | q10 | 1 | Q11 | 3 | 1 | h88..h95 | block1 | 48 |
| 520 | 2 | q11 | 2 | Q11 | 3 | 1 | h88..h95 | block1 | 48 |
| 653 | 3 | q9 | 0 | Q12 | 4 | 1 | h96..h103 | block1 | 0 |
| 654 | 3 | q10 | 1 | Q12 | 4 | 1 | h96..h103 | block1 | 0 |
| 655 | 3 | q11 | 2 | Q12 | 4 | 1 | h96..h103 | block1 | 0 |
| 666 | 3 | q9 | 0 | Q13 | 5 | 1 | h104..h111 | block1 | 16 |
| 667 | 3 | q10 | 1 | Q13 | 5 | 1 | h104..h111 | block1 | 16 |
| 668 | 3 | q11 | 2 | Q13 | 5 | 1 | h104..h111 | block1 | 16 |
| 679 | 3 | q9 | 0 | Q14 | 6 | 1 | h112..h119 | block1 | 32 |
| 680 | 3 | q10 | 1 | Q14 | 6 | 1 | h112..h119 | block1 | 32 |
| 681 | 3 | q11 | 2 | Q14 | 6 | 1 | h112..h119 | block1 | 32 |
| 692 | 3 | q9 | 0 | Q15 | 7 | 1 | h120..h127 | block1 | 48 |
| 693 | 3 | q10 | 1 | Q15 | 7 | 1 | h120..h127 | block1 | 48 |
| 694 | 3 | q11 | 2 | Q15 | 7 | 1 | h120..h127 | block1 | 48 |
| 827 | 4 | q9 | 0 | Q16 | 0 | 2 | h128..h135 | block2 | 0 |
| 828 | 4 | q10 | 1 | Q16 | 0 | 2 | h128..h135 | block2 | 0 |
| 829 | 4 | q11 | 2 | Q16 | 0 | 2 | h128..h135 | block2 | 0 |
| 840 | 4 | q9 | 0 | Q17 | 1 | 2 | h136..h143 | block2 | 16 |
| 841 | 4 | q10 | 1 | Q17 | 1 | 2 | h136..h143 | block2 | 16 |
| 842 | 4 | q11 | 2 | Q17 | 1 | 2 | h136..h143 | block2 | 16 |
| 853 | 4 | q9 | 0 | Q18 | 2 | 2 | h144..h151 | block2 | 32 |
| 854 | 4 | q10 | 1 | Q18 | 2 | 2 | h144..h151 | block2 | 32 |
| 855 | 4 | q11 | 2 | Q18 | 2 | 2 | h144..h151 | block2 | 32 |
| 866 | 4 | q9 | 0 | Q19 | 3 | 2 | h152..h159 | block2 | 48 |
| 867 | 4 | q10 | 1 | Q19 | 3 | 2 | h152..h159 | block2 | 48 |
| 868 | 4 | q11 | 2 | Q19 | 3 | 2 | h152..h159 | block2 | 48 |
| 1001 | 5 | q9 | 0 | Q20 | 4 | 2 | h160..h167 | block2 | 0 |
| 1002 | 5 | q10 | 1 | Q20 | 4 | 2 | h160..h167 | block2 | 0 |
| 1003 | 5 | q11 | 2 | Q20 | 4 | 2 | h160..h167 | block2 | 0 |
| 1014 | 5 | q9 | 0 | Q21 | 5 | 2 | h168..h175 | block2 | 16 |
| 1015 | 5 | q10 | 1 | Q21 | 5 | 2 | h168..h175 | block2 | 16 |
| 1016 | 5 | q11 | 2 | Q21 | 5 | 2 | h168..h175 | block2 | 16 |
| 1027 | 5 | q9 | 0 | Q22 | 6 | 2 | h176..h183 | block2 | 32 |
| 1028 | 5 | q10 | 1 | Q22 | 6 | 2 | h176..h183 | block2 | 32 |
| 1029 | 5 | q11 | 2 | Q22 | 6 | 2 | h176..h183 | block2 | 32 |
| 1040 | 5 | q9 | 0 | Q23 | 7 | 2 | h184..h191 | block2 | 48 |
| 1041 | 5 | q10 | 1 | Q23 | 7 | 2 | h184..h191 | block2 | 48 |
| 1042 | 5 | q11 | 2 | Q23 | 7 | 2 | h184..h191 | block2 | 48 |
| 1175 | 6 | q9 | 0 | Q24 | 0 | 3 | h192..h199 | block3 | 0 |
| 1176 | 6 | q10 | 1 | Q24 | 0 | 3 | h192..h199 | block3 | 0 |
| 1177 | 6 | q11 | 2 | Q24 | 0 | 3 | h192..h199 | block3 | 0 |
| 1188 | 6 | q9 | 0 | Q25 | 1 | 3 | h200..h207 | block3 | 16 |
| 1189 | 6 | q10 | 1 | Q25 | 1 | 3 | h200..h207 | block3 | 16 |
| 1190 | 6 | q11 | 2 | Q25 | 1 | 3 | h200..h207 | block3 | 16 |
| 1201 | 6 | q9 | 0 | Q26 | 2 | 3 | h208..h215 | block3 | 32 |
| 1202 | 6 | q10 | 1 | Q26 | 2 | 3 | h208..h215 | block3 | 32 |
| 1203 | 6 | q11 | 2 | Q26 | 2 | 3 | h208..h215 | block3 | 32 |
| 1214 | 6 | q9 | 0 | Q27 | 3 | 3 | h216..h223 | block3 | 48 |
| 1215 | 6 | q10 | 1 | Q27 | 3 | 3 | h216..h223 | block3 | 48 |
| 1216 | 6 | q11 | 2 | Q27 | 3 | 3 | h216..h223 | block3 | 48 |
| 1349 | 7 | q9 | 0 | Q28 | 4 | 3 | h224..h231 | block3 | 0 |
| 1350 | 7 | q10 | 1 | Q28 | 4 | 3 | h224..h231 | block3 | 0 |
| 1351 | 7 | q11 | 2 | Q28 | 4 | 3 | h224..h231 | block3 | 0 |
| 1362 | 7 | q9 | 0 | Q29 | 5 | 3 | h232..h239 | block3 | 16 |
| 1363 | 7 | q10 | 1 | Q29 | 5 | 3 | h232..h239 | block3 | 16 |
| 1364 | 7 | q11 | 2 | Q29 | 5 | 3 | h232..h239 | block3 | 16 |
| 1375 | 7 | q9 | 0 | Q30 | 6 | 3 | h240..h247 | block3 | 32 |
| 1376 | 7 | q10 | 1 | Q30 | 6 | 3 | h240..h247 | block3 | 32 |
| 1377 | 7 | q11 | 2 | Q30 | 6 | 3 | h240..h247 | block3 | 32 |
| 1388 | 7 | q9 | 0 | Q31 | 7 | 3 | h248..h255 | block3 | 48 |
| 1389 | 7 | q10 | 1 | Q31 | 7 | 3 | h248..h255 | block3 | 48 |
| 1390 | 7 | q11 | 2 | Q31 | 7 | 3 | h248..h255 | block3 | 48 |

## 6. Practical prototype sequence

1. Build a tagged C oracle for the mapping above:

```text
Phase123 raw output tags
  -> stage12 stripe tags
  -> post-stage12 slot tags
  -> stage345 block tags
```

2. Prototype a minimal direct-stage12 region for one row and one stripe:

```text
Q0, Q8, Q16, Q24 -> stage12 stripe0 -> post-stage12 Q0/Q8/Q16/Q24
```

3. If the one-stripe prototype is correct, expand only to stripes0-3 or
stripes4-7 for one row.  Do not attempt all three rows at once until the live
set is measured.

4. Only after correctness and live-set pressure are understood, decide whether
to regenerate the full Phase123+stage12 symbolic DAG for Slothy.
