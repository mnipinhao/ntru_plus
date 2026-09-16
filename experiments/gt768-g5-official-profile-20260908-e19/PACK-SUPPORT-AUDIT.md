# Production pack, support and residual-code audit

Source: aarch64-production ce617c87a39412958cddea17f10809fd2e0b3a3f.
Official: the same SHA256-pinned SUPERCOP 20260627 leaf as REPORT.md.
Read-only source/object audit. No production optimization or deletion performed.
Scalar instruction models/inventories are reproducible with audit_static.py;
results are in static-audit.json. Models are not a new assembly benchmark.

## Pack/unpack opportunities

The active Encap calls are poly_frombytes_encap, poly_tobytes_encap_loose(r),
poly_basemul_add_encap and poly_tobytes_encap(ciphertext). Exported kem.c.o call
relocations confirm them. Keygen uses poly_tobytes_keygen_cq; Decap uses the fused
decode/first-product, poly_frombytes_decap and poly_tobytes_decap.

Each polynomial has 768 signed-16 coefficients; bytes are 1152 canonical 12-bit
encodings. Reduced pack conditionally adds q to negative reduced representatives;
loose pack first reduces signed-16 representatives. Checked unpack decodes values
0..4095 and returns failure if any is >=3457, while materializing GT block-major order.

The Encap pack processes twelve 64-coefficient chunks. Each chunk gathers sixteen
64-bit quartic packets into eight q registers, then optionally reduces, corrects
sign, transposes and bitpacks to six output vectors. The frontend uses 192 d loads
and 96 lane-insert moves per call; all coefficient bytes are read once. This is not
a redundant second input pass. The compact core has 42 trn per chunk (504 dynamic),
24 sign-correction instructions and 16 bit-operation instructions, plus two stores.
The first transpose group and subsequent packing transpose are a concrete mapping
composition opportunity, but simply deleting a transpose changes output bytes.

The loose path adds eight sqdmulh/srshr/mls triplets per chunk (288 arithmetic
instructions per polynomial), twelve factor-vector loads and twelve mode checks.
96 triplets are real work; reducing raw output modulo q cannot simply be omitted.

Candidate A: scalar exhaustive proof confirms qhat=floor((9*x+16384)/32768),
r=x-3457*qhat gives residual [-3291,3291] for every signed-16 x. Thus the sequence
sqrdmulh with constant 9 followed by mls, then the existing negative correction,
produces exact canonical x mod q for all 65536 inputs. It can replace the three-
instruction quotient/reduction with two, saving 96 arithmetic instructions per
loose pack. Constants, liveness and concrete A76 schedule still need a candidate
gate. This alone is not a new performance finding; earlier instruction-reduction
experiments did not establish stable cycle wins. The meaningful reopen condition
is a bounded reduction-to-bitpack schedule, without full-core duplication.

Candidate B: give loose and reduced shared cores separate entry labels to remove
the per-chunk mode check; retain the compact bitpack body. Hoisting constants must
account for the core clobbering vector temporaries. This saves small control work,
not memory traffic, and needs full-path measurement. Same register names reused
for quotient temporaries do not by themselves prove a hardware dependency: A76
renaming must be distinguished from true producer/consumer chains.

Checked unpack is twelve unrolled chunks: total 504 trn, 96 value umax plus three
final merges, 96 output umov plus one status umov, and 192 64-bit stores. The check
already has four independent maximum chains and one final threshold/horizontal
check. Deleting canonical validation is not a legal speedup. The best target is
the decode-to-quartic output transpose and store tail.

Candidate C: keep exact decode/check/output contract; search direct decode-to-
quartic mapping to remove intermediate transpose edges. Model one 64-coefficient
chunk with unique lane IDs before assembly. Existing tail accounts for 24 trn per
chunk (288 total); this is a search budget, not a promised removable count.

Candidate D: replacing umov x9,vN.d[1]; str x9,[x0,#offset] by a lane store requires
a base register because st1 lane cannot encode the same arbitrary offset. A new
add plus st1 may merely trade instructions. Only accept if address bases are
amortized/reused and integer/vector transfer pressure actually decreases.

Do not transplant the earlier native-P/M compact pack blindly: that experiment
used a different Forward/basemul representation. P1 Slothy and P1.5 hot-fusion
records show modeled instruction savings can lose on Pi. Their rejection does
not establish that the current production block-major graph is optimal.

## add.s / support.S / decap_add.S

decap_add.S, after removing platform section directives and mapping its two entry
names back, is whitespace-normalized identical to Official add.s. The active
poly_sub_decap is the same subtraction instruction schedule, not a new algorithm.
Its sibling gt_decap_poly_triple has no current package caller.

support.S contains a separately scheduled poly_sub and poly_triple. Both traverse
1536 coefficient bytes in 192-byte stripes. Official triple is in-place with x0;
GT triple takes x0=out,x1=in. KEM Keygen passes the same buffer to both GT pointers.
GT poly_sub is not the current Decap subtraction call. GT support uses d8-d15
without preserving them: these are custom internal ABI helpers. kem_api.S saves
d8-d15 at public KEM boundaries; ABI tests mark these internal entries separately.
They must not be advertised as independently interchangeable AAPCS64 leaf APIs.

## crepmod3 is an arithmetic/contract difference

Official accepts [-q+1,q-1] and implements centered-mod-q then centered-mod-3.
It uses comparisons against +/-1728 to correct the value modulo 3 before a
sqrdmulh/MLS reduction. Since q=3457 is 1 mod 3, subtracting q is equivalent to
subtracting 1 for the final mod3 operation; adding q is equivalent to adding 1.

GT support directly computes centered mod3 with sqdmulh constant 21845,
srshr #1, mls by 3. It omits the q-centering correction and takes out/in pointers.
The versions agree on [-1728,1728], but not on all documented inverse outputs:

| x | GT | Official |
|---|---:|---:|
| -1729 | -1 | 0 |
| 1728 | 0 | 0 |
| 1729 | 1 | 0 |
| 2135 | -1 | 1 |

The active inverse in ntt.S labels its final range [-2135,2135]. Exhaustive scalar
models differ for 814 values in that interval. Therefore that range annotation
alone does not close the producer/consumer contract. Passing KAT does not prove
that the exceptional values cannot occur on valid decryptions or that all
affected malformed inputs are harmlessly rejected.

This is a verified helper-level semantic difference and unresolved full-Decap
contract question, not a demonstrated valid-ciphertext failure. Before reducing
more Decap arithmetic, prove the stronger reachable bound or test/restore the
Official-style centering with adversarial intermediate and full-path oracles.
The previous overview's description as mere support consolidation was incomplete.

## util.h / secure_clear.h

| Platform | Official | GT |
|---|---|---|
| Windows | SecureZeroMemory | SecureZeroMemory |
| glibc Linux (Pi) | explicit_bzero | explicit_bzero |
| Apple | explicit __APPLE__ branch calls memset_s | memset_s only when __STDC_LIB_EXT1__ is defined; otherwise volatile byte loop |
| Other Annex K platform | usually fallback loop | memset_s when __STDC_LIB_EXT1__ is defined |
| Other | volatile byte loop | volatile byte loop |

Official defines __STDC_WANT_LIB_EXT1__ on Apple and _DEFAULT_SOURCE on Linux before
including headers. GT instead provides an explicit glibc declaration, avoiding
include-order dependence under C99. The actual Mac branch depends on the SDK's
macro exposure; it is not justified to call the two Apple paths identical.

GT_SECURE_CLEAR_AUDIT_HOOK enables an after-clear callback that counts calls/bytes,
checks that memory is zero and notes expected buffer classes. It cannot prove
all secret copies/registers were cleared. It is enabled only for the Makefile
zeroization test. The measured package/export has no audit macro; e19 object
relocations call explicit_bzero with no audit callback. Thus no hook runtime
overhead is present in the published Pi benchmark. Clear coverage remains a
call-site question separate from helper implementation.

## Residual-code inventory

Strong removal candidates for the selected KEM package (definitions but no current
package/test caller found, and not selected by KEM object call relocations):

- ntt.S: gt_decap_reference_poly_ntt.
- decap_add.S: gt_decap_poly_triple (keep active poly_sub_decap).
- base.S: gt_decap_poly_basemul_scale, gt_decap_poly_basemul_add,
  gt_decap_poly_baseinv_1. Audit shared tables before deleting their storage.

Legacy chain not used by KEM but still explicitly exercised by ABI inventory:
decap_verify.c gt_decap_verify_predecoded_qsoa_to_bytes ->
base.S gt_decap_verify_pointwise -> support.S qsoa_tobytes;
qsoa_frombytes is also ABI-tested. These need an explicit library-scope decision;
move regression coverage with them rather than deleting tests to make removal pass.

Retain under the current public/test contract: poly_basemul, poly_invntt,
poly_ntt_encap_small (exact comparison endpoint), generic loose endpoint,
keygen/Encap lambda tables and all correctness tests. gt_rowbitrev_lambda is
referenced by active Encap basemul-add, so basemul_lambda.c is not dead.

Text-only residue: stale wave/module comments and unused SUPPORTS_SHAKE256_ASM
branch referencing CE/fips202.h, which is absent from the package. The production
Makefile does not enable that branch. check_release.py has a duplicate ntt.S set
entry; decap_verify.h references a retired helper name in a comment. These are
maintenance cleanup, not cycle savings.

The e19 SUPERCOP/profile link retains unused helpers. Some helpers have separate
ELF sections and can be garbage-collected by an appropriate link, while support.S
puts several helpers and constants in one .text section. Merely adding
-ffunction-sections does not split handwritten assembly. No claim is made that
all unused source contributes to every package build or that source deletion
necessarily yields faster hot-path cycles.
