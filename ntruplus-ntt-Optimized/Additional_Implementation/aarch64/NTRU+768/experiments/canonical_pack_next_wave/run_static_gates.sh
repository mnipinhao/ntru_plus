#!/bin/sh
set -eu

CODEX_HOME=${CODEX_HOME:-$HOME/.codex}
SKILL="$CODEX_HOME/skills/slothy-symbolic-asm-authoring"

python3 "$SKILL/scripts/check-kernel-contract.py" baseline-contract.yml
python3 "$SKILL/scripts/check-kernel-contract.py" kernel-contract.yml
python3 "$SKILL/scripts/check-kernel-contract.py" candidate-contract.yml --kind candidate
python3 "$SKILL/scripts/compare-kernel-contract.py" \
  baseline-contract.yml candidate-contract.yml
python3 "$SKILL/scripts/check-symbolic-asm.py" --candidate \
  --mode existing_region_replacement \
  --kernel-contract kernel-contract.yml \
  --baseline-contract baseline-contract.yml \
  pack_chunk_candidates.sym.S
python3 "$SKILL/scripts/check-physical-reg-leaks.py" \
  --contract kernel-contract.yml pack_chunk_candidates.sym.S
