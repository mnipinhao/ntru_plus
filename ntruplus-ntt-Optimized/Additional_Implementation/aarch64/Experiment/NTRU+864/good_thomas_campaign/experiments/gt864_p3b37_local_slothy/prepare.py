#!/usr/bin/env python3
from pathlib import Path
import subprocess,json,hashlib,yaml,re
class IndentDumper(yaml.SafeDumper):
    def increase_indent(self,flow=False,indentless=False):return super().increase_indent(flow,False)
def dump(data,**kw):return yaml.dump(data,Dumper=IndentDumper,**kw)
yaml.safe_dump=dump
H=Path(__file__).resolve().parent;E=H.parent;B=H/'build'
SK=Path('/Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring');PY='/Users/chenpinhao/slothy_and_ra/.venv/bin/python'
SOURCE=E/'gt864_p3b36_combined/build/sync/raw/gt864_forward_six_bank.S'
def run(args):return subprocess.check_output(args,text=True,stderr=subprocess.STDOUT)
def main():
    B.mkdir(exist_ok=True)
    (B/'repo-probe.txt').write_text(run(['bash',str(SK/'scripts/probe-slothy-repo.sh'),'/Users/chenpinhao/slothy_and_ra']))
    (B/'environment.txt').write_text(run([PY,'-c','import sys,slothy;print(sys.executable);print(slothy.__file__)'])+run(['git','-C','/Users/chenpinhao/slothy_and_ra/extern/slothy','rev-parse','HEAD']))
    run([PY,str(SK/'scripts/extract-slothy-region.py'),str(SOURCE),'--start','.Lgt864_a1t1_one_bank','--end','gt864_forward_six_bank_pass2_a1_t1_end','--output',str(B/'baseline-region.S')])
    text=(B/'baseline-region.S').read_text();body=text.splitlines()[1:-1]
    instructions=[line.split('//')[0].strip() for line in body if line.split('//')[0].strip()]
    assert instructions[-1]=='ret';instructions=[x.lower() for x in instructions[:-1]];assert len(instructions)==513,len(instructions)
    # MOV vector is an ORR alias; this local fork's two-datatype MOV parser
    # rejects equal .16b views. Expose the exact underlying instruction.
    instructions=[re.sub(r'^mov (v\d+\.16b), (v\d+\.16b)$',r'orr \1, \2, \2',x) for x in instructions]
    instructions=[x.replace('[x1]','[x1, #0]') if x.startswith('ldp ') else x for x in instructions]
    start='p3b37_slothy_start';end='p3b37_slothy_end'
    k=yaml.safe_load((E/'gt_t1_slothy_scheduling/kernel-contract.yml').read_text())
    outs=['v31','v1','v9','v26','v20','v24','v30','v29','v22','v19','v21','v23','v8','v10','v12','v6','v27','v0','x0','x1','x2','x3','v13','v14','v15']
    k.update(mode='existing_region_replacement',candidate_status='investigate')
    k['kernel'].update(id='P3B37',name='P3B36 fixed-register window scheduling',source='build/candidate.sym.S')
    k['slothy']={'workflow':'physical_register_preserving_split_window_schedule','driver':'optimize.py','expected_outputs':['build/scheduled.S'],'allow_spills':False}
    k['region']={'start_label':start,'end_label':end,'expected_instruction_count':513,'live_in':['x0','x1','x2','x3','v13','v14','v15'],'live_out':outs}
    k['abi']['inputs']=k['region']['live_in'];k['abi']['outputs']=outs
    k['abi']['fixed_vector_registers']=[f'v{i}' for i in range(32)]
    k['abi']['reserved_registers']=[f'x{i}' for i in range(4,31)]+['sp','v13','v14','v15']
    k['memory_contract'].update(loads=['one tail LDP','sixteen main LDR','fifty constant LDR'],pointer_updates=['x0+256','x1 unchanged','x2+336','x3+512'])
    k['range_contract'].update(input_ranges=['P3B35 exact raw top producers from natural coefficients [-3,4]'],intermediate_ranges=['P3B35 exact NTT16 marginal theorem; Forward abs<=26731'],output_ranges=['FR0 R0 int16 abs<=26731'])
    k['validation']={'oracle_command':'python3 run_pi.py --run','test_command':'python3 run_pi.py --validate','full_path_benchmark_command':'python3 run_pi.py --repeat --summarize','benchmark_metric':'complete Forward PMU median','lower_is_better':True}
    baseline={key:k[key] for key in ('region','abi','layout','memory_contract','constant_contract','range_contract','constant_time_contract')}
    baseline['baseline']={'id':'P3B36','source':str(SOURCE),'extracted_region':'build/baseline-region.S','function':'gt864_forward_six_bank_pass2_a1_t1','start_label':start,'end_label':end}
    baseline['region']=dict(k['region'],instruction_count=513)
    baseline['baseline_cost']={'static_instruction_count':513,'benchmark_command':'P3B36 three paired Pi5 Forward repeats','cycles':3524.834}
    for name,data in [('baseline-contract.yml',baseline),('kernel-contract.yml',k)]:
        (H/name).write_text(yaml.safe_dump(data,sort_keys=False));print(run([PY,str(SK/'scripts/check-kernel-contract.py'),str(H/name)]))
    dag={'id':'P3B37','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'instruction_stream':instructions,'inputs':k['region']['live_in'],'outputs':outs,'constraints':['retain physical register allocation','no spills','no DAG changes','MLS destructive operand','preserve public memory dependencies and live-out pointers'],'model':'neoverse_n1_experimental proxy, Pi5 A76 final test'}
    (H/'instruction-dag.yml').write_text(yaml.safe_dump(dag,sort_keys=False))
    comments='// live-in: x0 x1 x2 x3 v13 v14 v15\n// live-out: '+', '.join(outs)+'\n// coefficient range: P3B35 raw-top producer theorem; output abs <= 26731 R0\n// reserved physical registers: x4-x30 sp v13 v14 v15; all vector allocation fixed\n'
    (B/'candidate.sym.S').write_text(start+':\n'+comments+'\n'.join('    '+x for x in instructions)+'\n'+end+':\n')
    cand=dict(baseline);cand.pop('baseline');cand.pop('baseline_cost');cand['candidate']={'id':'P3B37','status':'investigate','kernel_contract':'kernel-contract.yml','symbolic_source':'build/candidate.sym.S','slothy_driver':'optimize.py'};cand['contract_preservation']={'preserved':True,'approved_changes':'none'}
    (H/'candidate-contract.yml').write_text(yaml.safe_dump(cand,sort_keys=False))
    commands=[['check-symbolic-asm.py',str(B/'candidate.sym.S'),'--candidate','--kernel-contract',str(H/'kernel-contract.yml')],['check-physical-reg-leaks.py',str(B/'candidate.sym.S'),'--contract',str(H/'kernel-contract.yml')],['compare-kernel-contract.py',str(H/'baseline-contract.yml'),str(H/'candidate-contract.yml')]]
    for args in commands:print(run([PY,str(SK/'scripts'/args[0]),*args[1:]]))
    (H/'iteration.yml').write_text(yaml.safe_dump({'iteration':{'id':'P3B37','mode':'existing_region_replacement','current_state':'Slothy_run_by_user','status':'investigate'},'authorization':'User explicitly asks agent to run Slothy locally on Mac; this authorizes agent execution of user-run stage.','workflow':'fixed physical allocation, small real-instruction split windows; no monolithic 513-instruction solve','gates':{'baseline_contract':'pass','kernel_contract':'pass','instruction_dag':'pass','static_checks':'pass','oracle_correctness':'pending','full_path_benchmark':'pending'}},sort_keys=False))
if __name__=='__main__':main()
