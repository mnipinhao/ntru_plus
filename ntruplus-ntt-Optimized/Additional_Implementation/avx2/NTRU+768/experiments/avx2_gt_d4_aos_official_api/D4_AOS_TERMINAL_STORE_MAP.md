# AoS terminal store map

After pair completion, branch 0 is low 128 and branch 1 high 128. CRT merge emits `A[0..3]` and `B[0..3]`, stored as `store64(out+4*i,A)` and `store64(out+384+4*i,B)`. This needs no `vextracti128`, 4×8 transpose, indexed output map, or coefficient-major reconstruction. A future staged inverse must preserve this two-qword terminal contract.
