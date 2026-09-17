#!/usr/bin/env python3
from pathlib import Path
import json,shutil,subprocess
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[1];E144=ROOT/'experiments/gt32_rhash_vs_official_144';BUILD=EXP/'build'
subprocess.run(['python3',str(E144/'tools/build.py')],check=True)
if BUILD.exists():shutil.rmtree(BUILD)
BUILD.mkdir();shutil.copy2(E144/'build/official',BUILD/'official');shutil.copy2(E144/'build/gt',BUILD/'gt')
manifest=json.loads((E144/'generated/build-manifest.json').read_text());(EXP/'generated').mkdir(exist_ok=True);(EXP/'generated/build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
