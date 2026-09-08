# ToBytes streaming pair prototype — rejected

The default production path is unchanged. Two route9 streams feed
normalization and 12-bit pair packing. Each pair writes three final bytes with
ST3 lane at nine-byte spacing. Pair stream order is (p0c0,p0c1), (p0c2,p1c0),
(p1c1,p1c2). Two tops, nine routed rows, eight lanes: every output byte is
written once, no merge/read of output. Each input coefficient is logically
loaded once; no full official[864]/post[864] array exists in the source.

Correctness: 864 single-coordinate impulses plus 672 random full-int16
vectors, output canaries, and six full-KEM differential processes passed.
Source-level small vector arrays did NOT remain solely in registers:

| Candidate | Pair stack frame | Keygen baseline/candidate | Encaps baseline/candidate | Decaps baseline/candidate |
|---|---:|---:|---:|---:|
| Loop | 304 bytes | 54121.375 / 57522.375 | 46094.450 / 48358.425 | 44434.325 / 46621.750 |
| Explicit output unroll | 400 bytes | 54264.875 / 57377.625 | 46082.425 / 48269.500 | 44425.275 / 46558.350 |

Pi5 GCC14.2.0, core3, median of six process medians; 41 samples/process.
Object inspection found real q-register stack stores/reloads at offsets
192,224,256,288,320 etc, beyond callee-save storage. Thus no-spill gate FAILS.
ST3-lane/address costs may also contribute; this experiment does not isolate
them from spills, and eliminating the large intermediate arrays was not enough.

Reject both for integration. Do not feed this unchanged DAG to Slothy expecting
scheduling alone to fix it. Next redesign must emit one routed pair at a time
instead of first materializing all nine outputs of both routes, and reconsider
the byte-store grouping. A new symbolic live-range gate precedes assembly.

Final library SHA256 ca8808c65ba9966e3ccaee6dffc6c425b571f391647b5db4e92927d023708234.
Object SHA256 b744e85f6ecd0f6e0fac0a51aaccd7acccdf5b96cc7fbf1e8d160158563cbd4d.
build.sh uses the frozen production objects and replaces only ToBytes at KEM
call sites. Copy production test/paired.c and ids.h to the remote experiment
directory, then run sh build.sh. This is not production code or a claimed
full constant-time/compiler proof.
