#!/usr/bin/env python3
"""Render the measured API and actual-caller component ledgers."""
from pathlib import Path
import json,csv
HERE=Path(__file__).resolve().parent
def main():
 s=json.loads((HERE/'build/summary.json').read_text());full=s['full'];prof=s['profile']
 lines=['# P3B25 — SUPERCOP-source versus frozen GT P3B23','',
 'Baseline: `/home/pi/supercop-20260627/crypto_kem/ntruplus864/aarch64`.',
 '**SUPERCOP installed/imported version; upstream latest not verified.**',
 'This checkout was reimported. Its import source directory is `import/ntruplus-20260723`,',
 'whose clean local HEAD is `0c249d5828b90e8dd5de2c8405323d5ee2a0ce41`',
 '(2026-07-25, Clear low-level cryptographic scratch state). The directory name',
 'and SUPERCOP archive date are not an upstream-latest claim. Exact installed',
 'source hashes are saved in `source-hashes.json`; the imported files include',
 'SUPERCOP integration edits and should be identified by those hashes.',
 '', 'Both use SHAKE256 and portable NO_CE Keccak on Pi5 Cortex-A76 core 3,',
 'GCC 14.2.0, `-O3 -march=armv8-a+simd -fPIC`. Each implementation is bound',
 'locally in its own shared object with `-Bsymbolic`; this preserves differing',
 'API signatures and prevents cross-version symbol interposition. RNG is the',
 'same deterministic xorshift benchmark RNG, not system entropy. These are',
 '**PMU measurements of SUPERCOP sources, not native SUPERCOP do-part/stq results**.',
 'GT is frozen P3B24: r9_to ToBytes, P3B23 FromBytes, existing Forward/D1/Inverse.',
 '', '## Uninstrumented full KEM', '',
 '| API | SUPERCOP cycles | GT cycles | GT minus SUPERCOP | Relative |',
 '| --- | ---: | ---: | ---: | ---: |']
 for op in ('keygen','encaps','decaps'):
  a=full[op+'/supercop']['cycles'];b=full[op+'/gt_p3b23']['cycles'];lines.append(f'| {op} | {a:.3f} | {b:.3f} | {b-a:+.3f} | {(b/a-1)*100:+.2f}% |')
 lines += ['', 'Three repetitions, both execution orders, 41 samples per API/order.',
 'Independent valid/tampered KEM correctness passes eight deterministic cases;',
 'public keys and ciphertexts also match across versions on those cases.',
 'Normal/instrumented outputs are separately checked for equivalence.',
 '', '## Actual KEM component profiler', '',
 'Values below are **total cycles per KEM call**, not cycles per primitive.',
 'The profiler redirects only direct calls made by kem.c; it does not count',
 'internal hash/NTT callees a second time. It uses actual valid caller inputs',
 'and a fixed no-retry keygen sample. Full Keygen averages four RNG seeds.',
 'The empty measurement boundary is about 67 cycles and is subtracted per',
 'call. Instrumentation changes code layout/cache state, so components are',
 'diagnostic estimates. They must not be forced to sum to uninstrumented PMU.',
 'Negative residuals below quantify this perturbation, not negative work.',
 'A dash means that version does not call that symbol.', '']
 csvrows=[]
 for op in ('keygen','encaps','decaps'):
  lines += [f'### {op}', '', '| Component | SC calls | SC cycles | GT calls | GT cycles |','| --- | ---: | ---: | ---: | ---: |']
  sums=[0.,0.]
  for name in sorted({k.split('/')[2] for k in prof if k.startswith(op+'/')}):
   values=[]
   for i,v in enumerate(('supercop','gt_p3b23')):
    r=prof.get('/'.join((op,v,name)));values.extend([','.join(map(str,r['calls'])) if r else '—',f"{r['cycles']:.1f}" if r else '—']);sums[i]+=r['cycles'] if r else 0
    if r:csvrows.append([op,v,name,'/'.join(map(str,r['calls'])),r['cycles']])
   lines.append('| '+name+' | '+' | '.join(values)+' |')
  lines += [f'| Component sum | | {sums[0]:.1f} | | {sums[1]:.1f} |',f"| Full minus component sum | | {full[op+'/supercop']['cycles']-sums[0]:+.1f} | | {full[op+'/gt_p3b23']['cycles']-sums[1]:+.1f} |",'']
 lines += ['## Interpretation and contract differences','',
 'The installed SUPERCOP version validates canonical encodings in FromBytes;',
 'GT P3B23 preserves all 12-bit representatives without the same rejection',
 'check. Its FromBytes advantage therefore compares different validation work.',
 'Valid ciphertext timing is reported; malformed-input latency/semantics are',
 'not declared equivalent. SUPERCOP Decaps uses one BaseMul and one',
 'BaseMul_scale paired with InvNTT_scale; GT uses two D1 BaseMuls and its',
 'existing Inverse API. Compare the complete pair, not just the normal BaseMul.',
 'GT BaseInv includes the coordinate bridges required by its representation.',
 'ToBytes remains r9_to; the isolated P3B6 ToBytes was not substituted.',
 '', 'Keygen is dominated by the BaseInv gap; Decaps by Inverse and ToBytes.',
 'Forward is now slower than this SUPERCOP baseline, reversing the older',
 'repository-baseline conclusion. Production was not changed.',
 '', '## Reproduction','',
 '1. Fetch the named SUPERCOP aarch64 directory plus cryptoint/crypto_uint64.h',
 '   into build/official-source. Preserve source-hashes.json identity.',
 '2. Run python3 prepare.py using the frozen P3B24 build/sync bundle.',
 '3. Sync build/sync to /home/pi/ntruplus-experiments/gt864-p3b25-supercop-profile.',
 '4. Run make -j4 there; run ./bench --check-only for correctness.',
 '5. Run python3 run_pi5.py and python3 summarize.py locally.',
 'Raw PMU, object audit and environment provenance are under build/raw.', '']
 (HERE/'results.md').write_text('\n'.join(lines))
 with (HERE/'components.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['API','variant','component','calls','cycles_per_KEM']);w.writerows(csvrows)
 source=HERE/'build/official-source';import hashlib
 (HERE/'source-hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.iterdir()) if p.is_file()},indent=2)+'\n')
if __name__=='__main__':main()
