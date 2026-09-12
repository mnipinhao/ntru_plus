"""Render all measured call-site groups without mixing incompatible boundaries."""
import json
from pathlib import Path
P=Path(__file__).resolve().parent;r=json.loads((P/'results.json').read_text())
lines=['# P8 GT864 vs selected Official — 2026-09-12','',
 'GT frozen revision: `766cc844`. Official source: `/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`.',
 'Both use SHAKE256. This is a fresh common-harness comparison of that SUPERCOP source, not the SUPERCOP do-part aggregate report. Upstream-latest status remains unverified.',
 '', '## Clean full-KEM PMU', '', '| Operation | Official cycles | GT cycles | GT minus Official | GT change | Official / GT instructions |', '|---|---:|---:|---:|---:|---:|']
for op,d in r['clean_full_kem'].items():
    a=d['official'];b=d['gt']
    lines.append(f"| {op} | {a['cycles']['median']:.3f} | {b['cycles']['median']:.3f} | {d['gt_cycle_delta']:+.3f} | {d['gt_cycle_delta_percent']:+.2f}% | {a['instructions']['median']:.1f} / {b['instructions']['median']:.1f} |")
lines += ['', '252 clean observations per implementation/operation, six balanced AB/BA processes. Clean end-to-end values decide wins; profiling instrumentation is not included in this table.',
 '', '## Complete call-site profiler', '',
 'Cycles below are median net cycles per whole KEM operation, not per call. Parentheses give calls/operation. Measured read-pair overhead is subtracted per call. A dash means no separate call, not a zero-cost operation. Component medians do not necessarily sum to clean totals.',
 'P8 combines inverse and ternary; compare GT Inverse_to_ternary against Official Inverse + Crepmod3. Compare all ToBytes variants together.']
for op,d in r['call_site_profile'].items():
    lines += ['',f'### {op}', '', '| Component | Official cycles (calls) | GT cycles (calls) |', '|---|---:|---:|']
    for g in sorted(set(d['official'])|set(d['gt'])):
        cells=[]
        for v in ('official','gt'):
            x=d[v].get(g)
            cells.append(f"{x['net_cycles']['median']:.3f} ({x['calls']['median']:g})" if x else '—')
        lines.append(f'| {g} | {cells[0]} | {cells[1]} |')
    def n(v,g):return d[v].get(g,{}).get('net_cycles',{}).get('median',0)
    a=n('official','ToBytes_full');b=n('gt','ToBytes_full')+n('gt','ToBytes_small')
    lines += ['',f'ToBytes total (sum of group medians): Official **{a:.3f}**, GT **{b:.3f}**, gap **{b-a:+.3f}** cycles.']
    if op=='decaps':
        a=n('official','Inverse')+n('official','Crepmod3');b=n('gt','Inverse_to_ternary')
        lines += [f'Inverse + ternary: Official **{a:.3f}**, GT **{b:.3f}**, gap **{b-a:+.3f}** cycles.']
lines += ['', '## Interpretation / work ledger', '',
 '- Keygen: BaseInv costs GT an extra2036.875 cycles across two calls; aggregate ToBytes adds1222.625. Forward saves750 and R0 BaseMul saves533. P10 BaseInv remains important.',
 '- Encaps: ToBytes adds946.050 cycles; Forward saves752.850 and BaseMulAdd saves730. GT wins overall despite its routing cost.',
 '- Decaps: ToBytes adds952.525 and inverse+ternary adds826.050. Forward saves740.800, R0 BaseMul saves266, checked FromBytes saves97.250; R^-1 BaseMul is effectively tied.',
 '- Keep P9 ToBytes routing search next because it affects all three operations; keep P10 BaseInv queued. Do not reopen rejected P6 without its static savings gate. P8 is complete, not pending.',
 '- Inverse still has a real residual gap, but it is no longer the previously measured +2896-cycle single-component gap. Any further inverse experiment must preserve the P8 combined boundary and be separately scoped.',
 '- Hashing dominates absolute Encaps/Decaps time, but implementations share the backend and measured hash gaps are small. It is not the main GT-specific regression.',
 '', '## Provenance and validation', '',
 '- Pi5 Cortex-A76 core3; GCC14.2; both use -O3 -march=armv8-a+simd, PIC and identical link policy. Builds are fresh in `/home/pi/ntruplus-official-profile-p8-20260912`; source SUPERCOP tree is not modified.',
 '- Official kem.c/symmetric.c/api.h hashes match the previously selected baseline exactly. Full copied-tree and binary hashes, source/object lists and environment are in results.json.',
 '- GT manifest-check, 64 KEM/tamper cases and100-case KAT digest pass: `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.',
 '- Six clean processes each compare100 byte-exact cross-implementation KEM transcripts and100 tampered ciphertexts. All12 instrumented-versus-clean equivalence tests pass.',
 '- Clean:42 samples/process, inner counts4/20/20 for Keygen/Encaps/Decaps, five warmup samples. Profile:21 samples/process, same inner counts, three warmup samples;126 observations per group.',
 '- Governor ondemand; temperature60.9→63.1C; throttling remains0x0; no competing benchmark observed. PMU excludes kernel/hypervisor time.',
 '- Both harnesses provide the same deterministic RNG for reproducibility, not an OS entropy source. RNG call-site differences are instrumentation/compiler effects, not an entropy-service speed comparison.',
 '- Cleanup rows count KEM-level secure_clear only; internal assembly scratch/register clearing is included in each kernel. Matching call counts alone does not prove identical global cleanup policy.',
 '- Raw CSV, generated profiled source and build logs remain under ignored raw/ and build/, also retained in the isolated Pi directory. No production algorithm or priorities were silently changed.',
 '', '## Reproduce', '',
 'Run prepare.py locally to freeze GT766cc844, upload this directory without build/raw, then run pi_run.py on the Pi. The runner refuses existing output directories, checks Official hashes and GT manifest/KAT, and runs the six clean/profile rounds. Run summarize.py followed by report.py after collecting raw/ and build/environment.json.']
(P/'RESULTS.md').write_text('\n'.join(lines)+'\n')
