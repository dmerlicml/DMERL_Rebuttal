# DMERL_Rebuttal

Short reviewer guide:

- `Table/DIMEvsDMERL.pdf`: main table comparing DIME and DMERL.
- `IQM/all_envs_methods_iqm_eval_return.png`: IQM performance summary figure.
- `IQM/all_envs_methods_grid_iqm_eval_return.png`: IQM grid-style comparison figure.
- `MultimodalActions/histo.png`, `MultimodalActions/multi_agents.png`, `MultimodalActions/multi_agents.gif`: side-by-side multimodal action comparisons.
- `MultimodalActions/utils/REPPO`, `MultimodalActions/utils/REPPO-DIME`, `MultimodalActions/utils/DME-REPPO`: per-method source figures used to build combined outputs.

Rebuild combined multimodal plots:

```bash
python MultimodalActions/utils/combine_plots.py \
  --root MultimodalActions/utils \
  --output MultimodalActions \
  --overwrite
```

Notes:

- The combine script requires `Pillow` (`pip install pillow`).
- `MultimodalActions/utils/` is ignored by Git (see `.gitignore`), so generated or copied utilities there are not pushed.
