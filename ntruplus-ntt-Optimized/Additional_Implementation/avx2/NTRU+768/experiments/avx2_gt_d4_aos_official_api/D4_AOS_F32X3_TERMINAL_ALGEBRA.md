# F32X3 fused-terminal algebra

For DFT slot `s`, the natural row is `(0,2,1)[s]`. For block `t`, packed bit `u`,
and branch `b`, define

`i = 64*r + 33*(2*t+u) mod 96`

and

`f_b = 96^-1 * twist_base[b]^-i mod q`, with `twist_base=(22,2)` and `q=3457`.

Let `alpha=(2735,723)` and `delta=(alpha0-alpha1)^-1`. After the mandatory compact
DFT3 Barrett boundary, branch values are `x0` and `x1`. The reference result is

`h = (x0*f0 - x1*f1)*delta`

`a = x0*f0 - alpha0*h`.

The bounded repair folds these equations into two lane-wise Montgomery products. P is
applied to `[x0|x1]` and Q to its 128-bit-half swap `[x1|x0]`:

- P low: `f0*(1-alpha0*delta)`; P high: `-f1*delta`.
- Q low: `f1*alpha0*delta`; Q high: `f0*delta`.

Their sum is `[a|h]`. One final packed Barrett and `q -> 0` canonicalization precede
four generated qword stores. The DFT3 slot is consumed immediately; D0/D1/D2 are never
written to semantic scratch and the old coefficient-major transpose is absent.
