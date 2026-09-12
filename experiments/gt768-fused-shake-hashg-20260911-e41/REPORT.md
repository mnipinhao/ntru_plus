# GT768 fused `hash_g` gate

Experiment ID: `gt768-fused-shake-hashg-20260911-e41`

This experiment is based on `aarch64-production` revision
`a64e7035cb13410554af1c67870d4132a30037b4`.  Production source is unchanged.

## Gate 0: exact data flow

The complete byte/lane contract is in `HASH_G_MAPPING.md`.  Its executable
oracle passed 259 messages: all-zero, all-one, byte-ramp, and 256 deterministic
random messages.  For each message it compared every lane of all eight full
blocks and the padded tail against the contiguous `0x01 || msg` construction.

Verified permutation count:

```text
8 full-block permutations
+ 1 padded-tail / first-output permutation
+ 1 continuation-squeeze permutation
= 10
```

The mapping exposes a one-byte seam.  Apart from the first lane, a word-wise
direct absorber reads message words beginning at offsets congruent to seven
modulo eight.  This is legal on AArch64, but input-load/extract cost must be
included in the candidate rather than assuming aligned 64-bit blocks.

## Gate 1: live-state feasibility

Static inspection of `keccakf1600.S` establishes the canonical boundary map
shown in `HASH_G_MAPPING.md`: 25 state lanes occupy 25 GPRs after the final
normalization.  Five architectural GPRs remain outside that map.  The caller
link register is already saved by the existing 128-byte frame.

The current scalar permutation performs, per call:

- 12 `ldp` plus one `ldr` to load the 25 state lanes;
- 12 `stp` plus one `str` to store them;
- six callee-save `stp` and six restore `ldp`, plus stack and return control;
- one bounded temporary state spill/reload inside the round schedule.

Ten calls therefore execute 260 state load/store instructions.  A fused path
does not need a memory-backed state and can store the 17+7 output lanes
directly.  It still needs one function prologue/epilogue and small stack slots
for the message pointer, output pointer, round-constant pointer, inner-round
counter, outer-permutation counter, and the existing bounded round temporary.

The existing body has a usable live-state re-entry point in principle: after
the 23 final normalization rotates, the next input block can be XORed into the
canonical register map and execution can re-enter the first-round arithmetic
after the standalone state loads.  The round-constant pointer is already
recoverable from the stack and the first-round code reinitializes the inner
round counter.

This proves architectural feasibility, not performance.  The next static gate
must account for:

- direct construction of the one-byte-shifted input lanes;
- the boundary branch and outer-loop control;
- whether the 23 normalization rotates remain at every boundary or can be
  absorbed into the next block representation;
- output stores and cleanup-policy equivalence;
- exact stack-frame growth and absence of additional state spills.

## Initial mapping-gate decision (superseded below)

Gate 0 passes.  Gate 1 does not find a register-capacity blocker, so the fused
candidate remains open.  No performance claim is made yet.  The next controlled
change is B: remove `data[1153]` while retaining the current ten standalone
permutation calls.  C then fixes the complete 1152-byte-input/192-byte-output
loop shape.  Only their measured residual justifies implementing D.

## B gate completed, 2026-09-12

B replaces only hash_g's materialized domain-prefixed input with a generic
one-byte-prefix absorber. The public hash_g ABI and overlap behavior remain
unchanged. The rest of SHAKE256, hash_f, hash_h and the polynomial sources
remain on their existing paths. The new helper still supports arbitrary
input/output lengths and still calls the scalar permutation ten times.

Both Mac and Pi packages passed make check, including byte-identical KAT
request/response files, KEM, ABI, canonical/failure, small-input and cleanup
checks. The KAT response SHA-256 remains
22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8.
The dedicated test passed 2080 differential and overlapping-buffer cases on
Mac and Pi; Mac ASan/UBSan passed the same cases. Instrumentation confirms
ten calls and three clears of 200+136+200=536 bytes for hash_g. There is no
1153-byte input image to clear. The whole-KEM audit removes exactly two such
clears (Encap and Decap): 30692 to 28386 bytes.

Pi5 GCC 14.2.0, core 3, base Armv8-A ISA with Cortex-A76 tuning. There are 62
pairs, each alternating AB/BA, 2000 operations/sample and 100 warmups.
Both sides use the same scalar x1 Keccak. This is an A/B comparison against
the current GT champion, not a new comparison against Official SUPERCOP.

| Operation | A median cycles | B median cycles | Change from medians | Median paired saving |
|---|---:|---:|---:|---:|
| hash_g | 10693.5 | 10521 | -1.61% | 174 |
| Encap | 31940.5 | 31760 | -0.57% | 174 |
| Decap | 29049 | 28911.5 | -0.47% | 135 |

Each operation won all 62 pairs. Paired-saving p10/p90 intervals were
159/184, 141/202 and 116/155 cycles respectively. The difference between
two medians and the median of paired differences is expected; both are
reported explicitly. Keygen was correctness-tested but not timed in this
gate, because its hash_g path is not involved.

The host was idle before testing. Throttling was 0x0 before, immediately
before timing, and after. The timing boundary temperatures were 63.1 and
64.2 degrees C; these are boundary observations, not a continuous maximum.

### Cost accounting

Four long AB/BA PMU runs, 200000 hash_g calls/run with no warmup, showed:

| Per hash_g (median) | A | B | Reduction |
|---|---:|---:|---:|
| instructions retired | 30690.1 | 30321.1 | 369.0 |
| ld_spec | 1404.3 | 1349.8 | 54.5 |
| st_spec | 880.5 | 799.7 | 80.8 |
| stall_backend | 1045.6 | 1003.7 | 41.9 |

The load/store events are speculative counts, not retired memory-operation
counts. External perf includes startup overhead amortized over 200000 calls;
all events report 100% scheduled time.

The scalar permutation's 288 linked instruction words match exactly between
A and B (1152 bytes). Consequently this B result comes from the surrounding
absorber, copy, cleanup and compiler choices, not a faster round function.

Static GCC frame accounting at a permutation call:

- A: hash_g 1200 + shake256 416 + keccak_absorb 368 + permutation 128 = 2112 bytes.
- B: tail-call hash_g 0 + prefix helper 560 + permutation 128 = 688 bytes.

This is 1424 fewer bytes along that path, excluding higher callers and libc
frames; it is not a measured whole-program stack high-water mark.

The tradeoff is code size. The full Encap binary's .text section grows from
73328 to 77296 bytes (+3968); GNU size's text category, which also includes
read-only metadata, grows from 83143 to 87207 (+4064). The new generic prefix
helper is 4016 bytes. Original shake256 is still needed by coins/hash_f/hash_h,
so both sponge paths stay linked. The standalone hash_g binary only grows
632 bytes because its dead-stripped old sponge does not remain linked.

Disassembly also shows GCC expanding the byte-oriented load64 loops into
NEON byte permutations. Direct unaligned ldr is architecturally sufficient;
the generated C code does not always choose it. That is a concrete follow-up
inspection point for C, not a reason to attribute these shuffles to SHAKE.

### Decision and next gate

Accept B as a measured experimental control. Keep it on this opt-in branch;
production and the tracked SUPERCOP leaf have not been modified. It has a
consistent speed/stack benefit, but its roughly 4 KiB code-size cost should
be addressed before considering promotion.

Next is C: specialize the 1152-byte-message/192-byte-output path, retaining
the same ten standalone permutations and cleanup semantics. Compare against
both A and B, and account for code size and emitted input-load sequences.
The register-resident D experiment remains a separate later gate.

### Reproduction

Stage the baseline package from git archive of
a64e7035cb13410554af1c67870d4132a30037b4, the candidate package from this branch,
this experiment directory, and the existing bench_hash.c / bench_kem.c /
perf_counter.c / perf_counter.h / deterministic_randombytes.c harness files.
Use baseline/, candidate/, experiment/ and harness/ beneath:

    /home/pi/gt768-fused-shake-hashg-20260911-e41

Run:

    python3 experiment/run_b_gate.py /home/pi/gt768-fused-shake-hashg-20260911-e41 --name b-gate-v1

The runner rejects an existing result directory; use a fresh run name for a
rerun. Flags, source hashes, binary hashes and persistent summaries are in
B-summary.json. Raw logs, commands, binaries, KAT output, samples and
disassembly are in .build/b-gate-v1 remotely and .build/pi-b-gate-v1 locally.
No raw samples or duplicate source snapshots are committed.
