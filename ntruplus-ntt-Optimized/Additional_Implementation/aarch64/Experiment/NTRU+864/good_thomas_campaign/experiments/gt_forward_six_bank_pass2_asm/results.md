# M5N results

- Callable assembly: complete six-bank P8-to-FR0 pass-2 symbol.
- Correctness: 1122 exact-representative cases, including every one of the 864
  meaningful input basis coordinates, zero, alternating proven bounds, and
  256 random bound-range inputs; zero mismatches against M5F.
- Padding: all 32 non-meaningful P8 positions independently poisoned on every
  case; zero output dependency.
- Memory: 864 meaningful input halfwords, 864 output halfwords, and zero
  intermediate coefficient traffic.
- Code: 790 static instructions: one 633-instruction helper, six `bl`, 108
  direct vector stores, public setup, and two static returns.
- Tables: 110 public vectors / 1760 bytes.
- Linked arm64 object: 4928 bytes, public symbol defined, zero undefined
  symbols, zero stack instructions.
- Static review: Arm feature warnings 0; secret-independence warnings 0.  Neon
  inventory reports the inherited 102 multiply-high, 54 transpose, and two
  table-permutation sites, all covered by M5G/M5J/M5L proofs.
- Assembly SHA-256:
  `259c7d4dfbdb0f5b2038511f81ade9b92663c2612570bb042a1463464a83db60`.

No cycle result is claimed.  The kernel is pass-2 only and is not Production.
