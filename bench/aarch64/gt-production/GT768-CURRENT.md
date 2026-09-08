# NTRU+768 current production — 2026-09-08

Champion package source commit: **8282a30e** (E20 cleanup promotion).
Previous champion: b2f9ee83350a3e11dc2eae802ae0e5d7651586d4.
E20 source/archive record: ebeb3cf1 (implementation561b6aa5).

This supersedes the historical E20 documents saying cleanup was not promoted.
The package-only change is now selected for aarch64-production; rejected
P/N/Slothy candidates are not included. No main merge or push is part of this gate.

Accepted for cleanup and centered-mod3 contract correction under a predeclared
0.3% full-KEM regression margin, **not as a universal speedup**. Eight native
SUPERCOP rounds: paired median Keygen +34cycles/+0.0936%, Encap −7.5/−0.0202%,
Decap +14.5/+0.0446%. Correctness, KAT, required/public ABI and clear coverage pass.

Evidence: ../../../experiments/gt768-e20-promotion-20260908-e24/REPORT.md
and results.json (paths relative to repository root when browsing).
Historical research index: experiments/gt768-pack-util-cleanup-20260908-e20/BRANCH-CONSOLIDATION.md.

Twelve requested experiment branches retain archive tags and branch names;
eleven corresponding clean worktrees were removed. E20 and promotion worktrees
are also removed after final fast-forward, retaining their commits/branches/tags.
Use /Users/chenpinhao/ntruplus-aarch64-production for ongoing production work.
Ignored raw build products are regenerable, not recoverable from Git.
