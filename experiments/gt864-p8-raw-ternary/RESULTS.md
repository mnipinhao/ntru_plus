# P8 — raw Inverse directly to ternary (promoted)

Baseline `500f4d59` (P7-C1). The coefficient ring/NTT is unchanged. New
`gt864_native_inverse_ternary` is used only by Decaps. Original
`gt864_native_inverse` still returns centered natural R0, unchanged.

## Mathematics and exact domain

P7-C1's closed chain is BaseMul output abs2497 → I9 abs2617 → I16 peak21397
→ raw natural R0 abs4577. P8 does not change those arithmetic kernels/tables.
The same source identities are inherited from the frozen baseline.

Let k = [x>1728] - [x<-1728]. For |x|<=4577 (<5186), centered_q(x)=x-3457*k.
Since 3457 mod3=1, centered_q(x) and x-k have identical residues mod3.
We therefore compute a=x-k, t=(10923*a+16384)>>15, y=a-3*t.
Signed int16 a is within +/-4576; quotient within +/-1525; y is in {-1,0,1}.
`proof.py` exhausts all 9155 raw inputs, using exact signed SQRDMULH semantics.
The contiguous valid symmetric domain is actually +/-5185, but the exposed
contract stays +/-4577. At 5186 the one-wrap shortcut is WRONG (1 instead of0),
so this must not be reused under the obsolete +/-6912 raw contract.

## Register/data flow

One iteration reads four Q registers = 32 consecutive int16 coefficients.
Constants v0=1728, v1=-1728, v2=10923, v3=3 remain live for all27 iterations.
Each input independently creates two CMGT masks (0 or -1); ADD/SUB creates
x-k; SQRDMULH and MLS produce centered mod3. No lane permutation occurs.
Four STR Q write the same addresses. x0 advances64 bytes; x8 is a public
27-iteration counter. No coefficient scratch or secret-dependent addressing.
Slothy allocates only volatile SIMD registers; v8-v15 are reserved.

The 32-instruction loop region has 4 loads, 24 arithmetic, 4 stores. Old
center864 used8 arithmetic/vector and crepmod3 used3: 11→6 per vector saves
540 arithmetic instructions. One 1728-byte load pass and one1728-byte store
pass disappear. Loop/call/ABI scaffolding savings are included in full PMU.

New inverse entry uses the identical I9/I16/tail and 1792-byte scratch wipe,
then calls the new consumer in place of center864. Decaps removes its separate
poly_crepmod3 call. Public wrapper still saves/restores and erases vector state.
To preserve the old API, the control wrapper is duplicated: public object text
1424→1936 B (+512); new consumer object176 B. No per-coefficient selector or
extra data-memory boundary is introduced. Future source deduplication must not
be confused with a cycle optimization.

## Measured Pi5 result

| Boundary | P7-C1 | P8 | Paired median difference |
|---|---:|---:|---:|
| Inverse + conversion cycles | 6182.235 | 5417.047 | -765.336 |
| Decaps cycles | 42085.125 | 41333.675 | -745.275 |
| Keygen cycles | 46367.750 | 46384.750 | +15.875 |
| Encaps cycles | 45761.900 | 45769.975 | +10.800 |

Decaps improves about1.8%; paired IQR [-796.337,-726.462]. Keygen/Encaps
instruction counts are unchanged and cycle IQRs include zero: no change claim.
Complete Decaps retires664 fewer instructions and31 fewer branches. Component
measurement retires678 fewer instructions and32 fewer branches because its
baseline function-pointer adapter adds14 instructions/one branch. That small
adapter overhead is NOT credited as a production optimization; Decaps decides.
This component is inverse PLUS conversion, not the P7-C1 inverse-only boundary.

Host pi@100.99.191.9, `/home/pi/ntruplus-p8-20260912`, core3, GCC14.2,
`-O3 -march=armv8-a+simd`, same SHAKE256 implementation, ondemand governor,
post-run61.5C, throttled0x0; no competing benchmark observed. Six alternating
AB/BA processes,366 inverse+conversion paired samples and186 per KEM, warmup
and repetition counts inherited from P7-C1. User-space perf cycles/instructions/
branches, no empty subtraction. Raw samples remain in ignored build/pi5 and
the isolated Pi directory; results.json retains medians/quartiles.
Official was NOT rerun. Selected Official is still SUPERCOP20260831 aarch64,
not independently confirmed upstream-latest. No fresh Official speedup claim.

## Correctness and Slothy evidence

- Native Mac AND Pi: exhaustive9155 raw values/canaries,1024 complete
  inverse+conversion input cases (including +/-2497), exact out-of-place and
  alias, AAPCS and1792-byte wipe probe on the new entry.
- Mac/Pi 64 KEM roundtrips/tamper rejection;100-case KAT digest unchanged:
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Pi malformed transcript:32 valid cases,32 tampered cases,1024 structured
  malformed cases, exact bytes/status digest both versions
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.
- Each PMU process also checks24 byte-exact KEM/tamper and256 inverse/alias.
- Local Slothy canonical contract/static gates;32-instruction combined solve,
  1.43 seconds, no spill, expected31 cycles/region; DFG selfcheck OK.
  Runtime native tests substitute for disabled Unicorn selftest.
- Canonical static lint omitted CMGT defs; static_check.py explicitly adds
  its real destination semantics, without fake live-ins or skipped errors.
  Symbol t0 collided with the Slothy HINT register class; renamed quotient0.
  Driver now supplies a logger to avoid an upstream selftest-warning error.
- Generic log parser incorrectly calls the successful binary-search log a
  failure because intermediate stall bounds are infeasible and config contains
  timeout fields. Its best-cycle0 is also not a schedule result. Final successful
  output header31, emitted source and DFG selfcheck establish the real result;
  slothy.json binds source and output hashes. No failed output was tested.
- Mac test snapshot alone has the inherited BaseInv Mach-O symbol alias shim.

Consumer source SHA256:
`ddeb67ba9b2030821a867cd18a68d13d2ec2d102cee553f866a76fdb6d28dff3`;
Linux object `00ac8a3520460b79adbc655054e83ab068d5250ac0b13dc4275e1ceccb439115`.
Pi libraries baseline/candidate:
`6d630315789b832ecad676dcbbd1feb6f8229d0206c95b427e967e76aeb0332d` /
`d28aa963e6457f2d685df8b53b2e60030b9728186878a0b1947ce468bf76e69d`.
Object relocation confirms Decaps calls gt864_native_inverse_ternary and no
longer calls crepmod3. Original inverse kernel sources remain byte-identical.

## Reproduce / remaining work

Run proof.py; generate.py; static_check.py and physical-reg checker; run
optimize.py with PYTHONPATH=/Users/chenpinhao/slothy and Python
/Users/chenpinhao/slothy_and_ra/.venv/bin/python. prepare.py pins source packages
to500f4d59 and applies only the candidate delta; verify_mac.py tests locally.
Pi: make -C each-package -j4 all test kat; compile test.c + probe.S against
candidate; compare malformed.c transcripts; compile bench.c using
`gcc -O3 -rdynamic -Icandidate bench.c -ldl -o bench`; run taskset core3 with
baseline/candidate paths and alternating final argument0/1. summarize.py reads
build/pi5/run*.csv. Production uses the exact tested consumer and wrappers.

Next P9: ToBytes smaller joint routing/normalization/packing DAG, keep P5
baseline until static reduction gate is met. P10 BaseInv remains queued.
P8 is done; no separate center-removal experiment remains on the KEM path.
