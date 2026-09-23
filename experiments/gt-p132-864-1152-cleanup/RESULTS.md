# P132 — NTRU+864/1152 cleanup, as NTRU+768's P121

Behaviour-preserving except where code was deleted.  Each step was checked
with `codehash.sh` (hash of the code and constant bytes of a KEM-only program
linked from the tree): comment, label and symbol-spelling steps leave it
unchanged; deletions are checked by `make check` and the KAT instead.

| step | what | check |
|---|---|---|
| 1 | Slothy schedule listings stripped (`slothy_strip.py`): `inverse16_paired.S` 299 -> 29 KB, `inverse_tail_direct.S` 198 -> 29 KB, 1152 `inverse16.S` 322 -> 15 KB, `inverse9.S` 55 -> 6 KB | codehash unchanged |
| 2 | non-global labels `.L`-local, unreferenced Slothy/region markers deleted (`labels.py`, which ignores `/* */` -- the Keccak headers carry YAML with `x0:` lines) | codehash unchanged |
| 2b | Keccak files replaced by NTRU+768's cleaned copies, so all three sets carry the same two files; this drops an unreferenced internal "live-state" permutation from `keccakf1600_v84a.S` (71 instructions never executed) | tests, KAT, 100,003-state SHA3 check |
| 3 | one symbol spelling, `C_SYM(X)` (`csym.py`, `csym_refs.py`), replacing dual labels, `#define X _X` aliases and `C(name)` | codehash unchanged |
| 4 | dead code removed: 864 `poly_crepmod3` (`crepmod3.S`, its `SUPPORT` line), `crepmod3_raw.S`, `frombytes_transpose`, `tables.h`; 1152 `poly_tobytes_compare` / `tobytes_compare_asm` (and its ABI case), a stale `poly_crepmod3` declaration, `gt_perm.h` | `make check`, KAT |
| 5 | comments describe the code, not the experiments (`comments.py`): P-numbers, gate/decision names and change logs replaced by the facts they carried; the 1152 `inverse16.S` range caveat replaced by the proof | codehash unchanged |
| 6 | 864's `ntt_api.c`, `inverse_api.c`, `unpack_api.c` merged into `api_glue.c`, as 1152 has | `make check`, KAT |
| 7 | READMEs rewritten as package READMEs (1152's was an experiment log); source maps match the files | -- |

Result: M2 and Linux `make check`, TIMECOP (`-O`..`-Os`) pass for both sets;
performance unchanged (P129 harness, M2: 864 3,815 -> 3,820 ns decaps within
layout noise, 1152 identical).  About 800 KB of comments and 55 KB of unused
tables removed.
