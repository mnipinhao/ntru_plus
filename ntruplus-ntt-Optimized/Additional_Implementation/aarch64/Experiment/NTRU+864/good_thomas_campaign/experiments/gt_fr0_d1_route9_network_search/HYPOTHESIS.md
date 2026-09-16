# D1-P3B0 hypothesis

Observation: P3A reduces the map to twelve copies of a
`K9,9 - perfect-matching` routing primitive.

Primary bottleneck: layout/permutation.

Hypothesis: after relabeling the missing matching to the diagonal, source lane
labels are cyclic and support at least two materially different bounded Neon
networks: transpose-plus-repair and TBL gather.

Falsifier: do not emit a route9 candidate if lane labels are neither cyclic nor
replayable by an exact network, or if the static estimate approaches the
measured scalar bridge's roughly 5,207 retired instructions.
