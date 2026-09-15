# P33 results — local physical and correctness gates

## Current decision

P33 is **investigate / Pi 5 pending**.  It passes the static, no-spill and
local correctness gates.  Production is unchanged.  Complete Inverse and
Decaps timing cannot begin until the isolated source payload is explicitly
authorized for upload to `pi@100.99.191.9`.

## Realized data flow

For each of the three components:

1. `p33_i16_prefix` loads all sixteen Q records of half zero, executes the
   exact P13-B inverse16 prefix, and overwrites the consumed 256-byte block
   with its sixteen preterminal values.
2. `p33_i16_pair` loads all sixteen Q records of half one and executes the
   same prefix while retaining the sixteen results in registers.
3. For each `t=0..15`, the pair helper loads the four composite constants
   once, loads `A[t]`, completes/scatters A, then completes/scatters the live
   `B[t]` at the exact `+24`-byte half offset.
4. Once `B[t]` is stored its register becomes available to later columns.

The tail, natural FR0 ordering, raw-to-ternary pass, 1792-byte scratch and
complete scratch wipe are unchanged.

## Static and Slothy evidence

- Slothy code root: `/Users/chenpinhao/slothy`.
- Interpreter/dependencies: `/Users/chenpinhao/slothy_and_ra/.venv/bin/python`.
- Target model: Cortex-A76; spilling disabled.
- The prefix allocates to 17 live vector outputs (`B[0..15]` and `q`).
- A joint 69-instruction `t=0` search was stopped after it did not converge;
  the same DAG was split into A and B timing windows while the four shared
  constants and all future B states remained fixed.  All 32 windows then
  allocated and scheduled without spill.
- The generic log parser reports false `timeout`/`infeasible` signals from
  intermediate binary-search probes.  The generated physical artifacts,
  zero remaining executable symbolic operands, all 32 completed logs and
  successful assembly are the authoritative completion evidence.

| main-I16 work | Production | P33 | Delta |
|---|---:|---:|---:|
| executable instructions | `6 x 667 = 4002` | `3 x (190 + 1112) = 3906` | **-96** |
| composite Q loads | 384 | 192 | **-192** |
| added preterminal Q store/load | 0 | 48 / 48 | +96 instructions |
| reusable helper text | 2672 B | 760 B prefix + 4448 B pair | +2536 B |

The pair helper is 6484 bytes smaller than P32's 10932-byte six-bank terminal
body and has no global six-bank phase barrier.

## Local correctness

- Both allocated assembly files assemble for arm64.
- 4096/4096 complete inverse-to-ternary exact, in-place alias, AAPCS and
  scratch-wipe probes pass.
- 64 KEM round trips and tampered-ciphertext rejection cases pass.
- 100-case KAT SHA-256 is
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`,
  identical to production.
- Production and P33 malformed transcripts are byte-identical: 417216 bytes,
  SHA-256
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.

## Remaining hard gate

Run paired Pi 5 PMU for main-I16, complete Inverse and full KEM.  Promotion
requires production-like IPC and strictly negative upper IQR bounds for both
complete Inverse and Decaps.  Until that evidence exists the status remains
`investigate` and no production source is changed.
