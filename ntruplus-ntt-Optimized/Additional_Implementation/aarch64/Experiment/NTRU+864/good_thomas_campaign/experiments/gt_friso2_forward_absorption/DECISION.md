# Decision

**REJECT M5U-CF0 explicit live-out absorption.**

Do not implement the matching explicit Inverse schedule and do not connect
this candidate to KEM or SUPERCOP.  Its Forward pair alone exceeds the entire
measured BaseMul saving, so an ordinary denormalization consumer cannot rescue
the operation.

Keep M5R-D/FR-0 as the active Forward experiment and keep direct-wide FR-ISO2
BaseMul isolated.  Reopen FR-ISO2 only with an exact scaled-NTT9 DAG that
algebraically deletes or merges scale multiplications inside existing radix-3
nodes.  The next candidate must first show a static reduction relative to the
72-mulmod CF0 control and then beat CF0 and the 334.194-cycle operation budget
on Pi 5 without another memory boundary.
