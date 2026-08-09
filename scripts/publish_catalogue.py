"""Regenerate the site's catalogue section from the Object Catalogue repo.

Source of truth is the catalogue repo's LaTeX:

    Private Repo/objects/<Const>/*.tex  +  Private Repo/constellations/*.tex

Everything this script writes is derived and disposable. Site catalogue HTML is
never hand-edited — it is overwritten wholesale on every run.

The three steps MUST run in this order. Step 2 and 3 both read objects_bw/ and
images_bw/, which step 1 produces; running them against a stale objects_bw
silently publishes stale notes, and git cannot warn you because objects_bw is
gitignored. Bundling the steps here is the whole point of the script.

    1. build_bw_test.py        (catalogue repo)  objects/ -> objects_bw/, catalogue.tex
    2. sync_catalogue_images.py (site repo)      images_bw/ -> catalogue/images/*.jpg
    3. convert_catalogue.py     (site repo)      objects_bw/ -> catalogue/**.html, objects.json

Usage (from anywhere):
    python scripts/publish_catalogue.py

Then review `git diff --stat` in the site repo before committing.
"""
import subprocess
import sys
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent
CAT = SITE_ROOT.parent / "Object Catalogue" / "Private Repo"

STEPS = [
    ("Rebuild B&W object pages", CAT, CAT / "scripts" / "build_bw_test.py"),
    ("Sync catalogue images", SITE_ROOT, SITE_ROOT / "scripts" / "sync_catalogue_images.py"),
    ("Convert catalogue to HTML", SITE_ROOT, SITE_ROOT / "scripts" / "convert_catalogue.py"),
]


def run_step(n, total, label, cwd, script):
    print(f"\n=== [{n}/{total}] {label} ===")
    print(f"    {script.name}  (cwd: {cwd.name})")
    result = subprocess.run([sys.executable, str(script)], cwd=str(cwd))
    if result.returncode != 0:
        print(f"\nFAILED at step {n} ({label}) with exit code {result.returncode}.")
        print("Site output may be half-regenerated — do not commit. Fix and re-run.")
        sys.exit(result.returncode)


def report_orphans():
    """objects_bw/ is never pruned by build_bw_test.py, so files linger after an
    object is dropped from its chapter. convert_catalogue.py filters them out of
    the site, but they rot quietly. Report, never delete."""
    src = CAT / "objects"
    bw = CAT / "objects_bw"
    if not (src.is_dir() and bw.is_dir()):
        return
    have = {(p.parent.name, p.stem) for p in src.rglob("*.tex")}
    orphans = sorted(
        f"{p.parent.name}/{p.stem}"
        for p in bw.rglob("*.tex")
        if (p.parent.name, p.stem) not in have
    )
    if orphans:
        print(f"\nNOTE: {len(orphans)} stale file(s) in objects_bw/ with no source "
              f"in objects/ — filtered from the site, safe to ignore, but worth a look:")
        for o in orphans:
            print(f"    {o}")


def main():
    if not CAT.is_dir():
        print(f"Catalogue repo not found at:\n    {CAT}")
        sys.exit(1)

    print(f"Site:      {SITE_ROOT}")
    print(f"Catalogue: {CAT}")

    for i, (label, cwd, script) in enumerate(STEPS, 1):
        if not script.is_file():
            print(f"\nMissing script: {script}")
            sys.exit(1)
        run_step(i, len(STEPS), label, cwd, script)

    report_orphans()

    print("\n=== Done. Review before committing: ===")
    subprocess.run(["git", "diff", "--stat"], cwd=str(SITE_ROOT))


if __name__ == "__main__":
    main()
