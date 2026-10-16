## Stage 4 [r6]: heliosli's R6 ConvNeXt-small and the v62 recipe, blended with v61's output (v63)

v61's `submission.csv` is complete at this point. The cells below add the R6 bundle `fe055406fad6a12f` (flip-TTA) exactly as
in v62 (its asset cell runs from a file in its own namespace and temp folder `probe_r6`; its controller and arguments as v62's
launch cell), recompute v62's per-finding stage-3 recipe on R384 + this notebook's R224 (anatomical mirror) + R6, and write
`mix = pct(0.5 pct(v61 anchor before the reader) + 0.5 pct(v62 recipe))`, then the reader at v61's 0.10 under v61's own
decision: `final = pct(0.9 pct(mix) + 0.1 pct(reader))` (without the reader, `final = mix`). Any skip, timeout, failure or implausible output restores v61's
`submission.csv` byte for byte. The stage starts only if the time left before the 8.65 h cut-off is at least 1.3 x this run's
R7 controller time (and 20 min); its process group is killed at the cut-off.
