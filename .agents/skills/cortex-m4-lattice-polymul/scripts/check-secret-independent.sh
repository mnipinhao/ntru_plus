#!/bin/sh
# Conservative secret-independence grep checks for Cortex-M4 code.

tool_name=check-secret-independent
strict=0

usage() {
  printf 'usage: sh scripts/check-secret-independent.sh [--strict] <file-or-dir>...\n' >&2
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --strict) strict=1; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) printf '%s: error: unknown option: %s\n' "$tool_name" "$1" >&2; usage; exit 2 ;;
    *) break ;;
  esac
done

if [ "$#" -eq 0 ]; then
  usage
  exit 2
fi

tmp_root=${TMPDIR:-/tmp}
file_list=$(mktemp "$tmp_root/check-secret-files.XXXXXX") || exit 2
target_list=$(mktemp "$tmp_root/check-secret-target.XXXXXX") || { rm -f "$file_list"; exit 2; }
pattern_file=$(mktemp "$tmp_root/check-secret-patterns.XXXXXX") || { rm -f "$file_list" "$target_list"; exit 2; }
match_file=$(mktemp "$tmp_root/check-secret-matches.XXXXXX") || { rm -f "$file_list" "$target_list" "$pattern_file"; exit 2; }
trap 'rm -f "$file_list" "$target_list" "$pattern_file" "$match_file"' 0 HUP INT TERM

patterns='if[[:space:]]*\(.*(secret|priv|sk|key|coeff|coef|poly|a\[|b\[|f\[|g\[)
while[[:space:]]*\(.*(secret|priv|sk|key|coeff|coef|poly|a\[|b\[|f\[|g\[)
\?.*:
\[[^]]*(secret|priv|sk|key|coeff|coef)[^]]*\]
(table|twiddle|root|zetas?)[A-Za-z0-9_]*[[:space:]]*\[[^]]*(coeff|coef|secret|priv|sk|key)[^]]*\]'
printf '%s\n' "$patterns" > "$pattern_file"

input_error=0
for target in "$@"; do
  if [ ! -e "$target" ]; then
    printf '%s: error: input does not exist: %s\n' "$tool_name" "$target" >&2
    input_error=1
  elif [ -f "$target" ]; then
    case "$target" in
      *.c|*.h|*.cc|*.cpp|*.s|*.S|*.inc) printf '%s\n' "$target" >> "$file_list" ;;
      *) printf '%s: error: unsupported source file: %s\n' "$tool_name" "$target" >&2; input_error=1 ;;
    esac
  elif [ -d "$target" ]; then
    : > "$target_list"
    if ! find "$target" -type f \( -name '*.c' -o -name '*.h' -o -name '*.cc' -o -name '*.cpp' -o -name '*.s' -o -name '*.S' -o -name '*.inc' \) -print > "$target_list"; then
      printf '%s: error: could not walk directory: %s\n' "$tool_name" "$target" >&2
      input_error=1
    elif [ ! -s "$target_list" ]; then
      printf '%s: error: no supported source files under: %s\n' "$tool_name" "$target" >&2
      input_error=1
    else
      sed -n 'p' "$target_list" >> "$file_list"
    fi
  else
    printf '%s: error: input is not a regular file or directory: %s\n' "$tool_name" "$target" >&2
    input_error=1
  fi
done

files_scanned=0
warn_count=0
while IFS= read -r file; do
  [ -n "$file" ] || continue
  if [ ! -r "$file" ]; then
    printf '%s: error: input is not readable: %s\n' "$tool_name" "$file" >&2
    input_error=1
    continue
  fi
  files_scanned=$((files_scanned + 1))
  while IFS= read -r pattern; do
    [ -n "$pattern" ] || continue
    grep -nE "$pattern" "$file" > "$match_file" 2>/dev/null
    grep_status=$?
    if [ "$grep_status" -gt 1 ]; then
      printf '%s: error: grep failed for: %s\n' "$tool_name" "$file" >&2
      input_error=1
      continue
    fi
    while IFS= read -r line; do
      [ -n "$line" ] || continue
      printf '%s:%s: warning[CT001]: review possible secret-dependent branch, select, or memory access\n' "$file" "$line"
      warn_count=$((warn_count + 1))
    done < "$match_file"
  done < "$pattern_file"
done < "$file_list"

printf '%s: files scanned: %d; warnings: %d\n' "$tool_name" "$files_scanned" "$warn_count"
if [ "$input_error" -ne 0 ] || [ "$files_scanned" -eq 0 ]; then
  exit 2
fi
if [ "$strict" -eq 1 ] && [ "$warn_count" -gt 0 ]; then
  exit 1
fi
exit 0
