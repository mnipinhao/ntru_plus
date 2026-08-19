PYTHON ?= python3
GEN := tools/generate_qword_kem_caller_closure_gate.py
OUT := generated/qword_kem_caller_closure_gate.json

.PHONY: all check clean

all: $(OUT)

$(OUT): $(GEN) ../gt32_cross_r3_qword_semantic_packet_013/generated/qword_semantic_packet_gate.json ../gt32_cross_r3_qword_b3_inverse_range_014/generated/qword_b3_inverse_range_gate.json ../../pack.s ../../basemul.s ../../encap.c ../../decap.c
	$(PYTHON) $(GEN) --output $(OUT)

check: $(OUT)
	$(PYTHON) -m json.tool $(OUT) >/dev/null
	$(PYTHON) -c 'import json; p=json.load(open("$(OUT)")); assert p["Q24_reduce9_contract"]["full_signed_int16"]["unchanged_Q24_sequence_closes"]; assert p["encap"]["zero_extra_instruction_closure"]; assert p["decap"]["zero_extra_instruction_closure"]; assert p["decision"]["status"] == "kem_caller_zero_cost_closure_pass"; assert not p["decision"]["inverse_014_blocks_current_KEM_callsites"]'

clean:
