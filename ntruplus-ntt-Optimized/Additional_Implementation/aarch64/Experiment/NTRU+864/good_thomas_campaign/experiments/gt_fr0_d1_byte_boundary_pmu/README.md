# D1-P3B3 byte boundary implementation

Status: Pi5 correctness, GCC object audit and Cortex-A76 PMU passed. Select R9-A plus stock for ToBytes (1849.450 cycles) and direct C1 for FromBytes (1183.250 cycles). Production-shaped KEM integration remains pending.

Four complete paths are implemented in both directions: current scalar coordinate bridge plus stock API, R9-A plus stock API, C1 four-output pipelined lane gathers, and C2 two-TBL4 gathers. Direct paths do not allocate an Official or decoded 864-coefficient temporary. Forward normalizes gathered vectors before packing; reverse consumes arbitrary 12-bit encodings without mod-q normalization, preserving stock behavior.

Run `python3 run.py --local` for Apple arm64 correctness, or `python3 run.py` for the authorized Pi5 campaign. `make audit` replays the static model and checks local assembly. Generated tables, source closure manifest, assembly, binary and raw results live under ignored build/.

C1 uses lane-major order across four independent vector destinations. Public reverse byte offsets and shift counts are compile-time tables. C2 explicitly unfolds four source pairs so compilers can retain decoded vectors in registers. Both consume all address-generation costs in the complete benchmark.

Reverse C1 loads two bytes per requested coefficient and then shifts/masks vectors. Reverse C2 decodes eight source groups of twelve bytes per output. Thus P3B2's decoded-coefficient byte-traffic estimates are not the actual FromBytes traffic: the C2 implementation reads 10368 byte-array bytes per polynomial, plus public tables.

The PMU harness includes independent normalization and pack helpers for attribution. These are diagnostic costs, not presumed additive cycle identities. Winners were selected independently per direction: C1 ToBytes loses to R9-A by 15.68%, while C1 FromBytes beats R9-A by 2.33%. C2 loses both directions. Production-shaped KEM remains dependent on these results.

## Correction to P3B2

Connectivity of a 54x54 graph does not imply 54 simultaneous partial outputs. The generator now emits input-once witness orders and replays tags with immediate output retirement. The forward witness peaks at 16 partial output vectors; reverse at 14. One additional input vector plus lane-insert temporaries still requires concrete allocation, but the previously claimed 54-vector lower bound is disproved.

This witness is a routing-register model, not a fused pack/unpack implementation or performance result. It keeps factorized input-oriented routing open. C1/C2 are controls, not an exhaustive architecture search.

C2's bounded output-order search finds adjacent source-set overlap totals of
728 forward and 724 reverse, compared with 0/504 in natural order. C2 uses
these public orders and stores to exact destinations. These are opportunities,
not saved loads. All C2 loads remain; retaining vectors needs concrete
TBL-bank/register handling before savings can be credited.
