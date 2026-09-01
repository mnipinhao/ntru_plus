# M5N: complete six-bank Forward pass-2 assembly hard gate

M5N turns the bounded M5M result into a callable full P8-to-FR0 kernel.  Its
public ABI is `gt864_forward_six_bank_pass2(out, p8)`, with disjoint aligned
output and input buffers.  This is the complete second Forward pass, not yet
the complete `poly_ntt`: top split still produces the 896-halfword P8 input.

The wrapper keeps immutable output and P8 bases in `x6/x7`, saves the caller's
link register stacklessly in helper-reserved `x16`, and sets public tail stride
`x4=16`.  It then executes six fully explicit `(top,component)` calls.  Each
call resets top-specific table pointers and invokes one shared copy of the
exact 633-instruction M5M returned schedule.  Sharing the body avoids roughly
five extra copies of 2.5 KiB arithmetic code.

The helper returns the fixed physical output map recorded by M5M.  Eighteen
`str q` instructions immediately write one bank in frozen FR-0 order:

`byte_offset = 2 * ((top*18 + row*2 + block)*24 + 8*component)`

where returned output number is `block*9+row`.  Across six banks, the 108
stores cover each of 864 output halfwords exactly once.  The helper reads 128
contiguous main halfwords and sixteen strided tails per call, so all 864
meaningful P8 halfwords are read once and all 32 padding halfwords are ignored.
There is no intermediate coefficient traffic.

The compile-time table section is 1760 bytes: 32 shared bytes, two 352-byte
NTT16 tables, and two 512-byte NTT9 tables.  The complete linked object is 4928
bytes on the local arm64 toolchain.  It has no undefined symbols, stack
instruction, secret-dependent branch, or secret-dependent address.

The actual assembly passes 864 one-hot meaningful-coordinate cases, zero,
alternating proven bounds, and 256 random bound-range cases against the M5F C
oracle: 1122 exact-representative cases total.  Independently changing all
padding words never changes output.  The candidate remains Experiment because
top split, full `poly_ntt`, Pi 5 PMU, KEM/KAT, and SUPERCOP are not integrated.
