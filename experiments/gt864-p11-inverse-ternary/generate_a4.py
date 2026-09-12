#!/usr/bin/env python3
"""Pure-unfold the measured A2 physical schedule by two without cross-record motion."""

from pathlib import Path

P=Path(__file__).resolve().parent
source=(P/"candidate-route-a2.alloc.S").read_text()
before,rest=source.split("p11a2_route32_slothy_start:\n",1)
body,after=rest.split("p11a2_route32_slothy_end:\n",1)
before=before.replace("p11a2","p11a4").replace("mov x8, #32","mov x8, #16")
after=after.replace("p11a2","p11a4")
output=(before+"// Pure unfolding: two unchanged A2 physical schedules, no cross-record motion.\n"
        +"p11a4_route64_start:\n"+body+body+"p11a4_route64_end:\n"+after)
(P/"candidate-route-a4.S").write_text(output)
print(P/"candidate-route-a4.S")
