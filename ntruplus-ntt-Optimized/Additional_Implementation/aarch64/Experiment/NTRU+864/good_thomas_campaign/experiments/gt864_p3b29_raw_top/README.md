# P3B29 small-input raw top

Hypothesis: remove only top SQRDMULH/MLS under the P3B28 [-3,4] proof,
reducing dynamic arithmetic by 128 instructions per Forward. Expect lower
Forward cycles and no register-pressure increase. Primary category: arithmetic.
Falsifiers: incorrect modulo-q output or KEM bytes, ABI/memory failure, unexpected
object delta, or paired Forward regression. No production edits or scheduling.

Baseline: P3B26 original T1, P3B23 FromBytes, r9_to ToBytes, D1 BaseMul.
Candidate: same except eight static instructions removed inside the 16-iteration
top loop. Keep even unused q/reciprocal setup to isolate this arithmetic change.
Specialized internal Forward/top symbols explicitly carry small_input names.

Run `python3 run.py --prepare` to rerun proof and stage sources, then
`python3 run.py --run` to upload only this bundle to the named Pi5 directory.
Compiler/DSO flags and PMU harness are inherited from P3B26; three repetitions,
both orders, CPU 3. Forward timing includes identical input-reset work.
Guard tests cover 256 bounded inputs at both memory edges, disjoint/exact alias.
Full-KEM checks include valid/tampered inputs and profile equivalence.
SUPERCOP comparator remains the frozen P3B25 snapshot, upstream latest unverified.
