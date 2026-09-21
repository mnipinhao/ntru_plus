#!/usr/bin/env python3
"""Lower the frozen W packet schedule to namespaced AVX2 research objects.

The clean sources are read as inputs only.  The output is deliberately kept
inside generated/ and never installed into a clean implementation.
"""
from __future__ import annotations

import json
from pathlib import Path

import generate_encap_wire_schedule as model

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT.parent.parent / "clean" / "avx2-gt32-clean"
OUT = ROOT / "generated"
PREFIX = "ntruplus768_wire_research_"


def fwd_source(packets: list[dict]) -> str:
    source = (CLEAN / "ntt_m.s").read_text()
    start = source.index(" .p2align 5\n .globl ntruplus768_ntt_m_avx2\n")
    end = source.index(" .macro FR_S45_W1\n", start)
    _, soa, _ = model.gt.serialized_mappings()
    actual = model.actual_d1_source_for_m()
    by_tile: dict[int,list[tuple[int,list[int]]]] = {i:[] for i in range(6)}
    for packet in range(48):
        source_words = [actual[soa[w]] for w in range(16*packet,16*packet+16)]
        assert all(source_words[4*j:4*j+4] == list(range(source_words[4*j],source_words[4*j]+4))
                   for j in range(4))
        assert len({x//16 for x in source_words}) == 2
        tile = source_words[0]//128
        assert all(x//128 == tile for x in source_words)
        by_tile[tile].append((packet,[source_words[4*j] for j in range(4)]))
    assert all(len(v)==8 for v in by_tile.values())
    s = [" .p2align 5", f" .globl {PREFIX}forward", f" .type {PREFIX}forward,@function",
         f"{PREFIX}forward:", " vmovdqa .Lfr_q(%rip), %ymm15", " xorl %ecx,%ecx",
         " .p2align 5", ".Lwire_forward_loop:"]
    s += [f" vmovdqu {32*i}(%rsi), %ymm{i}" for i in range(8)]
    s += [" FR_RAW_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7",
          " FR_MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_fwd_s2_qinv,.Ltile4_fwd_s2_factor",
          " FR_MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_fwd_s3_qinv,.Ltile4_fwd_s3_factor"]
    s += [f" FR_MONT_HALF_PAIR %ymm{2*i},%ymm{2*i+1},{32*i}" for i in range(4)]
    s += [f" FR_MONT_QWORD_PACKED %ymm{2*i},%ymm{2*i+1},{32*i}" for i in range(4)]
    # Public loop counter selects one of six fixed-immediate deposit blocks.
    # The arithmetic body is shared; all eight D1 outputs are still live here.
    s += [f" cmpl ${i},%ecx\n je .Lwire_terminal_{i}" for i in range(5)]
    s += [" jmp .Lwire_terminal_5"]
    for tile in range(6):
        s.append(f".Lwire_terminal_{tile}:")
        for packet,src in by_tile[tile]:
            vectors = sorted({x//16 for x in src})
            for temp,v in ((8,vectors[0]),(9,vectors[1])):
                qwords = [(word%16)//4 if word//16==v else 0 for word in src]
                imm = sum(q << (2*j) for j,q in enumerate(qwords))
                s.append(f" vpermq ${imm},%ymm{v%8},%ymm{temp}")
            mask=sum(3<<(2*j) for j,word in enumerate(src) if word//16==vectors[1])
            s += [f" vpblendd ${mask},%ymm9,%ymm8,%ymm10",
                  f" vmovdqu %ymm10,{32*packet-256*tile}(%rdi)"]
        s += [" jmp .Lwire_forward_next"]
    s += [".Lwire_forward_next:", " addq $256,%rsi", " addq $256,%rdi",
          " incl %ecx", " cmpl $6,%ecx", " jne .Lwire_forward_loop", " ret",
          f" .size {PREFIX}forward,.-{PREFIX}forward"]
    # Keep the exact clean macros and constants, but none of its exported
    # function definitions.  This also prevents symbol collisions in one ELF.
    head = source[:start]
    const_start = source.index(" .section .rodata\n", end)
    return head + "\n".join(s) + "\n" + source[const_start:]


def codec_source(packets: list[dict]) -> str:
    clean = (CLEAN / "pack.s").read_text()
    masks = clean[clean.index(".Lq24_decode_mask_0123:\n"):clean.index(" .section .text.gt32_q24_decode_aos_asm", clean.index(".Lq24_decode_mask_0123:\n"))]
    s = [" .text", " .p2align 5", f" .globl {PREFIX}decode",
         f" .type {PREFIX}decode,@function", f"{PREFIX}decode:",
         " vmovdqa .Lwire_low12(%rip),%ymm12", " vpxor %ymm8,%ymm8,%ymm8"]
    for p in packets:
        lo, hi = p["decode_load_offsets"]
        safe_lo, safe_hi = p["decode_safe_loads"]
        for offset, safe, dst in ((lo,safe_lo,"xmm14"),(hi,safe_hi,"xmm15")):
            if safe:
                s += [f" vmovq {offset}(%rsi),%{dst}",
                      f" vpinsrd $2,{offset+8}(%rsi),%{dst},%{dst}"]
            else:
                s += [f" vmovdqu {offset}(%rsi),%{dst}"]
        s += [" vinserti128 $1,%xmm15,%ymm14,%ymm0",
              f" vpshufb {p['decode_mask']}(%rip),%ymm0,%ymm0",
              " vpsrlw $4,%ymm0,%ymm14", " vpblendw $0xaa,%ymm14,%ymm0,%ymm0",
              " vpand %ymm12,%ymm0,%ymm0", " vpmaxuw %ymm0,%ymm8,%ymm8",
              f" vpermq ${p['vpermq_imm']},%ymm0,%ymm0",
              f" vmovdqu %ymm0,{32*p['packet']}(%rdi)"]
    s += [" vpcmpgtw .Lwire_qm1(%rip),%ymm8,%ymm8",
          " vpmovmskb %ymm8,%eax", " testl %eax,%eax", " setne %al",
          " movzbl %al,%eax", " ret", f" .size {PREFIX}decode,.-{PREFIX}decode",
          " .p2align 5", f" .globl {PREFIX}pack",
          f" .type {PREFIX}pack,@function", f"{PREFIX}pack:",
          " vmovdqa .Lwire_q(%rip),%ymm15", " vmovdqa .Lwire_v9(%rip),%ymm13",
          " xorl %ecx,%ecx", ".Lwire_pack_loop:",
          " vmovdqu (%rsi),%ymm0", " vpmulhrsw %ymm13,%ymm0,%ymm14",
          " vpmullw %ymm15,%ymm14,%ymm14", " vpsubw %ymm14,%ymm0,%ymm0",
          " vpsraw $15,%ymm0,%ymm14", " vpand %ymm15,%ymm14,%ymm14",
          " vpaddw %ymm14,%ymm0,%ymm0",
          " vpmaddwd .Lwire_pair_factor(%rip),%ymm0,%ymm0",
          " vpshufb .Lwire_pack_mask(%rip),%ymm0,%ymm0",
          " vmovdqu %xmm0,(%rdi)", " vextracti128 $1,%ymm0,%xmm14",
          " cmpl $47,%ecx", " je .Lwire_pack_tail",
          " vmovdqu %xmm14,12(%rdi)", " addq $32,%rsi", " addq $24,%rdi",
          " incl %ecx", " jmp .Lwire_pack_loop",
          ".Lwire_pack_tail:", " vmovq %xmm14,12(%rdi)",
          " vpextrd $2,%xmm14,20(%rdi)", " ret",
          f" .size {PREFIX}pack,.-{PREFIX}pack", " .section .rodata", " .p2align 5",
          ".Lwire_low12:", " .rept 16", " .short 4095", " .endr",
          ".Lwire_qm1:", " .rept 16", " .short 3456", " .endr",
          ".Lwire_q:", " .rept 16", " .short 3457", " .endr",
          ".Lwire_v9:", " .rept 16", " .short 9", " .endr",
          ".Lwire_pair_factor:", " .rept 8", " .short 1,4096", " .endr",
          ".Lwire_pack_mask:",
          " .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128",
          " .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128"]
    return "\n".join(s)+"\n"+masks+" .section .note.GNU-stack,\"\",@progbits\n"


def vec(name: str, values: list[int]) -> str:
    assert len(values) == 16
    return " .p2align 5\n" + name + ":\n .short " + ",".join(str(model.signed16(x)) for x in values) + "\n"


def muladd_source(packets: list[dict]) -> str:
    s = [" .text"]
    qinv = model.QINV
    identity = model.centered(model.R)
    identity_comp = model.signed16(identity*qinv)
    r2 = model.signed16(model.R*model.R % model.Q)
    r2comp = model.signed16(r2*qinv)

    def mont_product(hreg: int, rreg: int) -> list[str]:
        return [f" vpmullw %ymm{rreg},%ymm{hreg},%ymm8",
                f" vpmulhw %ymm{rreg},%ymm{hreg},%ymm9",
                " vpmullw .Lwire_qinv(%rip),%ymm8,%ymm8",
                " vpmulhw %ymm15,%ymm8,%ymm8",
                " vpsubw %ymm8,%ymm9,%ymm10"]

    def packet_step(p: int, degree: int) -> list[str]:
        h, r, acc = (0,1,4) if p == 0 else (2,3,5)
        hm, rm = model.mont_masks(degree)
        del hm,rm
        v = [f" vpshufb .Lwire_hmask_{degree}(%rip),%ymm{h},%ymm6",
             f" vpshufb .Lwire_rmask_{degree}(%rip),%ymm{r},%ymm7"]
        v += mont_product(6,7)
        if degree:
            imm = {1:0x11,2:0x33,3:0x77}[degree]
            v += [f" vpblendw ${imm},(%r9,%r8),%ymm13,%ymm11",
                  f" vpblendw ${imm},(%r10,%r8),%ymm14,%ymm12",
                  " vpmullw %ymm12,%ymm10,%ymm8",
                  " vpmulhw %ymm11,%ymm10,%ymm9",
                  " vpmulhw %ymm15,%ymm8,%ymm8",
                  " vpsubw %ymm8,%ymm9,%ymm10"]
        v += ([f" vmovdqa %ymm10,%ymm{acc}"] if degree == 0 else
              [f" vpaddw %ymm10,%ymm{acc},%ymm{acc}"])
        return v

    for npackets in (1,2):
        name = PREFIX + f"muladd_{npackets}"
        s += [" .p2align 5",f" .globl {name}",f" .type {name},@function",name+":",
              " vmovdqa .Lwire_q(%rip),%ymm15",
              " vmovdqa .Lwire_identity(%rip),%ymm13",
              " vmovdqa .Lwire_identity_comp(%rip),%ymm14",
              " leaq .Lwire_lambda(%rip),%r9",
              " leaq .Lwire_lambda_comp(%rip),%r10",
              " xorl %r8d,%r8d", ".Lwire_muladd_loop_"+str(npackets)+":",
              " vmovdqu (%rsi,%r8),%ymm0", " vmovdqu (%rdx,%r8),%ymm1"]
        if npackets == 2:
            s += [" vmovdqu 32(%rsi,%r8),%ymm2", " vmovdqu 32(%rdx,%r8),%ymm3"]
        for i in range(4):
            for p in range(npackets):
                if p:
                    s += [" addq $32,%r8"]
                s += packet_step(p,i)
                if p:
                    s += [" subq $32,%r8"]
        for p in range(npackets):
            if p:
                s += [" addq $32,%r8"]
            acc = 4 if p == 0 else 5
            s += [f" vpmullw .Lwire_r2comp(%rip),%ymm{acc},%ymm8",
                  f" vpmulhw .Lwire_r2(%rip),%ymm{acc},%ymm9",
                  " vpmulhw %ymm15,%ymm8,%ymm8",
                  " vpsubw %ymm8,%ymm9,%ymm9",
                  " vpaddw (%rcx,%r8),%ymm9,%ymm9",
                  " vmovdqu %ymm9,(%rdi,%r8)"]
            if p:
                s += [" subq $32,%r8"]
        s += [f" addq ${32*npackets},%r8", " cmpq $1536,%r8",
              " jne .Lwire_muladd_loop_"+str(npackets)," ret",
              f" .size {name},.-{name}"]
    s += [" .section .rodata",vec(".Lwire_q",[model.Q]*16),
          vec(".Lwire_qinv",[qinv]*16),
          vec(".Lwire_identity",[identity]*16),
          vec(".Lwire_identity_comp",[identity_comp]*16),
          vec(".Lwire_r2",[r2]*16),vec(".Lwire_r2comp",[r2comp]*16)]
    for i in range(4):
        hm,rm = model.mont_masks(i)
        s += [" .p2align 5",f".Lwire_hmask_{i}:\n .byte "+",".join(map(str,hm)),
              " .p2align 5",f".Lwire_rmask_{i}:\n .byte "+",".join(map(str,rm))]
    for label, companion in ((".Lwire_lambda",False),(".Lwire_lambda_comp",True)):
        s += [" .p2align 5",label+":"]
        for p in packets:
            values = [model.signed16(x*qinv) if companion else x for x in p["lambda_mont"]]
            s += [" .short "+",".join(str(x) for x in values for _ in range(4))]
    s += [" .section .note.GNU-stack,\"\",@progbits"]
    return "\n".join(s)+"\n"


def m_fused_control_source() -> str:
    source=(CLEAN/"basemul.s").read_text()
    original="TILE4_BASEMUL_B3_FUNCTION ntruplus768_basemul_general_m_avx2, TILE4_OUTPUT_SOA_LATE_RSQ,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA"
    assert source.count(original)==1
    source=source.replace(original,original.replace("TILE4_OUTPUT_SOA_LATE_RSQ,",
        "TILE4_OUTPUT_SOA_LATE_RSQ_ADD_M,"))
    macro_start=source.index(" .macro TILE4_BASEMUL_B3_FUNCTION name,output,inputa,inputb")
    macro_end=source.index(" .endm",macro_start)
    body=source[macro_start:macro_end]
    body=body.replace(" vmovdqa .Ltile4_bm_q(%rip), %ymm0",
                      " movq %rcx,%r10\n vmovdqa .Ltile4_bm_q(%rip), %ymm0",1)
    body=body.replace(" addq $128, %rdi", " addq $128, %rdi\n addq $128, %r10",1)
    source=source[:macro_start]+body+source[macro_end:]
    return source.replace("ntruplus768_","ntruplus768_wire_research_control_")


def main() -> None:
    report = json.loads((OUT / "tile4_encap_wire_schedule.json").read_text())
    packets = report["packets"]
    for name, body in (("forward",fwd_source(packets)),
                       ("codec",codec_source(packets)),
                       ("muladd",muladd_source(packets)),
                       ("m_add_control",m_fused_control_source())):
        path = OUT / f"encap_wire_{name}.S"
        path.write_text(body)
        print(path)
    _, soa, _ = model.gt.serialized_mappings()
    mapping = "#ifndef ENCAP_WIRE_MAP_H\n#define ENCAP_WIRE_MAP_H\n"
    mapping += "static const unsigned short wire_to_m[768] = {\n"
    mapping += "\n".join("  "+",".join(str(x) for x in soa[i:i+16])+"," for i in range(0,768,16))
    mapping += "\n};\n#endif\n"
    (OUT / "encap_wire_map.h").write_text(mapping)


if __name__ == "__main__":
    main()
