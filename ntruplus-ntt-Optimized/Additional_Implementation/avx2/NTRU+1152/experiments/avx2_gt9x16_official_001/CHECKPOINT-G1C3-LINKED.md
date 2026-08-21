# Checkpoint G1C3: linked BMScale plus inverse distance-1

G1C3 implements the first namespaced G1C-M/C2-L assembly leaf. It preserves
Official BMScale's degree-4 product, add, and Montgomery-reduction ordering,
rekeys only the 18 generated lane-factor vectors, and consumes each `c_j`
with GT inverse distance-1 at its actual live cutpoint. It reports no cycles.

## Differential boundary

The independent C oracle reproduces the Official BMScale operation ordering
with explicit signed-high and 16-bit-wrap semantics. Test operands come from
the already-qualified F-R3D/G1B terminal-major producer rather than arbitrary
`int16_t` vectors, because C2-L's alternating-sign identity depends on the
proved `[-27648,27648]` pre-Montgomery difference range.

Across 1,003 producer-real trials and every one of 1,152 cells:

- the raw diagnostic BMScale leaf is bit-exact with the scalar oracle;
- the linked BMScale plus inverse-distance1 leaf is bit-exact;
- boundary, alternating-bound, random, input-immutability, and output-canary
  checks pass;
- the observed raw maximum is 7,876 and the observed sum maximum is 13,864,
  within the generated 13,824/27,648 cutpoint bounds.

The raw leaf is diagnostic only. The selected candidate is the linked C2-L
symbol and contains no raw BMScale output seam.

## Linked-object audit

The linked object is straight-line and fully namespaced. Backward register
dataflow and instruction-shape checks establish:

- 72 inverse-distance1 sequences, each exactly eight instructions, immediately
  precede the 72 result stores;
- zero loads from the output edge and therefore zero materialized
  BMScale-to-inverse reloads;
- no call, conditional branch, frame, stack reference, vector spill, forbidden
  gather/divide, or `vzeroupper`;
- a peak of 16 live YMM registers in the BMScale core.

The earlier 13-YMM estimate omitted core arithmetic liveness and is
superseded. Sixteen is acceptable because the linked object remains spill-free.
The earlier 7-instruction D1 estimate is likewise corrected to eight: the
Montgomery multiply/reduction requires four instructions.

## Gate

G1C-M/C2-L is correctness- and structure-qualified for a paired diagnostic.
It is not performance-qualified, KEM-integrated, or production-qualified.
G1C-M2 subsequently completed this comparison. See `CHECKPOINT-G1C-M2.md` for
the materialized control, live-basis audit, and paired result. This historical
checkpoint alone makes no Official/SUPERCOP conclusion.
