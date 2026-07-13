---
name: ntruplus-gt-kernel-engineering
description: Repo-specific execution workflow for existing NTRU+768 GT production kernel work under ntruplus-ntt-Optimized. Use for GT assembly cleanup, linked-object audits, benchmark-only prototypes, aarch64-bench and Pi5 PMU runs, GT versus KPQC comparisons, Slothy artifact integration, or explicitly requested remote Slothy execution. Prefer this skill over generic lattice, Neon, or Slothy skills for existing NTRU+768 GT production work.
---

# NTRU+ GT Kernel Engineering

## Core Boundary

Use this as the execution entrypoint for existing NTRU+768 GT production work.
Inspect the linked source, object, wrapper, build flags, tests, and benchmark
target before changing code. Do not restart algebra or platform planning unless
the requested change alters the kernel contract.

For work spanning parameter sets, implementation families, KATs, or security
analysis, route through `ntruplus-repo-engineering` instead.

## Discover the Repository

Derive paths from the active checkout; never assume a user home directory:

```sh
REPO_ROOT="$(git rev-parse --show-toplevel)"
GT_ROOT="$REPO_ROOT/ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768"
KPQC_ROOT="$REPO_ROOT/ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768"
BENCH_ROOT="$REPO_ROOT/ntruplus-ntt-Optimized/aarch64-bench"
```

Confirm each required directory exists. When paths or documentation disagree,
trust the Makefile and object actually linked by the selected target.

Keep production GT assembly under `asm/gt` and generated production Slothy
artifacts under `asm/slothy/production` only when the active Makefile confirms
those paths.

## Workflow

1. Run a read-only probe with `git status --short`, `rg`, Makefile target
   search, and linked source/object inspection.
2. Classify the request as `cleanup`, `linked-object audit`, `benchmark-only
   prototype`, `Slothy artifact`, `Pi5 PMU`, `KPQC comparison`, or `production
   promotion`.
3. Identify the active wrapper, object, flags, and test/benchmark target before
   editing an existing symbol.
4. Keep prototypes off the default production path unless the user explicitly
   requests promotion. Prefer opt-in gates and benchmark-only targets.
5. Before revisiting a previously explored optimization family, read
   `references/decision-ledger.md` and verify its evidence against the active
   Makefile and current scoreboard.
6. Assemble and run correctness before benchmarking. For performance claims,
   report cycles, instructions, IPC, code size, sample method, and percent delta
   when available.

If the user explicitly asks to implement, connect, benchmark, run PMU, or run
Slothy, perform that repo action while authority, credentials, and required
hosts are available. Do not stop at a plan unless correctness, linkage, access,
or a required contract is blocked.

## Slothy Ownership

Use the installed `slothy-symbolic-asm-authoring` skill as the sole canonical
source for contracts, exact-region extraction, symbolic assembly, drivers,
static gates, result parsing, and promotion scoring. Do not create another
repo-local skill with that name.

For artifact authoring or review, remain in the canonical Slothy workflow. If
the user explicitly requests remote sync or execution and permissions allow
it, return to this GT front door after the canonical pre-run gates pass. Read
`references/remote-slothy-execution.md`, sync only named artifacts, run and poll
the remote driver, bring generated artifacts back, then resume canonical
post-run validation.

Use a Neoverse N1 model only as a scheduling candidate when the active remote
Slothy checkout still lacks an A76 model. Validate correctness and performance
on the configured Pi5/A76 host. Never claim A76 performance from solver
estimates alone.

## Routing

- Use `ntruplus-repo-engineering` for repo-wide, non-GT, multi-parameter,
  build/KAT, or security work.
- Use `aarch64-neon-lattice-polymul` when designing a new Neon kernel contract
  or materially changing layout or instruction selection.
- Use `lattice-polymul-core` when ring, transform, reduction, or representation
  assumptions are new or incomplete.
- Use `lattice-scheme-optimization` for scheme-level operation planning.
- Use canonical `slothy-symbolic-asm-authoring` for `.sym.S`, region extraction,
  drivers, `.alloc.S`, `.opt.S`, and generated-artifact review.

## Promotion Gates

Require all applicable evidence before production promotion:

- linked production object and wrapper confirmed
- explicit production intent; otherwise keep the prototype default-off
- assembler and linker success
- KAT or differential correctness
- ABI, live-in/live-out, and output-contract preservation
- keypair, encapsulation, and decapsulation correctness when touched
- Pi5 PMU or aarch64-bench evidence after correctness passes
- KPQC final comparison for scheme-level speedup claims
- decision-ledger scope and reopen conditions satisfied

Treat a complete scheme recap, full algebraic intake, and broad platform plan as
soft checks when existing repo contracts already fix those facts.
