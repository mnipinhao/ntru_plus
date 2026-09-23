# NTRU+768 Official AVX2 optimization branch

These instructions apply to branch `avx2-official-opt` and its dedicated worktree.

Before editing, confirm the branch and worktree status, then read `WORKFLOW.md`
and `docs/ntruplus768-official-opt.md`. Keep the original `avx2-gt-ntt`
worktree untouched. Never modify a pristine SUPERCOP snapshot, or an existing `clean/` implementation during research.

The Official baseline is the pinned SUPERCOP release in `bench/supercop.lock`.
Import `crypto_kem/ntruplus768/avx2` into a new experiment's `upstream/` once,
record its hash, and never edit that imported copy. Candidate source lives in
the experiment's `src/` or `asm/`; results and raw observations live there too.
The frozen GT comparator is `NTRU+768/clean/avx2-gt32-clean` at the branch-point
commit. It is a comparator, not the source of Official candidate code.

This branch keeps Official's decomposition, stage order, physical layout,
Montgomery domain, terminal factors, wire format, and KEM API. For any
small-input specialization, preserve the general-input implementation and
prove the caller's input range. Keep Keygen, Encap, and Decap conclusions
separate. Namespace local ASM symbols so Official and candidates can coexist
in a single diagnostic ELF. Use `.p2align 5` for AVX2 function entries and
YMM constants; aligned data moves require a proved pointer contract.

Prototype gates are risk-tiered: same-DAG scheduling may proceed directly to
ASM and differential testing; changing reduction requires an identity and
per-operation range proof. Before serious timing, require KAT/differential,
alias, canary, immutability, sanitizer, ABI, alignment, constant-time and
linked spill audits. A local component win does not promote a KEM candidate.

Native KEM timing uses unmodified SUPERCOP `crypto_kem/measure.c` in a
disposable working copy, with one enabled implementation at a time. Label
custom measurements `supercop-derived`, never native. Formal timing requires
a pinned physical P-core, performance governor and disabled turbo; scripts
must not change host controls. Preserve compiler selection, raw observations,
source and ELF hashes. Only a complete caller candidate with correctness and
Native evidence may be considered for a separate clean-production decision.
