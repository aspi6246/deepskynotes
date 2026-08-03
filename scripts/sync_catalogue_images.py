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
"""
import time
from pathlib import Path

from optimize_images import optimize_image, MAX_WIDTH_DSS, MAX_WIDTH_CHART

SITE_ROOT = Path(__file__).resolve().parent.parent
CAT = SITE_ROOT.parent / "Object Catalogue" / "Private Repo"
DEST = SITE_ROOT / "catalogue" / "images"
MAX_WIDTH_EP = 600


def sync():
    done = skipped = 0
    t0 = time.time()
    for const_dir in sorted((CAT / 'images_bw').iterdir()):
        if not const_dir.is_dir() or const_dir.name == 'constellation_art':
            continue
        const = const_dir.name
        slug = const.lower()

        for src in sorted(const_dir.glob('*.png')):
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
                dst = DEST / slug / src.name
                if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
                    skipped += 1
                    continue
                optimize_image(src, dst, MAX_WIDTH_DSS)
                done += 1

    print(f'optimized {done}, up-to-date {skipped}, in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    sync()
