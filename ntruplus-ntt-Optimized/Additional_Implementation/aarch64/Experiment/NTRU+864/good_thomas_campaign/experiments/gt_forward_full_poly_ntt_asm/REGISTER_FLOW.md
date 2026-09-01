# M5O wrapper register and memory flow

## Entry

- `x0 = fr0_out`: disjoint 864-halfword destination.
- `x1 = natural_in`: 864 natural-order input coefficients.
- `sp`: 16-byte aligned AAPCS64 stack pointer.

The wrapper first saves `x29/x30` and callee-saved `x19/x20` in a 32-byte
frame.  It freezes `fr0_out` in `x19` and `natural_in` in `x20`, then subtracts
1,792 bytes.  Therefore the new `sp` is still 16-byte aligned and names exactly
the 896-halfword P8-plus-tail scratch object.

## Producer call

```text
x0 = sp       -> P8 scratch[896]
x1 = x20      -> natural input[864]
bl gt864_top_split_ld3
```

The producer reads each natural coefficient once.  It writes six 128-halfword
main banks and sixteen tail vectors.  Tail lanes 0..5 contain the six
`(top,component)` values and lanes 6..7 are zero, giving 864 meaningful plus
32 padding halfwords.  No pointer to the caller's output is exposed here.

## Consumer call

```text
x0 = x19      -> FR-0 output[864]
x1 = sp       -> frozen P8 scratch[896]
bl gt864_forward_six_bank_pass2
```

M5N reads the 864 meaningful P8 positions exactly once, deliberately ignores
all 32 padding positions, and stores every FR-0 position exactly once.  Its
shared one-bank helper keeps its link register in `x16`; the wrapper's own
return address remains protected in the saved `x30` stack slot.

## Exit

The wrapper adds exactly 1,792 to `sp`, restores `x19/x20`, then restores
`x29/x30` while releasing the 32-byte frame.  Thus stack balance, alignment,
and all AAPCS64 callee-saved registers are unchanged at return.

The mathematical state changes as follows:

```text
natural coefficients (R0)
  -> top-split P8-plus-tail (R0, branch-specific split/twist included)
  -> complete NTT16 + oriented NTT9 FR-0 leaves (R0)
```

There is no runtime FR-0-to-Official permutation.  That public permutation is
only an oracle adapter in the differential test because BaseMul is allowed to
consume FR-0 directly.
