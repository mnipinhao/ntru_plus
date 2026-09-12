from pathlib import Path
P=Path(__file__).resolve().parent
s=['#ifdef __APPLE__','#define gt864_crepmod3_raw _gt864_crepmod3_raw','#endif',
   '.text','.p2align 4','.global gt864_crepmod3_raw','gt864_crepmod3_raw:',
   'mov w4, #1728','dup v0.8h, w4','mov w4, #-1728','dup v1.8h, w4',
   'mov w4, #10923','dup v2.8h, w4','movi v3.8h, #3','mov x8, #27',
   '.Lp8_loop:', '// live-in: x0 v0 v1 v2 v3; live-out: memory and same inputs',
   '// range: raw abs<=4577 -> ternary; reserved registers: v0-v3 v8-v15 x8', 'p8_slothy_start:']
for i in range(4):
    s += [f'ldr Q<a{i}>, [x0, #{16*i}]',f'cmgt V<h{i}>.8h, V<a{i}>.8h, v0.8h',
          f'cmgt V<l{i}>.8h, v1.8h, V<a{i}>.8h',
          f'add V<y{i}>.8h, V<a{i}>.8h, V<h{i}>.8h',
          f'sub V<y{i}>.8h, V<y{i}>.8h, V<l{i}>.8h',
          f'sqrdmulh V<quotient{i}>.8h, V<y{i}>.8h, v2.8h',
          f'mls V<y{i}>.8h, V<quotient{i}>.8h, v3.8h',f'str Q<y{i}>, [x0, #{16*i}]']
s+=['p8_slothy_end:','add x0, x0, #64','subs x8, x8, #1','b.ne .Lp8_loop','ret']
(P/'candidate.sym.S').write_text('\n'.join(s)+'\n')
