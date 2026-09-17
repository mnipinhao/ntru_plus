#!/usr/bin/env python3
import json,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[1];RUNNER=ROOT/'experiments/gt32_compact_q24_037/tools/run_fixed_elf_campaign.py';dst=E/'results/formal'
subprocess.run(['python3',str(RUNNER),'--control',str(E/'build/measure-control'),'--candidate',str(E/'build/measure-candidate'),'--control-name','production QL2 control + reserved rhash tail','--candidate-name','143 geometry-preserved direct r pack-to-hash','--cpu','1','--blocks','16','--output',str(dst)],check=True)
summary=json.loads((dst/'manifest.json').read_text())['summary'];(E/'generated/benchmark-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
