# D1 consumer closure

This experiment promotes B1-D1 from an isolated arithmetic result to explicit
consumer gates without modifying Production.

`D1-C1` executes the actual M5R-D Forward twice, the old or D1 FR0 BaseMul,
and the M5E Inverse. It compares both chains with schoolbook multiplication
modulo `X^864-X^432+1`, exercises BaseMul aliases, and protects the natural
output with sentinels. Paired Pi 5 PMU measurement asks how much of the
isolated 523.933-cycle saving survives the complete polynomial boundary.

`D1-C2a` executes three M5R-D Forwards, old or D1 BaseMulAdd, and the stock
NTRU+864 `poly_tobytes` implementation (`poly_shuffle2_asm` plus
`poly_tobytes_asm`). It requires byte-exact serialization for boundary,
random, and encap-shaped coefficient distributions.

`D1-C2b` reproduces the stock Encapsulation derivation with actual keypairs,
SHAKE256, `poly_cbd1`, stock Forward NTT and `poly_sotp_encode`. It captures
the resulting NTT-domain `h`, `r`, and `m`, applies the machine-generated exact
official-to-FR0 permutation, runs old and D1 GT BaseMulAdd, maps back to the
official coordinate order, and invokes the same stock serializer. Three
keypairs times eight deterministic coin strings produce 24 ciphertext cases;
both GT paths are byte-identical to the stock ciphertext in every case.

This closes the experimental serialization consumer and its explicit
coordinate bridge. It does not link D1 into Production or constitute a
production-shaped KEM/SUPERCOP benchmark.
