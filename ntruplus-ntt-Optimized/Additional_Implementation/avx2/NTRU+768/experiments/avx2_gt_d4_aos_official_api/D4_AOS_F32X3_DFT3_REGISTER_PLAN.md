# Compact DFT3 register plan

- `ymm0..ymm2`: Y0/Y1/Y2, dead after raw output formation
- `ymm3`: delta, then the single shared omega term
- `ymm4`: Montgomery low/correction
- `ymm5..ymm7`: raw then reduced D0/D1/D2
- `ymm8..ymm10`: independent Barrett quotients
- `ymm11`: q
- `ymm12`: Barrett reciprocal
- `ymm13`: omega qinv
- `ymm14`: signed Montgomery omega
- `ymm15`: free

Peak use is 15 YMM registers. There is no call, stack slot, spill, input reread,
coefficient transpose, or semantic DFT3 materialization inside the macro.
