#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, statistics, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(); p.add_argument('normal'); p.add_argument('reversed');
    p.add_argument('--launches',type=int,default=8); p.add_argument('--iterations',type=int,default=200000)
    p.add_argument('--repeats',type=int,default=15); p.add_argument('--cpu',type=int,default=1)
    p.add_argument('--output',default='results/tile4-mtl-shuffle-class-cost.json'); a=p.parse_args()
    all_results={}
    for placement,binary in [('normal',a.normal),('reversed',a.reversed)]:
        launches=[]
        for _ in range(a.launches):
            raw=subprocess.check_output([binary,str(a.iterations),str(a.repeats),str(a.cpu)],text=True)
            launches.append(json.loads(raw))
        aggregate=[]
        for index,item in enumerate(launches[0]['results']):
            row={'kind':item['kind'],'streams':item['streams']}
            for metric in ('core_per_op','tsc_per_op','instructions_per_op','ref_per_op'):
                row[metric]=statistics.median(x['results'][index][metric] for x in launches)
            aggregate.append(row)
        all_results[placement]={'launches':launches,'median':aggregate}
        mix_aggregate=[]
        for index,item in enumerate(launches[0]['mix_results']):
            row={k:item[k] for k in ('name','global','local','arithmetic')}
            for metric in ('core_per_tile','tsc_per_tile','instructions_per_tile'):
                row[metric]=statistics.median(x['mix_results'][index][metric] for x in launches)
            mix_aggregate.append(row)
        all_results[placement]['mix_median']=mix_aggregate
    def get(place,kind,streams):
        return next(x for x in all_results[place]['median'] if x['kind']==kind and x['streams']==streams)['core_per_op']
    break_even={}
    for place in all_results:
        g=get(place,'vperm2i128',8)
        locals_=[get(place,k,8) for k in ('unpack16','unpack32','unpack64')]
        l=statistics.mean(locals_)
        current_per_tile=16*g
        free_per_tile=8*g+16*l
        break_even[place]={'G_core_per_op':g,'L_mean_core_per_op':l,'L_over_G':l/g,'standalone_condition_L_lt_half_G':l < 0.5*g,
                          'current_routing_core_per_tile':current_per_tile,'free_terminal_routing_core_per_tile':free_per_tile,
                          'ideal_core_saving_per_tile':current_per_tile-free_per_tile,
                          'ideal_core_saving_per_six_tile_inverse':6*(current_per_tile-free_per_tile)}
    mix_analysis={}
    for place,data in all_results.items():
        rows={x['name']:x for x in data['mix_median']}
        mix_analysis[place]={
            'pure_base16_core':rows['base16']['core_per_tile'],
            'pure_free8_16_core':rows['free8_16']['core_per_tile'],
            'pure_free_saving_core':rows['base16']['core_per_tile']-rows['free8_16']['core_per_tile'],
            'dependency_free8_16_core':rows['dependency_free8_16']['core_per_tile'],
            'dependency_vs_base_delta_core':rows['dependency_free8_16']['core_per_tile']-rows['base16']['core_per_tile'],
            'arithmetic_base_core':rows['arith_base16']['core_per_tile'],
            'arithmetic_free_core':rows['arith_free8_16']['core_per_tile'],
            'arithmetic_free_saving_core':rows['arith_base16']['core_per_tile']-rows['arith_free8_16']['core_per_tile'],
            'arithmetic_dependency_free_core':rows['arith_dependency_free8_16']['core_per_tile'],
            'arithmetic_dependency_vs_base_delta_core':rows['arith_dependency_free8_16']['core_per_tile']-rows['arith_base16']['core_per_tile']}
    out={'experiment':'MTL-SHUFFLE-MIX-COST-002','includes':'MTL-SHUFFLE-CLASS-COST-001','methodology':{'launches':a.launches,'iterations':a.iterations,'repeats_per_launch':a.repeats,'cpu':a.cpu,'primary':'PERF_COUNT_HW_CPU_CYCLES','secondary':'TSC'},'placements':all_results,'isolated_additive_model':break_even,'mix_analysis':mix_analysis}
    path=ROOT/a.output; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(out,indent=2)+'\n')
    print(path.relative_to(ROOT)); print(json.dumps(mix_analysis,indent=2))
if __name__=='__main__': main()
