# Decision

- Delete the old cross-stage-fusion P3 idea.  No BaseMul-to-Inverse or whole
  Decapsulation fusion is authorized.
- Reject the naïve model `one FR0 24-coefficient tile -> one byte segment`.
- Accept `route9` as the correct internal routing unit: two
  `K9,9 - perfect-matching` components per top, reused across components.
- Accept direct post-shuffle ToBytes and inverse pre-shuffle FromBytes as exact
  candidates.  They must remove the materialized Official array and separate
  shuffle pass, not merely rewrite the scalar permutation loop.
- Run D1-P3B next: isolated current-scalar, leaf-factorized, route9, and direct
  byte-boundary candidates with tagged correctness, byte-exact tests,
  disassembly, and paired Pi 5 PMU.  Slothy remains premature until one
  concrete Neon routing region wins.
- Keep FR0-native BaseInv as D1-P3C, independently attributable from byte
  routing.  Keep raw Inverse decomposition as the separate second-priority
  campaign.
- Production, KAT, and SUPERCOP remain unchanged.
