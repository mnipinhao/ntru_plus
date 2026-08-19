.PHONY: all check clean

all: check

check:
	python3 tools/generate_degree8_packet_schedule_gate.py
	python3 -m json.tool generated/degree8_packet_schedule_gate.json >/dev/null

clean:
