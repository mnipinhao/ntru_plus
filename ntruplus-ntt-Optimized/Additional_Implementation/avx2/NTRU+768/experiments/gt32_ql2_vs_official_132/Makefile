.PHONY: build benchmark clean

build:
	python3 tools/build.py

benchmark: build
	python3 tools/run.py

clean:
	rm -rf build results generated/*.json

