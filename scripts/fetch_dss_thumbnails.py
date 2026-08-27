"""Fetch DSS thumbnails for each pair via CDS hips2fits and drop them into
observing-lists/thumbs/. Idempotent (re-running is safe; existing files are
overwritten with the current fetch).

Usage: python scripts/fetch_dss_thumbnails.py
"""

import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _visual_doubles_data import PAIRS  # noqa: E402

SITE_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = SITE_ROOT / "observing-lists" / "thumbs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# CDS hips2fits: reliable JPEG at arbitrary FOV; DSS2 red matches the survey
# already used on the object catalogue.
BASE = "https://alasky.cds.unistra.fr/hips-image-services/hips2fits"
HIPS = "CDS/P/DSS2/red"
PIXELS = 400  # 400x400 square; retina headroom for ~100 px display

for pair in PAIRS:
    slug = pair["slug"]
    ra, dec = pair["thumb_center"]
    fov = pair["thumb_fov_deg"]
    url = (
        f"{BASE}?hips={HIPS}"
        f"&ra={ra}&dec={dec}&fov={fov}"
        f"&width={PIXELS}&height={PIXELS}"
        f"&projection=SIN&format=jpg"
    )
    out = OUT_DIR / f"{slug}.jpg"
    try:
        urllib.request.urlretrieve(url, out)
        size_kb = out.stat().st_size / 1024
        print(f"  {out.name:32s} {size_kb:6.1f} KB   fov={fov}deg")
    except Exception as e:
        print(f"  {out.name:32s} FAILED: {e}")
    time.sleep(0.5)  # be nice to CDS

print(f"\nWrote {len(PAIRS)} thumbnails to {OUT_DIR.relative_to(SITE_ROOT)}")
