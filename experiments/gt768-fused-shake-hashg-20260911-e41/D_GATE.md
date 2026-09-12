# D: register-resident hash_g sponge

Experiment gt768-fused-shake-hashg-20260911-e41; C baseline
1493b298e790990038d15c146288280db943d79e.

Observation: C still calls the scalar permutation ten times and materializes
25 state lanes at every boundary. Its fixed wrapper has already removed
generic byte assembly and temporary absorb/squeeze buffers.

Hypothesis: keep those 25 lanes in their canonical GPR map between permutations,
absorb directly into those registers and store the 17+7 output lanes directly.
This removes repeated whole-state transfers and nine ABI save/restore pairs.
The round body's existing one-lane spill remains, so this is not a zero-memory
round implementation.

Exact change: factor the existing first-round/23-round-loop/normalization
instructions into one assembly macro, used by the unchanged standalone
permutation and a new fused hash_g entry. Two linked bodies exist because
generic SHAKE still needs standalone permutation; each contains one round
loop. The fused entry reuses its one body for all ten permutations.

Boundary allocation: lanes occupy
x1,x6,x11,x16,x21,x2,x7,x12,x17,x22,x3,x8,x13,x28,x23,x4,x9,x14,x19,x24,x5,x10,x15,x20,x25.
Free boundary temporaries: x0,x26,x27,x29,x30. x18 is never used.
All 12 callee-saved/LR registers x19..x30 are saved first.

Frame: 144 bytes, 16-byte aligned:
0 input cursor; 8 round-constant pointer; 16 inner round counter;
24 existing round temporary; 32..127 saved x19..x30;
128 output cursor; 136 outer permutation count.
No additional state spills. The existing first-round code resets the inner
counter to 1; the existing loop executes round constants 1 through 23.
After normalization, outer counts 1..7 absorb another full block,
8 absorbs the padded 65-byte tail, 9 stores 136 bytes and starts the last
permutation, 10 stores 56 bytes and returns.

Correctness/cleanup: exact original byte stream, padding and output; input
is exhausted before output stores, preserving all overlaps. Clear the entire
144-byte frame after restoring callee registers; clear caller-saved x0..x17
before returning. The saved caller values, x18 and vector registers are
preserved. This replaces clearing C's materialized 200-byte state, which no
longer exists. Verify the frame and registers with an assembly capture
trampoline, independently of the C cleanup hook.

Falsifiers: output or ABI mismatch, retained secret frame bytes, extra state
spill or round instruction changes, or no reproducible C-to-D cycle improvement.
Measure linked text growth, since sharing macro source still duplicates
the round body once in the binary.

## Result: accept as experimental champion, not production promotion

Pi 5 core 3, GCC 14.2.0, `-march=armv8-a -mtune=cortex-a76 -O3
-fomit-frame-pointer -ffunction-sections -fdata-sections -std=c99`.
66 balanced A/C/D groups, 2000 operations/sample, 100 warmups.
A is production a64e7035cb13410554af1c67870d4132a30037b4; C is the revision above.

| Operation | A median cycles | C median cycles | D median cycles | Paired C minus D median | D improvement vs C |
|---|---:|---:|---:|---:|---:|
| hash_g | 10689 | 9475 | 9164 | 311 | 3.28% |
| Encap | 31939.5 | 30720.5 | 30414.5 | 306.5 | 1.00% |
| Decap | 29048 | 27859 | 27554.5 | 303 | 1.09% |

D beats C and A in all 66 groups for every operation; sinks agree.
Paired C-minus-D p10/p90: hash_g 304/317, Encap 285/324,
Decap 288/315 cycles. No Keygen performance claim is made.

Six long PMU runs/variant, 200000 operations/run, user-space events,
100% event scheduling; amortized process overhead remains included:

| Per hash_g PMU median | C | D |
|---|---:|---:|
| instructions | 28092.07 | 27746.06 |
| ld_spec | 1248.63 | 1128.67 |
| st_spec | 758.95 | 529.25 |
| stall_backend | 544.59 | 431.52 |

These are speculative load/store events, not retired memory operations.
Boundary temperature readings were 58.7/64.8/64.8 C, frequency 2.4 GHz,
throttling 0x0 at each check; not a continuous maximum-temperature trace.

## Correctness, ABI, cleanup and footprint

- Mac and Pi full package `make check` pass, including full KEM, canonical,
  small-input and ABI tests. New fixed-hash ABI sentinel returns zero.
- KAT request/response byte-identical; response SHA256:
  `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.
- 3841 fixed-hash differential cases pass, including alignments, overlaps,
  canaries and protected input boundaries. Mac C-side ASan/UBSan also pass;
  assembly itself is not sanitizer-instrumented.
- 256 independent trampoline checks confirm output equality and zeroed
  x0..x17 plus the full 144-byte returned callee frame.
- The C-only cleanup hook falls from 39 calls/27714 bytes to 37/27314 in
  the KEM audit because two 200-byte C states no longer exist. This does
  not mean cleanup was dropped: assembly cleanup is checked independently.
- ELF audit proves the standalone 1152-byte permutation identical in A/C/D.
  All 243 instruction words of D's round/normalization body are byte-identical
  to the corresponding contiguous C body. Upstream provenance is retained;
  this integration is not claimed formally verified.
- Full Encap `.text`: A 73328, C 73744, D 74928 bytes. D costs 1184 bytes
  over C. Fused entry is 1644 bytes, with one loop body reused ten times.
- Local wrapper/permutation frame requirement falls from C's 272+128=400
  bytes to D's 144, excluding higher callers. The original one-lane round
  spill remains; no additional state spill is introduced.

## Reproduction and retained artifacts

Runner: `python3 run_b_gate.py /home/pi/gt768-fused-shake-hashg-20260911-e41
--gate D --name d-gate-v1`, with baseline/, candidate-c/, candidate-d/
populated from the recorded revisions. Full command list is in raw commands.json.
Run `python3 summarize_d_gate.py` locally after copying remote results.
Persistent evidence: D-summary.json, this record, source, tests and runners.
Ephemeral binaries/samples/disassembly/logs are gitignored under
`.build/pi-d-gate-v1`; remote `.build/d-gate-v1` in the root above.

Decision: the roughly 300-cycle full-operation benefit is reproducible and
worth retaining for 1184 bytes of text. D becomes the experimental champion.
Production and the tracked SUPERCOP leaf remain unchanged. A production-shaped
SUPERCOP export/integration gate is required before promotion; no push performed.
