#!/usr/bin/env python3
"""Generate the unified NTRU+ AVX2 benchmark report and CSV/JSON indexes."""
from __future__ import annotations
import csv,json,statistics,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_supercop_benchmark import decode_observations,stabilized_quartiles
from supercop_workflow import read_lock,sha256_file

ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/"results/ntruplus-avx2-768-864-1152-20260920"
DOC=ROOT/"docs/ntruplus-avx2-768-864-1152-benchmark-202609.md"
NATIVE={"768":{"official":"768-official","candidate":"768-gt32-clean"},
        "864":{"official":"864-official","candidate":None},
        "1152":{"official":"1152-official","candidate":"1152-exp017"}}
OPS=("keypair_cycles","enc_cycles","dec_cycles")
COMPONENT_PROFILES=("768-official-common-v3","864-official-common-v3",
                    "1152-official-common-v3","768-gt32-private",
                    "864-d3-mr32-v2","1152-exp017-current")
def summary(path): return json.loads(path.read_text())["operations"]
def launch_stq(directory,op):
  return [stabilized_quartiles(decode_observations(p.read_text(),op))[1]
          for p in sorted((directory/"fresh-launches").glob("*.out"))]
def write_csv(path,rows,fields):
  path.parent.mkdir(parents=True,exist_ok=True)
  with path.open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
def f2(x): return f"{x:.2f}"
def section_sizes(path):
  out=subprocess.run(["size","-A",str(path)],text=True,stdout=subprocess.PIPE,check=True).stdout
  found={}
  for line in out.splitlines():
    words=line.split()
    if len(words)>=2 and words[0] in (".text",".rodata") and words[1].isdigit():
      found[words[0]]=int(words[1])
  return found
def main()->int:
  lock=read_lock(); native_rows=[]; native_summary={}
  for p,names in NATIVE.items():
    offdir=RESULT/"native"/names["official"]; off=summary(offdir/"stq-summary.json")
    native_summary[p]={"official":off,"candidate":None,"delta":None}
    for op in OPS:
      native_rows.append({"parameter":p,"role":"official","implementation":names["official"],"operation":op,
        **{k:off[op][k] for k in ("observations","stq1","stq2","stq3")},"delta_cycles":"","delta_percent":"","faster_launches":""})
    if names["candidate"]:
      cdir=RESULT/"native"/names["candidate"]; cand=summary(cdir/"stq-summary.json")
      native_summary[p]["candidate"]=cand; native_summary[p]["delta"]={}
      for op in OPS:
        delta=cand[op]["stq2"]-off[op]["stq2"]; pct=100*delta/off[op]["stq2"]
        launch=[b-a for a,b in zip(launch_stq(offdir,op),launch_stq(cdir,op))]
        native_summary[p]["delta"][op]={"cycles":delta,"percent":pct,"faster_launches":sum(x<0 for x in launch),"launch_deltas":launch}
        native_rows.append({"parameter":p,"role":"candidate","implementation":names["candidate"],"operation":op,
          **{k:cand[op][k] for k in ("observations","stq1","stq2","stq3")},"delta_cycles":delta,"delta_percent":pct,
          "faster_launches":f"{sum(x<0 for x in launch)}/9"})
  write_csv(RESULT/"native.csv",native_rows,list(native_rows[0]))
  component_rows=[]
  for name in COMPONENT_PROFILES:
    directory=RESULT/"components"/name
    meta=json.loads((directory/"metadata.json").read_text()); ops=summary(directory/"stq-summary.json")
    for op,value in ops.items():
      component_rows.append({"profile":directory.name,"parameter":meta["parameter"],"implementation":meta["implementation"],
        "benchmark_class":meta["benchmark_class"],"operation":op,**{k:value[k] for k in ("observations","stq1","stq2","stq3")}})
  write_csv(RESULT/"components.csv",component_rows,list(component_rows[0]))
  caller_rows=[]
  common={p:{r["operation"]:r["stq2"] for r in component_rows
             if r["profile"]==f"{p}-official-common-v3"}
          for p in ("768","864","1152")}
  stage_specs={
    "keypair":(("sample_one_polynomial_cbd1","cbd1_cycles"),
               ("forward_one_polynomial","forward_small_cycles"),
               ("baseinv_one_polynomial","baseinv_cycles"),
               ("basemul_one_product","basemul_cycles"),
               ("serialize_one_polynomial","poly_tobytes_cycles"),
               ("hash_f","hash_f_cycles")),
    "encap":(("public_key_decode","poly_frombytes_cycles"),
             ("prehash_hash_f","hash_f_cycles"),("prehash_hash_h","hash_h_cycles"),
             ("cbd1","cbd1_cycles"),("forward_one_polynomial","forward_small_cycles"),
             ("serialize_r","poly_tobytes_cycles"),("hash_g","hash_g_cycles"),
             ("sotp_encode","sotp_encode_cycles"),("basemul_one_product","basemul_cycles"),
             ("poly_add","poly_add_cycles"),("ciphertext_serialize","poly_tobytes_cycles")),
    "decap":(("decode_one_polynomial","poly_frombytes_cycles"),
             ("basemul_scale","basemul_scale_cycles"),("inverse","inverse_cycles"),
             ("crepmod3","crepmod3_cycles"),("message_forward","forward_small_cycles"),
             ("poly_sub","poly_sub_cycles"),("recovery_basemul","basemul_cycles"),
             ("recovered_r_serialize","poly_tobytes_cycles"),("hash_g","hash_g_cycles"),
             ("sotp_decode","sotp_decode_cycles"),("hash_h","hash_h_cycles"),
             ("reencryption_forward","forward_small_cycles"))}
  for p in ("768","864","1152"):
    for operation,specs in stage_specs.items():
      for stage,label in specs:
        caller_rows.append({"parameter":p,"operation":operation,"stage":stage,
          "measurement_role":"isolated-building-block","profile":f"{p}-official-common-v3",
          "label":label,"stq2_cycles":common[p][label],"cumulative_cutpoint":"no"})
      native_label={"keypair":"keypair_cycles","encap":"enc_cycles","decap":"dec_cycles"}[operation]
      caller_rows.append({"parameter":p,"operation":operation,"stage":"native_total",
        "measurement_role":"supercop-native-kem","profile":NATIVE[p]["official"],
        "label":native_label,"stq2_cycles":native_summary[p]["official"][native_label]["stq2"],
        "cumulative_cutpoint":"yes-total-only"})
  write_csv(RESULT/"caller-components.csv",caller_rows,list(caller_rows[0]))
  paired_rows=[]
  for p in ("768","1152"):
    paired_rows+=json.loads((RESULT/"paired"/p/"summary.json").read_text())["rows"]
  for row in json.loads((RESULT/"paired/864-d3-research/summary.json").read_text())["rows"]:
    paired_rows.append({
      "parameter":row["parameter"],"setting":row["setting"],
      "operation":row["operation"],"paired_mean_delta_cycles":row["paired_mean_delta_cycles"],
      "paired_median_delta_cycles":statistics.median(row["block_deltas"]),
      "bootstrap_ci95_low":row["bootstrap_ci95_low"],
      "bootstrap_ci95_high":row["bootstrap_ci95_high"],
      "favorable_blocks":row["favorable_blocks"],"blocks":row["blocks"],
      "direction":"candidate-slower" if row["paired_mean_delta_cycles"]>0 else "candidate-faster"})
  write_csv(RESULT/"paired.csv",paired_rows,list(paired_rows[0]))
  pmu_rows=[]
  for directory in sorted((RESULT/"pmu").iterdir()):
    record=json.loads((directory/"summary.json").read_text())
    for component,events in record["baseline_adjusted_per_operation"].items():
      pmu_rows.append({"profile":directory.name,"component":component,**events})
  fields=["profile","component","cycles:u","instructions:u","mem_inst_retired.all_loads:u","mem_inst_retired.all_stores:u","ipc"]
  write_csv(RESULT/"pmu.csv",pmu_rows,fields)
  audit={p:json.loads((RESULT/"audit"/f).read_text()) for p,f in
         (("768","768-gt32.json"),("864","864-d3-mr32.json"),("1152","1152-exp017.json"))}
  fixed_layout={name:{"sha256":sha256_file(RESULT/"fixed-build"/name/"measure"),
                      "sections":section_sizes(RESULT/"fixed-build"/name/"measure")}
                for name in ("768-official-normal","768-candidate-normal",
                             "1152-official-normal","1152-candidate-normal")}
  record={"schema":"ntruplus-avx2-unified-benchmark/v1","created_at":datetime.now(timezone.utc).isoformat(),
    "supercop":lock,"campaign":"/home/nuc/src/supercop-campaign-unified-20260920-001","cpu":1,
    "native":native_summary,"paired":paired_rows,"components":component_rows,
    "caller_components":caller_rows,
    "pmu":pmu_rows,"static_audit":audit,"fixed_elf_layout":fixed_layout,
    "promotion":{"768":"not-qualified: encap is not a stable win across ASLR/placement controls",
                 "864":"N/A: no fully integrated Native candidate",
                 "1152":"not-qualified: Native encap has a stable regression"}}
  (RESULT/"summary.json").write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")

  n=native_summary; c768={r["operation"]:r for r in paired_rows if r["parameter"]=="768" and r["setting"]=="normal-aslr-off"}
  c1152={r["operation"]:r for r in paired_rows if r["parameter"]=="1152" and r["setting"]=="normal-aslr-off"}
  co={r["profile"]+":"+r["operation"]:r for r in component_rows}
  d3b=co["864-d3-mr32-v2:d3_packed_t3_baseline_cycles"]["stq2"]; d3m=co["864-d3-mr32-v2:d3_packed_t3_mr32_cycles"]["stq2"]
  of=co["1152-exp017-current:official_forward_cycles"]["stq2"]; gf=co["1152-exp017-current:gt_forward_full_cycles"]["stq2"]
  ot=co["1152-exp017-current:official_tail_cycles"]["stq2"]; ht=co["1152-exp017-current:h4_exact_egress_cycles"]["stq2"]
  lines=["# NTRU+ 768 / 864 / 1152 AVX2 統整與 Benchmark（SUPERCOP 20260831）","",
  f"產生時間：{record['created_at']}。正式 Native headline 使用 pinned SUPERCOP 的未修改 `crypto_kem/measure.c`；component 數字均標為 **supercop-derived-component**。","",
  "## 結論","",
  "- **768 GT32**：Native keygen、decap 勝出；encap pooled StQ2 小幅退步，且 fixed-ELF 在 ASLR/placement 間方向不一致，因此不是完整 production winner。",
  "- **864**：只報 Official Native。D3/MR32 是 component research，重新量測仍比 baseline 慢，不能冒充 KEM candidate。",
  "- **1152 exp017**：已整合 Serializer V2 direct `hash_g` stage，但 Native encap 仍穩定慢約 0.9k cycles；不 promotion。Forward 已在同一 harness 接近 Official，主要剩餘 debt 位於 fanout/tail/caller integration。","",
  "## Provenance 與方法","",
  f"- SUPERCOP `{lock['version']}`；archive SHA-256 `{lock['archive_sha256']}`。",
  f"- Official tree hashes：768 `{lock['ntruplus768_avx2_tree_sha256']}`；864 `{lock['ntruplus864_avx2_tree_sha256']}`；1152 `{lock['ntruplus1152_avx2_tree_sha256']}`。",
  "- 768 candidate：`avx2-gt32-clean`；1152 candidate：`avx2-gt9x16-wire-h3-pairunpack-serializer-v2-exp017-sc20260831`。",
  "- Host：Intel Core Ultra 7 155H，Linux 7.0.0-31-generic；CPU 1；performance governor；Intel turbo disabled；SMT siblings `1-2`。",
  "- Native compiler policy：SUPERCOP native selection。Fixed/component policy：`gcc -march=native -mtune=native -O3 -fwrapv -fPIC -fPIE -ffunction-sections -fdata-sections -Wl,--gc-sections -gdwarf-4 -Wall`。",
  "- Native：9 fresh processes、864 observations/operation、StQ2 headline。",
  "- Fixed common compiler：O3GC；16 blocks、64 launches/setting；normal/reversed × ASLR on/off。",
  "- PMU：4096 operations/process、3 fresh processes、empty-harness subtraction；只作診斷。","",
  "## Native SUPERCOP headline","",
  "| n | operation | Official StQ2 | Candidate StQ2 | delta cycles | delta % | candidate faster launches |",
  "|---:|---|---:|---:|---:|---:|---:|" ]
  for p in ("768","1152"):
    for op in OPS:
      o=n[p]["official"][op]["stq2"]; cc=n[p]["candidate"][op]["stq2"]; d=n[p]["delta"][op]
      lines.append(f"| {p} | {op.replace('_cycles','')} | {f2(o)} | {f2(cc)} | {d['cycles']:+.2f} | {d['percent']:+.2f}% | {d['faster_launches']}/9 |")
  for op in OPS: lines.append(f"| 864 | {op.replace('_cycles','')} | {f2(n['864']['official'][op]['stq2'])} | N/A | N/A | N/A | N/A |")
  lines += ["","> 864 的 N/A 是刻意的：目前沒有完整、通過 caller/KAT 的 AVX2 KEM candidate。","",
  "## Fixed-ELF paired control（normal placement, ASLR off）","",
  "| n | operation | paired delta | bootstrap 95% CI | favorable blocks |",
  "|---:|---|---:|---:|---:|"]
  for p,rows in (("768",c768),("1152",c1152)):
    for op in OPS:
      r=rows[op]; lines.append(f"| {p} | {op.replace('_cycles','')} | {r['paired_mean_delta_cycles']:+.2f} | [{r['bootstrap_ci95_low']:+.2f}, {r['bootstrap_ci95_high']:+.2f}] | {r['favorable_blocks']}/16 |")
  lines += ["",f"完整四種設定見 [`paired.csv`](../results/ntruplus-avx2-768-864-1152-20260920/paired.csv)。768 encap 在 normal/ASLR-off 是負值，但 normal/ASLR-on 與 reversed/ASLR-on 反向；1152 encap 四種設定全部是大幅正值。","",
  "## Component profiler","","### Official common primitives（StQ2 cycles）","",
  "| n | forward small | BaseMul | BaseMulScale | BaseInv | inverse | frombytes | tobytes | poly mul small |","|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
  for p in ("768","864","1152"):
    q=lambda op: co[f"{p}-official-common-v3:{op}_cycles"]["stq2"]
    lines.append(f"| {p} | {q('forward_small'):.2f} | {q('basemul'):.2f} | {q('basemul_scale'):.2f} | {q('baseinv'):.2f} | {q('inverse'):.2f} | {q('poly_frombytes'):.2f} | {q('poly_tobytes'):.2f} | {q('poly_mul_small'):.2f} |")
  lines += ["","### Official caller building blocks（StQ2 cycles）","",
  "| n | hash_f | hash_g | hash_h | SOTP encode | SOTP decode | add | sub | CBD1 | crepmod3 |",
  "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
  for p in ("768","864","1152"):
    q=lambda op: co[f"{p}-official-common-v3:{op}_cycles"]["stq2"]
    lines.append(f"| {p} | {q('hash_f'):.2f} | {q('hash_g'):.2f} | {q('hash_h'):.2f} | {q('sotp_encode'):.2f} | {q('sotp_decode'):.2f} | {q('poly_add'):.2f} | {q('poly_sub'):.2f} | {q('cbd1'):.2f} | {q('crepmod3'):.2f} |")
  lines += ["","### 768 GT32 caller-private components","",
  "| component | StQ2 cycles |","|---|---:|"]
  for op in ("forward_frontend","forward_m_full","forward_p_full","baseinv_j1","basemul_f0_j1","basemul_general_m","basemul_scale_m","inverse_m_core","inverse_m_tail","inverse_m_full","q24_unpack_m","q24_pack_m_centered","q24_equal_m"):
    lines.append(f"| {op} | {co['768-gt32-private:'+op+'_cycles']['stq2']:.2f} |")
  lines += ["","### 864 D3/MR32 research","",f"- Packed-T3 baseline：`{d3b:.2f}` cycles。",f"- Direct `vpmaddwd`/MR32：`{d3m:.2f}` cycles，delta `{d3m-d3b:+.2f}`。",f"- 16-block paired：ASLR-off `{next(r for r in paired_rows if r['parameter']=='864' and r['setting']=='normal-aslr-off')['paired_mean_delta_cycles']:+.2f}` cycles；ASLR-on `{next(r for r in paired_rows if r['parameter']=='864' and r['setting']=='normal-aslr-on')['paired_mean_delta_cycles']:+.2f}` cycles，兩者皆 0/16 favorable blocks。","- 結論：MR32 此 realization 被拒絕；雖然 stores 較少，instruction/load pressure 更高。","",
  "### 1152 current cumulative components","",f"- Official Forward：`{of:.2f}`；GT full Forward：`{gf:.2f}`，同 harness delta `{gf-of:+.2f}` cycles。",f"- Top split：`{co['1152-exp017-current:top_split_cycles']['stq2']:.2f}` cycles。",f"- Serializer V2：`{co['1152-exp017-current:serializer_v2_cycles']['stq2']:.2f}` cycles。",f"- Serializer V2 + `hash_g`：`{co['1152-exp017-current:serializer_v2_hash_g_cycles']['stq2']:.2f}` cycles。",f"- Official tail：`{ot:.2f}`；H4 exact egress：`{ht:.2f}`，delta `{ht-ot:+.2f}` cycles。","","> Component 數字是 isolated/caller-shaped diagnostics；不得直接相加預測 Native KEM。特別是 SHAKE 的 warm repeated PMU/cycle geometry和 fresh Native caller不同。","",
  "## Keygen / Encap / Decap caller stage map","",
  "[`caller-components.csv`](../results/ntruplus-avx2-768-864-1152-20260920/caller-components.csv) 將三個 operation 的 source-resolved stage 對應到本輪實測 building block，並保留 Native total。每個 building block 都從獨立 reset/residency 開始；它們不是 cumulative cutpoints，因此報告刻意不把 isolated medians 相加成假 waterfall。完整 cumulative caller waterfall 尚未達到可發布證據標準；Native totals 才是 operation headline。","",
  "- Keygen anchors：CBD1、Forward、BaseInv、BaseMul、serialization、`hash_f`。",
  "- Encap anchors：PK decode、prehash、CBD1、r/m Forward、r serialization + `hash_g`、SOTP、MulAdd、ciphertext egress。1152 另有 fused Serializer V2 + `hash_g` 與 H4 exact-tail cutpoint。",
  "- Decap anchors：decode、BaseMulScale、inverse、crepmod3、message Forward、recovery BaseMul、recovered-r serialization + `hash_g`、SOTP decode + `hash_h`、reencryption。","",
  "## PMU 與 linked audit","",f"- 864 D3 PMU：baseline `{next(r for r in pmu_rows if r['profile']=='864-d3-mr32-v2' and r['component']=='d3_baseline')['instructions:u']:.1f}` instructions、MR32 `{next(r for r in pmu_rows if r['profile']=='864-d3-mr32-v2' and r['component']=='d3_mr32')['instructions:u']:.1f}`；MR32 retired loads 也明顯增加。",f"- 1152 PMU：GT Forward約 `{next(r for r in pmu_rows if r['profile']=='1152-exp017' and r['component']=='gt_forward')['instructions:u']:.1f}` instructions/op，Official約 `{next(r for r in pmu_rows if r['profile']=='1152-exp017' and r['component']=='official_forward')['instructions:u']:.1f}`；GT instructions較少，但 loads較多。","- 完整 cycles/instructions/loads/stores/IPC 見 [`pmu.csv`](../results/ntruplus-avx2-768-864-1152-20260920/pmu.csv)。","","### Fixed Native ELF size（normal placement）","","| ELF | .text bytes | .rodata bytes | SHA-256 |","|---|---:|---:|---|"]
  for name in ("768-official-normal","768-candidate-normal","1152-official-normal","1152-candidate-normal"):
    entry=fixed_layout[name]
    lines.append(f"| {name} | {entry['sections']['.text']} | {entry['sections']['.rodata']} | `{entry['sha256']}` |")
  lines += ["","### Hot-symbol audit","",f"- 768 GT32 linked component ELF：`.text={audit['768']['sections']['.text']}`、`.rodata={audit['768']['sections']['.rodata']}` bytes；除 `baseinv_j1` 為16-byte offset外，其餘列入 audit 的 hot entries為32-byte aligned；leaf functions仍含既有 `vzeroupper`。",f"- 864 D3 research ELF：`.text={audit['864']['sections']['.text']}`、`.rodata={audit['864']['sections']['.rodata']}` bytes；baseline/MR32 entries均為32-byte aligned。",f"- 1152 exp017 component ELF：`.text={audit['1152']['sections']['.text']}`、`.rodata={audit['1152']['sections']['.rodata']}` bytes；Forward與H4 entries為32-byte aligned，Serializer V2 `hash_g` C bridge為16-byte aligned。","- 完整 symbol instruction/routing/stack/branch audit 位於 `results/.../audit/`。","",
  "## Correctness 與安全 gates","","- 768 clean：100-vector frozen KAT byte-exact；ASan/UBSan KAT通過；32 valid/tampered API trials、invalid-PK zeroization、immutability與canary通過。","- 1152 exp017：100-vector frozen KAT byte-exact；ASan/UBSan KAT通過；相同 API/invalid/canary gates通過。","- 1152 Serializer V2：1,000-case exact wire-byte differential、retained scale-1 `r` immutability與direct `hash_g` byte-exact gates通過；H4 C11 exact egress的semantic/canonical/machine-wire、overlap、decoder與linked structural gates通過。","- Public KEM API沒有宣告 overlapping-buffer contract，因此本輪不宣稱 public API alias support；內部 primitive alias gates仍沿用各 clean/experiment 的既有 differential evidence。","- 864 D3/MR32：10,003 tile differential cases、canonical equality、immutability、alignment與canary通過；但 performance rejection維持。","- SUPERCOP Native try/compile/measure均完成，沒有 `tryfails`/`measurefails`。","",
  "## 優化盤點","","### 已整合","","- 768：GT32/TILE4、P/J1 keygen、persistent-M encap/decap、Q24 native codecs、batch BaseInv。","- 1152：persistent-AoS、Natural-Q、T0-beta、scale-1 lazy Forward、MA2、H3 ingress、H4 C11 egress、pair-unpack、Serializer V2 direct `hash_g`。","","### 保留研究但未進 production","","- 864 D3/MR32：correct但較慢，未接 KEM。","- 1152 W1/multi-row wavefront與其他尚未 caller-complete的 Forward experiments。","","### 已拒絕","","- 1152 D1 pair-resident fusion：caller-shaped timing regression。","- 864 plane-major relocation與D3 MR32 current realization：無 structural/cycle win。","","## Promotion 判定","","- **768：不 promotion 為全操作 winner。** Keygen/decap有可靠 win，但 encap方向受 ASLR/placement影響且 Native pooled略退步。","- **864：N/A。** 沒有完整 Native candidate。","- **1152：不 promotion。** Fixed paired encap四種設定全部顯著退步；tail仍是主要可攻 debt之一。","","Machine-readable evidence：[`summary.json`](../results/ntruplus-avx2-768-864-1152-20260920/summary.json)、[`native.csv`](../results/ntruplus-avx2-768-864-1152-20260920/native.csv)、[`components.csv`](../results/ntruplus-avx2-768-864-1152-20260920/components.csv)、[`caller-components.csv`](../results/ntruplus-avx2-768-864-1152-20260920/caller-components.csv)、[`paired.csv`](../results/ntruplus-avx2-768-864-1152-20260920/paired.csv)、[`pmu.csv`](../results/ntruplus-avx2-768-864-1152-20260920/pmu.csv)。"]
  DOC.parent.mkdir(parents=True,exist_ok=True); DOC.write_text("\n".join(lines)+"\n")
  print(f"generated {DOC}"); return 0
if __name__=="__main__": raise SystemExit(main())
