#!/usr/bin/env python3
from run_gate import decode_line

assert decode_line("enc_cycles - 28000 -10+5+20") == [27990, 28005, 28020]
print("SUPERcop base+deviation parser regression: PASS")
