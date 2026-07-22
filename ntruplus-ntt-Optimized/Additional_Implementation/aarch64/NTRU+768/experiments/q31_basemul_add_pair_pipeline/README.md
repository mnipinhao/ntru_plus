# Q31 basemul-add pair pipeline

Status: selected and promoted to GT production on 2026-07-20.

This experiment keeps the encap-only Q31 byte contract and all quartic
arithmetic unchanged. It is not a generic `poly_basemul_add` replacement.
The optimized function remains behind the existing encap-to-bytes gate and
release guard.

## Schedule shape

The historical production loop processed 24 independent quartic groups one at
a time. `U2` mechanically unrolls two iterations and changes only the loop
count. The selected candidate schedules these two iterations together:

```text
iteration N final Q31 reduction/store
  || iteration N+1 a/b/lambda loads and quartic arithmetic
iteration N+1 final Q31 reduction/store
```

The next `a`, `b`, and lambda loads become ready before iteration N's final
store. The next `c` load remains after the current output registers are dead.
Slothy uses fixed vector allocation, no spills, and two ranges: a 90-instruction
cross-over window and a 33-instruction tail. Its instruction-multiset checks
pass for both ranges.

The production artifact preserves AAPCS64 low `d8-d15` with a 64-byte stack
frame. This adds 10 dynamic instructions but removes the ABI risk inherited
from the historical specialized leaf. The x19-x28/d8-d15 sentinel passes.

## Correctness and PMU

Raspberry Pi 5 Cortex-A76, core 3:

- 1,002-case production/U2/Slothy coefficient differential: zero mismatch.
- AAPCS64 sentinel: `abi_mask=0x0`.
- Q31 exhaustive reducer proof: 29,863,297 input values, zero mismatch.
- KEM same-binary paired checks: 366 checks, zero mismatch.
- Enabled and disabled Q31 symbol/call-site release guards: pass.

Direct PMU, `NTESTS=61`, `NITERATIONS=20000`:

| Variant | Cycles | Instructions | Delta vs historical production |
|---|---:|---:|---:|
| historical production | 2400.02 | 2221 | 0.00 |
| U2 source order | 2389.02 | 2197 | -11.00 |
| pair Slothy plus ABI save | 2308.02 | 2207 | -92.00 |

Same-binary full KEM, `NTESTS=61`, `NITERATIONS=2000`:

| Scope | Historical production | Candidate | Paired delta/call | Wins |
|---|---:|---:|---:|---:|
| keypair | 38468.59 | 38468.85 | noise | 28/61 |
| encapsulation | 38111.28 | 38030.84 | -80.44 | 61/61 |
| decapsulation | 32973.09 | 32973.62 | noise | 28/61 |

The post-promotion GT/KPQC profiler measures the actual encap pointwise row at
2,286 cycles for GT versus 2,569 for KPQC final, an 11.0% GT advantage. Full
encapsulation is 37,561 versus 39,076 cycles, a 3.88% GT advantage.

## Production linkage

Production source:

```text
asm/gt/basemul/poly_basemul_add_encap_tobytes_q31.n1.opt.S
```

`gt_production_sources.mk` is the source-of-truth. The historical one-iteration
file remains available only as the experiment baseline. Rebuild the production
artifact with:

```sh
python3 experiments/q31_basemul_add_pair_pipeline/generate_q31_pair_pipeline.py
SLOTHY_PATH=/path/to/slothy /path/to/slothy/venv/bin/python \
  experiments/q31_basemul_add_pair_pipeline/optimize_q31_pair_pipeline.py \
  --timeout 1800 \
  --production-output \
  asm/gt/basemul/poly_basemul_add_encap_tobytes_q31.n1.opt.S
```

Exact artifact hashes are in `artifact_hashes.json`.
