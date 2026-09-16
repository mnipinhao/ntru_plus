"""Persist clean PMU and six-process component medians, retaining raw timing."""
import pathlib, sys, json, statistics as s, subprocess
p = pathlib.Path(sys.argv[1])
out = pathlib.Path(__file__).resolve().parent
full = json.loads(subprocess.check_output([sys.executable, out/'summarize-integrated.py', p]))
profile = {}
for variant in ['official', 'gt']:
    batches = {}
    for n in range(6):
        rows = {}
        for line in (p/f'profile-{variant}-{n}.csv').read_text().splitlines():
            c = line.split(',')
            if c[0] != 'profile': continue
            key = c[1]+':'+c[3]
            rows.setdefault(key, []).append(list(map(float, c[4:])))
        for key, values in rows.items():
            assert len(values) == 21
            batches.setdefault(key, []).append([s.median(v[i] for v in values) for i in range(3)])
    profile[variant] = {k: dict(zip(['raw_cycles', 'corrected_cycles', 'calls'],
        [s.median(v[i] for v in values) for i in range(3)])) for k, values in batches.items()}
result = {'full_kem': full, 'profile': profile,
    'environment': json.loads((p/'environment.json').read_text()),
    'profile_binaries': json.loads((p/'profile-hashes.json').read_text()),
    'warning': 'Component timings are instrumented estimates, not additive clean full-KEM cycles. RNG is deterministic benchmark RNG.'}
(out/'checked-profile-results.json').write_text(json.dumps(result, indent=2)+'\n')
lines = ['# NTRU+864 checked FromBytes / KEM rejection gate — 2026-09-08', '',
 '## Scope and correctness', '',
 'Production now decodes FR0 and reports any 12-bit coefficient >= 3457. The checker does not reduce invalid values modulo q. A fixed 864-coefficient unsigned maximum scan adds one 1728-byte coefficient read pass after decoding.', '',
 'Encaps rejects noncanonical pk with return 1 and zero ct/ss. Decaps checks ct, then sk-f, then sk-hinv, rejecting with return 1 and zero ss. The order and RNG consumption match the selected Official implementation. This is explicit rejection, not an implicit-rejection fallback secret.', '',
 'Legacy CBD/SOTP/add/crepmod3 helpers clobbered d8-d15. Six public ABI wrappers now save/restore these registers; arithmetic is unchanged. The all-position differential test exposed caller-state corruption before this fix and passes afterward. No separate six-helper ABI sentinel suite was added.', '',
 '- Mac: 64 KEM round trips/tampered cases and 100 KAT cases passed.',
 '- Pi: fresh make check, 100 byte-exact Official KAT cases; BaseInv 808 cases including failure/alias/canary/ABI/wipe; Inverse 256 inputs plus 256 R^-1 multiplication chains passed.',
 '- Checked decoder: all 4096 uniform encodings, and q-1/q at all 864 wire positions passed.',
 '- Rejection: 10368 pk/ct/sk-f/sk-hinv boundary cases passed, comparing status, output clearing, input preservation and RNG consumption.',
 '- All 79 crafted noncanonical x+q ciphertext cases now agree with Official; old GT disagreed in all 79.', '',
 '## Exact comparison baseline', '',
 '`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64` (SHAKE256); not independently verified as upstream latest. Official sources copied without arithmetic edits. Source and binary hashes are in checked-profile-results.json.', '',
 'Standalone equal-policy GCC 14.2 -O3 -march=armv8-a+simd builds, not a complete SUPERCOP compiler sweep. Pi 5 CPU3, six processes, alternating AB/BA order, 41 samples per process, 4 Keygen or 20 Encaps/Decaps calls per sample. Median of process medians. Governor ondemand; no throttling reported. RNG is the deterministic harness RNG, not OS entropy acquisition.', '',
 '## Clean full-KEM PMU', '', '| Operation | Official cycles | GT cycles | GT change |', '|---|---:|---:|---:|']
for op in ['keygen','encaps','decaps']:
    v=full['official->gt:'+op]
    lines.append(f"| {op} | {v['baseline_cycles_instructions_branches'][0]:.2f} | {v['gt_cycles_instructions_branches'][0]:.2f} | {v['cycle_change_percent']:+.2f}% |")
lines += ['', 'Relative to the old unchecked integrated GT, costs changed by about +13 Keygen, +471 Encaps and +1203 Decaps cycles. This includes validation, cleanup and ABI restoration, not just the maximum scan.', '',
 '## Component profiler', '', 'Cycles below are per full KEM invocation, summed across calls of that component. Empty-probe overhead is subtracted. Arithmetic objects are shared with the clean build; only KEM call sites are instrumented. Instrumented/clean output equivalence passed. These are diagnostic estimates: instrumentation changes caller code, cache and register pressure, so they must not be summed as exact clean full-KEM cycles. Raw values are retained in JSON/CSV.', '']
for op in ['keygen','encaps','decaps']:
    lines += ['### '+op, '', '| Component | Official calls | GT calls | Official cycles | GT cycles |', '|---|---:|---:|---:|---:|']
    for key in sorted(set(profile['gt']) | set(profile['official'])):
        if not key.startswith(op+':'): continue
        a=profile['official'].get(key, {}); b=profile['gt'].get(key, {})
        lines.append(f"| {key.split(':')[1]} | {a.get('calls',0):g} | {b.get('calls',0):g} | {a.get('corrected_cycles',0):.1f} | {b.get('corrected_cycles',0):.1f} |")
    lines.append('')
lines += ['## Interpretation and limitations', '',
 '- Keygen: BaseInv is the largest GT-specific deficit (~7259 cycles across two calls). ToBytes total is ~4785 versus ~3336. Forward and D1 multiplication recover part of the gap.',
 '- Decaps: Inverse is the largest deficit (~3125 cycles). ToBytes total adds ~1089 and three checked FromBytes calls add ~440 relative to Official. The R^-1 BaseMul alone is essentially tied.',
 '- Encaps: Forward and BaseMulAdd gains narrowly offset the more expensive byte boundaries. A 0.62% full-KEM lead is small and should not be treated as a broad performance win.',
 '- Next priorities: BaseInv, Inverse, then ToBytes routing/scratch. Integrate validity aggregation into the existing FromBytes producer later to remove its extra coefficient scan without changing rejection.',
 '- Cleanup policy is not fully equal: Official Keygen has seven directly profiled clear calls, current GT Keygen has none. This turn closes decoding/rejection, not all secret-erasure parity. Hash-internal clearing is inside hash timings. KAT/rejection success is not a proof of constant-time behavior.', '',
 '## Reproduction / artifacts', '',
 'Pi workspace: `/home/pi/ntruplus-experiments/gt864-checked-profile-20260908.jbWPzF`.',
 'Run `pi-integrated.py --checked` then `pi-profile.py` inside that isolated source package (requires its frozen old/ baseline). Local evidence: `build/checked-profile/`; summarization: `summarize-checked-profile.py build/checked-profile`. Production source changes are in byte_api.c, gt864_frombytes.h, kem.c, gt864_secure_clear.h, gt864_support_abi.S and Makefile.', '']
(out/'CHECKED-PROFILE-RESULTS.md').write_text('\n'.join(lines))
for op in ['keygen', 'encaps', 'decaps']:
    print('\n'+op+' (cycles per KEM, overhead corrected)')
    for key in sorted(set(profile['gt']) | set(profile['official'])):
        if not key.startswith(op+':'): continue
        a=profile['official'].get(key, {}); b=profile['gt'].get(key, {})
        print(f"{key.split(':')[1]:22s} {a.get('corrected_cycles',0):9.1f} {b.get('corrected_cycles',0):9.1f} calls {a.get('calls',0):g}/{b.get('calls',0):g}")
