# GT864 P39

This experiment audits the production P7-C1 `packed_i9` arithmetic under the
P39 frozen P35-I16 and memory contract. Run `python3 audit.py` from this
directory or from the repository root. `results.json` is the checked compact
output; `RESULTS.md` explains the decision and the P40 reopen condition.

P39 is rejected at the static arithmetic gate. Consequently this directory
contains no candidate assembly or Slothy/Pi output: generating either would
misrepresent a one-instruction lead as the required complete Algorithm-10
deletion.
