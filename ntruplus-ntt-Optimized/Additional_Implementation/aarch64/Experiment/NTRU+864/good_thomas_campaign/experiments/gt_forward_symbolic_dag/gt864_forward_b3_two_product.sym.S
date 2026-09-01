/* M5G symbolic two-product B3; no physical vector allocation. */
// live-in: V<a>, V<b>, V<c>, V<roots>, V<modq>
// live-out: V<a>=y0, V<b>=y1, V<c>=y2
// live-through pressure: fifteen data vectors are reserved by optimize.py
// roots: h[0]=rho, h[1]=rho_prime, h[2]=rho2, h[3]=rho2_prime
// range: prove_exact_dag.py; maximum signed16 magnitude 28568
// forbidden DAG: no 2a or 3a intermediate
// spills: forbidden; physical v8-v15: forbidden

gt864_forward_b3_slothy_start:
    orr       V<saved_a>.16b, V<a>.16b, V<a>.16b
    add       V<a>.8h, V<a>.8h, V<b>.8h
    add       V<a>.8h, V<a>.8h, V<c>.8h

    sqrdmulh  V<quotient>.8h, V<b>.8h, V<roots>.h[1]
    mul       V<b>.8h, V<b>.8h, V<roots>.h[0]
    mls       V<b>.8h, V<quotient>.8h, V<modq>.8h

    sqrdmulh  V<quotient>.8h, V<c>.8h, V<roots>.h[3]
    mul       V<c>.8h, V<c>.8h, V<roots>.h[2]
    mls       V<c>.8h, V<quotient>.8h, V<modq>.8h

    add       V<b>.8h, V<b>.8h, V<c>.8h
    add       V<b>.8h, V<b>.8h, V<saved_a>.8h

    sub       V<c>.8h, V<saved_a>.8h, V<a>.8h
    sub       V<quotient>.8h, V<saved_a>.8h, V<b>.8h
    add       V<c>.8h, V<c>.8h, V<quotient>.8h
    add       V<c>.8h, V<c>.8h, V<saved_a>.8h
gt864_forward_b3_slothy_end:
