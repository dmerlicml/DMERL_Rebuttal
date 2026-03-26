#!/usr/bin/env python3
"""Combine matching plots or GIFs from subfolders into side-by-side comparisons."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from PIL import Image, ImageDraw, ImageSequence

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".gif"}


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description=(
            "Combine plots/GIFs with the same filename from multiple subfolders in "
            "MultimodalActions."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=script_dir,
        help="Root folder containing comparison subfolders.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output folder for combined files (default: <root>/combined).",
    )
    parser.add_argument(
        "--folders",
        nargs="*",
        default=None,
        help="Specific subfolder names to include (default: all immediate subfolders).",
    )
    parser.add_argument(
        "--names",
        nargs="*",
        default=None,
        help="Specific filenames to combine (e.g., histo.png multi_agents.gif).",
    )
    parser.add_argument(
        "--padding",
        type=int,
        default=18,
        help="Padding in pixels around and between panels.",
    )
    parser.add_argument(
        "--background",
        default="white",
        help="Canvas background color (e.g., white, black, #f5f5f5).",
    )
    parser.add_argument(
        "--no-labels",
        action="store_true",
        help="Disable subfolder name labels above each panel.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files.",
    )
    return parser.parse_args()


def resolve_folders(root: Path, folder_names: Sequence[str] | None, output_dir: Path) -> List[Path]:
    if folder_names:
        folders = [root / name for name in folder_names]
    else:
        folders = [p for p in root.iterdir() if p.is_dir()]

    resolved = []
    for folder in sorted(folders):
        if folder.resolve() == output_dir.resolve():
            continue
        if folder.name.startswith("."):
            continue
        if not folder.exists():
            print(f"[WARN] Missing folder: {folder}")
            continue
        resolved.append(folder)

    return resolved


def collect_matching_files(
    folders: Sequence[Path], selected_names: Sequence[str] | None
) -> Dict[str, List[Tuple[str, Path]]]:
    selected_set = set(selected_names) if selected_names else None
    grouped: Dict[str, List[Tuple[str, Path]]] = {}

    for folder in folders:
        for file_path in sorted(folder.iterdir()):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            if selected_set and file_path.name not in selected_set:
                continue
            grouped.setdefault(file_path.name, []).append((folder.name, file_path))

    return grouped


def get_label_height(with_labels: bool) -> int:
    return 24 if with_labels else 0


def combine_images(
    entries: Sequence[Tuple[str, Path]],
    output_path: Path,
    padding: int,
    background: str,
    with_labels: bool,
) -> None:
    loaded = [(label, Image.open(path).convert("RGBA")) for label, path in entries]
    label_h = get_label_height(with_labels)

    max_height = max(img.height for _, img in loaded)
    total_width = padding * (len(loaded) + 1) + sum(img.width for _, img in loaded)
    total_height = padding * 2 + label_h + max_height

    canvas = Image.new("RGBA", (total_width, total_height), color=background)
    draw = ImageDraw.Draw(canvas)
    font = ImageFontCache.default()

    x = padding
    for label, img in loaded:
        y = padding + label_h + (max_height - img.height) // 2
        canvas.paste(img, (x, y), img)
        if with_labels:
            text_w = draw.textlength(label, font=font)
            text_x = x + max((img.width - int(text_w)) // 2, 0)
            draw.text((text_x, padding), label, fill="black", font=font)
        x += img.width + padding

    save_static(canvas, output_path)


def save_static(image: Image.Image, output_path: Path) -> None:
    if output_path.suffix.lower() in {".jpg", ".jpeg"}:
        image.convert("RGB").save(output_path, quality=95)
    else:
        image.save(output_path)


def load_gif_frames(path: Path) -> Tuple[List[Image.Image], List[int]]:
    gif = Image.open(path)
    frames: List[Image.Image] = []
    durations: List[int] = []
    for frame in ImageSequence.Iterator(gif):
        frames.append(frame.convert("RGBA"))
        durations.append(int(frame.info.get("duration", gif.info.get("duration", 100))))
    if not frames:
        raise ValueError(f"No frames found in GIF: {path}")
    return frames, durations


def combine_gifs(
    entries: Sequence[Tuple[str, Path]],
    output_path: Path,
    padding: int,
    background: str,
    with_labels: bool,
) -> None:
    label_h = get_label_height(with_labels)
    font = ImageFontCache.default()

    gif_data = []
    for label, path in entries:
        frames, durations = load_gif_frames(path)
        panel_w = max(frame.width for frame in frames)
        panel_h = max(frame.height for frame in frames)
        gif_data.append((label, frames, durations, panel_w, panel_h))

    max_frame_count = max(len(frames) for _, frames, _, _, _ in gif_data)
    max_height = max(panel_h for _, _, _, _, panel_h in gif_data)
    total_width = padding * (len(gif_data) + 1) + sum(panel_w for _, _, _, panel_w, _ in gif_data)
    total_height = padding * 2 + label_h + max_height

    combined_frames: List[Image.Image] = []
    combined_durations: List[int] = []

    for frame_idx in range(max_frame_count):
        canvas = Image.new("RGBA", (total_width, total_height), color=background)
        draw = ImageDraw.Draw(canvas)

        x = padding
        frame_durations = []
        for label, frames, durations, panel_w, panel_h in gif_data:
            src_idx = min(frame_idx, len(frames) - 1)
            frame = frames[src_idx]

            fx = x + (panel_w - frame.width) // 2
            fy = padding + label_h + (max_height - frame.height) // 2
            canvas.paste(frame, (fx, fy), frame)

            if with_labels:
                text_w = draw.textlength(label, font=font)
                text_x = x + max((panel_w - int(text_w)) // 2, 0)
                draw.text((text_x, padding), label, fill="black", font=font)

            frame_durations.append(durations[src_idx])
            x += panel_w + padding

        combined_frames.append(canvas)
        combined_durations.append(max(frame_durations) if frame_durations else 100)

    combined_frames[0].save(
        output_path,
        save_all=True,
        append_images=combined_frames[1:],
        duration=combined_durations,
        loop=0,
        disposal=2,
    )


class ImageFontCache:
    _font = None

    @classmethod
    def default(cls):
        if cls._font is None:
            from PIL import ImageFont

            cls._font = ImageFont.load_default()
        return cls._font


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    output_dir = (args.output or (root / "combined")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    folders = resolve_folders(root, args.folders, output_dir)
    if len(folders) < 2:
        raise SystemExit("Need at least two valid subfolders to combine plots.")

    grouped = collect_matching_files(folders, args.names)
    if not grouped:
        raise SystemExit("No matching files found to combine.")

    combined_count = 0
    for file_name in sorted(grouped):
        entries = sorted(grouped[file_name], key=lambda x: x[0])
        if len(entries) < 2:
            continue

        output_path = output_dir / file_name
        if output_path.exists() and not args.overwrite:
            print(f"[SKIP] {file_name} already exists (use --overwrite).")
            continue

        suffix = output_path.suffix.lower()
        try:
            if suffix == ".gif":
                combine_gifs(
                    entries=entries,
                    output_path=output_path,
                    padding=args.padding,
                    background=args.background,
                    with_labels=not args.no_labels,
                )
            else:
                combine_images(
                    entries=entries,
                    output_path=output_path,
                    padding=args.padding,
                    background=args.background,
                    with_labels=not args.no_labels,
                )
            combined_count += 1
            print(f"[OK] Wrote {output_path}")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[WARN] Failed for {file_name}: {exc}")

    if combined_count == 0:
        print("No files were combined (possibly due to existing outputs or missing pairs).")
    else:
        print(f"Combined {combined_count} file(s) into {output_dir}")


if __name__ == "__main__":
    main()
