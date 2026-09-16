# D1-P3B8 decision

Decision: **reject as a performance optimization.**

Direct immediate input addressing removes exactly 106 retired instructions
per full call and changes no other important target-object count, but the Pi 5
median regresses by 2.742 cycles.  This establishes that input-address
materialization is hidden behind the current Neon work and is not the ToBytes
critical path.

Do not combine this change with another candidate merely to improve its static
instruction count.  Keep P3B6 at 1502.443 cycles as the measured champion and
move the next search to vector lane routing or packing/store dependencies.
