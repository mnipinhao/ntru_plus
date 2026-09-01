# M5M decision

Status: passed as an Experiment hard gate; not Production and not a full-path
performance claim.

Freeze the exact one-bank producer-consumer shape: 144 meaningful coefficient
loads, no coefficient scratch/store, packed main constants, bit-reversed state
naming, delayed roots load, fixed `v17/v16` tail ABI, and frozen M5K consumer.

The next hard gate is repeated-bank integration: add public loop/control and
the exact FR-0 stores around this region, prove all six banks cover every P8
input and every 864-coefficient transform-domain output exactly once, then run
the complete Forward oracle and linked-object memory/code-size audit.  Pi 5
PMU and SUPERCOP remain later promotion gates.
