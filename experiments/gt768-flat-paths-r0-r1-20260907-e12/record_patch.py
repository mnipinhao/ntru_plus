#!/usr/bin/env python3
"""Print persistent inventory/verification summaries as an apply_patch proposal."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
pi = json.loads((root / '.build/pi/audit.json').read_text())
mac = json.loads((root / '.build/mac-audit/audit.json').read_text())
finish = json.loads((root / '.build/pi/finish-summary.json').read_text())
mapping = json.loads((root / 'path-and-include-map.json').read_text())
assert pi['objects_equal'] and mac['objects_equal'] and finish['cleanup_equal']
assert all(x['runtime_sections_equal'] for x in finish['binaries'])
assert all(a['baseline']['source_sha256'] == b['baseline']['source_sha256']
           for a, b in zip(pi['units'], mac['units']))
lines = ['# R0 source/object/reference inventory', '',
         'Baseline: `d598969f830090de33ca9cc2462e102b668e437e`.', '',
         'This is a conservative inventory, not authorization to delete uncalled symbols.',
         'Object undefined references, local textual references and linked root membership are distinct.',
         'The ABI fixture deliberately retains more symbols than the three KEM roots.', '',
         '## Path map (32 files; no functions renamed)', '', '| Before | After |', '|---|---|']
lines += [f'| `{old}` | `{new}` |' for old, new in sorted(mapping['mapping'].items())]
lines += ['', '## Ordered 28-unit source closure', '',
          'Definitions include weak aliases; names beginning `_` are retained platform aliases.',
          'Undefined names are per-object dependencies, not unresolved final-link failures.', '']
for i, unit in enumerate(pi['units']):
    definitions = [x for x in unit['candidate']['definitions'] if x.split()[-2].isupper()]
    data = [x for x in unit['candidate']['definitions'] if x.split()[-2] in 'rRdDbB' and not x.split()[-1].startswith('.')]
    lines += [f'### {i:02d}: `{unit["old"]}` → `{unit["new"]}`', '',
              '- Exported definitions: ' + ', '.join('`' + x.split()[-1] + '` (' + x.split()[-2] + ')' for x in definitions),
              '- Named data symbols: ' + (', '.join('`' + x.split()[-1] + '`' for x in data) or '(none; inline .text tables are indexed below)'),
              '- Undefined references: ' + (', '.join('`' + x.split()[-1] + '`' for x in unit['candidate']['undefined']) or '(none)'), '']
lines += ['## Explicit local assembly label/reference index', '',
          'Includes code labels and inline data labels: do not assume symbol type `t` means code.',
          'Line numbers refer to the baseline source; all assembly bytes are unchanged.',
          'Macro-expanded/generated assembler labels are additionally captured by the object symbol/relocation audit.', '',
          '| Source | Label | Definition line | Same-file textual reference lines |', '|---|---|---:|---|']
for label in pi['local_label_reference_index']:
    lines.append(f'| `{label["source"]}` | `{label["label"]}` | {label["line"]} | ' + ', '.join(map(str,label['same_file_text_refs'])) + ' |')
lines += ['', '## Linked KEM roots: surviving project symbols', '',
          'Built with the three public KEM entrypoints rooted by the six-path fixture and `--gc-sections`.',
          'Presence may reflect sharing an indivisible assembly section, not direct call reachability.', '', '```text']
for symbol in finish['linked_kem_root_symbols']:
    fields = symbol.split()
    if fields and (fields[-1].startswith(('gt_', '_gt_', 'poly_', '_poly_', 'crypto_kem_', 'hash_', 'shake256'))):
        lines.append(symbol)
lines += ['```', '', '## Relocation reference graph', '',
          'Cross-object call/jump/data edges are retained in `reference-graph.json`.',
          'Owner names are objdump symbol anchors, not a proof of exact intra-section ownership.',
          'Local PC-relative tables can have no relocation: use the label index above as well.', '']
summary = {
    'experiment_id': 'gt768-flat-paths-r0-r1-20260907-e12',
    'baseline_revision': 'd598969f830090de33ca9cc2462e102b668e437e',
    'candidate_revision': '739e0472ab6545fcad2264815dbd7cf85cc736d2',
    'candidate_manifest_sha256': '93e8536dfc4b64056f306216d27cc5d94487778570023338e636d1c5860f9459',
    'decision': 'R0/R1 pass; isolated candidate, not promoted',
    'moves': 32, 'production_units': 28,
    'mac': {'host': mac['host'], 'compiler': mac['compiler'], 'preprocessed_equal': True, 'objects_equal': True, 'make_check': 'PASS'},
    'pi': {'host': pi['host'], 'compiler': pi['compiler'], 'preprocessed_equal': True, 'objects_equal': True, 'make_check': 'PASS'},
    'six_path_cleanup_equal': True, 'binaries': finish['binaries'],
    'kat_rsp_sha256': '22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8',
    'source_hashes': [{'old': u['old'], 'new': u['new'], 'baseline_sha256': u['baseline']['source_sha256'],
                       'candidate_sha256': u['candidate']['source_sha256'],
                       'pi_object_sha256': u['candidate']['object_sha256'],
                       'mac_object_sha256': m['candidate']['object_sha256']} for u, m in zip(pi['units'],mac['units'])],
    'benchmark_run': False,
}
outputs = {'INVENTORY.md': '\n'.join(lines), 'verification-summary.json': json.dumps(summary, indent=2),
           'reference-graph.json': json.dumps(finish['object_relocation_index'], indent=2)}
print('*** Begin Patch')
for name, text in outputs.items():
    print('*** Add File: ' + str(root / name))
    print('\n'.join('+' + x for x in text.splitlines()))
print('*** End Patch')
