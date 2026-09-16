"""Functional RA first, then bounded fixed-register real-instruction windows."""
from pathlib import Path
import logging, time, json
from slothy import Slothy
import slothy.targets.aarch64.aarch64_neon as arch
import slothy.targets.aarch64.neoverse_n1_experimental as target
H = Path(__file__).resolve().parent
B = H / 'build'
OUT = ['v31','v1','v9','v26','v20','v24','v30','v29','v22',
       'v19','v21','v23','v8','v10','v12','v6','v27','v0',
       'x0','x1','x2','x3','v13','v14','v15']

def instance(stage):
    s = Slothy(arch, target, logger=logging.getLogger(stage))
    s.config.outputs = OUT
    s.config.inputs_are_outputs = False
    s.config.allow_useless_instructions = False
    s.config.selftest = False
    s.config.reserved_regs = [f'x{i}' for i in range(4,31)] + ['sp','v13','v14','v15']
    s.config.constraints.allow_spills = False
    s.config.rename_inputs = {'arch':'static','symbolic':'any'}
    s.config.rename_outputs = {'arch':'static','symbolic':'any'}
    s.config.timeout = 30
    return s

def main():
    logging.basicConfig(level=logging.INFO,
        handlers=[logging.FileHandler(B/'slothy.log', mode='w'), logging.StreamHandler()])
    t = time.time()
    ra = instance('allocation')
    ra.load_source_from_file(str(B/'candidate.sym.S'))
    ra.config.constraints.allow_renaming = True
    ra.config.locked_registers = ['x0','x1','x2','x3']
    ra.config.constraints.allow_reordering = False
    ra.config.constraints.functional_only = True
    ra.config.split_heuristic = True
    ra.config.split_heuristic_factor = 16.0
    ra.config.split_heuristic_stepsize = 0.05
    ra.config.split_heuristic_repeat = 1
    ra.config.split_heuristic_estimate_performance = False
    ra.optimize(start='p3b38_slothy_start', end='p3b38_slothy_end')
    ra.write_source_to_file(str(B/'allocated.S'))
    ra_seconds = time.time() - t
    s = instance('schedule')
    s.load_source_from_file(str(B/'allocated.S'))
    s.config.constraints.allow_renaming = False
    s.config.locked_registers = [f'v{i}' for i in range(32)] + ['x0','x1','x2','x3']
    s.config.constraints.allow_reordering = True
    s.config.constraints.functional_only = False
    s.config.variable_size = True
    s.config.constraints.stalls_first_attempt = 64
    s.config.split_heuristic = True
    s.config.split_heuristic_factor = 16.0
    s.config.split_heuristic_stepsize = 0.05
    s.config.split_heuristic_repeat = 1
    s.config.split_heuristic_estimate_performance = False
    s.optimize(start='p3b38_slothy_start', end='p3b38_slothy_end')
    s.write_source_to_file(str(B/'scheduled.S'))
    (B/'solver-result.json').write_text(json.dumps({
        'emitted':True, 'elapsed_seconds':time.time()-t, 'ra_seconds':ra_seconds,
        'allocation':'internal renaming; static boundary',
        'target':'N1 proxy', 'timeout_per_solver':30, 'split_factor':16,
        'complete_kernel_cycle_estimate':None}, indent=2)+'\n')

if __name__ == '__main__':
    main()
