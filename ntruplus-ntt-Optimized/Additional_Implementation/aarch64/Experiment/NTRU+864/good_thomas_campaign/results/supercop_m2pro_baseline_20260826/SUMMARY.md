# NTRU+864 Production SUPERCOP baseline — Apple M2 Pro

Date: 2026-08-26 (Asia/Taipei)

Result: valid local full-KEM baseline. Production source was not modified.

## Identity

- Repository source revision: `5c2e3053b33a32b7d637a74296759cac2103534b`
- Source: `ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+864`
- SUPERCOP: `20260627`
- SUPERCOP primitive: `crypto_kem/ntruplus864repo`
- SUPERCOP implementation: `neon-production`
- Security lane: `timingleaks`

The separate `ntruplus864repo` name is intentional. SUPERCOP's built-in
`ntruplus864` uses SHA-256 for `hash_f`, while this repository implementation
uses SHAKE256. They are not the same byte-level KEM contract and must not share
checksums or compete as implementations of one primitive.

## Host and selected measurement configuration

- Host database name: `haomacbookpro`
- Hardware: MacBook Pro `Mac14,9`, Apple M2 Pro, 10 CPU cores (6P + 4E), 32 GB
- OS: macOS 26.4.1 build 25E253; Darwin 25.4.0; arm64
- Compiler identity: Apple LLVM 21.0.0 (`clang-2100.1.1.101`)
- Selected flags: `gcc -march=native -mtune=native -O3 -fwrapv -fPIC -fPIE -gdwarf-4 -Wall`
- Cycle backend: `arm64-vct`
- SUPERCOP-reported counter frequency: 2,400,000,000 cycles/second
- CPU pinning: unavailable in this macOS `do-part` run
- TIMECOP/Valgrind: unavailable; this is the SUPERCOP `timingleaks` build lane,
  not a Valgrind TIMECOP result

`gcc` on this host is Apple's clang driver, as recorded by the compiler
identity above.

## Correctness gate

The repository test binary completed the 100,000-iteration KEM test with
`count: 0`. Its native tick results are not compared with SUPERCOP cycles.

The first SUPERCOP run had no expected checksum. Eight compiler configurations
agreed on:

```text
checksumsmall 8aeae8ad8b9e35da1e4305e959faf23fdda81d457c32625a0d2d48b5c47b4da9
checksumbig   3c81a5d47099996b23a626428dc0cc8a171e79b20e8c90641e39617ab1d84769
```

`clang -mcpu=native -O3` instead produced
`b0cdac767e2e48039693200e36eb3f404722e1a383e56856d7edd2a37b48e04c /
206acd115bdf985bed1e43be837054da8bcdd54a43d934baf1dc791bd3575647`.
After installing the consensus checksum, the final run marked the eight
consistent configurations `ok` and the divergent configuration `fails`.
The failed configuration was excluded before implementation selection and
measurement.

## Full-KEM cycles

Each of three SUPERCOP measurement batches contains 32 samples. The aggregate
Q1/median/Q3 below applies SUPERCOP's stabilized-quartile construction from
`stq.h` to all 96 decoded samples.

| Operation | Q1 | Median | Q3 | Per-batch stabilized medians |
| --- | ---: | ---: | ---: | --- |
| Key generation | 7,075.0 | 7,304.2 | 8,204.2 | 8,387.5; 7,000.0; 7,300.0 |
| Encapsulation | 3,791.7 | 3,933.3 | 4,700.0 | 4,700.0; 3,725.0; 3,900.0 |
| Decapsulation | 5,029.2 | 5,100.0 | 5,187.5 | 4,950.0; 5,150.0; 5,100.0 |

The first batch has visible warm-up/outlier inflation, especially for keygen
and encapsulation. The raw data is retained; no samples were deleted. This
baseline is suitable for same-host Production-versus-Experiment A/B runs. It
is not an authoritative Raspberry Pi 5 number and cannot be compared directly
with a pinned Linux PMU run.

## Required SUPERCOP adapter work

No change was made to Production. The package lane performs three explicit
adaptations:

1. flatten repo `asm/` and `CE/` source files because SUPERCOP compiles only
   sources beside the implementation `api.h`;
2. prepend SUPERCOP's generated `crypto_kem.h` to packaged `kem.c` so public
   KEM symbols receive SUPERCOP namespaces;
3. omit the repo-local `randombytes.h` so SUPERCOP's deterministic/fast
   randombytes implementation and measurement counters are visible.

On macOS, SUPERCOP 20260627 also required the recorded `cpuid/do` portability
patch. Its GNU-`od`-specific `sed` generated invalid C from BSD `od`; the patch
tokenizes whitespace before emitting the byte array.

The working command order was:

```text
./do-part init
./do-part crypto_stream chacha20
./do-part crypto_rng
./do-part crypto_kem ntruplus864repo
```

The stream and RNG steps are real prerequisites for segmented SUPERCOP runs:
they install ChaCha20 plus `knownrandombytes.o` and `fastrandombytes.o`.

## Artifacts and hashes

- `supercop-data.txt`: complete final SUPERCOP database; SHA-256
  `00ee656b1f5b968c02b1caf2d92d77aacb9b3044690cd68e2410210f98db5f95`
- `statistics.json`: decoded samples and stabilized statistics; SHA-256
  `83228543d42fb24e15468c9ba649e4587eedc13b970b7051a0bac37c4ef3d375`
- `package-PROVENANCE.txt`: packaged source identity and adapter policy;
  SHA-256 `18768291220138b73b30ee1d22dd9d7357a71386ca766247883a429f66b57fc6`
- `cpuid-bsd-od.patch`: exact SUPERCOP portability change

Future GT runs must use the same primitive checksums, host/counter/compiler
policy, package lane, and raw-data retention. A target-host baseline must be
repeated before any Production promotion decision.
