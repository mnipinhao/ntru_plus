# P53 — fixed-size NO_CE hash_g

P53 adapts the NTRU+768 `aarch64-production` fixed-size scalar sponge
organization to the NTRU+864 `hash_g` transcript. It deliberately reuses only
the hash backend organization and release discipline, not any 768 NTT,
layout, scale, or range assumption.

The exact transcript is SHAKE256(`0x01 || input[1296]`) → 216 bytes. The
assembly absorbs nine complete 136-byte blocks, a 73-byte tail, and squeezes
136+80 bytes. Keccak state stays in GPRs across all eleven permutations. This
is the Pi 5 / Armv8-A NO_CE path and contains no Arm SHA3 instructions.

Run `python3 prepare.py`, then `python3 run_pi5.py` from the repository root.
The experiment always extracts the exact P50 production baseline, stages the
candidate separately, and records paired PMU results.
