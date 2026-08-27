# GT32 B3 destructive-output alias gate (095)

Control baseline: `b2a4bea`.

This gate asks only whether the selected production general B3 kernel can
overwrite either exact input without changing its instruction stream:

```text
B3(out, h, r)  versus  B3(h, h, r)  versus  B3(r, h, r)
```

It does not change the production caller or reduce the four-polynomial frame.
That integration belongs to 096, and is allowed only if this gate passes.

## Static contract

The production kernel processes twelve independent 128-byte M-layout tiles.
For each tile it loads all four vectors from `b`, then all four vectors from
`a`, before the first output store.  All later arithmetic reads registers or
constant tables.  The three polynomial pointers then advance by the same 128
bytes, and no earlier tile is reloaded.

Consequently exact `out == a` and exact `out == b` are safe.  Partial overlap
is deliberately outside this contract.

Run the complete gate with:

```sh
python3 tools/run.py
```

The generated reports are written under `generated/`.
