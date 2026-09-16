"""Experiment-local A76 TBL3 parser and measured timing model.

The active Slothy checkout does not yet describe the three-register TBL form.
Keep the extension local to this experiment.  The timing values come from the
Pi 5 isolated throughput/dependency microbenchmark in pi-results/unscheduled.
"""

from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch, cortex_a76 as Target


class vtbl_3(Arch.AArch64Instruction):
    pattern = "tbl <Vd>.16b, {<Va>.16b, <Vb>.16b, <Vc>.16b}, <Ve>.16b"
    inputs = ["Va", "Vb", "Vc", "Ve"]
    outputs = ["Vd"]

    @classmethod
    def make(cls, src):
        obj = Arch.AArch64Instruction.build(cls, src)
        obj.args_in_combinations = [
            ([0, 1, 2], [[f"v{i}", f"v{i + 1}", f"v{i + 2}"] for i in range(30)])
        ]
        return obj


def install(*, timing):
    if vtbl_3 not in Arch.Instruction.all_subclass_leaves:
        Arch.Instruction.all_subclass_leaves.append(vtbl_3)

    # Both vector pipes accept TBL.  Occupying the selected pipe for two model
    # cycles gives one TBL3/cycle aggregate throughput across the two pipes.
    # The four-cycle dependency latency is the conservative integer rounding
    # of the measured 3.938 cycles/TBL3 chain.
    Target.execution_units[vtbl_3] = Target.ExecutionUnit.V()
    Target.inverse_throughput[vtbl_3] = 2 if timing else 1
    Target.default_latencies[vtbl_3] = 4 if timing else 1

    probe = Arch.Instruction.parser(
        SourceLine("tbl V<out>.16b, {V<a>.16b, V<b>.16b, V<c>.16b}, V<index>.16b")
    )[0]
    assert probe.args_in == ["a", "b", "c", "index"]
    assert probe.args_out == ["out"]
    assert len(probe.args_in_combinations[0][1]) == 30
    assert Arch.Instruction.parser(SourceLine(probe.write()))[0].args_in == probe.args_in


MEASURED = {
    "pi5_tbl2_throughput_cycles": 0.4373786375,
    "pi5_tbl3_throughput_cycles": 0.9805856875,
    "pi5_tbl2_dependency_cycles": 1.9379854,
    "pi5_tbl3_dependency_cycles": 3.9383411125,
    "model_tbl3_inverse_throughput": 2,
    "model_tbl3_latency": 4,
}
