.PHONY: check clean

check:
	@mkdir -p build
	python3 prove_absorption_cost.py > build/proof.json
	@grep -q '"status": "reject"' build/proof.json

clean:
	rm -rf build
