# PREPARED-P0 decoded-key ceiling (2026-08-14)

## Contract

`gt32_prepare_pk_p0` validates and decodes the canonical public-key polynomial
once into private M/SoA and retains the public-key bytes required by `hash_f`.
`gt32_prepare_sk_p0` validates and decodes fixed `f` and `hinv` into private
M/SoA and retains the 32-byte secret-key hash field.  The prepared operation
bodies consume these contexts directly; they do not copy the decoded
polynomials into per-call scratch.

Context sizes are 2688 bytes for the public key and 3136 bytes for the secret
key after 64-byte alignment.  This is an opt-in repeated-key API experiment,
not a change to the standard KEM API.

Correctness is checked inside every fresh benchmark process before timing:

- deterministic normal/prepared Encap ciphertext and shared secret exact;
- valid normal/prepared Decap return and shared secret exact;
- 16 distributed ciphertext bit-flip cases have exact return/shared-secret
  behavior;
- key preparation uses the already-qualified canonical Q24 decoder.

## Method

- Control and prepared functions are in one fixed ELF.
- SUPERcop `default-perfevent/PERF_COUNT_HW_CPU_CYCLES` backend.
- 16 fresh processes pinned to CPU 1.
- Each launch supplies the custom SUPERcop measurement distribution; its
  stabilized Q2 is the statistical unit.
- Control/prepared order reverses inside alternating measurement loops.
- Prepare-PK and Prepare-SK are measured independently to calculate amortized
  break-even.

## Results

| Operation | Normal GT | Prepared GT | Saving | Launches | 95% bootstrap CI | Prepare | Break-even |
|---|---:|---:|---:|---:|---:|---:|---:|
| Encap | 28199.60 | 28012.52 | **211.19 cycles (0.749%)** | 14/16 | [129.75, 266.50] saving | 409.56 | 1.94 calls |
| Decap | 19221.73 | 18883.88 | **364.85 cycles (1.898%)** | 16/16 | [331.42, 406.63] saving | 562.19 | 1.54 calls |

The public-key result has two slightly unfavorable launches, but the
launch-median bootstrap interval remains wholly favorable.  Secret-key
preparation is stronger and favorable in every launch.

## Decision

- Decoded-key caching is worthwhile when a key is reused at least twice.
- It is not a path to a 10% KEM speedup by itself: the measured ceiling is
  about 0.75% for Encap and 1.90% for Decap.
- At 1000 uses, prepare cost is negligible and the result approaches the
  per-call ceiling.
- The Encap saving is larger than the clean GT's current 65-cycle loss to
  Official, so a prepared-PK GT API is likely to cross parity; this remains an
  engineering hypothesis until a separate prepared workload is paired against
  an equivalently defined Official prepared/control API.
- Continue only as a distinct prepared-key API.  Do not alter the standard KEM
  API or claim that its one-shot benchmark includes this saving.

Artifacts:

- `results/tile4-supercop-prepared-p0-20260814.json`
- `results/tile4-supercop-prepared-p0-raw-20260814/`
- `results/supercop-prepared-p0-measure-20260814`
- `src/tile4_kem_prepared_p0.c`
- `src/tile4_kem_prepared_p0.h`
