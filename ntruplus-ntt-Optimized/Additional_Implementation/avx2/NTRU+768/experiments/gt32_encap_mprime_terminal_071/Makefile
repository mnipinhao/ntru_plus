EXP070 := ../gt32_encap_mprime_layout_070

.PHONY: check clean

check: generated/terminal_search.json generated/permutation_classes.csv
	python3 tools/search_terminal.py --search070 $(EXP070)/generated/search.json \
		--ntt ../../ntt_m.s --output generated/terminal_search.json \
		--classes generated/permutation_classes.csv --check

generated/terminal_search.json generated/permutation_classes.csv: \
	tools/search_terminal.py $(EXP070)/generated/search.json ../../ntt_m.s
	python3 tools/search_terminal.py --search070 $(EXP070)/generated/search.json \
		--ntt ../../ntt_m.s --output generated/terminal_search.json \
		--classes generated/permutation_classes.csv

clean:
	@true
