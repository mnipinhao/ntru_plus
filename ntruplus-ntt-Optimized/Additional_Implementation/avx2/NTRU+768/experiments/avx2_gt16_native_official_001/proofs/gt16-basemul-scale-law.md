# Basemul and baseinv scale laws

For a slot stored as `A~=s*A`, addition and subtraction require identical
`s`.  Multiplying two such values produces `s^2*A*B`, so an output retaining
scale `s` requires compensation `s^-1`.  Inverting `A~` produces
`s^-1*A^-1`; an output retaining scale `s` requires compensation `s^2`.

Encode, comparison, and every Official wire boundary must multiply by `s^-1`
and canonicalize.  The generated per-slot metadata records these laws even
though the initial candidate fixes `s=1` and therefore uses identity
compensation.
