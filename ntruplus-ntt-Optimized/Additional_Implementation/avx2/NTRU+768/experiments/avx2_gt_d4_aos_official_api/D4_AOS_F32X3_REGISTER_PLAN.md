# F32X3 inverse register plan

Target interval allocation: `ymm0..2` three row loads / D0-D2; `ymm3..5` omega Montgomery and Barrett temporaries; `ymm6..9` branch merge and factors; `ymm10..12` normalization/output formation; `ymm13..15` q, qinv, and constants. Peak target is 16 and DFT3 results have no semantic store. This is a design contract; compiler validation awaits the factorized intrinsics implementation.
