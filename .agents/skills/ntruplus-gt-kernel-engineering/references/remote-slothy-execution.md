# Remote Slothy and Pi5 Execution

Read this reference only when the user explicitly requests remote Slothy sync,
remote Slothy execution, or Pi5 correctness/PMU work.

## Configuration

Use SSH config aliases or user-supplied environment configuration. Never embed
host addresses, usernames, ports, private keys, or home-directory paths in this
skill.

Require the relevant values before acting:

```sh
NTRUPLUS_SLOTHY_SSH="${NTRUPLUS_SLOTHY_SSH:?set an SSH config alias}"
NTRUPLUS_SLOTHY_ROOT="${NTRUPLUS_SLOTHY_ROOT:?set the remote repo root}"
NTRUPLUS_SLOTHY_PYTHON="${NTRUPLUS_SLOTHY_PYTHON:?set the remote venv python}"
NTRUPLUS_PI5_SSH="${NTRUPLUS_PI5_SSH:-}"
NTRUPLUS_PI5_ROOT="${NTRUPLUS_PI5_ROOT:-}"
```

Put non-default ports in the named SSH host entry. Do not construct a shell
command by evaluating environment-variable contents.

## Preflight

1. Derive the local root with `git rev-parse --show-toplevel`.
2. Probe the configured alias with `BatchMode=yes` and a bounded connect timeout.
3. Confirm the remote repo root, exact driver, symbolic source, contracts, and
   output parent directories.
4. Invoke the configured venv interpreter directly and print `sys.executable`
   plus `slothy.__file__`. Do not install packages before probing existing
   environments.
5. Confirm the driver target module. Use the repo's N1 selector only when the
   active checkout still lacks an A76 target.

Stop if any configured path resolves to an unexpected checkout.

## Sync

Run from the local repo root. Preserve repo-relative paths and sync only the
artifacts named by the active Slothy handoff:

```sh
rsync -avR path/to/kernel.sym.S path/to/driver.py path/to/kernel-contract.yml \
  "$NTRUPLUS_SLOTHY_SSH:$NTRUPLUS_SLOTHY_ROOT/"
```

Include a baseline contract and instruction DAG when the selected canonical
Slothy mode requires them. Never use `--delete`, flatten artifacts into the
remote root, or clean remote files without explicit user approval.

## Run and Poll

Run the exact reviewed driver with absolute remote paths and the configured
venv interpreter. Keep long executions in a managed session, poll at intervals
short enough to provide user updates, and preserve stdout/stderr as iteration
evidence. Do not start a second solver merely because the first is quiet.

After completion:

1. Record the driver, source, contract, target model, command, exit status, log,
   and generated paths.
2. Sync back only the expected `.alloc.S`, `.real_alloc.S`, `.opt.S`, and log or
   report artifacts, preserving relative paths.
3. Resume the canonical `slothy-symbolic-asm-authoring` post-run gates.

## Pi5 Validation

Require `NTRUPLUS_PI5_SSH` and `NTRUPLUS_PI5_ROOT` for remote Pi5 work. Confirm
the checkout revision and active Makefile target before building. Run assembly,
link, differential/KAT, ABI, and full-path checks before PMU measurements.

Use paired or otherwise reproducible measurements when possible. Record core
pinning, sample count, warmup, hash backend, variant flags, cycles,
instructions, IPC, and dispersion. Local macOS timing and Slothy estimates are
not evidence of Pi5/A76 performance.
