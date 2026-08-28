# Decision

Status: passed and frozen.

Keep the candidate as proof that the official normal-domain top split can be
fused with `LD3` and can produce a layout directly consumable by lane-wise
length-16 transforms.  The main bank carries `s=0..7`; the padded tail carries
the six `(top,branch)` transforms for `s=8`.

This is not yet a performance result.  The next bounded experiment should
connect an NTT16 to this exact 896-coefficient contract and compare the cost of
the 32 padding coefficients plus tail lane packing against a compact 864-value
layout.  Do not add NTT16 candidates to this frozen directory.
