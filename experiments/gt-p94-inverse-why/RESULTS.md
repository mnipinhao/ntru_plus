# P94 — why GT's inverse transform does not beat Official's

Prompted by a simpler question: why is NTRU+768's inverse so much better than
NTRU+864's?

## It is not.  768 does not have a GT inverse

768's decapsulation inverse, `poly_invntt_decap_scale`, is **344 instructions
against Official's 343**, with an identical instruction mix bar one `add` and
identical loop counters -- 1536 stepping by 128, then 128 stepping by 16.  It is
Official's kernel.  Measured, they are indistinguishable: **253.9 ns against
253.7**.

That holds for most of 768's decapsulation:

| GT 768 decap entry | GT | Official | |
|---|---:|---:|---|
| `poly_frombytes_decap` | 69 | 68 | Official's |
| `poly_tobytes_decap` | 82 | 81 | Official's |
| `poly_basemul_decap` | 103 | 108 | Official's |
| `poly_invntt_decap_scale` | 344 | 343 | Official's |
| `poly_ntt_decap` | **3110** | 299 | **GT's** |

768's decapsulation replaces the *forward* transform and keeps everything else.
Its -15.3% is Official's arithmetic plus GT's forward transform, one unpack
fused into the multiply, and a cheaper sponge.

## What the Good-Thomas inverse actually costs

Dynamic instruction counts per coefficient, from the sources and their trip
counts:

| | total | **multiply-class** | lane extract + narrow store | rest |
|---|---:|---:|---:|---:|
| Official 768 | 4.09 | 2.12 | 0 | 1.97 |
| Official 864 | 4.52 | **2.27** | 0 | 2.25 |
| Official 1152 | 4.40 | 2.27 | 0 | 2.13 |
| **GT 864** | **7.89** | **2.02** | **2.13** | 3.74 |
| **GT 1152** | **5.89** | **1.98** | 0.13 | 3.78 |

**The decomposition delivers what it promises.**  GT needs 2.0 multiplies per
coefficient where Official needs 2.27 -- about 12% fewer.

**It pays for it in data movement.**  Total instructions are 30% to 75% higher.
At 864 that is dominated by 2.13 `umov` + `strh` per coefficient, lane
extraction through general-purpose registers and two-byte stores, which Official
does not issue at all.

## Which machine cares

| | GT / Official |
|---|---:|
| **Cortex-A76**, 864 | **0.98x** -- GT wins |
| **M2 Pro**, 864 | **1.36x** -- GT loses |
| M2 Pro, 1152 | **1.04x** |

A76 has one multiply pipe at two cycles, so 12% fewer multiplies is a real win
and the extra data movement hides behind them.  M2 has four, so the multiplies
are not the constraint and the instruction count is.  This is the campaign's
"A76-only blind spot", quantified at the level of a single kernel.

## The thing that changes the plan

1152 is 34% above Official in instructions and only **4% behind in time**.  864
is 75% above and **36% behind**.  The difference between them is precisely the
`umov`/`strh`: 2.13 per coefficient at 864, 0.13 at 1152 after P67/P68's lane
basis.

So the extra instructions are nearly free on M2 *if they are vector work*.  It is
the general-purpose round trip that is not.

**P89's estimate was low.**  It put the addressable part of 864's inverse at
43 ns, on the assumption that the `umov`/`strh` pairs would be *narrowed* to
`st1` or `str s` -- six instructions a group becoming two or three.  1152 shows
they can be *eliminated*: 2.13 per coefficient to 0.13.  Taking 864 from 7.89 to
1152's 5.76 would put it at roughly 1.04x, which is **404 ns to about 310 --
94 ns, not 43**.

## The open question

P89 established that 1152's lane swap does not port: it works because four
components fill four inner lanes, and 864 has three, so swapping would need
eight calls where six suffice.  That conclusion stands.

What does not follow is that the `umov`/`strh` are unavoidable.  1152 removed
them by making the inner lanes the components; 864 needs some *other* route to
the same end -- an output arrangement in which a group's three components are
already contiguous in a register.  Its tail already has that property
(P89: lanes 0,1,2 land on three consecutive halfwords, 32 of 32 groups).  The
main kernel does not, because a group's three components are written by three
different calls.

That is the question worth answering next: **can 864's invntt16 be restructured
so that a call produces contiguous components, without needing eight calls
instead of six?**  94 ns says it is worth an answer.

---

# Answering it: no, and for two independent reasons

## 1.  The lane swap needs four components and 864 has three

P89's finding, unchanged.  1152's inner four lanes become its four components
exactly.  At 864 three lanes of four would be used, a call would cover one `s`
value instead of four, and eight calls would be needed where six suffice.  The
extra calls cost more than the stores save.

## 2.  Fusing the three component calls does not fit in the register file

The idea that would work in principle: run the three components together so a
group's three outputs are in three registers at once, and store them with one
`st3 {v0.h, v1.h, v2.h}[lane]` -- three contiguous halfwords, exactly the layout
the output wants, four per group instead of twelve `umov` and twelve `strh`.

It does not fit.  `inverse16.S` **peaks at 27 of 32 live vector registers**, and
the transform cannot produce one group's output without completing the whole
16-point network over all 32 groups, so three components co-resident means three
working sets.  Eighty-one live values against thirty-two.

Only **three** registers feed all 128 `umov`, so the outputs themselves roll
through a tiny window -- but the *state that produces them* does not.

## What is actually reachable

| route | instructions saved | inverse | note |
|---|---:|---:|---|
| post-indexed `st1 {v.h}[l], [xT], #6` | ~670 | 404 -> ~373 ns | serialises stores Slothy interleaved |
| store the 32 output registers contiguously, then a second pass gathering three components with `st3` | ~900 | 404 -> ~358 ns | adds 3 KB of memory traffic and a pass |

Both are well short of the 94 ns the 1152 comparison suggested, because that
figure assumed 864 could reach 1152's 5.76 instructions per coefficient and both
routes to it are closed.  **Call it 30-45 ns, against a +106 ns gap.**

## What this means for the campaign

864's inverse is the one place where the Good-Thomas decomposition is a clear
regression on M2 -- 1.36x Official -- and it cannot be repaired to better than
about 1.25x within its current structure.  The decomposition's 12% multiply
saving is real and wins on A76 by 2%; it does not survive a machine with four
multiply pipes.

The honest options are to take the 30-45 ns, or to do at 864 what 768 already
does: **keep Official's inverse**.  768's `poly_invntt_decap_scale` is Official's
kernel to within one instruction, and 768 has the best decapsulation of all nine
numbers.  Whether 864's layout admits that is a separate question, and it is the
larger one.
