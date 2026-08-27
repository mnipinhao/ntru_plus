# GT32-QL2-VIRTUAL-PRODUCT-105

This experiment starts from the qualified 104 QL2 research architecture and
reopens only the B3-product materialization boundary.  It retains the three
raw B3 output scratch stores/reloads required by the saturated 16-YMM quartic
DAG, but deletes the four final QL2 stores and four later serializer reloads
per tile.

The candidate uses one compact B3 loop and twelve bounded final-Q/pack
continuation stubs selected by one indirect jump per tile.  It does not inline
twelve copies of the B3 arithmetic and does not modify production.

A second executable mutation replaces the indirect dispatch with one
direct-call tile core and twelve fall-through continuations.  `RESULTS.md`
records why both forms lose despite deleting the intended memory traffic.
