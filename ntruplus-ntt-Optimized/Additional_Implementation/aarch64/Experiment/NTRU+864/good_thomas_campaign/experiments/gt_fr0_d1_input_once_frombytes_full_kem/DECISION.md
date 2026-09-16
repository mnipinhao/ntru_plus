# D1-P3B12 decision

Decision: **accept P3B11 as the experimental production-shaped FromBytes
champion; Production remains unchanged.**

The full-KEM oracle, relocation audit and paired Pi 5 PMU pass.  Encaps saves
242.063 cycles and Decaps saves 817.050 cycles versus frozen P3B4.  Their exact
instruction/branch changes equal one and three copies of the isolated
FromBytes delta.  Keypair has no FromBytes call and exactly zero retired-count
change.

Do not combine another FromBytes modification with the next experiment.  Move
ToBytes to a separate structured-routing/completion-order gate; P3B7, P3B8 and
P3B10 already reject local instruction deletion and partner scratch under the
P3B6 schedule.
