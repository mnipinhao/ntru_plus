# Cross-Skill Routing Policy

When multiple lattice polynomial multiplication skills match, route in this
order:

1. If the request targets this workspace's NTRU+768 GT production work, use
   `ntruplus-gt-kernel-engineering` first.
2. If the request targets another existing repository implementation with known
   scheme, linked source/object paths, tests, and benchmark targets, use the
   normal repo-engineering workflow first. Do not restart scheme/core intake
   unless the requested change could alter the ring profile, transform,
   reduction contract, or representation contract.
3. If a scheme context is present and the task is scheme-level planning, start with
   `lattice-scheme-optimization`.
4. If ring, modulus, polynomial modulus, operand range, representation, or
   transform assumptions are incomplete, route through `lattice-polymul-core`.
5. If the target platform is AArch64 Armv8-A or Armv9-A Neon and the task needs
   new kernel layout, instruction selection, or range contracts, use
   `aarch64-neon-lattice-polymul` only after the algebraic/ring decision is
   clear. Existing asm cleanup, PMU harnesses, linked-object audits, and
   benchmark-only prototypes do not need this platform-planning skill unless
   they change the kernel contract.
6. If the target platform is Cortex-M4 or Armv7E-M and the task needs a new
   scalar-DSP kernel, transform plan, register/stack contract, or range contract,
   use `cortex-m4-lattice-polymul` only after the algebraic/ring decision is
   clear.
7. If the user requests Slothy, stop platform planning at instruction
   selection, layout, range contract, constant contract, memory contract, and
   reserved-register constraints, then hand off to
   `slothy-symbolic-asm-authoring`.
8. Existing schemes are routing context or case studies only. Do not import
   scheme-specific constants, root tables, cutoffs, or reductions unless the
   user explicitly asks for that concrete scheme.
