# GT32 pair-native `vpmaddwd` QBM gate 022

021 proves that one-rank-1-term-at-a-time contraction cannot cross the AVX2
first cut.  This gate asks whether a rank-2 hardware dot product changes the
resource count.

## Coverage correction

The selected GT16 `QBM-PREWEIGHT` is already pair-native:

```text
c0 = vpmaddwd([e0,e1], [f0,root*f1])
c1 = vpmaddwd([e0,e1], [f1,f0])
```

For each eight-factor YMM it performs one 16-bit Montgomery preweight, two
`vpmaddwd`, two five-instruction REDC32 chains, packing, and store.  The
complete QBM is 1,056 instructions with peak 11 YMM.  Its exact accumulator
bounds are 11,943,936 and 23,887,872, safely inside signed i32.

Thus the proposed two pair dots are not a new QBM implementation.  They still
use two instructions, and the first result must live while both inputs remain
needed by the second dot.

## Atomic dual-output packet

Making one `vpmaddwd` emit both outputs requires duplicated packets:

```text
A = [e0,e1,e0,e1]
B = [f0,root*f1,f1,f0]
```

One YMM then holds only four quadratic factors instead of eight.  Two packets
are required to cover the same work, so total madd and REDC32 counts remain
96 each.  Best-case preweight count also remains 48.

On-the-fly construction has a lower bound of 26 instructions per current
eight-factor group, versus 22 selected: +192 instructions for the polynomial.
A persistent expanded ABI can optimistically save 144 QBM instructions, but
adds 96 producer stores and 96 QBM loads.  It is already net +48 instructions
before charging formation or preweight work.

Keeping the results as i32 does not remove the reducers: interpolation and
inverse entry require distinct constant weights.  Without REDC32 and packing,
those weights require `vpmulld`, wider products, or additional output dots.

## Decision

No assembly is emitted in 022.  This is a **static rejection under the modeled
ABI and reduction schedule**, not a cycle-level hard stop.  The simple
pair-native `vpmaddwd` direction is already embodied by the selected QBM;
the particular duplicated packet has no instruction-count advantage.  A
cross-factor packing proof, scheduled ASM comparison, and complete
producer/QBM/inverse gate remain necessary before closing the broader idea.

A repeatedly reused prepared operand remains a separate API-level direction:
the existing asymmetric-dual schedule costs 912 runtime QBM instructions
after a 240-instruction precompute, but loses for a standard single call
(1,152 versus 1,056).  It should reopen only when a prepared-key API and
amortization target are explicitly in scope.

Experiment 023 tests whether the apparent four-factor density is structural
for a pre-REDC i32-coordinate ABI or merely an artifact of this packet.

## Reproduction

```sh
make check
```
