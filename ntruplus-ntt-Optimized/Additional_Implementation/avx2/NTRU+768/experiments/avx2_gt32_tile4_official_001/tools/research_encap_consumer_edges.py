#!/usr/bin/env python3
"""Consumer-edge research: executable W arithmetic model, never ASM/timing.

Keep physical register assignments and AVX2 word semantics explicit.  The
range interpreter checks every non-wrapping add/sub before the word machine
executes it.  This is executable evidence, not a theorem-prover certificate.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
from collections import Counter
from pathlib import Path

import generate_encap_wire_schedule as old

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT.parent.parent / "clean" / "avx2-gt32-clean"
Q, R, QINV, BOUND = old.Q, old.R, old.QINV, old.MAX_SMALL
OUT = ROOT / "generated/tile4_encap_consumer_edges_research.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def schedule():
    steps = []

    def emit(op, dst, *src, imm=None, stage="product"):
        steps.append(dict(op=op, dst=dst, src=list(src), imm=imm, stage=stage))

    def product(i, dst):
        emit("vpshufb", 6, 0, f"hmask{i}")
        emit("vpshufb", 7, 1, f"rmask{i}")
        emit("vpmullw", 8, 6, 7)
        emit("vpmulhw", 9, 6, 7)
        emit("vpmullw", 8, 8, "qinv")
        emit("vpmulhw", 8, 8, 15)
        emit("vpsubw", dst, 9, 8)

    def fixed(src, dst, key, stage):
        emit("vpmullw", 8, src, key + "comp", stage=stage)
        emit("vpmulhw", 9, src, key, stage=stage)
        emit("vpmulhw", 8, 8, 15, stage=stage)
        emit("vpsubw", dst, 9, 8, stage=stage)

    emit("vmovdqu", 0, "h", stage="load")
    emit("vmovdqu", 1, "r", stage="load")
    # q = ymm15 and zero = ymm14 are loop-invariant.  For degree j,
    # wrap[j] must be sum(T_i[j], i>j); suffix sums give it in three blends.
    product(3, 4)
    emit("vpblendw", 5, 14, 4, imm=0x77, stage="wrapped_sum")
    for i, mask in ((2, 0x33), (1, 0x11)):
        product(i, 10)
        emit("vpaddw", 4, 4, 10, stage="cyclic_sum")
        emit("vpblendw", 5, 5, 4, imm=mask, stage="wrapped_sum")
    fixed(5, 11, "k", "lambda_minus_one")
    product(0, 10)
    emit("vpaddw", 4, 4, 10, stage="cyclic_sum")
    emit("vpaddw", 4, 4, 11, stage="corrected_e_minus_1")
    fixed(4, 9, "r2", "finalizer_e0")
    emit("vpaddw", 9, 9, "m", stage="add_m_e0")
    emit("store", None, 9, stage="store")
    return steps


def constants(packet):
    # lambda_mont already represents lambda*R.  Subtract R, not integer 1.
    k = [old.centered(lam - R) for lam in packet["lambda_mont"] for _ in range(4)]
    for leaf, lam in enumerate(packet["lambda_mont"]):
        assert k[4*leaf] * pow(R, -1, Q) % Q == (lam * pow(R, -1, Q) - 1) % Q
    result = dict(k=k, kcomp=[old.signed16(x * QINV) for x in k],
                  r2=[R * R % Q] * 16,
                  r2comp=[old.signed16((R * R % Q) * QINV)] * 16,
                  qinv=[QINV] * 16)
    for i in range(4):
        result[f"hmask{i}"], result[f"rmask{i}"] = old.mont_masks(i)
    return result


def shuffle_words(values, mask):
    raw = list(b"".join((v & 65535).to_bytes(2, "little") for v in values))
    out = [0 if k & 128 else raw[(j // 16) * 16 + (k & 15)]
           for j, k in enumerate(mask)]
    return [old.signed16(out[j] + 256 * out[j+1]) for j in range(0, 32, 2)]


def execute(steps, h, r, m, const):
    reg = {14: [0]*16, 15: [Q]*16}
    memory = dict(const, h=h, r=r, m=m)
    trace = []
    for step in steps:
        args = [reg[x] if isinstance(x, int) else memory[x] for x in step["src"]]
        op = step["op"]
        if op == "store":
            return args[0][:], trace
        if op == "vmovdqu":
            value = args[0][:]
        elif op == "vpshufb":
            value = shuffle_words(*args)
        elif op == "vpblendw":
            value = [args[1 if (step["imm"] >> (j % 8)) & 1 else 0][j]
                     for j in range(16)]
        elif op == "vpmullw":
            value = [old.signed16(a*b) for a, b in zip(*args)]
        elif op == "vpmulhw":
            value = [(a*b) // R for a, b in zip(*args)]
        elif op in ("vpaddw", "vpsubw"):
            value = [a+b if op == "vpaddw" else a-b for a, b in zip(*args)]
            assert all(-32768 <= x <= 32767 for x in value), (step, value)
        else:
            raise AssertionError(op)
        reg[step["dst"]] = value
        trace.append(max(map(abs, value)))
    raise AssertionError("missing output store")


def interval_replay(steps, const):
    reg = {14: [(0, 0)]*16, 15: [(Q, Q)]*16}
    memory = {key: [(v, v) for v in val] for key, val in const.items()}
    memory.update(h=[(0, Q-1)]*16, r=[(-BOUND, BOUND)]*16,
                  m=[(-BOUND, BOUND)]*16)
    trace = []
    for i, step in enumerate(steps):
        op = step["op"]
        if op == "vpshufb":
            # All masks select whole i16 words within one 128-bit half.
            mask = const[step["src"][1]]
            assert all(mask[j] % 2 == 0 and mask[j+1] == mask[j]+1
                       for j in range(0, 32, 2))
            value = [reg[step["src"][0]][(j//16)*8 + mask[j]//2]
                     for j in range(0, 32, 2)]
        else:
            args = [reg[x] if isinstance(x, int) else memory[x] for x in step["src"]]
            if op == "store":
                value = args[0]
            elif op == "vmovdqu":
                value = args[0]
            elif op == "vpblendw":
                value = [args[1 if (step["imm"] >> (j % 8)) & 1 else 0][j]
                         for j in range(16)]
            elif op == "vpmullw":
                value = [(-32768, 32767)]*16  # intentional low-word wrap
            elif op == "vpmulhw":
                value = []
                for a, b in zip(*args):
                    products = [x*y for x in a for y in b]
                    value.append((min(products)//R, max(products)//R))
            elif op == "vpaddw":
                value = [(a[0]+b[0], a[1]+b[1]) for a, b in zip(*args)]
            elif op == "vpsubw":
                value = [(a[0]-b[1], a[1]-b[0]) for a, b in zip(*args)]
            else:
                raise AssertionError(op)
        assert all(-32768 <= lo <= hi <= 32767 for lo, hi in value), (i, step, value)
        trace.append(dict(index=i, stage=step["stage"], op=op, lane_bounds=value,
                          intentional_wrap=op == "vpmullw"))
        if step["dst"] is not None:
            reg[step["dst"]] = value
    return trace


def liveness(steps):
    # Backward physical def/use with write kills; include constants required
    # on the next iteration to model the compact loop, not just one packet.
    live = {14, 15}
    trace = []
    peak = len(live)
    for i in range(len(steps)-1, -1, -1):
        s = steps[i]
        after = sorted(live)
        if s["dst"] is not None:
            live.discard(s["dst"])
        live.update(x for x in s["src"] if isinstance(x, int))
        peak = max(peak, len(live), len(after))
        trace.append(dict(index=i, before=sorted(live), after=after))
    assert live == {14, 15}, live
    assert peak <= 16
    initialized = {14, 15}
    for s in steps:
        assert all(x in initialized for x in s["src"] if isinstance(x, int))
        if s["dst"] is not None:
            initialized.add(s["dst"])
    return dict(peak_live_ymm=peak, spills=0, frame_bytes=0,
                physical_registers_used=sorted(initialized), trace=list(reversed(trace)),
                evidence="explicit physical instruction model; no linked ASM")


def reference(h, r, m, packet):
    # Ordinary integer schoolbook in Z_q[x]/(x^4-lambda); independent of
    # cyclic correction, Montgomery representatives and shuffle masks.
    out = []
    for leaf, lamr in enumerate(packet["lambda_mont"]):
        lam = lamr * pow(R, -1, Q) % Q
        terms = [0]*7
        for i in range(4):
            for j in range(4):
                terms[i+j] += h[4*leaf+i] * r[4*leaf+j]
        for j in range(6, 3, -1):
            terms[j-4] += lam * terms[j]
        out.extend((terms[j]+m[4*leaf+j]) % Q for j in range(4))
    return out


def main():
    if not __debug__:
        raise SystemExit("run with Python assertions enabled")
    refined = json.loads((ROOT / "generated/tile4_encap_range_refined.json").read_text())
    assert refined["stage_exact_marginal_maxima"][-1] == BOUND
    for name, expected in refined["source_sha256"].items():
        path = CLEAN / Path(name).name if Path(name).is_absolute() else ROOT / name
        assert sha(path) == expected, ("refined range source changed", name)
    packets, _ = old.packet_map()
    steps = schedule()
    consts = [constants(p) for p in packets]
    ranges = [interval_replay(steps, k) for k in consts]
    counts = Counter()
    raw_differences = 0
    observed = [0]*len(steps)

    def check(h, r, m, p, family):
        nonlocal raw_differences
        before = (h[:], r[:], m[:])
        result, trace = execute(steps, h, r, m, consts[p])
        assert [v % Q for v in result] == reference(h, r, m, packets[p])
        assert old.pack(result) == old.pack(reference(h, r, m, packets[p]))
        previous = old.simulate_mont_packet(h, r, m, packets[p]["lambda_mont"])
        assert [v % Q for v in result] == [v % Q for v in previous]
        raw_differences += sum(a != b for a, b in zip(result, previous))
        assert before == (h, r, m)
        for i, mag in enumerate(trace):
            observed[i] = max(observed[i], mag)
        counts[family] += 1

    # Every leaf and degree pair, both impulse signs, all 48 packets.
    for p in range(48):
        for a, b, sign in itertools.product(range(4), range(4), (-1, 1)):
            h = [int(j % 4 == a) for j in range(16)]
            r = [sign * int(j % 4 == b) for j in range(16)]
            check(h, r, [0]*16, p, "basis_packets")
        for hs, rs, ms in itertools.product((0, 1, Q-1), (-BOUND, 0, BOUND), (-BOUND, BOUND)):
            check([hs]*16, [rs]*16, [ms]*16, p, "uniform_boundaries")
        for bits in range(16):
            h = [Q-1 if (bits >> (j % 4)) & 1 else 0 for j in range(16)]
            r = [BOUND if (bits >> ((j+1) % 4)) & 1 else -BOUND for j in range(16)]
            m = [BOUND if j % 2 else -BOUND for j in range(16)]
            check(h, r, m, p, "mixed_boundaries")
    rng = random.Random(0x768C022)
    for i in range(10003):
        check([rng.randrange(Q) for _ in range(16)],
              [rng.randint(-BOUND, BOUND) for _ in range(16)],
              [rng.randint(-BOUND, BOUND) for _ in range(16)], i % 48, "random_packets")

    # Count the existing emitted straight-line packet body, not an earlier
    # symbolic estimate.  Its indexed lambda loads are constant operands too.
    asm = (ROOT / "generated/encap_wire_muladd.S").read_text()
    body = asm.split(".Lwire_muladd_loop_1:\n", 1)[1].split(" addq $32,%r8\n", 1)[0]
    old_lines = [line.strip() for line in body.splitlines() if line.strip()]
    old_ops = Counter(line.split()[0] for line in old_lines)
    old_constant = sum("(%rip)" in line or "(%r9,%r8)" in line or "(%r10,%r8)" in line for line in old_lines)
    new_ops = Counter(s["op"] for s in steps)
    new_constant = sum(isinstance(x, str) and x not in ("h", "r", "m")
                       for s in steps for x in s["src"])
    paths = [Path(__file__), ROOT / "tools/generate_encap_wire_schedule.py",
             ROOT / "tools/generate_tile4.py", ROOT / "generated/tile4_encap_range_refined.json",
             ROOT / "generated/encap_wire_muladd.S",
             ROOT / "results/encap-wire-mont-short-20260921-closed/summary.json",
             *[p for p in sorted(CLEAN.iterdir()) if p.is_file()]]
    document = dict(
        checkpoint="GT32-ENCAP-CONSUMER-EDGES-REENTRY-001",
        scope="research models and byte checks; no new optimization ASM or benchmark",
        input_contract=dict(h=[0, Q-1], r_m=[-BOUND, BOUND], output_exponent=0,
                            ABI="existing W; four wire quartics per YMM; all 16 lanes used"),
        identity=dict(product="T_i[j]=Mont(h_i,r_((j-i) mod 4)), e=-1",
                      cyclic="S_j=sum_i T_i[j]",
                      wrapped="U_j=sum_(i>j) T_i[j]",
                      corrected="S_j+Mont(U_j, centered((lambda-1)*R)), e=-1",
                      output="Mont(corrected,R^2)+m_j, e=0",
                      note="congruence only; deferred normalization may change raw representatives"),
        instruction_model=steps, constants=consts, liveness=liveness(steps),
        range=dict(method="per-lane interval replay for every packet/actual constant",
                   upstream_refined_proof_source_hashes_verified=True,
                   every_signed_add_sub_safe=True, new_reductions=0, packets=ranges,
                   post_add_max_abs=max(abs(x) for packet in ranges for pair in packet[-1]["lane_bounds"] for x in pair),
                   observed_instruction_abs_max=observed),
        checks=dict(packet_counts=dict(counts), total_packets=sum(counts.values()),
                    total_quartics=4*sum(counts.values()), leaves=192,
                    raw_different_coefficients_vs_old_W=raw_differences,
                    residue_and_wire_bytes="pass", immutable_inputs="pass"),
        ledger=dict(
            taxonomy="one polynomial/Encap MulAdd unless explicitly per_packet; model not linked",
            M=dict(runtime_chains=192, lambda_chains=36, R2_chains=48, total_chains=276),
            old_W=dict(runtime_chains=192, lambda_or_identity_chains=144, R2_chains=48, total_chains=384,
                       source_packet_instructions=len(old_lines), source_packet_opcodes=dict(old_ops),
                       constant_operands_per_packet=old_constant),
            proposed_W=dict(runtime_chains=192, lambda_minus_one_chains=48, R2_chains=48, total_chains=288,
                            model_packet_instructions=len(steps), model_packet_opcodes=dict(new_ops),
                            constant_operands_per_packet=new_constant,
                            runtime_routing_per_packet=8+3, data_loads_per_packet=3, data_stores_per_packet=1,
                            loop_control_per_packet=3, entry="q load, zero, 2 table addresses, index zero; ret",
                            constant_table_bytes=48*32*2, reused_mask_bytes=8*32,
                            extra_scratch_bytes=0, M_planes_formed=False),
            proposed_minus_old_W=dict(chains=-96, body_instructions=48*(len(steps)-len(old_lines)),
                                      constant_operands=48*(new_constant-old_constant),
                                      data_loads=0, data_stores=0, new_cross_half_routes=0),
            fixed_W_edges=dict(producers=2, decode=1, pack=2,
                               terminal_routing_delta_vs_M=0, ingress_routing_delta_vs_M=-96,
                               two_pack_routing_delta_vs_M=-384),
            add_m_fusion="separate credit: 48 c reloads and 48 c stores; compare M fused-add control",
            limitation="Montgomery chain count and def-use depth do not predict cycle delta"),
        direct_hash_stage=dict(
            current="pack_M(ct,r); hash_g(ct,ct) copies 1152 bytes into 0x01-prefixed data",
            proposed="data[0]=1; pack_M(data+1,r); shake256(ct,192,data,1153); secure_clear(data,1153)",
            input_read_bytes_removed=1152, destination_write_bytes_removed=1152,
            r_retained=True, hash_input_bytes=1153, hash_output_bytes=192,
            full_serializer_pass_removed=False, Keccak_permutations_saved=0,
            new_polynomial_scratch=0, old_hash_buffer_reused=True,
            not_GT_specific=True, performance="unmeasured",
            streaming_deferred="24-byte packet versus 136-byte rate plus prefix; retain contiguous fast absorb"),
        decision="verify copy-free hash stage first; aggregated W is a new arithmetic mechanism worth a bounded prototype",
        unresolved=["no linked allocation/range correspondence for proposed W",
                    "no whole-caller KAT for the new arithmetic", "no performance result",
                    "fix historical wire benchmark timed dispatch and match input-bank order before pricing"],
        source_sha256={str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p.relative_to(CLEAN.parent.parent)): sha(p) for p in paths},
    )
    OUT.write_text(json.dumps(document, sort_keys=True, separators=(",", ":"))+"\n")
    print(json.dumps({k: document[k] for k in ("checkpoint", "checks", "ledger", "decision")}, indent=2))


if __name__ == "__main__":
    main()
