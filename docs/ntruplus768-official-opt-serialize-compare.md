# Official-opt roadmap, first gate: Decap serialize-and-compare

Date: 2026-09-22. Branch `avx2-official-opt`. This completes the roadmap's
immediate serializer gate through Native and paired controls, **not the entire
BaseInv / GS / Yang research roadmap**. Clean production, the qualification
export, imported upstream and pristine SUPERCOP remain unchanged.

## Frozen control and implementation

Control is `qualification/avx2-officialopt-caller-lazy-qual001`: all 26 file
hashes are checked against its existing manifest before generation. The new
research implementation is `avx2-officialopt-lazy-serialize-compare-exp004`.
It changes only Decap's second `poly_tobytes(buf2,&f); verify(buf1,buf2,1152)`.
All six caller-lazy Forward calls, first recovered-r serialization, hash_g,
invalid-input behavior and original buffer clears remain.

The helper signature is internally `int compare(const uint8_t *wire,
const poly *input)`: polynomial input is 32-byte aligned, wire may be unaligned,
both are read-only, and the result is exactly 0 for equal / 1 for different.

Register flow per 128-coefficient / 192-byte block:

1. Original input loads → YMM0…7. YMM14=q and YMM15=v remain constants.
2. Unchanged Official canonicalization and packing → six wire vectors YMM0…5.
3. Six memory-form XORs with existing wire bytes → six difference vectors.
4. Five ORs reduce the differences to YMM0; `vptest; setnz; movzbl; or`
   accumulates mismatch in EAX. This accumulator survives the next block
   without consuming a YMM register.
5. Advance public pointers and repeat six times, without an early exit.

There is no new modular arithmetic, gauge, reduction or signed-overflow
precondition. The generated arithmetic prefix is copied exactly from
SHA-verified Official pack.s. Random signed-word tests establish differential
behavior against that serializer; they do not newly assert canonicalization
correctness for every arbitrary polynomial domain.

The linked helper is 692 B, 32-byte aligned, with peak live YMM=14 in the
unrolled def/use replay, no stack reference, call, vector store or vzeroupper.
Only the fixed six-block pointer loop branches. Per call it avoids the second
output's 36 vector stores and the later readback of those 1152 bytes. The 36
loads of **existing** reference bytes remain. Packing and canonicalization
are not removed. No polynomial scratch is added and existing clearing remains.
These are structural counts, not cycle predictions. Source-prefix equality
and linked register/branch census are distinct checks, not a formal binary
equivalence proof.

## Correctness and retry coverage

- 10,003 signed-word primitive differentials; equal and unequal wire strings,
  mismatch positions cover all 1152 bytes, unaligned wire, input immutability.
- Final wire read terminates exactly at a protected guard page.
- 100 deterministic KEM vectors, PK/SK/CT/shared-secret equality, tampered CT,
  noncanonical PK and SK; rejection/output behavior matches Official.
- Genuine controlled g=0 inversion failure exercises a retry.
- New one-shot **f BaseInv failure injection** is run for both caller-lazy
  control and serializer candidate. The failed output is poisoned; three
  matching Keygen RNG draws, exact keys and a subsequent KEM without reseeding
  confirm matching continuation. This is not a naturally noninvertible f.
- ASan/UBSan C harness passes; LeakSanitizer is disabled for the host's ptrace
  restriction. This does not substitute for assembly memory checks.
- Repeated generator output hashes agree; source/ELF and raw observations are
  retained in the experiment's results directories.

The actual natural f-failure coverage gap remains explicitly open.

## Cycle results

CPU 1, performance governor, turbo disabled, normal placement / ASLR-on
preselected. Actual backend is `default-perfevent`, not RDPMC. Diagnostic
uses common O3GC, same ELF, 16 identical read-only banks, matched warmup;
selection, fixture preparation and verification are outside timing. Original
serializer output scratch is included on the control side because the old
operation requires it. StQ follows pinned `include/stq.h`; sample counts are
multiples of eight so the slice-average implementation is exact.

Nine-process SUPERCOP-derived serious results (candidate minus caller-lazy):

| Region | Control StQ2 | Candidate StQ2 | Delta | Favorable |
|---|---:|---:|---:|---:|
| Serializer + equality helper | 493.07 | 465.47 | −27.60 | 9/9 |
| Complete Decap | 19361.69 | 19312.60 | −49.09 | 9/9 |

The helper control implements the original byte-XOR equality loop; the
complete caller test is the actual unchanged caller-lazy path versus the
new helper substitution. Do not add their deltas. The first short runner
attempt stopped parsing cpucycles trace setup text; its incomplete directory
is retained and is not evidence. The corrected short campaign was 3/3
favorable in both regions; serious used nine new processes.

### Native: one campaign, four implementations

Disposable tree: `/tmp/ntruplus768-officialopt-serialize-compare-20260922`.
Pinned SUPERCOP 20260831, unmodified measure.c, normal compiler selection,
nine fresh processes per implementation, serial execution. All selected
GCC 15.2.0 O2. These independent pooled StQ2 values are not paired estimates.

| Operation | Official | Caller-lazy | New candidate | Frozen GT |
|---|---:|---:|---:|---:|
| Keypair | 21584.21 | 21381.08 | 21425.48 | 21262.76 |
| Encap | 28180.96 | 28007.58 | 27873.70 | 28205.63 |
| Decap | 19474.98 | 19275.65 | 19231.52 | 19144.94 |

New candidate minus caller-lazy: Keypair **+44.39**, Encap **−133.88**,
Decap **−44.13**. Only Decap arithmetic/caller code changed. Unchanged
operations' shifts must not be attributed to serializer algorithm savings.

### Fixed-ELF controls: candidate versus caller-lazy, not versus Official

Common O3GC, 16 balanced ABBA/BAAB blocks / 64 fresh launches per setting.
The existing runner uses the generic label `official`; here that label means
**caller-lazy control**, as recorded in the ELF paths and source manifests.
Reversed order renames source members without changing their bytes.

| Setting | Keypair mean Δ | Encap mean Δ | Decap mean Δ [95% CI] |
|---|---:|---:|---:|
| Normal / ASLR off | −42.32 | +30.24 | −37.96 [−60.78, −14.03] |
| Normal / ASLR on (primary) | −40.98 | +55.92 | +10.36 [−32.19, +71.54] |
| Reversed / ASLR off | +11.91 | +81.12 | −75.51 [−105.56, −42.87] |
| Reversed / ASLR on | −18.67 | −17.26 | −43.94 [−109.11, +6.24] |

The primary Decap CI crosses zero. Reversed/ASLR-off Encap has a significant
regression, CI **[+52.13,+111.43]**. Thus this realization **does not qualify**,
despite its local win and favorable Native Decap number. No further link-order
search, cumulative optimization or clean promotion is authorized by this
result. The controls demonstrate image sensitivity; they do not isolate an
instruction-cache or individual-placement causal mechanism.

## BaseInv follow-up and remaining roadmap

A new census of the current diagnostic ELF finds BaseInv inlined batch code
inside `poly_baseinv`, 189 static RSP-referencing instruction rows and 13 call
rows (including alternate failure paths). These are not dynamic counts.
The source explicitly clears `inv`, intermediate product arrays, `inv1`,
`INV`, `tmp` and `inv0`. Calls to zeroization routines occur while recovery
values are still needed. Under SysV, all YMM registers are caller-clobbered:
such lifetimes need explicit preservation unless the clear schedule itself
is redesigned and justified. Therefore “remove C stack traffic” is not yet
an executable same-DAG proposal.

This finding does **not** prove the stack traffic minimal. The second ASM
slot remains unused and the BaseInv allocation gate remains open. Required
next work is a full last-use/zeroization-aware reverse-recovery/application
schedule with exact scale and retry semantics, then current-control Keygen
pricing. No new BaseInv performance claim is made.

Original GS lane-to-lane reduction proof and Yang radix-3/gauge alternatives
are **not completed in this gate**. In particular, the previous CT
`±7644` envelope is conditional evidence, not a newly proved complete GS
consumer contract. Historical CT/wresident failures and old isolated phase
timings must not be relabeled as results of this roadmap.

## Reproduce

From `.../NTRU+768/experiments/avx2_official_opt_001`:

```sh
python3 tools/generate_serialize_compare.py
make check-serialize-compare build/bench_serialize_compare
python3 tools/audit_serialize_compare.py
python3 tools/audit_baseinv_followup.py
ASAN_OPTIONS=detect_leaks=0 make BUILD=build_compare_san \
  CFLAGS='-O1 -g -mavx2 -march=native -fsanitize=address,undefined -fno-omit-frame-pointer -fwrapv' \
  check-serialize-compare
python3 tools/run_serialize_compare.py --tag NEW_TAG --launches 9
```

Key artifacts under `results/`: `serialize-compare-control.json`,
`serialize-compare-linked.json`, `serialize-compare-validation-20260922/`,
`officialopt-serialize-compare-serious-20260922/`,
`native-sc-{official,control,candidate,gt}-20260922/`,
`fixed-sc-paired-20260922/`, and `baseinv-followup-census.json`.
Native installations use `tools/install_supercop.py --variant SC` in a fresh
verified disposable campaign. Benchmark recipes and source/ELF identities
are preserved with the observations; existing result directories are not
overwritten.
