# Results

The hard gate passes at the mathematical and symbolic-source levels:

- exact B3 input union `[-16816,16816]`;
- exact NTT16 maximum magnitude 9342;
- complete two-product Forward DAG maximum magnitude 28568 at
  `top0.column13.level2.g0.y2`;
- output union `[-28568,28565]` and zero unsafe signed-halfword nodes;
- two Algorithm-10 fixed products and 15 instructions per B3;
- zero loads, stores, concrete GPRs, or physical vector-register tokens in the
  symbolic region;
- M5F C replay: 55 cases, zero mod-q mismatches, observed output maximum
  13886, 864 meaningful pass-2 loads and stores, and no intermediate NTT16
  traffic.

The rejected `2a -> 3a` DAG reached magnitude 50448 at 176 nodes even though
the same small C differential set passed. This demonstrates why the exact DAG
proof is a correctness gate rather than supporting documentation.

The Slothy candidate remains `investigate`. Static symbolic checks pass, but
the remote Slothy run, returned allocation, schedule log, complete Forward
integration, target cycle measurement, and SUPERCOP evidence are all missing.
