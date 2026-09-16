"""Reuse P3B37 exact-region gates; change only experiment identity and RA policy."""
from pathlib import Path
import subprocess
H = Path(__file__).resolve().parent
P = H.parent / 'gt864_p3b37_local_slothy'

def main():
    # Reuse the audited extraction/contract workflow without maintaining a copy.
    source = (P / 'prepare.py').read_text()
    source = source.replace('P3B36', 'P3B37').replace('P3B37 fixed-register', 'P3B38 RA-first')
    source = source.replace("'P3B37'", "'P3B38'").replace('p3b37_', 'p3b38_')
    source = source.replace('gt864_p3b36_combined', 'gt864_p3b37_local_slothy')
    source = source.replace('3524.834', '3518.28')
    source = source.replace('physical_register_preserving_split_window_schedule',
                            'RA_only_then_fixed_register_window_schedule')
    source = source.replace("'retain physical register allocation'",
                            "'retain boundary registers; internal renaming allowed'")
    source = source.replace('fixed physical allocation, small real-instruction split windows; no monolithic 513-instruction solve',
                            'fixed-order functional RA followed by fixed-allocation small scheduling windows')
    # Full physical names are valid baseline syntax, not a global allocator lock.
    source = source.replace('all vector allocation fixed',
                            'physical input syntax; internal definitions may be renamed by RA')
    exec(compile(source, str(P / 'prepare.py'), 'exec'),
         {'__file__': str(H / 'prepare.py'), '__name__': '__main__'})

if __name__ == '__main__':
    main()
