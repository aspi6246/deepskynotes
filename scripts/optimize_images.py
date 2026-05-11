"""Batch-optimize images for the Wiruna Wanderings website."""

import sys
import os
from pathlib import Path
from PIL import Image

QUALITY_JPG = 82
MAX_WIDTH_DSS = 800
MAX_WIDTH_CHART = 1200
MAX_WIDTH_ARTICLE = 1000
THUMB_SIZE = 80


def optimize_image(src: Path, dst: Path, max_width: int, quality: int = QUALITY_JPG):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as img:
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > max_width:
            ratio = max_width / img.width
            new_h = int(img.height * ratio)
            img = img.resize((max_width, new_h), Image.LANCZOS)
        img.save(dst, 'JPEG', quality=quality, optimize=True)


def generate_thumbnail(src: Path, dst: Path, size: int = THUMB_SIZE):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as img:
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        img = img.crop((left, top, left + side, top + side))
        img = img.resize((size, size), Image.LANCZOS)
        img.save(dst, 'JPEG', quality=75, optimize=True)


def process_catalogue_images(source_dir: Path, dest_dir: Path, thumb_dir: Path | None = None):
    total_src = 0
    total_dst = 0
    count = 0

    for constellation_dir in sorted(source_dir.iterdir()):
        if not constellation_dir.is_dir():
            continue
        constellation = constellation_dir.name
        for img_path in sorted(constellation_dir.iterdir()):
            if img_path.suffix.lower() not in ('.jpg', '.jpeg', '.png'):
                continue
            name_lower = img_path.stem.lower()
            if '_dss' in name_lower:
                max_w = MAX_WIDTH_DSS
            elif '_ep' in name_lower:
                max_w = 600
            else:
                max_w = MAX_WIDTH_CHART

            dst_name = img_path.stem + '.jpg'
            dst_path = dest_dir / constellation / dst_name
            optimize_image(img_path, dst_path, max_w)

            src_size = img_path.stat().st_size
            dst_size = dst_path.stat().st_size
            total_src += src_size
            total_dst += dst_size
            count += 1

            if thumb_dir and '_dss' in name_lower:
                thumb_path = thumb_dir / f"{img_path.stem}.jpg"
                generate_thumbnail(img_path, thumb_path)

    print(f"Processed {count} images")
    print(f"Source total: {total_src / 1024 / 1024:.1f} MB")
    print(f"Output total: {total_dst / 1024 / 1024:.1f} MB")
    print(f"Savings: {(1 - total_dst / total_src) * 100:.0f}%")


def process_article_images(source_dir: Path, dest_dir: Path):
    count = 0
    for img_path in sorted(source_dir.iterdir()):
        if img_path.suffix.lower() not in ('.jpg', '.jpeg', '.png'):
            continue
        if img_path.name.startswith('~'):
            continue
        dst_name = img_path.stem + '.jpg'
        dst_path = dest_dir / dst_name
        optimize_image(img_path, dst_path, MAX_WIDTH_ARTICLE)
        count += 1
    print(f"Processed {count} article images to {dest_dir}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python optimize_images.py <source_dir> <dest_dir> [--thumbs <thumb_dir>]")
        sys.exit(1)

    source = Path(sys.argv[1])
    dest = Path(sys.argv[2])
    thumb = None
    if '--thumbs' in sys.argv:
        idx = sys.argv.index('--thumbs')
        thumb = Path(sys.argv[idx + 1])

    if not source.exists():
        print(f"Source directory not found: {source}")
        sys.exit(1)

    process_catalogue_images(source, dest, thumb)
