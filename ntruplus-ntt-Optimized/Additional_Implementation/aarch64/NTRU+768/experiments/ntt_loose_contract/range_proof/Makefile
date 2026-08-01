PYTHON ?= python3
PROOF := p1c_per_store_proof.py
JSON := p1c_per_store_bounds.json

.PHONY: check gate

check:
	$(PYTHON) $(PROOF) --emit $(JSON)

# A future ASM generator must depend on this target.  Failure is intentional
# until every per-store producer and downstream consumer proof succeeds.
gate:
	$(PYTHON) $(PROOF) --require-safe
