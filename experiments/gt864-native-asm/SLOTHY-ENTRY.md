# Slothy entry policy (user instruction, 2026-09-08)

Use `/Users/chenpinhao/slothy` as the primary source checkout and `cortex_a76`
as the model for this campaign. Do not use the stale vendored source at
`slothy_and_ra/extern/slothy`.

The dependency interpreter currently remains
`/Users/chenpinhao/slothy_and_ra/.venv/bin/python`; that is a runtime, not the
source entry. Set `PYTHONPATH=/Users/chenpinhao/slothy`, and check module paths
and hashes in preflight output before solver execution.
