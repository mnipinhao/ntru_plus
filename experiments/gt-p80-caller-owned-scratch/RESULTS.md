# P80 — caller-owned scratch, and a missing clear it exposed

mlkem-native's property is not "no scratch" but **the assembly allocates nothing
the C caller cannot name**: its `intt` works in place on a caller-owned poly and
borrows 64 bytes for the `d8-d15` spill.  Six leaves across the three trees
break that, each allocating a working buffer the C caller cannot reach:

| tree | leaf | bytes | cleared before this? |
|---|---|---:|---|
| 1152 | `inverse_ntt.S` | 2,304 | yes, in assembly |
| 864 | `ntt.S` | 1,792 | **no** |
| 864 | `inverse.S` (baseinv) | 1,200 | yes |
| 864 | `inverse.S` (invntt) | 1,792 | yes |
| 768 | `asm/ntt.S` | 1,696 | yes |
| 768 | `asm/internal/decap_forward.S` | 1,696 | yes |

This gate converts two of them and finds why the property is worth having.

## NTRU+864's forward NTT was never cleared

`ntt.S` allocated 1,792 bytes, used them and returned.  NTRU+768's `asm/ntt.S`
has cleared its 1,696-byte equivalent since the P0 work and its release gate
pins that (`mov x10, #106`, `.Lp0b_clear_1696:`); 864's gate did not mention
`ntt.S` at all.  The buffer holds the forward transform of `f`, `g` and the
recovered message.

This is pre-existing, not introduced by this campaign, and it is the second
clearing gap found by writing a gate rather than by reading code — P76 was the
first.

## The refactor closes it at a third of the cost

Three ways to have the forward NTT not leave 1,792 bytes behind, A76 KEM total,
median of three runs:

| | total | vs the gap |
|---|---:|---:|
| as shipped, not cleared | 108,220 | — |
| add an assembly clear, mirroring 768 | 109,527 | **+1,307** |
| **caller-owned scratch, cleared in C** | **108,678** | **+458** |

**2.85x cheaper**, because `secure_clear` reaches libc's `memset` where the
handwritten `str q` loop does not — P73 measured the same ratio directly (77
against 144 cycles for 2,304 bytes).  M2 is flat: 16,860/16,910 against
16,950/16,970.

It also makes the clear **auditable**.  `ntt_api.c` joins the audit build, and
`test_zeroization` now reports `clear_calls` 21 -> 27 and `clear_bytes`
24,028 -> 34,780, the six `poly_ntt` calls x 1,792 bytes that were invisible
before.  The gate pins the C declaration and the clear rather than an assembly
loop.

## NTRU+1152

`inverse_ntt.S` converted the same way, except the wipe stays in assembly: the
leaf is the last thing to touch the buffer, and P72 measured moving that clear
to C at +2.5ns on M2 against -0.5 for the ownership change alone.  Free on both
hosts — **M2 +0.0ns, A76 +1 cycle** — and every gate passes with the KAT
byte-identical.

## Cost of the ABI change

Each converted leaf takes one more argument.  For 864's `ntt_asm` that meant
saving `x21` and widening its frame from 96 to 112 bytes, and updating the ABI
sentinel, which calls the leaf directly and segfaulted until it was given a
scratch to pass.  That sentinel failure is the ABI contract working as
intended.

## Not converted

768's two leaves and 864's two `inverse.S` sites remain.  Both trees' clears
there are already present and pinned, so converting them buys the structural
property and audit coverage but not a fix — unlike 864's `ntt.S`, which was a
real gap.  Worth doing, but as its own step.
