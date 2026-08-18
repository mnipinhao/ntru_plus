# F32X3 terminal generated-table manifest

Experiment: `AVX2-GT-D4-AOS-F32X3-TERMINAL-001`.

The deterministic generator is `tools/generate_f32x3_ct_l0_l2.py`. The checked-in
terminal artifacts are under `generated/f32x3_terminal/` and the aggregate deterministic
digest is:

`9a609525c63981688f489497aeae59c9ceb29f832aa962322285b7cb0f6abbac`

| Artifact | SHA-256 |
| --- | --- |
| assembly include | `18861febcf06043551797efca9d1a46ff526d3ba69a23987fdc4766ef5cf86e7` |
| C header | `5a3ee78def4bcb01acfcb7be9962b8b301ffcc7d295b855552e1b152c3597dd6` |
| JSON metadata | `6956c055d3602c6ea0b83b773f0a90547440e5d62816fba6463f77039be97586` |
| manifest | `c10cd698fc4b6ada34a5b2e32475d17c15238207eec9c630c4a64e1205ed3a95` |

Each of the 48 records contains the mathematical constituents, physical lane order,
natural output offsets, and the P/Pqinv/Q/Qqinv vectors consumed by the repaired direct
CRT terminal. `make d4-aos-f32x3-terminal-generated-check` regenerates into a temporary
directory and byte-compares every artifact.
