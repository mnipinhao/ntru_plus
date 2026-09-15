.PHONY: all search check clean

all: check

generated/search.json: tools/search.py
	mkdir -p generated
	python3 tools/search.py --output $@

search: generated/search.json

check: generated/search.json
	python3 tools/search.py --check $<

clean:
	rm -rf generated
