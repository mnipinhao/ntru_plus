---
name: ntruplus-repo-engineering
description: Route repository-wide NTRU+ engineering across parameter sets 768, 864, and 1152 and scalar, Cortex-M-oriented, AVX2, and AArch64 implementations. Use for locating the active implementation, builds, KATs, cross-variant comparisons, security analysis, or repo-level work not yet scoped to one kernel. Route existing NTRU+768 GT production work to ntruplus-gt-kernel-engineering and new algebra, platform-kernel, or Slothy artifact work to the corresponding specialized skill.
---

# NTRU+ Repository Engineering

## Core Boundary

Use repository facts to select one parameter set, implementation family, and
test contract before editing. Do not assume similarly named directories share
the same sources, Makefile behavior, transform contract, or platform support.

The Official comparison baseline is the SUPERCOP release pinned in
`bench/supercop.lock` (`ntruplus-KpqC-Final` was removed 2026-09-23). Treat
`ntruplus-ntt-Optimized` as the active optimization workspace.

Read `references/repo-map.md` when the target path is unknown, the request spans
implementations, or build/KAT/security commands are needed.

## Intake

1. Derive `REPO_ROOT` with `git rev-parse --show-toplevel`.
2. Select parameter set `NTRU+768`, `NTRU+864`, or `NTRU+1152` from the request,
   target `params.h`, or KAT name. Do not infer one from another parameter set's
   Makefile.
3. Select the lane: scalar reference, scalar optimized, Cortex-M-oriented,
   AVX2, AArch64, KAT, benchmark, or security analysis.
4. Identify the requested action: locate/audit, build, test, compare, optimize,
   port, or analyze security.
5. Inspect `git status --short`, the target Makefile, source list, wrappers,
   compile flags, and host requirements before changing or running anything.

## Routing

- Route existing NTRU+768 GT production assembly, wrappers, Pi5 PMU, or remote
  Slothy execution to `ntruplus-gt-kernel-engineering`.
- Route new ring, transform, reduction, range, or representation decisions to
  `lattice-polymul-core`.
- Route scheme-level operation DAG and optimization planning to
  `lattice-scheme-optimization`.
- Route new Cortex-M4 kernel planning to `cortex-m4-lattice-polymul`.
- Route new AArch64 Neon layout or instruction selection to
  `aarch64-neon-lattice-polymul`.
- Route symbolic assembly, Slothy contracts/drivers, and generated artifact
  review to the installed canonical `slothy-symbolic-asm-authoring` skill.
- Keep AVX2 repo implementation, build, KAT, and audit work here unless a more
  specific installed skill applies.

Do not route ordinary source lookup, Makefile repair, KAT comparison, or frozen
baseline audits into algorithm-design skills.

## Remote Slothy Policy

Run Slothy itself, its Python drivers, solver-backed allocation, and scheduling
on `pinhao@172.25.166.141` over SSH port `51208`. Do not use the local host for
Slothy execution unless the user explicitly overrides this repo policy.

Keep source inspection, contract review, and ordinary repo editing in the local
checkout. Before a run, complete the canonical
`slothy-symbolic-asm-authoring` pre-run gates, then sync only the named inputs
to the remote checkout. Sync back only the expected generated artifacts and
logs, and complete the canonical post-run gates locally. For existing
NTRU+768 GT production work, follow
`ntruplus-gt-kernel-engineering/references/remote-slothy-execution.md`.

## Repository Workflow

1. Confirm the selected directory and read its Makefile plus `params.h`.
2. Use `make -n test` and, when present, `make -n PQCgenKAT_kem` to inspect the
   real source list and flags before building.
3. Build and test only in the selected implementation directory. Architecture
   lanes require a compatible host or toolchain.
4. For KAT work, record parameter set, implementation path, revision, command,
   and compared `.req`/`.rsp` files. Do not overwrite frozen KAT vectors.
5. For cross-implementation performance, compare the same parameter set,
   operation contract, hash policy, compiler policy, and host. Run correctness
   before timing.
6. For source changes, inspect all touched keypair, encapsulation, and
   decapsulation consumers rather than relying on a micro-kernel test alone.

## Security Boundary

KAT success proves compatibility for tested vectors; it does not prove
constant-time behavior, failure probability, range safety, or parameter
security. For changes to parameters, distributions, encoding, reductions, or
secret-dependent control/data flow:

- route algebra and range reasoning to the appropriate specialized skill
- inspect constant-time branches and memory access, randomness, and failure paths
- rerun applicable KAT, differential, and decryption-failure checks
- rerun the repository security estimators when their assumptions change
- report estimator/tool revision and assumptions; do not claim security from a
  successful build or benchmark

## Evidence Before Completion

Report the selected parameter set and lane, active source/Makefile path, exact
commands run, host/toolchain constraints, correctness/KAT result, and any
remaining platform or security limitation. Performance claims require a
compatible host and reproducible baseline/candidate evidence.
