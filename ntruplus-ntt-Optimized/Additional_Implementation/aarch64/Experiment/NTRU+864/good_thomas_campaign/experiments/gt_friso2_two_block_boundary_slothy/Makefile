.PHONY: prepare contracts static-check audit

prepare:
	python3 prepare_baseline.py
	python3 generate_pairs.py

contracts:
	python3 /Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts/check-kernel-contract.py baseline-contract.yml --kind baseline --mode existing_region_replacement
	python3 /Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts/check-kernel-contract.py kernel-contract.yml --kind kernel --mode existing_region_replacement
	python3 /Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts/check-kernel-contract.py candidate-contract.yml --kind candidate --mode existing_region_replacement --candidate-source gt864_friso2_two_block_variants.sym.S

static-check: prepare contracts
	python3 verify_pairs.py
	python3 /Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts/check-symbolic-asm.py --candidate --kernel-contract kernel-contract.yml --baseline-contract baseline-contract.yml --mode existing_region_replacement gt864_friso2_two_block_variants.sym.S
	python3 /Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts/check-physical-reg-leaks.py --contract kernel-contract.yml gt864_friso2_two_block_variants.sym.S
	python3 /Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts/compare-kernel-contract.py baseline-contract.yml candidate-contract.yml --allow-contract-change

audit: static-check
	python3 audit_slothy.py
