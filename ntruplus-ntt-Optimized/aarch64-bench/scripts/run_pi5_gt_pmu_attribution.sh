#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bench_dir="$(cd "${script_dir}/.." && pwd)"

perf_repeats="${PERF_RUNS:-${RUNS:-3}}"
perf_bin="${PERF_BIN:-perf}"
sudo_cmd="${SUDO-sudo}"
core="${CORE:-3}"
bench_cycles="${BENCH_CYCLES:-PERF}"
use_shake_asm="${USE_SHAKE_ASM:-0}"
n_tests="${NTESTS:-500}"
n_iterations="${NITERATIONS:-300}"
n_warmup="${NWARMUP:-50}"
stamp="$(date +%Y%m%d-%H%M%S)"
suite_dir="${SUITE_DIR:-${bench_dir}/logs/pi5-gt-pmu-${stamp}}"
dry_run="${DRY_RUN:-0}"

pmu_modes="${PMU_MODES:-invntt,basemul,basemul_add,ntt_mul_pipeline,ntt_basemul_add_pipeline,kem_dec}"

if [[ -n "${PERF_GROUPS:-}" ]]; then
  IFS=';' read -r -a event_groups <<< "${PERF_GROUPS}"
else
  event_groups=(
    "core:cycles,instructions,branches,branch-misses"
    "cache:cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses,L1-dcache-stores"
    "front:L1-icache-load-misses,dTLB-load-misses,iTLB-load-misses"
  )
fi

IFS=',' read -r -a modes <<< "${pmu_modes}"
sudo_prefix=()
if [[ -n "${sudo_cmd}" ]]; then
  sudo_prefix=("${sudo_cmd}")
fi

if [[ "${dry_run}" != "1" ]] && ! command -v "${perf_bin}" >/dev/null 2>&1; then
  {
    echo "error: perf not found (PERF_BIN=${perf_bin})."
    echo
    echo "Install the package that provides perf on the Pi, or rerun with"
    echo "PERF_BIN=/absolute/path/to/perf."
    echo
    echo "On Raspberry Pi OS/Debian this is usually:"
    echo "  sudo apt update"
    echo "  sudo apt install linux-perf"
    echo
    echo "Then verify:"
    echo "  command -v perf"
    echo "  sudo perf stat -e cycles -- taskset -c ${core} true"
  } >&2
  exit 127
fi

mkdir -p "${suite_dir}"
summary_csv="${suite_dir}/summary_pmu.csv"
perf_raw_csv="${suite_dir}/perf_events_raw.csv"
printf 'case,mode,group,events,status,make_vars,log,perf_csv\n' > "${summary_csv}"
printf 'case,mode,group,perf_csv_row\n' > "${perf_raw_csv}"

csv_quote() {
  local value="${1//\"/\"\"}"
  printf '"%s"' "${value}"
}

quote_cmd() {
  printf '$'
  printf ' %q' "$@"
  printf '\n'
}

run_logged() {
  local log="$1"
  shift
  quote_cmd "$@" | tee -a "${log}"
  if [[ "${dry_run}" == "1" ]]; then
    printf '[dry-run]\n\n' | tee -a "${log}"
    return 0
  fi
  "$@" 2>&1 | tee -a "${log}"
}

run_case() {
  local case_name="$1"
  shift
  local make_vars=("$@")
  local make_vars_text="${make_vars[*]}"

  for mode in "${modes[@]}"; do
    [[ -n "${mode}" ]] || continue
    local case_mode_dir="${suite_dir}/${case_name}/${mode}"
    mkdir -p "${case_mode_dir}"
    local build_log="${case_mode_dir}/build.log"

    {
      printf 'case=%s\n' "${case_name}"
      printf 'mode=%s\n' "${mode}"
      printf 'bench_cycles=%s\n' "${bench_cycles}"
      printf 'make_vars=%s\n' "${make_vars_text}"
      printf '\n'
    } > "${build_log}"

    run_logged "${build_log}" make clean
    run_logged "${build_log}" make \
      "CYCLES=${bench_cycles}" \
      "VARIANT=gt_opt" \
      "BENCH_MODE=${mode}" \
      "USE_SHAKE_ASM=${use_shake_asm}" \
      "NTESTS=${n_tests}" \
      "NITERATIONS=${n_iterations}" \
      "NWARMUP=${n_warmup}" \
      "${make_vars[@]}"

    for raw_group in "${event_groups[@]}"; do
      [[ -n "${raw_group}" ]] || continue
      local group_name="${raw_group%%:*}"
      local events="${raw_group#*:}"
      if [[ "${group_name}" == "${events}" ]]; then
        group_name="custom"
      fi

      local log="${case_mode_dir}/${group_name}.log"
      local perf_csv="${case_mode_dir}/${group_name}.perf.csv"
      local status="ok"

      {
        printf 'case=%s\n' "${case_name}"
        printf 'mode=%s\n' "${mode}"
        printf 'group=%s\n' "${group_name}"
        printf 'events=%s\n' "${events}"
        printf 'perf_repeats=%s\n' "${perf_repeats}"
        printf '\n'
      } > "${log}"

      if ! run_logged "${log}" "${sudo_prefix[@]}" "${perf_bin}" stat -x, -r "${perf_repeats}" -e "${events}" -o "${perf_csv}" taskset -c "${core}" ./bench; then
        status="failed"
      fi

      if [[ -s "${perf_csv}" ]]; then
        while IFS= read -r perf_row; do
          printf '%s,%s,%s,' "${case_name}" "${mode}" "${group_name}" >> "${perf_raw_csv}"
          csv_quote "${perf_row}" >> "${perf_raw_csv}"
          printf '\n' >> "${perf_raw_csv}"
        done < "${perf_csv}"
      fi

      printf '%s,%s,%s,"%s",%s,"%s",%s,%s\n' \
        "${case_name}" \
        "${mode}" \
        "${group_name}" \
        "${events}" \
        "${status}" \
        "${make_vars_text}" \
        "${log}" \
        "${perf_csv}" >> "${summary_csv}"
    done
  done
}

cd "${bench_dir}"

run_case gt_promoted_default

run_case gt_legacy_directstage123_branchfold \
  GT_INVNTT_ASM=ntruplus/asm/inv_my_ntt_directstage123_branchfold.s

run_case gt_post_branchfold_constgrp3 \
  GT_INVNTT_ASM=ntruplus/asm/inv_my_ntt_post_branchfold_constgrp3.s

run_case gt_post_branchfold_consthalf \
  GT_INVNTT_ASM=ntruplus/asm/inv_my_ntt_post_branchfold_consthalf.s

echo "wrote ${suite_dir}"
echo "summary: ${summary_csv}"
echo "perf events: ${perf_raw_csv}"

python3 - "${summary_csv}" "${suite_dir}/perf_events_summary.csv" <<'PY'
import csv
import sys
from pathlib import Path

summary_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])

rows = []
baseline = {}
with summary_path.open(newline="", encoding="utf-8") as fh:
    for item in csv.DictReader(fh):
        if item.get("status") != "ok":
            continue
        perf_csv = Path(item["perf_csv"])
        if not perf_csv.exists():
            perf_csv = summary_path.parent / item["case"] / item["mode"] / Path(item["perf_csv"]).name
        if not perf_csv.exists():
            continue
        with perf_csv.open(encoding="utf-8", errors="replace") as pf:
            for line in pf:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                cols = line.split(",")
                if len(cols) < 3:
                    continue
                try:
                    value = float(cols[0])
                except ValueError:
                    continue
                row = {
                    "case": item["case"],
                    "mode": item["mode"],
                    "group": item["group"],
                    "event": cols[2],
                    "value": f"{value:.0f}",
                    "ratio_to_promoted_default": "",
                    "perf_csv": str(perf_csv),
                }
                rows.append(row)
                if item["case"] == "gt_promoted_default":
                    baseline[(item["mode"], cols[2])] = value

for row in rows:
    base = baseline.get((row["mode"], row["event"]))
    if base:
        row["ratio_to_promoted_default"] = f"{float(row['value']) / base:.6f}"

fields = [
    "case",
    "mode",
    "group",
    "event",
    "value",
    "ratio_to_promoted_default",
    "perf_csv",
]
with out_path.open("w", newline="", encoding="utf-8") as out:
    writer = csv.DictWriter(out, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"perf summary: {out_path}")
PY
