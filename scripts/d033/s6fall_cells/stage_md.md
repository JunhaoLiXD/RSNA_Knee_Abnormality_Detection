## Stage 2f: nartaa's all-data S6 ConvNeXt-small, "S6F0" (the addition)

S6F0 is one ConvNeXt-small checkpoint (`E_prior_s42_fall.pt` from `nartaa/rsna-knee-s6fall-weights`, CC BY-NC 4.0; heliosli's S6 architecture
retrained by nartaa on all 4,263 competition studies with report-derived soft labels, gold-58 excluded; 0.950 public alone in nartaa's notebook
`rsna-knee-s6fall-solo`). It is run exactly as nartaa's notebook runs its component B: heliosli's older `compact_infer.py` (sha256 `34f433fe...`,
not R7's) through nartaa's launcher with `--arm E_prior`, `--amp fp16`, size 320, crop 288, v4 views from the SKM-TEA anatomy V-Net, one process
per GPU, his receipt checks and one retry of failed studies. His code bundle (`s6_extras.bin` plus files of heliosli's code dataset) and the
checkpoint are checked against pinned sha256 values first. The stage uses its own temp folder (`TMP / 's6f'`) and writes only `ours_s6f_sub.csv`,
`ours_s6f_receipt.json` and `s6f_*_log.txt`; no file or global of the R7 stage is touched. It runs in its own process groups under an absolute
cut-off that leaves the outer reader its launch allowance. Any failure, timeout, skip or malformed output leaves `S6F_OK` False and stage 3
exactly as without this stage.
