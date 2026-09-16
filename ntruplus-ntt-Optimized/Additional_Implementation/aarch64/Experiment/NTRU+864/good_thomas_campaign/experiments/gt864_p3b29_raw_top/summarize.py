#!/usr/bin/env python3
from pathlib import Path
import json,re,statistics,hashlib
H=Path(__file__).resolve().parent;B=H/'build';S=B/'sync'
f=json.loads((B/'forward.json').read_text())['measurements']
k=json.loads((B/'kem.json').read_text())
assert round(f['raw']['instructions']-f['t1']['instructions'])==-128
for op in ('keygen','encaps','decaps'):
    assert round(k['measurements'][op+'/raw']['instructions']-k['measurements'][op+'/t1']['instructions'])==-256
changes={str(p.relative_to(S/'t1')) for p in (S/'t1').rglob('*') if p.is_file() and p.read_bytes()!=(S/'raw'/p.relative_to(S/'t1')).read_bytes()}
assert changes=={'gt864_top_split.s','gt864_forward_poly_ntt.S','gt864_poly_api.c'},changes
asm=(S/'raw/gt864_top_split.s').read_text()
assert not re.search(r'^\s*(sqrdmulh|mls)\s',asm,re.M)
assert len(re.findall(r'^\s*mul\s',asm,re.M))==4
audit=(B/'raw/objects.log').read_text()
assert 'R_AARCH64_CALL26\tgt864_top_split_small_input' in audit
assert '<_gt864_forward_poly_ntt_small_input>' in audit
assert 'polynomial_product=pass' in (B/'raw/product.log').read_text()
lines=['# P3B29 — small-input raw-top result','','Decision: **accept as the experimental small-input Forward champion**.',
       'Production unchanged. T1 general-input baseline remains available. P3B6',
       'ToBytes is NOT integrated into this candidate; it still uses r9_to.',
       '', '## Correctness and scope','',
       '- P3B28 complete range proof rerun before generation.',
       '- 256 guard cases per Forward process: both allocation edges, disjoint/exact alias.',
       '- 64 Forward cases per process: T1/raw/SUPERCOP serialized bytes match.',
       '- 32 complete raw 2F + D1 BaseMul + Inverse products match schoolbook.',
       '- Full-KEM eight valid/tampered cases and instrumented equivalence pass before timing.',
       '- No claim of bit-exact intermediate representatives or general-input safety.',
       '', '## Forward paired PMU','',
       'Pi 5 Cortex-A76, GCC 14.2.0, CPU 3, three repetitions, both orders.',
       '61 samples/order, 400 calls/sample. Every timed call includes the same',
       'input reset; these are not pure NTT absolute timings.',
       '', '| Variant | cycles | instructions | branches |','|---|---:|---:|---:|']
for name in ('t1','raw','sc'):lines.append(f"| {name} | {f[name]['cycles']:.3f} | {f[name]['instructions']:.3f} | {f[name]['branches']:.3f} |")
lines+=['',f"Raw saves {f['t1']['cycles']-f['raw']['cycles']:.3f} cycles versus T1; remaining SUPERCOP gap is {f['raw']['cycles']-f['sc']['cycles']:.3f} cycles.",
        'SUPERCOP is the unchanged P3B25 source snapshot, upstream latest not verified.',
        '', '## Full-KEM paired PMU','','41 samples/API/order; keygen 4 iterations, encaps/decaps 20.',
        '', '| API | T1 | raw | delta cycles | delta instructions |','|---|---:|---:|---:|---:|']
for op in ('keygen','encaps','decaps'):
    a=k['measurements'][op+'/t1'];b=k['measurements'][op+'/raw']
    lines.append(f"| {op} | {a['cycles']:.3f} | {b['cycles']:.3f} | {b['cycles']-a['cycles']:+.3f} | {b['instructions']-a['instructions']:+.0f} |")
lines+=['','Per-repetition deltas, both orders pooled:','', '| Repetition | Forward | Keygen | Encaps | Decaps |','|---|---:|---:|---:|---:|']
for rep in range(3):
    rows={}
    for kind in ('forward','kem'):
        for order in (0,1):
            txt=(B/f'raw/{kind}-{rep}-{order}.log').read_text()
            for line in txt.splitlines():
                p=line.split(',')
                if p[0]=='forward':rows.setdefault(('forward',p[1]),[]).append(float(p[2]))
                if p[0]=='full':rows.setdefault((p[1],p[2]),[]).append(float(p[3]))
    deltas=[statistics.median(rows[op,'raw'])-statistics.median(rows[op,'t1']) for op in ('forward','keygen','encaps','decaps')]
    assert all(x<0 for x in deltas),deltas
    lines.append('| '+str(rep+1)+' | '+' | '.join(f'{x:+.3f}' for x in deltas)+' |')
lines+=['', '## Object audit and decision','',
        'Source delta is exactly top split plus two symbol-reference changes.',
        'Eight static instructions removed; top object 276 -> 244 bytes.',
        'Actual linked wrapper targets small_input. Four MULs remain per loop;',
        'no SQRDMULH or MLS remains in top. Loads/stores, register allocation and',
        'ABI save/restore are unchanged by construction; no spill is introduced.',
        'PMU agrees: -128 instructions/Forward, -256 per KEM, unchanged branches.',
        'No new Slothy run, layout change, or constant-setup cleanup was mixed in.',
        '', 'Reproduce: `python3 run.py --prepare`, `python3 run.py --run`,',
        '`python3 run.py --product`, `python3 summarize.py`.',
        'Exact source hashes, raw logs, object hashes and JSON metrics are in build/.',
        '', 'Next: combine the independently verified P3B6 ToBytes with this small-input',
        'Forward in a separate full-KEM candidate; do not add historical cycle gains',
        'and label the sum a measurement. General GT API and production stay unchanged.','']
(H/'results.md').write_text('\n'.join(lines))
(B/'source-hashes.json').write_text(json.dumps({str(p.relative_to(S)):hashlib.sha256(p.read_bytes()).hexdigest() for p in S.rglob('*') if p.is_file()},indent=2)+'\n')
print('source_delta=pass object=pass pmu_instruction_delta=pass all_repetition_gains=pass')
