PYTHON ?= python3
GEN := tools/generate_qword_b3_inverse_range_gate.py
OUT := generated/qword_b3_inverse_range_gate.json

.PHONY: all check clean

all: $(OUT)

$(OUT): $(GEN) ../gt32_cross_r3_qword_semantic_packet_013/generated/qword_semantic_packet_gate.json ../../basemul.s ../../invntt.s
	$(PYTHON) $(GEN) --output $(OUT)

check: $(OUT)
	$(PYTHON) -m json.tool $(OUT) >/dev/null
	$(PYTHON) -c 'import json; p=json.load(open("$(OUT)")); assert p["B3_edge_aware_proof"]["all_B3_edges_int16_safe"]; assert not p["zero_cost_current_inverse_range_proof"]["range_closed"]; assert p["vector_selective_normalization"]["selected_vector_count"] == 24; assert p["end_to_end_static_accounting"]["end_to_end_static_instruction_delta"] == 8; assert not p["decision"]["assembly_eligible"]'

clean:
