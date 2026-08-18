# D4AOS-F32X3-V2 coordinates

`j=2*t+u`; `u=j0`; `t` carries `(j1,j2,j3,j4)` in natural order.  The physical word is unchanged: `16*(16*r+t)+8*b+4*u+c`.  Input and output Good–Thomas maps are `i=64*r+33*j (mod 96)` and `k=32*R+3*J (mod 96)`.  Their product is `32*r*R+3*j*J (mod 96)`, proving independent length-3 and length-32 transforms.  The state is exactly `3*16` YMM blocks / 1536 bytes; branch boundaries never cross 128 bits.
