# Yang-style assembly application ledger

For compact DFT3, one `Y2-Y1` delta feeds one signed Montgomery omega chain. The omega
term is shared by D1 and D2; D0/D1/D2 are each formed once. Inputs die before the three
independent packed Barrett chains, allowing D0/D1/D2 to remain register-resident.

Immediate Barrett remains at the proved boundary. The complete endpoint consumes each
reduced D value immediately with generated direct-CRT P/Q factors. This folds inverse-96,
untwist, branch merge and normalization into two Montgomery chains without changing the
accepted DFT3 arithmetic or its reduction placement.

Compared with separate output evaluation, the microkernel removes two repeated omega
chains and all coefficient-major reconstruction. DFT3 constants are loaded once before
the sixteen-group loop. Terminal factor records are consumed in `t`-major D0/D1/D2 order;
no DFT3 result is materialized.

The complete Y1 and Y2 endpoints are correct and spill-free, but Y2 measures 868-880
TSC versus Official 498 and GT SoA 828-840. The implementation therefore remains a
default-off, rejected realization rather than a production application.
