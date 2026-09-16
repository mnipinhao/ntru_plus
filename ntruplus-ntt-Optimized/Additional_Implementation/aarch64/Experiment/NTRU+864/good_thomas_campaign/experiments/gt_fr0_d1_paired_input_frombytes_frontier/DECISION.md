# D1-P3B14 decision

Decision: **reject adjacent-pair `LD3`; retain P3B11 FromBytes.**

Do not generate or benchmark this candidate.  Continue FromBytes work only
with a concrete vector-routing subnetwork (`TRN`/`ZIP`/`EXT`/`TBL` families)
that reduces P3B11's lane moves without increasing the coefficient memory
boundary.  Slothy is appropriate only after such a changed DAG exists.
