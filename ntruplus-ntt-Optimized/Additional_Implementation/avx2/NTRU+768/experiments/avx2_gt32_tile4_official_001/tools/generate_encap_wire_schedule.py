#!/usr/bin/env python3
"""Executable, non-ASM schedule gate for the Encap wire-packet ABI.

This models instruction ownership and live values. It is deliberately not a
linked-object or cycle claim; proposed operations are labelled separately
from instructions read from the frozen clean implementation.
"""

from __future__ import annotations

import hashlib
import json
import random
from collections import Counter
from pathlib import Path

import generate_tile4 as gt

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT.parent.parent / "clean" / "avx2-gt32-clean"
Q, R, QINV = 3457, 1 << 16, 12929
MAX_SMALL = 15592


def centered(x: int) -> int:
    x %= Q
    return x-Q if x > Q//2 else x


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signed16(x: int) -> int:
    x &= 65535
    return x - 65536 if x & 32768 else x


def mont(x: int, y: int) -> int:
    t = x * y
    low = signed16((t * QINV) & 65535)
    return (t - low * Q) // R


def pack(values: list[int]) -> bytes:
    out = bytearray()
    for a, b in zip(values[::2], values[1::2]):
        a, b = a % Q, b % Q
        out.extend((a & 255, (a >> 8) | ((b & 15) << 4), b >> 4))
    return bytes(out)


def encode_raw12(values: list[int]) -> bytes:
    assert len(values)%2 == 0 and all(0 <= x <= 4095 for x in values)
    out = bytearray()
    for a,b in zip(values[::2],values[1::2]):
        out.extend((a&255, (a>>8)|((b&15)<<4), b>>4))
    return bytes(out)


def decode_raw12(data: bytes) -> list[int]:
    assert len(data)%3 == 0
    out = []
    for a,mid,b in zip(data[::3],data[1::3],data[2::3]):
        out.extend((a|((mid&15)<<8), (mid>>4)|(b<<4)))
    return out


def op(name: str, reads=(), writes=(), *, kind="arithmetic", memory=None):
    return dict(op=name, reads=list(reads), writes=list(writes), kind=kind,
                memory=memory)


def replay(steps: list[dict], inputs=()) -> dict:
    """Exact virtual def/use replay, with last use releasing a register."""
    last = {}
    for i, step in enumerate(steps):
        for value in step["reads"]:
            last[value] = i
    live = set(inputs)
    peak = len(live)
    trace = []
    for i, step in enumerate(steps):
        missing = set(step["reads"]) - live
        assert not missing, (i, step["op"], sorted(missing))
        live.update(step["writes"])
        peak = max(peak, len(live))
        for value in set(step["reads"]) | set(step["writes"]):
            if last.get(value, i) == i:
                live.discard(value)
        trace.append(len(live))
    assert not live, sorted(live)
    return dict(peak_ymm=peak, final_live=0, last_use=last,
                live_after=trace, instructions=len(steps))


def allocate_ymm(steps: list[dict], inputs=(), reserved=()) -> dict:
    """Greedy physical assignment with read-before-write register reuse."""
    last = {}
    for i, step in enumerate(steps):
        for value in step["reads"]:
            last[value] = i
    live = {value: i for i, value in enumerate(inputs)}
    assert not set(range(len(inputs))) & set(reserved)
    free = [i for i in range(len(inputs), 16) if i not in reserved]
    assignments = []
    peak = len(live)+len(reserved)
    for i, step in enumerate(steps):
        assert all(value in live for value in step["reads"])
        reads = {value: live[value] for value in step["reads"]}
        for value in step["reads"]:
            if last[value] == i:
                free.append(live.pop(value))
        writes = {}
        for value in step["writes"]:
            assert value not in live and free, (i, step["op"], len(live))
            register = min(free)
            free.remove(register)
            live[value] = register
            writes[value] = register
        for value in step["writes"]:
            if last.get(value, i) == i:
                free.append(live.pop(value))
        peak = max(peak, len(live)+len(reserved))
        assignments.append(dict(index=i, op=step["op"],
                                reads=reads, writes=writes))
    assert not live and len(free) == 16-len(reserved)
    return dict(physical_ymm=16, spills=0, frame_bytes=0,
                peak_live_after=peak, reserved=list(reserved), assignments=assignments)


def dependency_stats(steps: list[dict]) -> dict:
    depth = {}
    max_depth = 0
    for step in steps:
        current = 1+max((depth[value] for value in step["reads"]), default=0)
        for value in step["writes"]:
            depth[value] = current
        max_depth = max(max_depth,current)
    return dict(longest_def_use_path_instructions=max_depth,
                independent_packet_streams=2 if any("h1" in step["writes"]
                    for step in steps) else 1,
                note="dependency depth is not cycles; port pressure and instruction latencies excluded")


def packet_map() -> tuple[list[dict], list[dict]]:
    aos, soa, owners = gt.serialized_mappings()
    codec = json.loads((ROOT / "generated/tile4_q24_codec.json").read_text())
    packets = []
    for p, old in enumerate(codec["packets_detail"]):
        wire = list(range(16 * p, 16 * p + 16))
        src = [aos[s] for s in wire]
        vector = src[0] // 16
        assert {x // 16 for x in src} == {vector}
        qwords = [src[4 * j] % 16 // 4 for j in range(4)]
        assert all(src[4*j:4*j+4] == list(range(16*vector+4*q,
                                                16*vector+4*q+4))
                   for j, q in enumerate(qwords))
        assert qwords == old["source_to_destination_qword"]
        assert [owners[s]["quartic_coefficient"] for s in wire] == [j % 4 for j in range(16)]
        packets.append(dict(packet=p, wire_words=wire, byte_interval=[24*p, 24*p+24],
                            source_aos_vector=vector, source_tile=vector // 4,
                            source_vector_in_tile=vector % 4,
                            forward_loop=vector // 8,
                            rdi_loop_store_displacement=32*p-256*(vector//8),
                            vpermq_output_source_qwords=qwords,
                            vpermq_imm=sum(q << (2*j) for j,q in enumerate(qwords)),
                            lambda_mont=[gt.lambda_montgomery(owners[s]["k3"],
                                 owners[s]["physical_q"], owners[s]["branch"])
                                 for s in wire[::4]],
                            decode_mask=old["mask_label"],
                            decode_load_offsets=[old["low_load_offset"],
                                                 old["high_load_offset"]],
                            decode_safe_loads=[old["low_load_safe12"], old["high_load_safe12"]]))
    assert len(packets) == 48 and sorted(aos) == sorted(soa) == list(range(768))
    assert sorted(x["source_aos_vector"] for x in packets) == list(range(48))
    return packets, owners


def terminal_schedule(packets: list[dict]) -> dict:
    # The clean ntt_m.s D1 deposits two four-vector groups per loop. The
    # vpshufb is the existing FR_PACKED_TO_L1 byte orientation; only the
    # vpermq and W-address store are proposed.
    by_src = {p["source_aos_vector"]: p for p in packets}
    steps = []
    for src in range(48):
        p = by_src[src]
        v = f"d1_{src}"
        shuf = f"quartic_{src}"
        dest = f"wire_{p['packet']}"
        steps += [op("vpshufb", [v], [shuf], kind="routing"),
                  op("vpermq", [shuf], [dest], kind="routing"),
                  op("vmovdqu", [dest], [], kind="data-store",
                     memory=f"rdi+{p['rdi_loop_store_displacement']}")]
    assert len({p["packet"] for p in packets}) == 48
    # A four-register deposit is the scheduling unit. Other D1 registers
    # remain live, so report both local and conservative shared peak.
    deposit = steps[:12]
    local = replay(deposit, [f"d1_{i}" for i in range(4)])
    assert local["peak_ymm"] <= 8
    # Label routing is checked for every one of the 768 coefficients.
    labels = [f"coefficient_{i}" for i in range(768)]
    aos = [None] * 768
    mapped, _, _ = gt.serialized_mappings()
    for wire, src in enumerate(mapped):
        aos[src] = labels[wire]
    output = []
    for p in packets:
        v = aos[16*p["source_aos_vector"]:16*(p["source_aos_vector"]+1)]
        for q in p["vpermq_output_source_qwords"]:
            output.extend(v[4*q:4*q+4])
    assert output == labels
    return dict(steps=steps, packet_deposit_peak=local["peak_ymm"],
                full_D1_live_peak_upper=16,
                physical_register_contract="same ymm0:7 D1 results, ymm14 byte mask, ymm15 q; vpshufb/vpermq in-place; ymm8:13 D1 temporaries dead at deposit",
                no_M_materialization=True, raw_owner_exact=768,
                instruction_counts=dict(Counter(x["op"] for x in steps)))


def decode_schedule(packets: list[dict]) -> dict:
    # Validation ordering mirrors Q24_DECODE_REG: decode, mask, vpmaxuw,
    # then W deposit. The new W deposit is a qword permutation + store.
    steps = []
    packet_peaks = []
    for p in packets:
        i = p["packet"]
        local_steps = []
        for side in range(2):
            value = f"{'lo' if side == 0 else 'hi'}{i}"
            offset = p["decode_load_offsets"][side]
            if p["decode_safe_loads"][side]:
                local_steps += [op("vmovq", [], [value+"low8"], kind="data-load",
                                   memory=f"pk+{offset}:8"),
                                op("vpinsrd", [value+"low8"], [value],
                                   kind="data-load", memory=f"pk+{offset+8}:4")]
            else:
                assert offset+16 <= 1152
                local_steps.append(op("vmovdqu_xmm", [], [value],
                                      kind="data-load", memory=f"pk+{offset}:16"))
        local_steps.extend([
            op("vinserti128", [f"lo{i}", f"hi{i}"], [f"raw{i}"], kind="routing"),
            op("vpshufb", [f"raw{i}"], [f"sh{i}"], kind="routing"),
            op("vpsrlw", [f"sh{i}"], [f"shift{i}"], kind="arithmetic"),
            op("vpblendw", [f"sh{i}", f"shift{i}"], [f"blend{i}"], kind="routing"),
            op("vpand", [f"blend{i}"], [f"decoded{i}"], kind="arithmetic"),
            op("vpmaxuw", [f"decoded{i}"], [f"validated{i}"], kind="validation"),
            op("vpermq", [f"decoded{i}"], [f"wire{i}"], kind="routing"),
            op("vmovdqu", [f"wire{i}"], [], kind="data-store",
               memory=f"hW+{32*i}"),
        ])
        packet_peaks.append(replay(local_steps)["peak_ymm"]+5)
        steps.extend(local_steps)
    # Register accumulators and low12 mask are retained in physical ymm8:12;
    # virtual peak below is packet-local and excludes these five fixed regs.
    assert max(packet_peaks) <= 16
    first = steps[:10]
    return dict(steps=steps, packet_peak_with_validation=max(packet_peaks),
                physical_first_packet_allocation=allocate_ymm(first, reserved=(8,9,10,11,12)),
                validation_accumulators=4, low12_mask=1,
                implementation_geometry="48 unrolled packet deposits, matching clean decode validation order",
                finish="unchanged Q24_DECODE_FINISH before caller proceeds",
                invalid_pk="same return/ct zeroization/ss clear before hash_f or CBD",
                instruction_counts=dict(Counter(x["op"] for x in steps)))


def pack_schedule() -> dict:
    # W already has exact wire order. Reuse the selected v=9 reducer and
    # 12-bit packing sequence from clean pack.s, omitting M transpose and
    # qword reorder. The final 24-byte packet uses two safe short stores.
    steps = [op("vmovdqu", [], ["w"], kind="data-load"),
             op("vpmulhrsw", ["w"], ["quotient"], kind="reduction", memory="v9"),
             op("vpmullw", ["quotient"], ["multiple"], kind="reduction", memory="q"),
             op("vpsubw", ["w", "multiple"], ["centered"], kind="reduction"),
             op("vpsraw", ["centered"], ["sign"], kind="canonicalization"),
             op("vpand", ["sign"], ["q_if_negative"], kind="canonicalization", memory="q"),
             op("vpaddw", ["centered", "q_if_negative"], ["canonical"], kind="canonicalization"),
             op("vpmaddwd", ["canonical"], ["paired"], kind="packing", memory="pair_factor"),
             op("vpshufb", ["paired"], ["packed"], kind="packing", memory="pack_mask"),
             op("vmovdqu_xmm", ["packed"], [], kind="byte-store", memory="bytes+0:16"),
             op("vextracti128", ["packed"], ["upper"], kind="routing"),
             op("vmovdqu_xmm", ["upper"], [], kind="byte-store", memory="bytes+12:28")]
    model = replay(steps)
    assert model["peak_ymm"] + 2 <= 16  # q and v9 constants
    return dict(packet_body=steps, body_liveness=model,
                body_allocation=allocate_ymm(steps),
                per_packet_opcodes=dict(Counter(x["op"] for x in steps)),
                packets=48, common_r_c_body=True,
                implementation_geometry="47 ordinary packets in compact shared loop, final packet safe tail",
                final_packet="replace upper 16B store by vmovq(8B)+vpextrd(4B)",
                byte_store_overlap="ordinary packet writes 4B into next packet; subsequent packet overwrites it",
                no_oob_last_packet=True)


def range_ledger() -> dict:
    f, h = MAX_SMALL, Q-1
    def mb(a: int, b: int) -> int:
        return (a*b + R-1)//R + (Q+1)//2
    product = mb(h, f)
    twisted = mb(product, (Q-1)//2)
    mont_sum = 4*max(product, twisted)
    mont_e0 = mb(mont_sum, 867)
    dot_raw = 4*h*f
    red_direct = (dot_raw+R-1)//R+(Q+1)//2
    red_wrap = (3*h*f+R-1)//R+(Q+1)//2
    dot_twist = mb(red_wrap, (Q-1)//2)
    dot_acc = red_direct+dot_twist
    dot_e0 = mb(dot_acc, 867)
    assert max(mont_sum, dot_acc, mont_e0+f, dot_e0+f) < 32768
    assert dot_raw < 2**31
    # x*QINV in VPMULLD intentionally keeps only low 32 bits. It is not a
    # signed-dword mathematical multiplication; all other dwords are safe.
    return dict(input=dict(r_m=[-f,f], h=[0,h]),
        montgomery=dict(runtime_product_abs=product,
            lambda_or_identity_abs=twisted, pre_R2_acc_abs=mont_sum,
            e0_abs=mont_e0, post_add_m_abs=mont_e0+f),
        vpmaddwd=dict(two_term_dot_abs=2*h*f, four_term_dot_abs=dot_raw,
            red_direct_abs=red_direct, red_wrapped_abs=red_wrap,
            vpackssdw_saturation_unreachable=max(red_direct,red_wrap)<32768,
            lambda_abs=dot_twist, pre_R2_acc_abs=dot_acc,
            e0_abs=dot_e0, post_add_m_abs=dot_e0+f,
            qinv_low_word_wrap="intentional modulo 2^32 in VPMULLD"),
        montgomery_low_word_wrap="intentional modulo 2^16 in VPMULLW; VPADDW/VPSUBW mathematical results stay signed-i16",
        all_signed_i16_preoperations_safe=True,
        all_non_wrap_signed_i32_preoperations_safe=True,
        serializer=dict(input="signed i16", exhaustive_domain_proof="tile4_encap_range_closure.json"),
        proof_method="per-operation conservative interval, not reachable witness")


def constant_tables(packets: list[dict]) -> dict:
    one_R = centered(R)
    mont_factors = []
    dot_lambdas = []
    for p in packets:
        dot_lambdas.append([p["lambda_mont"][j//4] for j in range(16)])
        mont_factors.append([
            [p["lambda_mont"][j//4] if i > j%4 else one_R
             for j in range(16)] for i in (1, 2, 3)])
    masks = {}
    for group in range(2):
        for part in ("direct", "wrapped"):
            for pair in range(2):
                hmask, rmask = dot_masks(group, part, pair)
                masks[f"g{group}_{part}_pair{pair}"] = dict(h=hmask, r=rmask)
    mont_routing_masks = {f"i{i}":dict(h=mont_masks(i)[0],r=mont_masks(i)[1])
                          for i in range(4)}
    assert all(all(-32768 <= x <= 32767 for x in row)
               for p in mont_factors for row in p)
    return dict(alignment=".p2align 5",
        montgomery_lambda_or_R_reference=mont_factors,
        montgomery_full_factor_and_companion_bytes_if_materialized=48*3*32*2,
        montgomery_selected_compact_lambda=dot_lambdas,
        montgomery_selected_companion=[[signed16(x*QINV) for x in row]
                                         for row in dot_lambdas],
        montgomery_selected_lambda_and_companion_bytes=48*32*2,
        montgomery_blend_immediates={"i1":0x11,"i2":0x33,"i3":0x77},
        montgomery_R_identity=centered(R),
        vpmaddwd_lambda=dot_lambdas,
        vpmaddwd_lambda_bytes=48*32,
        vpmaddwd_lambda_and_companion_bytes=48*32*2,
        vpmaddwd_lambda_companion=[[signed16(x*QINV) for x in row]
                                   for row in dot_lambdas],
        vpmaddwd_pair_masks=masks,
        vpmaddwd_pair_mask_bytes=16*32,
        vpmaddwd_degree_pair_pack_mask=degree_pair_pack_mask(),
        montgomery_routing_masks=mont_routing_masks,
        common_h_broadcast_r_rotate_masks_bytes=8*32,
        companion_rule="signed16(factor*12929 mod 65536), offline generated",
        companion_bytes_equal_factor_bytes=True)


def movement_ledger(terminal: dict, ingress: dict,
                    arithmetic: dict, packing: dict) -> dict:
    mont = arithmetic["montgomery_1packet"]["opcode_counts"]
    dot = arithmetic["vpmaddwd_1packet"]["opcode_counts"]
    pack = packing["per_packet_opcodes"]
    const_operand = {key:sum(1 for step in value["steps"]
                             if step["memory"] is not None and step["kind"]
                             not in ("data-load","data-store","add-m"))
                     for key,value in arithmetic.items()}
    # Source-derived structural counts. B3's 156-instruction loop is a
    # historical linked audit, not a cycle measurement or exact current
    # classification of every sub-opcode.
    return dict(unit="per Encap", multiplicity=dict(producer=2,
            h_decode=1, muladd=1, pack=2),
        current_M=dict(
            forward_terminal=dict(vpshufb=2*48, unpack_routes=2*96,
                                  stores=2*48),
            h_ingress=dict(decode_packets=48, AoS_to_M_transpose_routes=144),
            arithmetic=dict(B3_loops=12, B3_linked_loop_instructions_per_block=156,
                            product_Montgomery_chains=16*12,
                            lambda_Montgomery_chains=3*12,
                            R2_Montgomery_chains=4*12,
                            output_stores=48),
            separate_add_m=dict(c_reload=48, m_load=48, c_store=48, vpaddw=48),
            packing=dict(calls=2, packets=96, M_to_AoS_routes=2*12*12,
                         packet_vpermq=96, input_loads=96)),
        W_montgomery=dict(
            forward_terminal=dict(vpshufb=96, vpermq=96, stores=96),
            h_ingress=dict(decode_packets=48, decode_to_W_vpermq=48,
                           W_stores=48, extra_validation_passes=0),
            arithmetic=dict(packets=48, packet_opcodes=mont,
                expanded_packet_instructions=sum(mont.values()),
                full_arithmetic_instructions=48*sum(mont.values()),
                hot_body_instruction_model={"one_packet":sum(mont.values())+8,
                                            "two_packet":2*sum(mont.values())+8},
                runtime_product_Montgomery_chains=4*48,
                lambda_or_identity_Montgomery_chains=3*48,
                R2_Montgomery_chains=48,
                constant_memory_operands=48*const_operand["montgomery_1packet"],
                loop_address_instructions={"one_packet":48*8,"two_packet":24*8},
                peak_virtual_ymm={"one_packet":arithmetic["montgomery_1packet"]["liveness"]["peak_ymm"],
                                  "two_packet":arithmetic["montgomery_2packet"]["liveness"]["peak_ymm"]},
                add_m_fused=True, output_stores=48),
            packing=dict(calls=2, packets=96,
                         packet_opcodes=pack, expanded_instructions=96*sum(pack.values()))),
        W_vpmaddwd=dict(
            forward_terminal="same W terminal as W-Montgomery",
            h_ingress="same W ingress as W-Montgomery",
            arithmetic=dict(packets=48, packet_opcodes=dot,
                expanded_packet_instructions=sum(dot.values()),
                full_arithmetic_instructions=48*sum(dot.values()),
                hot_body_instruction_model={"one_packet":sum(dot.values())+7,
                                            "two_packet":2*sum(dot.values())+7},
                paired_dot_vectors=8*48, REDC32_vectors=4*48,
                lambda_Montgomery_chains=48, R2_Montgomery_chains=48,
                constant_memory_operands=48*const_operand["vpmaddwd_1packet"],
                loop_address_instructions={"one_packet":48*7,"two_packet":24*7},
                peak_virtual_ymm={"one_packet":arithmetic["vpmaddwd_1packet"]["liveness"]["peak_ymm"],
                                  "two_packet":arithmetic["vpmaddwd_2packet"]["liveness"]["peak_ymm"]},
                add_m_fused=True, output_stores=48),
            packing="same W pack as W-Montgomery"),
        interpretation=dict(
            representation_credit="terminal/decoder/pack routes removed, exact counts above",
            add_m_fusion_credit="48 c reloads + 48 c stores removed; m loads and 48 vpaddw remain",
            caution="W arithmetic handles 4 leaves per YMM vs M's 16; static instruction deltas are not cycle predictions"))


def caller_lifetimes() -> dict:
    return dict(
        scratch_bytes="reuse five aligned 1536-byte arrays h/r/m/c/work from clean encap_scratch",
        polynomial_sized_new_temporary_bytes=0,
        h=dict(first_write="PK decode+validation into h(W)",
               last_read="MulAdd h operand", mutable_after_validation=False),
        r=dict(first_write="r Forward terminal into r(W)",
               reads=["r pack/hash_g input", "MulAdd r operand"],
               last_read="MulAdd r operand", immutable=True),
        m=dict(first_write="m Forward terminal into m(W)",
               last_read="MulAdd addend", immutable=True),
        c=dict(first_use="frontend scratch for r/m Forward",
               last_frontend_read="m D1 terminal completed",
               first_MulAdd_write="after m Forward", last_read="ciphertext pack"),
        work=dict(reuse="CBD1 r, then SOTP m; never live as two polynomials"),
        invalid_pk=dict(order="decode/validate before hash_f, CBD1, Forward, or SOTP",
                        effect="same ct zero, ss clear, early return"),
        external_wire=dict(r_pack="ct temporary hash_g input; does not mutate r(W)",
                           c_pack="final 1152 ciphertext bytes"),
        alignment=dict(code=".p2align 5", constants=".p2align 5",
                       scratch="64-byte aligned", external_ct="unaligned stores"))


def verify_storage(packets: list[dict]) -> dict:
    poly_bytes = 1536
    regions = {name:(i*poly_bytes,(i+1)*poly_bytes)
               for i,name in enumerate(("h","r","m","c","work"))}
    assert all(regions[a][1] <= regions[b][0]
               for a,b in zip(regions, list(regions)[1:]))
    phases = dict(pk_decode=0,r_frontend=1,r_terminal=2,r_pack_hash=3,
                  sotp=4,m_frontend=5,m_terminal=6,muladd=7,c_pack=8)
    assert phases["r_terminal"] < phases["r_pack_hash"] < phases["muladd"]
    assert phases["m_frontend"] < phases["m_terminal"] < phases["muladd"]
    assert phases["m_terminal"] < phases["muladd"]  # c frontend dies first
    assert phases["pk_decode"] < phases["muladd"] < phases["c_pack"]
    for p in packets:
        addr = 256*p["forward_loop"]+p["rdi_loop_store_displacement"]
        assert addr == 32*p["packet"] and 0 <= addr <= poly_bytes-32
    # The existing vector pack intentionally overlaps four bytes of the
    # next packet. Replay byte ownership and ensure the final packet uses
    # 16+8+4 rather than an out-of-bounds second 16-byte store.
    byte_owner = [None]*1152
    for p in range(48):
        start = 24*p
        stores = [(start,16),(start+12,16)] if p < 47 else [
            (start,16),(start+12,8),(start+20,4)]
        for address,size in stores:
            assert 0 <= address and address+size <= 1152
            for byte in range(address,address+size):
                # Only 12 bytes from each packed 128-bit half are semantic.
                valid = (start <= byte < start+12) if address == start else (
                    start+12 <= byte < start+24)
                byte_owner[byte] = p if valid else None
    assert byte_owner == [byte//24 for byte in range(1152)]
    return dict(scratch_regions=regions, phase_order=phases,
        terminal_W_store_intervals_checked=48, wire_bytes_checked=1152,
        final_packet_store_sizes=[16,8,4], final_byte=1151,
        polynomial_sized_new_temporary_bytes=0,
        output_alias_contract="external ct does not overlap W scratch")


def quartic_reference(h: list[int], r: list[int], m: list[int], lam: int) -> list[int]:
    ordinary = [0] * 4
    for i in range(4):
        for j in range(4):
            ordinary[(i+j) % 4] += h[i]*r[j]*(lam if i+j >= 4 else 1)
    return [(ordinary[k] + m[k]) % Q for k in range(4)]


def dot_masks(group: int, part: str, pair: int) -> tuple[list[int], list[int]]:
    """Legal 128-bit-local VPSHUFB masks for 8 paired output coefficients."""
    assert group in (0, 1) and part in ("direct", "wrapped") and pair in (0, 1)
    masks = [[], []]
    for lane in range(8):
        quartic, degree = divmod(lane, 2)
        degree += 2 * group
        for slot in range(2):
            i = 2*pair + slot
            valid = (i > degree) == (part == "wrapped")
            for which, word in enumerate((4*quartic+i,
                                          4*quartic+(degree-i)%4)):
                # VPSHUFB controls are relative to the 128-bit half.
                if not valid:
                    masks[which].extend((0x80, 0x80))
                else:
                    assert word//8 == lane//4
                    masks[which].extend((2*(word%8), 2*(word%8)+1))
    assert all(len(x) == 32 for x in masks)
    return masks[0], masks[1]


def degree_pair_pack_mask() -> list[int]:
    # VPACKSSDW(g0,g1) is 128-bit lane-local. Per half the word order is
    # [q0.j0,q0.j1,q1.j0,q1.j1,q0.j2,q0.j3,q1.j2,q1.j3].
    words = (0, 1, 4, 5, 2, 3, 6, 7)
    mask = [byte for word in words for byte in (2*word, 2*word+1)] * 2
    src = list(range(16))
    assert apply_word_mask(src, mask) == [src[8*(j//8)+words[j%8]] for j in range(16)]
    return mask


def mont_masks(i: int) -> tuple[list[int], list[int]]:
    masks = [[], []]
    for word in range(16):
        leaf, j = divmod(word, 4)
        for which, source in enumerate((4*leaf+i, 4*leaf+(j-i)%4)):
            assert source//8 == word//8
            masks[which].extend((2*(source%8), 2*(source%8)+1))
    return masks[0], masks[1]


def apply_word_mask(words: list[int], mask: list[int]) -> list[int]:
    out = []
    for word in range(16):
        lo, hi = mask[2*word:2*word+2]
        assert lo == hi == 0x80 or hi == lo+1
        out.append(0 if lo == 0x80 else words[8*(word//8)+lo//2])
    return out


def simulate_mont_packet(h: list[int], r: list[int], m: list[int], lam: list[int]) -> list[int]:
    h_inputs, r_inputs = [], []
    for i in range(4):
        hm, rm = mont_masks(i)
        h_inputs.append(apply_word_mask(h, hm))
        r_inputs.append(apply_word_mask(r, rm))
    out = []
    for leaf in range(4):
        for j in range(4):
            acc = 0
            for i in range(4):
                product = mont(h_inputs[i][4*leaf+j], r_inputs[i][4*leaf+j])
                if i:
                    factor = lam[leaf] if i > j else centered(R)
                    product = mont(product, factor)
                acc += product
            out.append(mont(acc, signed16((R*R) % Q)) + m[4*leaf+j])
    return out


def simulate_dot_packet(h: list[int], r: list[int], m: list[int], lam: list[int]) -> list[int]:
    direct, wrapped = [0]*16, [0]*16
    for group in range(2):
        for part, target in (("direct", direct), ("wrapped", wrapped)):
            for pair in range(2):
                hm, rm = dot_masks(group, part, pair)
                hv, rv = apply_word_mask(h, hm), apply_word_mask(r, rm)
                for lane in range(8):
                    quartic, degree = divmod(lane, 2)
                    degree += 2*group
                    output = 4*quartic+degree
                    target[output] += hv[2*lane]*rv[2*lane] + hv[2*lane+1]*rv[2*lane+1]
    out = []
    for leaf in range(4):
        for j in range(4):
            k = 4*leaf+j
            value = mont(direct[k], 1) + mont(mont(wrapped[k], 1), lam[leaf])
            out.append(mont(value, signed16((R*R) % Q)) + m[k])
    return out


def mont_instructions(a: str, b: str, out: str, tag: str, *, fixed=False) -> list[dict]:
    """AVX2 signed-16 Montgomery data dependency, q as memory operand."""
    lo, hi, qlo = (f"{tag}_{x}" for x in ("lo", "hi", "qlo"))
    if fixed:
        return [op("vpmullw", [a], [lo], kind="montgomery", memory=f"{b}_qinv"),
                op("vpmulhw", [a], [hi], kind="montgomery", memory=b),
                op("vpmulhw", [lo], [qlo], kind="montgomery", memory="q"),
                op("vpsubw", [hi, qlo], [out], kind="montgomery")]
    return [op("vpmullw", [a, b], [lo], kind="montgomery"),
            op("vpmulhw", [a, b], [hi], kind="montgomery"),
            op("vpmullw", [lo], [qlo], kind="montgomery", memory="QINV"),
            op("vpmulhw", [qlo], [lo+"q"], kind="montgomery", memory="q"),
            op("vpsubw", [hi, lo+"q"], [out], kind="montgomery")]


def mont_blended_instructions(a: str, factor: str, companion: str,
                              out: str, tag: str) -> list[dict]:
    lo, hi, qlo = (f"{tag}_{x}" for x in ("lo", "hi", "qlo"))
    return [op("vpmullw", [a, companion], [lo], kind="montgomery"),
            op("vpmulhw", [a, factor], [hi], kind="montgomery"),
            op("vpmulhw", [lo], [qlo], kind="montgomery", memory="q"),
            op("vpsubw", [hi, qlo], [out], kind="montgomery")]


def redc32_instructions(source: str, out: str, tag: str) -> list[dict]:
    # m = signed16(low16(x*qinv)); REDC = high16(x)-high16(m*q).
    names = [f"{tag}_{i}" for i in range(6)]
    return [op("vpmulld", [source], [names[0]], kind="redc32", memory="QINV"),
            op("vpslld", [names[0]], [names[1]], kind="redc32"),
            op("vpsrad", [names[1]], [names[2]], kind="redc32"),
            op("vpmulld", [names[2]], [names[3]], kind="redc32", memory="q"),
            op("vpsrad", [names[3]], [names[4]], kind="redc32"),
            op("vpsrad", [source], [names[5]], kind="redc32"),
            op("vpsubd", [names[5], names[4]], [out], kind="redc32")]


def arithmetic_schedule(mode: str, packets: int) -> dict:
    """Instruction-model schedule using W-native quartic ownership."""
    assert packets in (1, 2) and mode in ("montgomery", "vpmaddwd")
    steps = []
    for p in range(packets):
        steps += [op("vmovdqu", [], [f"h{p}"], kind="data-load"),
                  op("vmovdqu", [], [f"r{p}"], kind="data-load")]
    if mode == "montgomery":
        # All 16 lanes are output coefficients. The i-th cyclic product
        # uses h_i broadcast inside each quartic and r_{j-i mod 4}; a
        # per-lane constant is lambda*R for j<i, R otherwise. This never
        # constructs four M degree planes, even transiently.
        for p in range(packets):
            steps += [op("vmovdqa", [], [f"lambda{p}"], kind="constant-load",
                         memory=f"lambda_W+{32*p}"),
                      op("vmovdqa", [], [f"lambdaq{p}"], kind="constant-load",
                         memory=f"lambda_qinv_W+{32*p}")]
        for i in range(4):
            for p in range(packets):
                tag = f"p{p}i{i}"
                steps += [op("vpshufb", [f"h{p}"], [tag+"h"],
                             kind="routing", memory=f"h_broadcast_mask_{i}"),
                          op("vpshufb", [f"r{p}"], [tag+"r"],
                             kind="routing", memory=f"r_rotate_mask_{i}")]
                steps += mont_instructions(tag+"h", tag+"r", tag+"prod", tag)
                result = tag+"prod"
                if i:
                    result = tag+"twisted"
                    blend = {1:0x11, 2:0x33, 3:0x77}[i]
                    factor, companion = tag+"factor", tag+"companion"
                    steps += [op("vpblendw", [f"lambda{p}"], [factor],
                                 kind="constant-routing", memory=f"R_identity_imm{blend}"),
                              op("vpblendw", [f"lambdaq{p}"], [companion],
                                 kind="constant-routing", memory=f"R_identity_qinv_imm{blend}")]
                    steps += mont_blended_instructions(tag+"prod", factor,
                                                       companion, result, tag+"lambda")
                if i:
                    steps.append(op("vpaddw", [f"acc{p}_{i-1}", result],
                                    [f"acc{p}_{i}"], kind="arithmetic"))
                else:
                    steps.append(op("vmovdqa", [result], [f"acc{p}_0"],
                                    kind="register-move"))
        for p in range(packets):
            steps += mont_instructions(f"acc{p}_3", "R2", f"scaled{p}",
                                        f"p{p}final", fixed=True)
            steps += [op("vpaddw", [f"scaled{p}"], [f"sum{p}"],
                         kind="add-m", memory=f"mW+{32*p}"),
                      op("vmovdqu", [f"sum{p}"], [], kind="data-store",
                         memory=f"cW+{32*p}")]
    else:
        # Process 8 output coefficients per YMM. Each output has direct
        # terms (i<=j) and wrapped terms (i>j). Two two-term vpmaddwd
        # rounds per part, with zero-padding masks where a part is short.
        # Four signed-i32 REDCs per packet precede lambda and R2.
        for half in range(2):
            for p in range(packets):
                for part in ("direct", "wrapped"):
                    for pair in range(2):
                        tag = f"p{p}h{half}{part}{pair}"
                        steps += [op("vpshufb", [f"h{p}"], [tag+"a"],
                                     kind="routing", memory=tag+"_hmask"),
                                  op("vpshufb", [f"r{p}"], [tag+"b"],
                                     kind="routing", memory=tag+"_rmask"),
                                  op("vpmaddwd", [tag+"a", tag+"b"], [tag+"dot"],
                                     kind="i32-dot")]
                        if pair:
                            steps.append(op("vpaddd", [f"p{p}h{half}{part}0dot",
                                                        tag+"dot"],
                                            [f"p{p}h{half}{part}sum"], kind="i32-add"))
                    steps += redc32_instructions(f"p{p}h{half}{part}sum",
                                                  f"p{p}h{half}{part}red",
                                                  f"p{p}h{half}{part}")
        for p in range(packets):
            for part in ("direct", "wrapped"):
                tag = f"p{p}{part}"
                steps += [op("vpackssdw", [f"p{p}h0{part}red", f"p{p}h1{part}red"],
                             [tag+"packed"], kind="routing"),
                          op("vpshufb", [tag+"packed"], [tag+"words"],
                             kind="routing", memory="pack_degree_pairs")]
            steps += mont_instructions(f"p{p}wrappedwords", f"lambda_{p}",
                                        f"twisted{p}", f"p{p}lambda", fixed=True)
            steps.append(op("vpaddw", [f"p{p}directwords", f"twisted{p}"],
                            [f"acc{p}"], kind="arithmetic"))
            steps += mont_instructions(f"acc{p}", "R2", f"scaled{p}",
                                        f"p{p}final", fixed=True)
            steps += [op("vpaddw", [f"scaled{p}"], [f"sum{p}"],
                         kind="add-m", memory=f"mW+{32*p}"),
                      op("vmovdqu", [f"sum{p}"], [], kind="data-store",
                         memory=f"cW+{32*p}")]
    model = replay(steps)
    assert model["peak_ymm"] <= 16
    return dict(mode=mode, packets=packets, steps=steps, liveness=model,
                physical_allocation=allocate_ymm(steps),
                dependency=dependency_stats(steps),
                instruction_class_counts=dict(Counter(x["kind"] for x in steps)),
                opcode_counts=dict(Counter(x["op"] for x in steps)),
        eligibility="virtual def/use pass; linked physical allocation not claimed")


def main() -> None:
    packets, owners = packet_map()
    prior = json.loads((ROOT/"generated/tile4_encap_packet_abi_gate.json").read_text())
    assert [x for block in prior["blocks"] for x in block["lambda_R"]] == [
        lam for packet in packets for lam in packet["lambda_mont"]]
    terminal = terminal_schedule(packets)
    decode = decode_schedule(packets)
    packing = pack_schedule()
    constants = constant_tables(packets)
    arithmetic = {f"{mode}_{n}packet": arithmetic_schedule(mode, n)
                  for mode in ("montgomery", "vpmaddwd") for n in (1, 2)}
    rng = random.Random(0x768091)
    valid = 0
    for _ in range(10003):
        h = [rng.randrange(Q) for _ in range(16)]
        r = [rng.randrange(-MAX_SMALL, MAX_SMALL+1) for _ in range(16)]
        m = [rng.randrange(-MAX_SMALL, MAX_SMALL+1) for _ in range(16)]
        # Actual lambda identity, never a synthetic arbitrary field element.
        packet = packets[rng.randrange(48)]
        lam = packet["lambda_mont"]
        expected = []
        for leaf in range(4):
            lambda_plain = lam[leaf] * pow(R, -1, Q) % Q
            expected += quartic_reference(h[4*leaf:4*leaf+4],
                                          r[4*leaf:4*leaf+4],
                                          m[4*leaf:4*leaf+4], lambda_plain)
        assert [x % Q for x in simulate_mont_packet(h,r,m,lam)] == expected
        assert [x % Q for x in simulate_dot_packet(h,r,m,lam)] == expected
        valid += 1
    ranges = range_ledger()
    arithmetic_max = {"montgomery":0,"vpmaddwd":0}
    boundary_cases = 0
    for packet in packets:
        lam = packet["lambda_mont"]
        for mode in range(12):
            h = [Q-1 if (j+mode)%3 else 0 for j in range(16)]
            r = [0]*16 if mode == 0 else [(-MAX_SMALL if (j+mode)&1 else MAX_SMALL)
                                            for j in range(16)]
            if 1 <= mode <= 4:
                r = [MAX_SMALL if j%4 == mode-1 else 0 for j in range(16)]
            m = [(-MAX_SMALL if (j+mode)&1 else MAX_SMALL) for j in range(16)]
            for name, fn in (("montgomery",simulate_mont_packet),
                             ("vpmaddwd",simulate_dot_packet)):
                vals = fn(h,r,m,lam)
                arithmetic_max[name] = max(arithmetic_max[name],max(map(abs,vals)))
                assert all(-32768 <= x <= 32767 for x in vals)
            boundary_cases += 1
    # Wire-byte and validation semantics, including q-1/q/4095 and a bad
    # coefficient in every packet, are independent of register layout.
    for bad in (Q, 4095):
        for packet_index in range(48):
            coefficients = [0]*768
            coefficients[16*packet_index+15] = bad
            encoded = encode_raw12(coefficients)
            decoded = decode_raw12(encoded)
            assert decoded == coefficients and max(decoded) >= Q
    boundary = [0]*768
    boundary[-1] = Q-1
    assert decode_raw12(encode_raw12(boundary)) == boundary
    assert max(boundary) < Q
    for _ in range(128):
        values = [rng.randrange(-32768,32768) for _ in range(768)]
        before = values[:]
        by_packet = b"".join(pack(values[16*p:16*p+16]) for p in range(48))
        assert by_packet == pack(values) and values == before and len(by_packet) == 1152
        canonical = [x%Q for x in values]
        assert decode_raw12(by_packet) == canonical
    provenance = {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): digest(p)
        for p in (ROOT/"tools/generate_encap_wire_schedule.py", ROOT/"tools/generate_tile4.py",
                  ROOT/"tools/generate_encap_packet_abi_gate.py",
                  ROOT/"generated/tile4_q24_codec.json", ROOT/"generated/tile4_encap_packet_abi_gate.json",
                  ROOT/"generated/tile4_encap_range_refined.json",
                  CLEAN/"ntt_m.s", CLEAN/"pack.s", CLEAN/"basemul.s", CLEAN/"encap.c")}
    clean_manifest = {str(p.relative_to(CLEAN)): digest(p) for p in sorted(CLEAN.rglob("*"))
                      if p.is_file() and "__pycache__" not in p.parts}
    ledger = movement_ledger(terminal, decode, arithmetic, packing)
    report = dict(schema="gt32-encap-wire-schedule-v1", branch="avx2-gt-ntt",
        scope="executable ownership and instruction-class schedule; no ASM or performance proof",
        frozen=dict(q=Q, montgomery_exponent=0, source_sha256=provenance,
                    clean_control="avx2-gt32-clean", clean_source_manifest=clean_manifest),
        validation=dict(owners=768, leaves=192, packets=48, blocks=12,
            packet_raw_mapping=True, scalar_quartic_random_cases=4*valid,
            arithmetic_boundary_packets=boundary_cases,
            arithmetic_boundary_max_abs=arithmetic_max,
            codec_random_polynomials=128, invalid_coefficient_packet_positions=96,
            decoder_valid_boundary=Q-1, decoder_invalid_boundaries=[Q,4095],
            last_wire_byte=1151, last_W_word=767, r_immutable_by_schedule=True),
        packets=packets, terminal=terminal, ingress=decode,
        arithmetic=arithmetic, packing=packing, range=ranges,
        constants=constants, ledger=ledger, caller_lifetimes=caller_lifetimes(),
        storage_proof=verify_storage(packets),
        decision="model schedules/ranges pass; exact linked allocation and performance remain unproven")
    out = ROOT/"generated/tile4_encap_wire_schedule.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print(out)
    print(report["decision"])


if __name__ == "__main__":
    main()
