"""Experiment-local three-register TBL support for the measured A76 target."""

from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch, cortex_a76 as Target


class vtbl_3(Arch.AArch64Instruction):
    pattern = "tbl <Vd>.16b, {<Va>.16b, <Vb>.16b, <Vc>.16b}, <Ve>.16b"
    inputs = ["Va", "Vb", "Vc", "Ve"]
    outputs = ["Vd"]

    @classmethod
    def make(cls, src):
        obj = Arch.AArch64Instruction.build(cls, src)
        obj.args_in_combinations = [([0, 1, 2], [[f"v{i}", f"v{i+1}", f"v{i+2}"] for i in range(30)])]
        return obj


def install() -> None:
    if vtbl_3 not in Arch.Instruction.all_subclass_leaves:
        Arch.Instruction.all_subclass_leaves.append(vtbl_3)
    Target.execution_units[vtbl_3] = Target.ExecutionUnit.V()
    Target.inverse_throughput[vtbl_3] = 2
    Target.default_latencies[vtbl_3] = 4
    probe = Arch.Instruction.parser(SourceLine("tbl V<o>.16b, {V<a>.16b, V<b>.16b, V<c>.16b}, V<i>.16b"))[0]
    assert probe.args_in == ["a", "b", "c", "i"]
