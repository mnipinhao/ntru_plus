# D1-P3B4 selected byte boundaries in production-shaped KEM

This default-off experiment holds the GT-D1 Forward, BaseInv, BaseMul and
Inverse contracts fixed. It changes only real KEM byte callers: ToBytes uses
P3B3 R9-A plus stock shuffle/pack; FromBytes uses P3B3 direct C1.

Official, GT-D1 baseline and GT-D1+selected-byte candidate are linked in one
binary. Eight deterministic valid/tampered cases must be byte-exact before
paired Pi5 PMU for Keypair, Encaps and Decaps. Production remains unchanged.

The gate passed. The selected pair saves 1141.500 cycles in Keypair, 2666.900
in Encaps and 6288.450 in Decaps versus GT-D1. Encaps is now within 1174.950
cycles of Official; Keypair and Decaps remain 8791.875 and 4196.225 cycles
behind. See `results.md` for the exact call-ledger closure.
