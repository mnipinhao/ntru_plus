# Inverse transform scale law

The inverse GT uses inverse length-16 and length-3 transforms, whose combined
normalization is `48^-1 mod q`, followed by `F^i`.  The two beta residues are
merged with `1/2` and `1/(2*beta)`.  The two top residues are then merged with
`1/(phi-phi^-1)`.

The scalar test evaluates both legal transform orders and checks exact
round-trip modulo 3457.  Production candidates must fuse these fixed scales
into inverse twiddles or the final store without changing the per-slot
representation scale recorded by the consumer type system.
