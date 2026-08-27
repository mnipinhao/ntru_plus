.PHONY: all build audit correctness benchmark clean

all: audit correctness

build:
	python3 tools/build.py

audit: build
	python3 tools/audit.py

correctness: build
	python3 tools/correctness.py

benchmark: audit correctness
	python3 tools/run_benchmark.py

clean:
	rm -rf build results/formal results/official generated/*.s generated/*.ld generated/*.json
