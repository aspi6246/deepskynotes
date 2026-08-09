"""Sync catalogue images from the Object Catalogue repo into the site.

Each object page on the site needs five images under
catalogue/images/<constellation-slug>/ (slug = lowercase constellation):

    <slug>_dss.jpg        from  Private Repo/images/<Const>/       (800 px)
    <slug>_ultrawide.jpg  from  Private Repo/images_bw/<Const>/    (1200 px)
    <slug>_wide.jpg       ditto                                    (1200 px)
    <slug>_finder.jpg     ditto                                    (1200 px)
    <slug>_ep.jpg         ditto                                    (600 px)

Incremental: a destination is rewritten only when missing or older than its
source, so a full run after a small catalogue change is cheap. Run after
build_bw_test.py and alongside convert_catalogue.py, then commit the site.

Only objects the site actually builds a page for are synced. The chapter files
are the gate, and it is the same gate convert_catalogue.py uses — imported from
there so there is exactly one definition. Without it this script happily
optimises assets for objects that have no page (chapter-orphans like
Carina/mel_96), which land untracked in catalogue/images/ and get swept into a
commit by any `git add -A`. That has needed a manual cleanup before (bf5e217,
"Remove four ghost catalogue pages and their assets").
"""
import time
from pathlib import Path

from optimize_images import optimize_image, MAX_WIDTH_DSS, MAX_WIDTH_CHART
from convert_catalogue import chapter_referenced

SITE_ROOT = Path(__file__).resolve().parent.parent
CAT = SITE_ROOT.parent / "Object Catalogue" / "Private Repo"
DEST = SITE_ROOT / "catalogue" / "images"
MAX_WIDTH_EP = 600

# Longest first: 'mel_96_ultrawide' must not be matched by '_wide'.
IMAGE_SUFFIXES = ('_ultrawide', '_finder', '_wide', '_dss', '_ep')


def object_slug(stem: str) -> str:
    """'mel_96_ultrawide' -> 'mel_96' — the slug the chapter files reference."""
    for suffix in IMAGE_SUFFIXES:
        if stem.endswith(suffix):
            return stem[:-len(suffix)]
    return stem


def sync():
    done = skipped = ghosts = 0
    allowed = chapter_referenced()
    t0 = time.time()
    for const_dir in sorted((CAT / 'images_bw').iterdir()):
        if not const_dir.is_dir() or const_dir.name == 'constellation_art':
            continue
        const = const_dir.name
        slug = const.lower()

        def wanted(src: Path) -> bool:
            nonlocal ghosts
            if allowed and (const, object_slug(src.stem)) not in allowed:
                ghosts += 1
                return False
            return True

        for src in sorted(const_dir.glob('*.png')):
            if not wanted(src):
                continue
            max_w = MAX_WIDTH_EP if src.stem.endswith('_ep') else MAX_WIDTH_CHART
            dst = DEST / slug / (src.stem + '.jpg')
            if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
                skipped += 1
                continue
            optimize_image(src, dst, max_w)
            done += 1

        colour_dir = CAT / 'images' / const
        if colour_dir.is_dir():
            for src in sorted(colour_dir.glob('*_dss.jpg')):
                if not wanted(src):
                    continue
                dst = DEST / slug / src.name
                if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
                    skipped += 1
                    continue
                optimize_image(src, dst, MAX_WIDTH_DSS)
                done += 1

    ghost_note = f', skipped {ghosts} not in any chapter' if ghosts else ''
    print(f'optimized {done}, up-to-date {skipped}{ghost_note}, in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    sync()
