# D-033 tools (copied from the agent's session scratchpad on 2026-10-15)

The notebooks in `notebooks/` are the source of truth; these builders recreate them and may need path fixes (they were
written in a scratch folder: `build_v49.py` expects `mavit/v49_mavit.py`, `build_v61.py` expects `cells/` = `s6fall_cells/`,
`build_v50.py`/`build_v55.py`/`build_v60.py` were sub-agent builders).

- `rank_cross.py <snapshot before> <snapshot after>`: the D-022 rank-crossing test on two leaderboard downloads
  (`kaggle competitions leaderboard -c rsna-knee-abnormality-detection --download -p external/lb/<name>`); our team id 16678028.
- `check_probe_gates.py v49|v50 <run dir>`, `check_v48_gates.py <run dir>`: commit-run gates.
- `check_v61_gates.py [results/v61/run1]`: read-only notebook audit plus downloaded-output checks (inherited cells,
  unchanged v54 stages, S6F0/reader receipts, official format, independent blend recomputation); writes
  `codex_gate_report.json` inside the run directory. Covers placeholder studies only, not hidden-test receipts.
- `build_combo.py <ver> flip,r224,mavit`: combination builder over the probe notebooks.
- `auto_v56_v57.sh`, `auto_after_v57.sh`: examples of the background "wait, check, submit" automation.
