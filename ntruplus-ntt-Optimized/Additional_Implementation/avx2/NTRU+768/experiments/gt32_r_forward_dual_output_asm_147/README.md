# 147 — Forward(r) M + WIRE12 dual-output executable gate

This experiment implements the architecture admitted by Gate 146.  It does
not modify production.

The control is the selected production pair:

```text
ntruplus768_ntt_m_avx2
  -> materialized r_M
ntruplus768_pack_m_lazy10788_avx2
  -> WIRE12
```

The candidate branches at the post-S5 QL2 transient and emits both the same
materialized M object and the same canonical WIRE12 bytes.  It includes all
M stores, WIRE12 stores, packet reduction and packing work.  No synthetic
layout conversion is omitted.

Two executable schedules were tested:

- V1: one packet temporary, preserving all constants in registers;
- V2: release three terminal constants and expose four independent packet
  chains, using memory-source constants.  V2 is the committed candidate.

Reproduce on the configured benchmark host with:

```sh
make check
make audit
make benchmark
```

The benchmark follows the local SUPERCOP-style policy used by this tree:
same ELF, alternating paired order, CPU pinning, 16 launches, and ASLR off
through `setarch x86_64 -R`.

