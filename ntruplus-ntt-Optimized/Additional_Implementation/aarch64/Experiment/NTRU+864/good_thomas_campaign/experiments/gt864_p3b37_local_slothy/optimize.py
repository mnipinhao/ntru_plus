#!/usr/bin/env python3
from pathlib import Path
import logging,time,json
from slothy import Slothy
import slothy.targets.aarch64.aarch64_neon as arch
import slothy.targets.aarch64.neoverse_n1_experimental as target
H=Path(__file__).resolve().parent;B=H/'build'
def main():
    logging.basicConfig(level=logging.INFO,handlers=[logging.FileHandler(B/'slothy.log',mode='w'),logging.StreamHandler()])
    s=Slothy(arch,target,logger=logging.getLogger('p3b37'));s.load_source_from_file(str(B/'candidate.sym.S'))
    s.config.outputs=['v31','v1','v9','v26','v20','v24','v30','v29','v22','v19','v21','v23','v8','v10','v12','v6','v27','v0','x0','x1','x2','x3','v13','v14','v15']
    s.config.inputs_are_outputs=False;s.config.allow_useless_instructions=False;s.config.selftest=False
    s.config.reserved_regs=[f'x{i}' for i in range(4,31)]+['sp','v13','v14','v15']
    s.config.constraints.allow_spills=False;s.config.constraints.allow_renaming=False
    s.config.locked_registers=[f'v{i}' for i in range(32)]+['x0','x1','x2','x3']
    s.config.constraints.allow_reordering=True;s.config.constraints.functional_only=False
    s.config.variable_size=True;s.config.constraints.stalls_first_attempt=64
    s.config.split_heuristic=True;s.config.split_heuristic_factor=16.0;s.config.split_heuristic_stepsize=0.05
    s.config.split_heuristic_repeat=1;s.config.split_heuristic_estimate_performance=False;s.config.timeout=30
    t=time.time();s.optimize(start='p3b37_slothy_start',end='p3b37_slothy_end');s.write_source_to_file(str(B/'scheduled.S'))
    (B/'solver-result.json').write_text(json.dumps({'emitted':True,'elapsed_seconds':time.time()-t,'allocation':'unchanged','target':'N1 proxy','timeout_per_solver':30,'split_factor':16,'complete_kernel_cycle_estimate':None},indent=2)+'\n')
if __name__=='__main__':main()
