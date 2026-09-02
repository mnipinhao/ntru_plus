# Decision

The M5U-CF2 isolated-register hard gate passes.  Keep the four allocated and
scheduled regions as experimental evidence, but keep the candidate status
`investigate`.

Do not integrate the four regions directly into the Forward and do not run a
full-bank 600-plus-instruction allocation.  Independent successful allocations
do not guarantee a copy-free inter-block boundary.

## Next hard gate

Construct one **two-block boundary-composition** experiment per required
`(top, component)` pairing:

1. precolor the first block's nine outputs into the exact held-register set
   required while the sibling block runs;
2. allocate the sibling block with those nine values live and immutable;
3. prove that both output sets reach the existing store consumer with no
   register-to-register preservation copies, spill, or new memory boundary;
4. account for common packed-constant loads across the pair rather than per
   isolated region;
5. replay the exact arithmetic, range, table-pointer, and output-row checks.

Only after this two-block gate passes should the selected pair be substituted
into one frozen M5R-D bank and subjected to linked Forward correctness and Pi 5
PMU timing.  Production and the SUPERCOP baseline remain unchanged.
