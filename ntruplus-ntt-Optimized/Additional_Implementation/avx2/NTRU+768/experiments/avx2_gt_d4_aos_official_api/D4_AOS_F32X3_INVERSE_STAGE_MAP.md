# F32X3 Inverse stage map

Inverse NTT32 runs on each `R` row first, using reciprocal stages 32,16,8,4,2 and inverse-32 scale. Then one inverse DFT3 consumes `V[0,t]`, `V[1,t]`, and `V[2,t]` for each compact block. Its three results map directly to Good–Thomas `r` coordinates, untwist, CRT branch merge, normalization, and the existing two-qword terminal store map. This order is the required no-DFT3-scratch handoff contract for the future intrinsics path.

For a retained DFT3 result `D_r[t]`, its two compact quartics store at natural
indices `i(r,t,u)=64*r+33*(2*t+u) mod 96`.  They are not adjacent to each
other, but each quartic remains one contiguous qword; terminal work therefore
needs four qword stores per `D_r[t]` (low/high natural halves for each `u`),
not an SoA transpose or indexed coefficient-vector reconstruction.
