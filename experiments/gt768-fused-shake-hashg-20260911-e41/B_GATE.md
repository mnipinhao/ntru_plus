# B: generic prefix absorber

Baseline: a64e7035cb13410554af1c67870d4132a30037b4.

Observation: hash_g creates a 1153-byte image, then calls generic SHAKE256
with ten standalone scalar permutations and clears that image.

Hypothesis: absorbing a virtual one-byte prefix using word loads, while
retaining the generic input/output loops and current permutation ABI, saves
cycles and stack traffic.

Exact change: add a generic ntruplus_shake256_prefix(out, outlen, prefix,
input, inlen), route only hash_g through it. First block combines the prefix
with seven bytes, then loads the other sixteen lanes; subsequent blocks use
the existing 17-word XOR loop. Arbitrary input and output lengths remain
supported. Absorb completes before any output store, preserving overlap.

Static effects: remove data[1153], its 1152-byte memcpy and 1153-byte clear.
Keep the 200-byte tail scratch, 136-byte squeeze scratch, 200-byte state and
all three clears (536 bytes total). Keep ten permutation calls for hash_g.
The first block now uses assignments into zero state; generic prefix handling
also adds branches. A/B timing therefore measures the complete prefix
absorber replacement, not an isolated memcpy latency.

Register pressure: C compiler owns allocation; inspect frame sizes and calls.
No change to the scalar permutation instruction body.

Correctness: compare with unchanged one-shot SHAKE across rate-boundary
lengths, arbitrary prefix bytes, alignments, output lengths and overlapping
hash_g buffers; instrument permutation calls and cleanup; compare KAT files
and run affected KEM callers before timing.

Falsifier: any byte, alias, cleanup or permutation-count mismatch, or paired
Pi5 cycles failing to improve beyond dispersion.

Controls for later gates: C may specialize input/output lengths. D may keep
state in registers. Neither change belongs to this B comparison.

Correction to gate 0: unaligned AArch64 ldr directly implements the displaced
word loads. It does not require a shift/extract for every subsequent word.
Only the initial prefix lane needs byte assembly.
