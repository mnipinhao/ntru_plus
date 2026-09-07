#!/usr/bin/env python3
"""Pi-only cleanup equivalence and linked release-root inventory."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
build = root / '.build'
package = root / 'NTRU+768'
baseline_build = build / 'baseline-package'
fixture = Path('/home/pi/gt768-production-policy-threeway-20260907-e08/.build/coverage-all.c')
rng = Path('/home/pi/ntruplus-fwd-child0-identity-specialize-20260903-e01/bench/aarch64/gt-production/deterministic_randombytes.c')
objects = sorted((build / 'audit/candidate').glob('*.o'))
assert len(objects) == 28
command = ['gcc', '-I' + str(package), '-O3', '-fomit-frame-pointer', '-std=c99',
           '-ffunction-sections', '-fdata-sections', str(fixture), str(rng)]
command += [str(p) for p in objects]
command += ['-Wl,--gc-sections', '-Wl,--wrap=explicit_bzero',
            '-Wl,-Map=' + str(build / 'coverage.map'), '-o', str(build / 'coverage')]
subprocess.run(command, check=True)
coverage = subprocess.check_output([str(build / 'coverage')])
(build / 'coverage.log').write_bytes(coverage)
expected = Path('/home/pi/gt768-production-d1-small-official-policy-20260907-e10/.build/e10-candidate-coverage.log')
assert coverage == expected.read_bytes(), 'Cleanup sequence changed'
binary_results = []
for name in ['test_kem', 'test_abi', 'test_canonical', 'test_zeroization', 'test_ntt_small', 'PQCgenKAT_kem']:
    before, after = baseline_build / name, build / 'package' / name
    entry = {'name': name, 'candidate_sha256': hashlib.sha256(after.read_bytes()).hexdigest()}
    entry['baseline_sha256'] = hashlib.sha256(before.read_bytes()).hexdigest()
    entry['equal'] = before.read_bytes() == after.read_bytes()
    # GCC driver uses randomly named temporary assembly objects when compiling
    # many .S files in one link command. Compare all ELF sections and explicitly
    # report metadata differences instead of asserting whole-file identity.
    def sections(path):
        import struct
        data = path.read_bytes()
        assert data[:6] == b'\x7fELF\x02\x01'
        shoff = struct.unpack_from('<Q', data, 40)[0]
        entsize, count, namesindex = struct.unpack_from('<HHH', data, 58)
        headers = [struct.unpack_from('<IIQQQQIIQQ', data, shoff + i * entsize) for i in range(count)]
        namesheader = headers[namesindex]
        names = data[namesheader[4]:namesheader[4]+namesheader[5]]
        result = {}
        for h in headers[1:]:
            name = names[h[0]:].split(b'\0')[0].decode()
            payload = b'' if h[1] == 8 else data[h[4]:h[4]+h[5]]
            result[name] = {'type': h[1], 'flags': h[2], 'address': h[3], 'size': h[5],
                            'alignment': h[8], 'sha256': hashlib.sha256(payload).hexdigest()}
        return result
    s0, s1 = sections(before), sections(after)
    entry['differing_sections'] = [n for n in sorted(set(s0) | set(s1)) if s0.get(n) != s1.get(n)]
    allowed = {'.note.gnu.build-id', '.symtab', '.strtab'}
    entry['runtime_sections_equal'] = not (set(entry['differing_sections']) - allowed)
    assert entry['runtime_sections_equal'], entry
    binary_results.append(entry)

inventory = []
for obj in objects:
    dis = subprocess.check_output(['objdump', '-dr', str(obj)]).decode()
    Path(str(obj) + '.disasm').write_text(dis)
    # Owner labels are objdump symbol anchors. Assembly interior labels may be
    # absent; edges are conservative and never used as permission to delete.
    owner = None
    edges = []
    for line in dis.splitlines():
        match = re.match(r'^[0-9a-f]+ <(.+)>:', line)
        if match:
            owner = match.group(1)
        relocation = re.search(r'R_AARCH64_([A-Z0-9_]+)\s+(\S+)', line)
        if relocation:
            edges.append({'owner_anchor': owner, 'kind': relocation.group(1), 'target': relocation.group(2)})
    inventory.append({'object': obj.name, 'relocation_edges': edges})
linked = subprocess.check_output(['nm', '-S', '-n', str(build / 'coverage')]).decode()
(build / 'coverage.nm').write_text(linked)
summary = {'cleanup_equal': True, 'cleanup_fixture': str(fixture), 'rng': str(rng),
           'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest(),
           'rng_sha256': hashlib.sha256(rng.read_bytes()).hexdigest(),
           'command': command, 'binaries': binary_results,
           'object_relocation_index': inventory, 'linked_kem_root_symbols': linked.splitlines()}
(build / 'finish-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print('Six-path cleanup byte-for-byte match: PASS')
for result in binary_results:
    print(result)
