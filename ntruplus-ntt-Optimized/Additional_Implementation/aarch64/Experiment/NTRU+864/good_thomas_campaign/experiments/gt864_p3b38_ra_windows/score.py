"""Preserve generic parser results, review timeout configuration, score evidence."""
from pathlib import Path
import json, subprocess
H = Path(__file__).resolve().parent
B = H / 'build'
PY = '/Users/chenpinhao/slothy_and_ra/.venv/bin/python'
SK = Path('/Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts')

def main():
    parsed = subprocess.run([PY,str(SK/'parse-slothy-log.py'),str(B/'slothy.log')],
                            text=True,capture_output=True)
    (B/'parsed-slothy.json').write_text(parsed.stdout)
    raw = json.loads(parsed.stdout)
    log = (B/'slothy.log').read_text()
    assert raw['signals']['bad'] == ['timeout']
    assert all('Setting timeout' in x for x in log.splitlines() if 'timeout' in x.lower())
    for stage in ('allocation','schedule'):
        assert f'{stage}.p3b38_slothy_start.split.split_heuristic_full:OK!' in log
    assert json.loads((B/'solver-result.json').read_text())['emitted']
    reviewed = {'slothy_status':'pass','expected_cycles_best':None,
                'explanation':'Successful split RA and scheduling. Generic parser timeout matches configuration, not failure; overlapping windows and functional RA have no comparable aggregate cycle estimate. Failed global RA is separately retained in global-ra-timeout.log.'}
    (B/'reviewed-slothy.json').write_text(json.dumps(reviewed,indent=2)+'\n')
    measured = json.loads((B/'measurement.json').read_text())['medians']
    score = (H.parent/'gt864_p3b37_local_slothy/candidate-score.yml').read_text()
    score = score.replace('P3B37','P3B38').replace('3524.9355',str(measured['t1']['cycles']))
    score = score.replace('3518.28',str(measured['raw']['cycles']))
    score = score.replace('Fixed allocation and identical arithmetic',
                          'Renamed internals, fixed boundary and identical exact DAG')
    score = score.replace('Tiny measured improvement; no aggregate model estimate and no production promotion.',
                          'Judge same-boundary Pi result; aggregate model estimate unavailable; no production promotion.')
    (H/'candidate-score.yml').write_text(score)
    result = subprocess.run([PY,str(SK/'score-candidate.py'),str(H/'candidate-score.yml'),'--json'],
                            text=True,capture_output=True)
    (B/'score.json').write_text(result.stdout)
    print(result.stdout)

if __name__ == '__main__':
    main()
