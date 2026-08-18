# F32X3 fused-terminal range record

The compact DFT3 input is canonical post-L4 R^0. Its mandatory packed Barrett produces
the proved inclusive range `[0,3457]`; the terminal preserves R^0 input and output scale.

Exhaustive evaluation of every generated direct P/Q lane factor for every input in
`[0,3457]` gives a conservative pre-final-Barrett sum range of `[-3453,3780]`. This is
inside signed int16 and therefore the `vpaddw` cannot wrap. Exhaustive evaluation of the
packed Barrett formula across that whole interval gives `[0,3457]`. The following
compare/mask/sub maps the sole `3457` representative to zero, establishing canonical
output `[0,3456]`.

The complete differential suite separately checks byte-exact representatives, modular
equality, scale, range, 768 basis states, 768 q-representative states, 10,000 deterministic
states and 1,000 valid Forward/Basemul products under ASan/UBSan.
