# GT1152-P08 — the inverse NTT port

Completes G6b. The whole NTRU+1152 decapsulation arithmetic chain now runs:

```
forward -> basemul_rinv -> invntt_ternary  ==  crepmod3(schoolbook product)
```

**16 cases × 1152 coefficients, exact**, against a model sharing no code with
any of it. Built and run on the local arm64 host — not Cortex-A76, no
performance claim.

```sh
make generate     # re-emit the ported sources from NTRU+864
make check
```

## What each piece is, and why

| file | origin | how |
| --- | --- | --- |
| `inverse9.S` | 864 `packed_i9` | immediate remap, 8 offsets |
| `inverse16.S` | 864 `invntt16_asm` | immediate remap, 127 offsets |
| `crepmod3_raw.S` | 864 | loop count 27 → 36 |
| `inverse_ntt.S` | 864 `invntt_ternary_asm` | 13 declared rules |
| `inverse16_tail.c` | **new** | C, from a measured map |
| `inverse.c` | G5 | `baseinv` and `basemul_rinv` |

Each remap preserves the instruction multiset exactly, so NTRU+864's A76
schedule stays legal. That is asserted by the generator, not assumed.

### The driver stays assembly

`packed_i9` and `invntt16_asm` clobber v8–v15 (48 and 170 references). A C
driver would violate AAPCS64, which is precisely why `SAVE_PUBLIC` preserves
d8–d15 once per public call. `invntt16_tail_asm` being a C function is fine —
the driver reaches it through the ordinary argument registers.

### Slothy annotations were stripped, not carried over

The generated kernels keep their live-in/live-out contracts but drop Slothy's
cycle maps and its commented copy of the pre-schedule order. Those describe the
schedule Slothy produced **for NTRU+864**; no solver was run for 1152, so
carrying them — edited or not — would document a schedule that does not exist.

A first version of the generator silently rewrote offsets inside those comments
too (256 `strh` lines: 128 real, 128 commented). Stripping removes the problem
rather than papering over it.

### The tail, in C

G6a established that `invntt16_tail_asm` cannot be remapped: it is called once
and covers every component, so its output count grows from 96 to 128.

Rather than reimplement 1205 lines of solver output, the kernel was **measured**.
It emits raw values (`crepmod3_raw` does the ternary step), so it is linear, and
128 delta probes recover it exactly. Superposition was then checked to hold
**mod q** on random inputs — it is not bit-exact, because lazy reduction picks
different representatives, but congruence is what the contract asks for.

The measured map is one *2 banks × 16 t → 32 outputs* block, identical across
branches; 864 runs it three times, 1152 four. It carries over unchanged because
the 16-point inverse and the α/β CRT are leaf-degree independent and `n/d = 288`
for both.

Reduction is the branch-free Barrett G4 re-proved for degree 4, giving
`|out| ≤ 3024`, inside the consumer's contract.

**Cost:** 4096 multiply-accumulates against 589 assembly instructions. Correct
and directly derived from the validated kernel, which is what Milestone 1 needs,
but materially slower. Assembly stays the target.

## Not established

- No Pi 5 measurement, no performance claim.
- The coefficient-range comments inherited in the remapped kernels are 864's.
  For 1152 they hold under D7's normalization but have not been re-derived.
- The tail's C form is a dense map, not the structured 16-point inverse. An
  assembly version needs the structure, not this table.
