# Multimodal Plot Combiner

This folder contains combined comparison plots and the utility script:

- `utils/combine_plots.py`

## Requirements

Install Pillow:

```bash
pip install pillow
```

## Basic usage

Run from the repository root:

```bash
python MultimodalActions/utils/combine_plots.py \
  --root MultimodalActions/utils \
  --output MultimodalActions \
  --overwrite
```

The script:

- scans each selected method folder recursively
- matches files by relative path (so newly added nested subfolders are included)
- combines matching images/GIFs side-by-side
- places `DME-*` methods on the top row and non-`DME-*` methods on the bottom row

## GIF speed

Use `--gif-speed` to control playback speed:

- `1.0` = original speed
- `2.0` = faster
- `0.5` = slower

Example:

```bash
python MultimodalActions/utils/combine_plots.py \
  --root MultimodalActions/utils \
  --output MultimodalActions \
  --dppo-zoom 1. \
  --gif-speed 0.25 \
  --overwrite
```

## Useful options

- `--folders DME-PPO DPPO WPO`: only include selected method folders
- `--names histo.png multi_agents.gif`: only combine specific names/paths
- `--columns 4`: fallback max columns when `DME-*` vs non-`DME-*` grouping is not applicable
- `--no-labels`: hide folder labels above each panel
- `--padding 24`: adjust spacing between panels
- `--separator-width 2`: black border width around each method panel
- `--dppo-zoom 0.9`: zoom DPPO out in `multi_agents` panels (`<1` out, `>1` in)
- `--background "#ffffff"`: set canvas background color

Get full CLI help:

```bash
python MultimodalActions/utils/combine_plots.py --help
```
