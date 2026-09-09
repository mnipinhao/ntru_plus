#!/usr/bin/env python3
"""Make the strict Official-shell candidate from the verified E33 export."""
from pathlib import Path
import argparse, hashlib, json, shutil
p=argparse.ArgumentParser();p.add_argument('--e33-leaf',type=Path,required=True)
p.add_argument('--official',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
a=p.parse_args();assert not a.output.exists();shutil.copytree(a.e33_leaf,a.output)
replaced={}
for name in ('api.h','params.h','util.h'):
    src=a.official/name; shutil.copy2(src,a.output/name)
    replaced[name]=hashlib.sha256(src.read_bytes()).hexdigest()
(a.output.with_suffix('.identity.json')).write_text(json.dumps({
  'base_e33_leaf':str(a.e33_leaf.resolve()),'official_leaf':str(a.official.resolve()),
  'official_headers_replaced':replaced},indent=2)+'\n')
print(a.output)
