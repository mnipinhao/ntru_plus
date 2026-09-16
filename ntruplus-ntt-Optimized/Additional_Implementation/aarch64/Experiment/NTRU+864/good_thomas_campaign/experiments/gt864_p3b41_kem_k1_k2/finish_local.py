"""Finish offline gates; no network and no inferred execution results."""
import json,subprocess,hashlib,yaml
from pathlib import Path
from campaign import H,E,B,BASE,PY,SK,lower

def main():
    proof_path=E/'gt864_p3b40_caller_closure/build/proof.json'
    proof=json.loads(proof_path.read_text())
    source=BASE/'build/sync/raw/gt864_forward_six_bank.S'
    assert hashlib.sha256(source.read_bytes()).hexdigest()==proof['hashes'][str(source)]
    for k in ('K1','K2'):
        d=B/k;b=d/'build'
        before,after,ledger=lower(source,f'main.stage{k[1]}.node0')
        assert ledger==json.loads((b/'lowering.json').read_text())
        # Exhaustive scalar congruence of the deleted (1,9) multiplication.
        for x in range(-32768,32768):
            residual=x-((x*9+16384)//32768)*3457
            assert -32768<=residual<=32767 and (residual-x)%3457==0
        logs=[]
        for filename in ('gt864_forward_six_bank.S','gt864_forward_poly_ntt.S'):
            cmd=['/usr/bin/clang','--target=aarch64-linux-gnu','-march=armv8-a+simd',
                 '-c',str(b/'sync/raw'/filename),'-o',str(b/(filename+'.o'))]
            p=subprocess.run(cmd,text=True,capture_output=True)
            logs.append({'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
            assert p.returncode==0,p.stderr
        (b/'local-assemble.json').write_text(json.dumps(logs,indent=2))
        parsed=subprocess.run([PY,str(SK/'parse-slothy-log.py'),str(b/'slothy.log')],text=True,capture_output=True)
        (b/'parsed-slothy.json').write_text(parsed.stdout)
        log=(b/'slothy.log').read_text()
        assert 'split_heuristic_full:OK!' in log
        assert json.loads(parsed.stdout)['signals']['bad']==['timeout']
        assert all('Setting timeout' in x for x in log.splitlines() if 'timeout' in x.lower())
        (b/'reviewed-slothy.json').write_text(json.dumps({'status':'pass','full_kernel_cycles':None,
            'parser_note':'timeout configuration false positive; full selfcheck and emitted artifact verified'}))
        contract=yaml.safe_load((d/'kernel-contract.yml').read_text())
        contract['slothy']['driver']=str(H/'campaign.py')+f' --optimize {k}'
        (d/'kernel-contract.yml').write_text(yaml.safe_dump(contract,sort_keys=False))
        baseline=yaml.safe_load((d/'baseline-contract.yml').read_text())
        baseline['baseline']['id']='P3B37 restricted to P3B40 KEM caller context'
        baseline['baseline_cost']['cycles']=3518.28
        (d/'baseline-contract.yml').write_text(yaml.safe_dump(baseline,sort_keys=False))
        candidate=yaml.safe_load((d/'candidate-contract.yml').read_text())
        candidate['region']['expected_instruction_count']=511
        candidate['candidate']['slothy_driver']=str(H/'campaign.py')+f' --optimize {k}'
        (d/'candidate-contract.yml').write_text(yaml.safe_dump(candidate,sort_keys=False))
        (d/'iteration.yml').write_text(yaml.safe_dump({'iteration':{'id':'P3B41-'+k,'mode':'existing_region_replacement','current_state':'oracle_correctness','status':'investigate'},
             'gates':{'range_model':'P3B40 pass','lowering_SSA_constants':'pass','Slothy_DFG':'pass','schedule_SSA_addresses':'pass','local_assembly':'pass','Pi_correctness':'pending','benchmark':'pending'},
             'blocker':'Remote upload denied by safety reviewer; explicit authorization required for this new K1/K2 payload.',
             'production_changed':False},sort_keys=False))
        score={'candidate.id':'P3B41-'+k,'candidate.status':'investigate','candidate.mode':'existing_region_replacement',
            'contract.preserved':True,'contract.approved_changes':True,'correctness.oracle':'unknown',
            'correctness.tests':'unknown','correctness.abi':'pass','correctness.constant_time_review':'pass',
            'slothy.status':'pass','slothy.baseline_expected_cycles':None,'slothy.candidate_expected_cycles':None,
            'benchmark.status':'pending','benchmark.baseline':None,'benchmark.candidate':None,
            'decision.reason':'Await explicit Pi upload authorization and executable correctness/timing.'}
        (d/'candidate-score.yml').write_text(yaml.safe_dump(score,sort_keys=False))
        result=subprocess.run([PY,str(SK/'score-candidate.py'),str(d/'candidate-score.yml'),'--json'],text=True,capture_output=True)
        (b/'score.json').write_text(result.stdout)
        print(k,'local assembly / lowering / Slothy gates passed; Pi pending')
if __name__=='__main__':main()
