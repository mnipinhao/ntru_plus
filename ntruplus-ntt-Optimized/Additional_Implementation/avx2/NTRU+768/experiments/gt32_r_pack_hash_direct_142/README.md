# 142 — direct r serializer to hash input

This gate keeps production QL2, Forward_M, r_M, B3, and the serializer assembly
unchanged.  It changes only the transient dataflow:

```text
control:   pack(ct,r_M) -> hash_g copies ct to data[1..] -> SHAKE
candidate: pack(data+1,r_M) ------------------------------> SHAKE
```

The candidate deletes the 1152-byte `memcpy` read plus write.  It does not
claim to delete the serializer's 144-route network.  The primary gate is the
same-ELF paired full Encap result; the pack+hash interval is causal attribution.

Run `make benchmark` and `make pmu`.
