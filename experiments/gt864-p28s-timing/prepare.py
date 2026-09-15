#!/usr/bin/env python3
"""Extract P28's fixed-allocation sources and add route timing windows."""

from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
P28 = HERE.parent / "gt864-p28-paired-i16"


def window_route():
    lines = (P28 / "candidate-route.S").read_text().splitlines()
    output = []
    armed = False
    active = False
    windows = 0
    for line in lines:
        stripped = line.strip()
        if stripped == "p28_route_slothy_end:":
            armed = False
        if armed and not active and stripped and not stripped.startswith("//"):
            if stripped.endswith(":") or stripped == "ret":
                output.append(line)
                continue
            output.append(f"p28s_route_window_{windows}_start:")
            active = True
            armed = False
        output.append(line)
        if stripped == "movi v7.8h, #3":
            armed = True
        if active and stripped.startswith("str q10,"):
            output.append(f"p28s_route_window_{windows}_end:")
            windows += 1
            active = False
            armed = True
    if active or windows != 108:
        raise RuntimeError(f"route window extraction failed: active={active} windows={windows}")
    (HERE / "baseline-route.windowed.S").write_text("\n".join(output) + "\n")


def main():
    shutil.copy2(P28 / "candidate-main.alloc.S", HERE / "baseline-main.alloc.S")
    shutil.copy2(P28 / "candidate-tail.alloc.S", HERE / "baseline-tail.alloc.S")
    window_route()
    print("prepared fixed-allocation main, tail, and 108 route windows")


if __name__ == "__main__":
    main()
