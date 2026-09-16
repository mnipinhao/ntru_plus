# Model

For a legacy cubic leaf `A(X)` modulo `X^3-z`, choose `X=uY` and store

`phi_u(A) = (a0, u*a1, u^2*a2)`.

The transformed leaf is modulo `Y^3-z'`, where `z'=z/u^3`.  This geometric
component scaling is an algebra homomorphism; an arbitrary scalar scaling of
the complete leaf is not interchangeable with it.

For GT864:

- `z = theta^(1+6c+96r)` in the alpha top;
- `z = theta^(5+6c+96r)` in the beta top.

FR-ISO2 uses

- `u = theta^(2c+32r)` for alpha;
- `u = 27*theta^(2c+32r)` for beta;

and therefore obtains `z'=9` or `z'=3`.

The zero-post-add candidate removes the row factor:

- `u0 = theta^(2c)` for alpha;
- `u0 = 27*theta^(2c)` for beta.

It consequently has `z'=9*theta^(96r)` or `3*theta^(96r)`.
