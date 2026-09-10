"""Authorized local functional RA only. TBL3 timing placeholders are NOT A76 data."""
import contextlib, hashlib, importlib.util, json, logging, pathlib, re, subprocess, sys
from slothy import Slothy
from slothy.core.heuristics import Heuristics
from slothy.targets.aarch64 import aarch64_neon as Arch, cortex_a76 as Target
from tbl3_a76_model import install
P=pathlib.Path(__file__).resolve().parent
assert pathlib.Path(Arch.__file__).resolve().is_relative_to('/Users/chenpinhao/slothy')
install(timing=False)
SKILL=pathlib.Path('/Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts')
# The generic text checker lacks TBL output and INS read/write semantics.
# Extend its opcode classification locally; do not invent live-ins to silence it.
sys.path.insert(0,str(SKILL))
spec=importlib.util.spec_from_file_location('symbolic_check',SKILL/'check-symbolic-asm.py')
symbolic_check=importlib.util.module_from_spec(spec);spec.loader.exec_module(symbolic_check)
symbolic_check.DEST_DEFINES.update(['tbl','ins'])
symbolic_check.DEST_READWRITE.update(['ins','sli'])
windowed='--windows' in sys.argv
for mode in [x for x in sys.argv[1:] if x!='--windows'] or ['small','full']:
    work=P/('bytes-'+mode);kid='pair_merge_'+mode
    saved_argv=sys.argv
    sys.argv=['check-symbolic-asm.py','--candidate','--kernel-contract',str(work/'kernel-contract.yml'),str(work/'candidate.sym.S')]
    with (work/'static-check.log').open('w') as log,contextlib.redirect_stdout(log):
        assert symbolic_check.main()==0
    sys.argv=saved_argv
    for cmd in [['check-physical-reg-leaks.py','--contract',str(work/'kernel-contract.yml'),str(work/'candidate.sym.S')]]:
        subprocess.run([sys.executable,str(SKILL/cmd[0])]+cmd[1:],check=True)
    # Version-aware reverse liveness of the original instruction order.
    body=[l.strip() for l in (work/'candidate.sym.S').read_text().splitlines()
          if l.startswith('    ') and l.strip()!='ret' and not l.strip().startswith('//')]
    live=set();peak=0;peaks=[];live_before={len(body):set()}
    for pos in range(len(body)-1,-1,-1):
        ins=Arch.Instruction.parser(SourceLine(body[pos]))[0]
        defs={r for r,t in zip(ins.args_out,ins.arg_types_out) if t==Arch.RegisterType.NEON}
        rw={r for r,t in zip(ins.args_in_out,ins.arg_types_in_out) if t==Arch.RegisterType.NEON}
        uses={r for r,t in zip(ins.args_in,ins.arg_types_in) if t==Arch.RegisterType.NEON}
        live=(live-defs-rw)|uses|rw
        live_before[pos]=set(live)
        if len(live)>peak:peak=len(live);peaks=[{'instruction':pos,'source':body[pos],'live':sorted(live)}]
    assert not live
    logger=logging.getLogger(mode);logger.setLevel(logging.INFO)
    logger.addHandler(logging.FileHandler(work/('slothy-window-ra.log' if windowed else 'slothy-ra.log'),mode='w'))
    s=Slothy(Arch,Target,logger=logger)
    s.config.selftest=False
    s.config.inputs_are_outputs=True
    s.config.constraints.allow_spills=False
    s.config.constraints.functional_only=True
    s.config.constraints.allow_reordering=False
    s.config.variable_size=False
    s.config.reserved_regs=[f'x{i}' for i in range(18,31)]+['sp','xzr']
    s.config.timeout=60
    report={'interpreter':sys.executable,'architecture':Arch.__file__,
            'architecture_sha256':hashlib.sha256(pathlib.Path(Arch.__file__).read_bytes()).hexdigest(),
            'mode':mode,'instructions':len(body),'vector_liveness_peak':peak,
            'peak_example':peaks,'TBL3_timing':'placeholder; timing forbidden',
            'allow_spills':False,'allow_reordering':False}
    print(json.dumps(report),flush=True)
    try:
        if not windowed:
            s.load_source_from_file(str(work/'candidate.sym.S'))
            s.optimize(start=kid+'_slothy_start',end=kid+'_slothy_end')
            s.write_source_to_file(str(work/'candidate.alloc.S'))
        else:
            cuts=[0]+[i for i,l in enumerate(body) if re.match(r'ldr Q<idx[0-8]>',l)]+[len(body)]
            mapping={};allocated=[];regions=[]
            for block,(lo,hi) in enumerate(zip(cuts,cuts[1:])):
                part=body[lo:hi]
                mentioned=set(re.findall(r'<(\w+)>','\n'.join(part)))
                held=live_before[lo]-mentioned
                cfg=s.config.copy();cfg.inputs_are_outputs=False;cfg.timeout=30
                # Keep a contiguous 12-register work bank free at the frontend
                # boundary. Slothy selects the mapping of all 20 live values;
                # later row regions can use all 32 registers.
                if block==0:cfg.reserved_regs += [f'v{i}' for i in range(20,32)]
                cfg.outputs=sorted(live_before[hi]&mentioned)+['x0','x1','x2','x3','x4','x6','x7','x9']
                cfg.reserved_regs += [mapping[v] for v in held]
                cfg.rename_inputs={'arch':'static','symbolic':'any',**{v:mapping[v] for v in live_before[lo]&mentioned}}
                cfg.rename_outputs={'arch':'static','symbolic':'any'}
                # Fix still-live input values, but permit consumed inputs to die.
                cfg.rename_outputs.update({v:mapping[v] for v in live_before[lo]&live_before[hi]&mentioned})
                result=Heuristics.linear(SourceLine.read_multiline('\n'.join(part)),logger.getChild(f'row{block}'),cfg)
                assert result.success
                mapping={v:mapping[v] for v in held}
                mapping.update({v:r for v,r in result.output_renamings.items() if v in live_before[hi]})
                assert set(mapping)==live_before[hi]
                allocated += [l.text for l in result.code_raw]
                regions.append({'block':block,'instructions':hi-lo,'held':sorted(held),'live_out_mapping':dict(mapping)})
                print(mode,'allocated block',block,flush=True)
            text=['.text',f'.global {kid}',f'{kid}:',f'{kid}_slothy_start:']+['    '+l.strip() for l in allocated]+[f'{kid}_slothy_end:','    ret']
            (work/'candidate.alloc.S').write_text('\n'.join(text)+'\n')
            report['regions']=regions
        report['allocation']='pass'
    except Exception as exc:
        report['allocation']='not-proven';report['error']=str(exc)
    (work/'allocation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)
