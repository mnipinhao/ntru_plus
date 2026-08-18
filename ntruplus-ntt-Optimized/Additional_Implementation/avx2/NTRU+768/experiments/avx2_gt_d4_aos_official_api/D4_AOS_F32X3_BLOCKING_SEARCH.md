# Blocking search — F32X3-001

The selected finite candidate is DIT, natural output, bit-reversed NTT32 input, `u=j0`, and natural Good–Thomas row order. It gives exactly one INTRA-YMM-U layer (length 2: `3*16=48` groups) and four CROSS-YMM-SAME-U layers (length 4/8/16/32: `4*3*8=96` groups), for 144 vector butterfly groups. DFT3 has 16 same-`(t,u)` three-row groups. No branch crosses a 128-bit half and no whole-array transpose is required. The initial bit-reversal is a bounded 32-index row permutation, not a SoA conversion.
