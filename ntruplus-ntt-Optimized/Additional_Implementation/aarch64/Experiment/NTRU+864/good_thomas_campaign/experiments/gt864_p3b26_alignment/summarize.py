#!/usr/bin/env python3
from pathlib import Path
import json, re, statistics, hashlib
HERE=Path(__file__).resolve().parent
B=HERE/'build'
lines=['# P3B26 T1 alignment / P3B27 independent ToBytes integration','',
       'Decision: accept T1 as the experimental Forward baseline; accept P3B6 as',
       'a separately validated experimental full-KEM ToBytes replacement.',
       'Production unchanged. No combined T1+P3B6 result is claimed.',
       'T1 Keygen is noisy: one of three repetition medians regresses by 53.750',
       'cycles despite the pooled gain. The Forward/component result and all',
       'Encaps/Decaps repetitions support baseline selection; do not claim a',
       'repeatably fixed Keygen gain. P3B6 improves all APIs in all repetitions.','',
       'Pi 5 Cortex-A76, GCC 14.2.0, -O3 -march=armv8-a+simd, portable SHAKE256.',
       'Three repetitions, both execution orders, 41 samples/API/order; CPU 3.',
       'Eight valid/tampered KEM cases before each process; instrumented equivalence',
       'and cross-version public-key/ciphertext byte equality pass. No throttling.',
       'These are PMU measurements on frozen SUPERCOP sources, not native do-part/stq.',
       'SUPERCOP source snapshot is inherited from P3B25; upstream latest not verified.','']
for pair,title in [('gt-t1','P3B26: T1 only'),('gt-tb','P3B27: P3B6 ToBytes only'),('sc-t1','SUPERCOP versus T1 (old ToBytes retained)')]:
    s=json.loads((B/(pair+'.json')).read_text());a,b=pair.split('-')
    lines += ['## '+title,'','| API | baseline cycles | candidate cycles | delta | instruction delta |','|---|---:|---:|---:|---:|']
    for op in ('keygen','encaps','decaps'):
        x,y=s['full'][op+'/'+a],s['full'][op+'/'+b]
        lines.append(f"| {op} | {x['cycles']:.3f} | {y['cycles']:.3f} | {y['cycles']-x['cycles']:+.3f} | {y['instructions']-x['instructions']:+.0f} |")
    lines += ['','Per-repetition cycle deltas (both orders pooled):','']
    for rep in range(3):
        rows={}
        for order in (0,1):
            text=(B/f'raw/{pair}-{rep}-{order}.log').read_text()
            for line in text.splitlines():
                p=line.split(',')
                if p[0]=='full':rows.setdefault((p[1],p[2]),[]).append(float(p[3]))
        deltas=[statistics.median(rows[op,b])-statistics.median(rows[op,a]) for op in ('keygen','encaps','decaps')]
        lines.append(f'- Repetition {rep+1}: '+', '.join(f'{x:+.3f}' for x in deltas)+'.')
    lines+=['','Actual-caller component totals (cycles per KEM, not per call):','',
            '| API | component | baseline | candidate |','|---|---|---:|---:|']
    for op in ('keygen','encaps','decaps'):
        for comp in ('poly_ntt','poly_tobytes'):
            lines.append(f"| {op} | {comp} | {s['profile'][op+'/'+a+'/'+comp]:.3f} | {s['profile'][op+'/'+b+'/'+comp]:.3f} |")
    lines+=['']
s=json.loads((B/'forward.json').read_text())
lines+=['## Forward diagnostic','','Every timed call includes the same 1728-byte input reset. Do not label these',
        'absolute numbers pure NTT cycles or subtract reset-only cycles as an exact',
        'decomposition. 64 inputs in [-3,4], including all -3 and all +4: T0/T1',
        'raw output bit equality and SUPERCOP/GT serialized output equality pass.',
        '61 samples/order, 400 calls/sample, three repetitions.','',
        '| Variant | cycles including reset | instructions | branches |','|---|---:|---:|---:|']
for k,v in s.items():lines.append(f"| {k} | {v['cycles']:.3f} | {v['instructions']:.3f} | {v['branches']:.3f} |")
lines+=['',f"T1 saves {s['gt']['cycles']-s['t1']['cycles']:.3f} cycles versus T0, but remains {s['t1']['cycles']-s['sc']['cycles']:.3f} cycles above SUPERCOP at this common boundary.",
        '', '## Source and object audit','',
        'The T1 wrapper actually calls gt864_tail_layout_bank_major_inplace then',
        'gt864_forward_six_bank_pass2_a1_t1. Tail preparation is included.',
        'The P3B27 byte wrapper actually jumps to gt864_fr0_input_once_tobytes;',
        'FromBytes remains gt864_fr0_cluster_transpose_frombytes.',
        'The P3B6 target object stack accesses are limited to d8-d15 ABI saves',
        'and the outer x29/x30 frame: no coefficient-vector spills or scratch.',
        'Retired instruction savings are 1700 per ToBytes under this full-KEM',
        'build, not the old isolated result of 1591; do not reuse old object counts.',
        '', '## Remaining Forward gap: next algebra/range gate','',
        'SUPERCOP fuses levels 0/1/2 before its first coefficient store and uses',
        'a raw -722 multiplication at level 0 under its [-3,4] input contract.',
        'GT top split retains 64 vector Algorithm-10 products (four per iteration',
        'times sixteen). Replacing only their reductions would remove 128',
        'arithmetic instructions, not merely load encodings. This is NOT implemented.',
        'For low,high in [-3,4], raw alpha output low-722*high lies in',
        '[-2891,2170], beta output low+723*high in [-2172,2896]. Local int16 fit',
        'does not prove the subsequent NTT16/one-product NTT9/M5C/M5E chain.',
        'The next gate must verify all KEM input producers and re-close that chain',
        'before changing the general GT kernel or claiming a cycle improvement.',
        'The remaining roughly 929-instruction measured boundary gap also includes',
        'Pass-2 arithmetic/routing and wrapper differences; top reduction alone',
        'cannot explain it. No cycle attribution is inferred from instruction count.',
        '', 'Raw evidence, profiler details and exact hashes: build/raw/,',
        'build/*-*.json, build/source-hashes.json. No combined candidate has been run.','']
(HERE/'results.md').write_text('\n'.join(lines))
# Source-delta gate: unchanged files really are identical to the frozen bundle.
root=B/'sync'
expected={'t1':{'gt864_forward_poly_ntt.S','gt864_forward_six_bank.S'},'tb':{'byte_api.c'}}
for variant,allowed in expected.items():
    changed={str(p.relative_to(root/'gt')) for p in (root/'gt').rglob('*') if p.is_file() and p.read_bytes()!=(root/variant/p.relative_to(root/'gt')).read_bytes()}
    assert changed==allowed,(variant,changed)
audit=(B/'raw/objects.log').read_text()
assert 'R_AARCH64_CALL26\tgt864_tail_layout_bank_major_inplace' in audit
assert 'R_AARCH64_CALL26\tgt864_forward_six_bank_pass2_a1_t1' in audit
assert 'R_AARCH64_JUMP26\tgt864_fr0_input_once_tobytes' in audit
body=audit.split('tb/input_once_tobytes.o:')[1]
stack=[line for line in body.splitlines() if '[sp' in line]
assert len(stack)==10 and all(re.search(r'\b(?:stp|ldp)\s+(?:d(?:8|10|12|14)|x29),',line) for line in stack),stack
hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
(B/'source-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
print('source_delta_gate=pass target_call_gate=pass P3B6_no_spill_gate=pass')
