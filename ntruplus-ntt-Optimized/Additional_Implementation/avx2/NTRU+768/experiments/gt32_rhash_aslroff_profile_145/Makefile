.PHONY: build benchmark profile all

build:
	python3 tools/build.py

benchmark: build
	python3 tools/benchmark.py

profile: build
	python3 tools/capture_lbr.py
	python3 tools/analyze_lbr.py --manifest lbr-manifest.json --output generated/lbr-analysis.json
	python3 tools/analyze_decap_lbr.py --manifest lbr-manifest.json --output generated/decap-lbr-analysis.json

all: benchmark profile
