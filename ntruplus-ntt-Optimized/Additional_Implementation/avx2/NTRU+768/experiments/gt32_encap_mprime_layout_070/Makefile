EXP068 := ../gt32_encap_consumer_abi_068
MAPPING_JSON := $(EXP068)/generated/mapping.json
MAPPING_CSV := $(EXP068)/generated/mapping.csv

.PHONY: check clean

check: generated/search.json generated/mprime_lanes.csv
	python3 tools/search_mprime.py --mapping-csv $(MAPPING_CSV) \
		--mapping-json $(MAPPING_JSON) --output generated/search.json \
		--lanes generated/mprime_lanes.csv --check

generated/search.json generated/mprime_lanes.csv: tools/search_mprime.py \
	$(MAPPING_JSON) $(MAPPING_CSV)
	python3 tools/search_mprime.py --mapping-csv $(MAPPING_CSV) \
		--mapping-json $(MAPPING_JSON) --output generated/search.json \
		--lanes generated/mprime_lanes.csv

clean:
	@true
