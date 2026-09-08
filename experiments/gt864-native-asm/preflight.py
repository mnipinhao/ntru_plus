"""Parser/model preflight only. Does not invoke allocation or scheduling."""
import argparse,hashlib,json,sys,logging
from pathlib import Path
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch,cortex_a76 as Target
from slothy.core.config import Config
from slothy.core.dataflow import DataFlowGraph

def check(path):
    count=0;lines=[]
    for line in path.read_text().splitlines():
        text=line.strip()
        if not text or text.startswith(('.', '//')) or text.endswith(':') or text=='ret':continue
        try:inst=Arch.Instruction.parser(SourceLine(text))[0]
        except Exception as exc:raise RuntimeError(f'{path}: {text}: {exc}') from exc
        # Roundtrip and cost coverage; not a proof that the whole region allocates.
        Arch.Instruction.parser(SourceLine(inst.write()))
        Target.get_inverse_throughput(inst)
        Target.get_resource_usages(inst)
        Target.get_dispatch_uops(inst)
        count+=1;lines.append(text)
    config=Config(Arch,Target,logging.getLogger('preflight'))
    config.inputs_are_outputs=True
    DataFlowGraph(SourceLine.read_multiline('\n'.join(lines)),logging.getLogger('preflight'),config)
    return {'file':str(path),'instructions':count,
      'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('files',nargs='*');args=parser.parse_args()
    root=Path(__file__).resolve().parent
    paths=[Path(p) for p in args.files] or sorted(root.glob('*/candidate.sym.S'))
    print(json.dumps({'arch':Arch.__file__,'target':Target.__file__,
      'arch_sha256':hashlib.sha256(Path(Arch.__file__).read_bytes()).hexdigest(),
      'target_sha256':hashlib.sha256(Path(Target.__file__).read_bytes()).hexdigest(),
      'interpreter':sys.executable,'files':[check(p) for p in paths],
      'solver_run':False},indent=2))
