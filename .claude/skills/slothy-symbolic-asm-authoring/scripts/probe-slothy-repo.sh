#!/usr/bin/env bash
set -u

ROOT="${1:-.}"
cd "$ROOT" 2>/dev/null || {
  echo "probe-slothy-repo: cannot enter $ROOT" >&2
  exit 1
}

if git_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  cd "$git_root" || exit 1
else
  git_root="$(pwd)"
fi

echo "repo_root: $git_root"

echo "slothy_locations:"
found_slothy=0
for path in slothy extern/slothy external/slothy third_party/slothy vendor/slothy; do
  if [ -d "$path" ]; then
    echo "  - $path"
    found_slothy=1
  fi
done
if [ "$found_slothy" -eq 0 ]; then
  echo "  - none_found"
fi

echo "python_interpreters:"
for path in venv/bin/python .venv/bin/python extern/slothy/venv/bin/python python3; do
  if command -v "$path" >/dev/null 2>&1 || [ -x "$path" ]; then
    echo "  - $path"
  fi
done

echo "slothy_venv_rule:"
if [ -x "venv/bin/python" ]; then
  echo "  preferred_command_prefix: venv/bin/python"
elif [ -x ".venv/bin/python" ]; then
  echo "  preferred_command_prefix: .venv/bin/python"
elif [ -x "extern/slothy/venv/bin/python" ]; then
  echo "  preferred_command_prefix: extern/slothy/venv/bin/python"
else
  echo "  preferred_command_prefix: none_found"
  echo "  note: create or identify the repo venv before handing off Slothy commands; use global python only with explicit approval"
fi

echo "slothy_drivers:"
find . -path ./.git -prune -o \( -name 'optimize.py' -o -name '*slothy*driver*.py' -o -name 'slothy-cli' \) -type f -print | sed 's#^\./#  - #'

echo "assembly_sources:"
find . -path ./.git -prune -o \( -name '*.S' -o -name '*.s' -o -name '*.asm' \) -type f -print | sed 's#^\./#  - #' | head -200

echo "slothy_region_labels:"
if command -v rg >/dev/null 2>&1; then
  rg -n 'slothy_(start|end)|_slothy_(start|end)' -g '*.S' -g '*.s' -g '*.asm' . | head -200 | sed 's#^\./#  - #'
else
  grep -RInE 'slothy_(start|end)|_slothy_(start|end)' --include='*.S' --include='*.s' --include='*.asm' . | head -200 | sed 's#^\./#  - #'
fi

echo "tests_and_benchmarks:"
find . -path ./.git -prune -o \( -iname '*test*' -o -iname '*bench*' -o -iname '*kat*' \) -type f -print | sed 's#^\./#  - #' | head -200
