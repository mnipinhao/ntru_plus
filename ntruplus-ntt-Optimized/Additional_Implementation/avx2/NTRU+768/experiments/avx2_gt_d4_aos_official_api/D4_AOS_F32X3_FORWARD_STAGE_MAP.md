# F32X3 Forward stage map

Per row: bit-reverse input, then radix-2 lengths 2,4,8,16,32. Length 2 swaps/adds the two compact quartics inside each YMM; later layers pair same-`u` quartics in two YMM blocks. DFT3 combines matching physical blocks from rows 0/1/2 and writes final `R` rows directly. Twiddles repeat four times per quartic group; all arithmetic stays d4AoS.
