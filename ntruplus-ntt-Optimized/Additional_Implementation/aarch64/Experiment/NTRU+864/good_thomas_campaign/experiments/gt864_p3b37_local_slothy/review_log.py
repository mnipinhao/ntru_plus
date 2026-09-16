"""Preserve generic parser output and explicitly review its false positives."""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE / 'build'
PYTHON = '/Users/chenpinhao/slothy_and_ra/.venv/bin/python'
SCRIPTS = Path('/Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts')
result = subprocess.run([PYTHON, str(SCRIPTS / 'parse-slothy-log.py'),
                         str(BUILD / 'slothy.log')], capture_output=True, text=True)
(BUILD / 'parsed-slothy.json').write_text(result.stdout)
raw = json.loads(result.stdout)
log = (BUILD / 'slothy.log').read_text()
solver = json.loads((BUILD / 'solver-result.json').read_text())
assert raw['signals']['bad'] == ['timeout'], raw
assert all('Setting timeout' in line for line in log.splitlines() if 'timeout' in line.lower())
assert 'split_heuristic_full:OK!' in log
assert solver['emitted'] and (BUILD / 'scheduled.S').is_file()
review = {
    'slothy_status': 'pass',
    'expected_cycles_best': None,
    'raw_parser_exit_code': result.returncode,
    'explanation': 'Generic parser mistakes timeout configuration for failure and logger digits for cycle estimates. Full DFG selfcheck passes; scheduled artifact emitted. Overlapping window estimates are not full-kernel cycles.',
    'elapsed_seconds': solver['elapsed_seconds'],
}
(BUILD / 'reviewed-slothy.json').write_text(json.dumps(review, indent=2) + '\n')
score = subprocess.run([PYTHON, str(SCRIPTS / 'score-candidate.py'),
                        str(HERE / 'candidate-score.yml'), '--json'],
                       capture_output=True, text=True)
(BUILD / 'score.json').write_text(score.stdout)
print(score.stdout)
print('score exit:', score.returncode)
