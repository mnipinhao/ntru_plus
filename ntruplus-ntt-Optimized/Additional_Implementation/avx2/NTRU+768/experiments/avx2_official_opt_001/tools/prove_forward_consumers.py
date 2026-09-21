#!/usr/bin/env python3
"""Conservative consumer word bounds for a no-terminal-Barrett Forward ABI.

This is a separate sound magnitude envelope, intentionally independent of
the precise Forward interval engine. It proves word safety of the actual
quartic formulas and zero-detection contract, not performance.
"""

import argparse
import ctypes
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORWARD = ROOT / "results/officialopt-forward-lane-proof-20260921.json"
OUTPUT = ROOT / "results/officialopt-forward-consumer-proof-20260921.json"
Q = 3457
MAX_WORD = 32767
LAMBDA = 1728
R2 = 867


def mont(a, b):
    """Safe |Mont(a,b)| for |a|<=A, |b|<=B, signed 16-bit operands.

    hi(a*b) lies within ceil(A*B/65536), and hi(q*low16) contributes at
    most 1729. The low-word wrap is intentional, not an input overflow.
    """
    if a > MAX_WORD or b > MAX_WORD:
        raise ValueError(f"Montgomery operand outside signed i16: {a}, {b}")
    return (a * b + 65535) // 65536 + 1729


def check(label, bound, steps):
    steps[label] = bound
    if bound > MAX_WORD:
        raise ValueError(f"unproved signed-i16 operation {label}: {bound}")
    return bound


def basemul(a, b, label, addend=0):
    steps = {}
    p = check("runtime_montgomery_product", mont(a, b), steps)
    wrap3 = check("three_product_wrap_sum", 3 * p, steps)
    wrap2 = check("two_product_wrap_sum", 2 * p, steps)
    terms = [check("c0_pre_finalizer", p + mont(wrap3, LAMBDA), steps),
             check("c1_pre_finalizer", 2 * p + mont(wrap2, LAMBDA), steps),
             check("c2_pre_finalizer", 3 * p + mont(p, LAMBDA), steps),
             check("c3_pre_finalizer", 4 * p, steps)]
    peak = max(terms)
    final = check("R2_finalizer", mont(peak, R2), steps)
    if addend:
        check("add_m_after_finalizer", final + addend, steps)
    return {"label": label, "input_abs": [a, b], "addend_abs": addend,
            "intermediate_abs_bounds": steps}


def baseinv(a):
    steps = {}
    p = check("quartic_runtime_product", mont(a, a), steps)
    check("double_runtime_product", 2 * p, steps)
    check("three_product_t1_partial", 3 * p, steps)
    t0 = check("t0", p + mont(3 * p, LAMBDA), steps)
    t1 = check("t1", 3 * p + mont(p, LAMBDA), steps)
    t0_sq = check("t0_square", mont(t0, t0), steps)
    t1_sq = check("t1_square", mont(t1, t1), steps)
    den = check("denominator", t0_sq + mont(t1_sq, LAMBDA), steps)
    adj = check("adjugate", mont(a, t0) + mont(mont(a, LAMBDA), t1), steps)
    local = check("six_chain_local_product", mont(den, den), steps)
    pair = check("three_pair_products", mont(local, local), steps)
    aggregate = check("two_aggregate_products", mont(pair, pair), steps)
    inv_input = check("R3_correction", mont(aggregate, 460), steps)
    # A=1800 is an inductive cap: M(1800,1800)=1779 <= 1800.
    if inv_input > 1800 or mont(1800, 1800) > 1800:
        raise ValueError("field inversion inductive cap failed")
    check("field_inversion_chain_cap", 1800, steps)
    back = check("reverse_tree_recovery", mont(den, 1800), steps)
    check("apply_inverse", mont(adj, back), steps)
    if local >= Q:
        raise ValueError("zero check could see a nonzero multiple of q")
    return {"input_abs": a, "intermediate_abs_bounds": steps,
            "zero_check_argument": "Each six-chain local product has magnitude < q; a zero residue must be the exact word zero. Nonzero denominators remain nonzero in the field.",
            "zero_check_local_product_abs": local}


def serializer():
    outputs = []
    for x in range(-32768, 32768):
        v = x - Q * ((x * 9 + 16384) >> 15)
        if not -32768 <= v <= 32767:
            raise ValueError("serializer first subtract wraps")
        canonical = v + (Q if v < 0 else 0)
        if not 0 <= canonical < Q or canonical != x % Q:
            raise ValueError(f"serializer canonicalization fails at {x}")
        outputs.append(v)
    return {"input": [-32768, 32767],
            "post_barrett": [min(outputs), max(outputs)],
            "canonical_exact_for_all_signed_words": True}


def crepmod3():
    values = []
    for x in range(-32768, 32768):
        y = x + (Q if x < 0 else 0)
        if not -32768 <= y <= 32767:
            raise ValueError("crepmod3 first conditional add overflows")
        y -= 1729
        if not -32768 <= y <= 32767:
            raise ValueError("crepmod3 first centering subtract overflows")
        y += Q if y < 0 else 0
        if not -32768 <= y <= 32767:
            raise ValueError("crepmod3 second conditional add overflows")
        y -= 1728
        if not -32768 <= y <= 32767:
            raise ValueError("crepmod3 pre-reduction word overflow")
        quotient = (y * 10923 + 16384) >> 15
        value = y - 3 * quotient
        if not -32768 <= value <= 32767:
            raise ValueError("crepmod3 final word overflow")
        values.append(value)
    return {"input": [-32768, 32767],
            "output": [min(values), max(values)],
            "all_signed_words_checked": True}


def check_linked_word_consumers():
    upstream = ROOT / "upstream/supercop-avx2"
    with tempfile.TemporaryDirectory(prefix="officialopt-consumer-word-") as temp:
        library = Path(temp) / "consumer.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-mavx2", "-o", str(library),
                        str(upstream / "crepmod3.s"), str(upstream / "pack.s"),
                        str(upstream / "consts.c")], check=True, capture_output=True)
        dll = ctypes.CDLL(str(library))
        dll.poly_crepmod3.argtypes = [ctypes.c_void_p]
        dll.poly_tobytes.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        def aligned_buffer(size):
            raw = ctypes.create_string_buffer(size + 31)
            return raw, (ctypes.addressof(raw) + 31) & ~31

        input_raw, input_address = aligned_buffer(1536)
        canonical_raw, canonical_address = aligned_buffer(1536)
        packed_raw, packed_address = aligned_buffer(1152)
        packed_canon_raw, packed_canon_address = aligned_buffer(1152)
        original = (ctypes.c_int16 * 768).from_address(input_address)
        canonical = (ctypes.c_int16 * 768).from_address(canonical_address)
        packed = (ctypes.c_uint8 * 1152).from_address(packed_address)
        packed_canon = (ctypes.c_uint8 * 1152).from_address(packed_canon_address)
        count = 0
        for start in range(-32768, 32768, 768):
            words = [x if x <= 32767 else 0 for x in range(start, start + 768)]
            original[:] = words
            canonical[:] = [x % Q for x in words]
            dll.poly_tobytes(packed_address, input_address)
            dll.poly_tobytes(packed_canon_address, canonical_address)
            if bytes(packed) != bytes(packed_canon):
                raise ValueError(f"linked serializer differs on signed-word block {start}")
            original[:] = words
            dll.poly_crepmod3(input_address)
            for i, x in enumerate(words):
                y = x + (Q if x < 0 else 0)
                y -= 1729
                y += Q if y < 0 else 0
                y -= 1728
                expected = y - 3 * ((y * 10923 + 16384) >> 15)
                if original[i] != expected:
                    raise ValueError(f"linked crepmod3 mismatch at {x}")
            count += min(768, 32768 - start)
        return {"signed_inputs_checked": count,
                "poly_tobytes_byte_exact_vs_canonical": True,
                "poly_crepmod3_word_exact": True,
                "pack_source_sha256": hashlib.sha256((upstream / "pack.s").read_bytes()).hexdigest(),
                "crepmod3_source_sha256": hashlib.sha256((upstream / "crepmod3.s").read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing overwrite: {args.output}")
    forward = json.loads(FORWARD.read_text())
    domains = forward["domains"]
    for name, result in domains.items():
        if result["signed_word_failures"]:
            raise ValueError(f"Forward word proof failed: {name}")
    bound = lambda name: max(abs(domains[name]["pre_barrett_min"]),
                             abs(domains[name]["pre_barrett_max"]))
    f, g, r, m = map(bound, ("keygen_f", "keygen_g", "encap_r", "encap_m"))
    decap_msg = bound("decap_message")
    crep = crepmod3()
    if domains["decap_message"]["input_other_coefficients"] != crep["output"]:
        raise ValueError("Decap Forward input domain is narrower than crepmod3")
    # PK/CT/SK decoders accept canonical coefficient words [0,q-1].
    decoded = Q - 1
    recovered_c = check("decoded_ciphertext_minus_message_forward",
                        decoded + decap_msg, {})
    base_f = baseinv(f)
    base_g = baseinv(g)
    results = {
        "class": "conservative signed-word consumer envelope; no candidate ASM",
        "forward_proof": str(FORWARD.relative_to(ROOT)),
        "assumptions": {"q": Q, "terminal_lambda_abs": LAMBDA,
                        "decoded_pk_ct_sk_abs": decoded,
                        "montgomery_bound": "ceil(A*B/65536)+1729"},
        "keygen": {"f_baseinv": base_f, "g_baseinv": base_g,
                   "f_times_ginv": basemul(f, base_g["intermediate_abs_bounds"]["apply_inverse"],
                                             "keygen_f_times_ginv"),
                   "g_times_finv": basemul(g, base_f["intermediate_abs_bounds"]["apply_inverse"],
                                             "keygen_g_times_finv")},
        "encap": {"h_times_r_plus_m": basemul(r, decoded,
                                               "encap_h_times_r_plus_m", m)},
        "decap": {"ciphertext_minus_message": recovered_c,
                  "crepmod3_word_contract": crep,
                  "recovery_basemul": basemul(recovered_c, decoded,
                                               "decap_recovered_r")},
        "serializer": serializer(),
        "linked_word_consumer_differential": check_linked_word_consumers(),
        "conclusion": "All listed i16 arithmetic envelopes and serializer word canonicalization pass; raw representative equality is not required. Differential and invalid-input gates remain before timing or promotion.",
    }
    args.output.write_text(json.dumps(results, indent=2) + "\n")
    print("BaseInv f/g denominator", base_f["intermediate_abs_bounds"]["denominator"],
          base_g["intermediate_abs_bounds"]["denominator"])
    print("Encap final add-m", results["encap"]["h_times_r_plus_m"]
          ["intermediate_abs_bounds"]["add_m_after_finalizer"])
    print("Decap recovered-r input", recovered_c)


if __name__ == "__main__":
    main()
