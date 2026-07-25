# NTRU+768 NTT Consumer Code-Size Audit

Date: 2026-07-23

## Scope

This audit measures the linker-GC full-KEM closure, not the larger component
profiler closure. The binaries contain the complete keygen, encapsulation, and
decapsulation call graph because the deterministic decapsulation benchmark
setup creates a key pair and ciphertext before the measured call.

Build conditions:

```text
host: Raspberry Pi 5, AArch64 Linux
hash: portable NO_CE
compiler: GCC 14.2.0
flags: -ffunction-sections -fdata-sections -Wl,--gc-sections
benchmark mode: kem_dec
```

The three compared binaries are:

```text
KPQC: unmodified KPQC final
GT:   selected mixed-BPQ/CQ GT production
CQ:   default-off all-CQ keygen + shared generic/direct-CQ NTT
```

## Linked Size

| Variant | `.text` bytes | Data | BSS | `.text` delta vs GT |
|---|---:|---:|---:|---:|
| KPQC final | 23,098 | 744 | 4,880 | -66,656 |
| GT production | 89,754 | 744 | 4,880 | baseline |
| all-CQ shared NTT | 92,714 | 752 | 4,880 | +2,960 |

These numbers are lower than older non-uniform size reports because all three
variants use the same section-GC policy.

## Large GT Address Spans

Several generated assembly symbols do not carry complete ELF `.size`
annotations. The table therefore uses consecutive linker-map labels. Spans can
include alignment padding and embedded constants.

| GT production region | Address span bytes | Role |
|---|---:|---|
| canonical decap verify pointwise F2 | 11,984 | block-major gather, QSoA quartic products, QSoA output |
| canonical pack | 5,456 | GT block-major to protocol bytes |
| canonical unpack U1 | 4,400 | protocol bytes to GT block-major |
| forward NTT code | 14,776 | generic GT block-major endpoint |
| forward NTT tables | 3,264 | zetas, twist, NTT32 vectors |
| keygen CQ pack | 5,168 | CQ to protocol bytes |
| keygen BPQ P1 pack | 5,264 | BPQ to protocol bytes |
| rminus1 inverse NTT | 16,352 | inverse rows, post path, constants |
| rminus1 basemul | 368 | paired decapsulation product |
| encapsulation Q31 basemul-add | 816 | byte-contract product before canonical pack |

The selected KEM closure does not contain generic `poly_invntt`,
generic `poly_basemul`, generic `poly_basemul_add`, or generic
`poly_baseinv`. Those symbols are added by component-profiler builds.

## Why All-CQ Adds Only 2,960 Bytes

The shared generic/direct-CQ NTT region is larger:

```text
GT generic NTT code: 14,776 bytes
CQ dual-endpoint code: 24,416 bytes
delta:                 +9,640 bytes
```

But the all-CQ keygen removes several mixed-layout regions:

```text
block-major -> BPQ adapter
BPQ baseinv wrapper and prepare
BPQ x CQ basemul
BPQ P1 pack
```

It replaces them with smaller C/Neon CQ prepare and CQ x CQ basemul code while
retaining the shared hierarchical tree, CQ finish, CQ pack, and fqinv15.
Approximate address-span accounting is:

```text
mixed GT keygen-specific regions: 15,776 bytes
all-CQ keygen-specific regions:    9,072 bytes
keygen backend saving:            -6,704 bytes

larger dual-endpoint NTT:          +9,640 bytes
expected net:                     +2,936 bytes
observed linked .text delta:       +2,960 bytes
```

The 24-byte difference is alignment and surrounding call-graph code.

## Artifacts

```text
size.txt
kpqc.nm.txt
gt.nm.txt
cq.nm.txt
kpqc.nm-n.txt
gt.nm-n.txt
cq.nm-n.txt
consumer-size-kpqc.map
consumer-size-gt.map
consumer-size-cq.map
```
