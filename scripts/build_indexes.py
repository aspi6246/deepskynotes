"""Regenerate published/index.html.

The Published section was merged into Articles on 2026-09-02: each article page
now carries its own "Download as published" button, and Published is no longer
in the site nav. This page survives as an unlinked archive so existing
bookmarks still resolve, and because one flat list of every issue is genuinely
handy. It is not reachable from the nav by design -- hence the pointer back to
Articles at the top.

Run after dropping a new extract into published/:

    python scripts/build_indexes.py

Three things this script used to get wrong, all fixed here; re-check them if you
touch it:
  * the nav was two revisions stale (no Observing Lists, no Links, and a
    Published item that no longer exists anywhere else on the site);
  * `glob('*.pdf')` picked up the `-full.pdf` files too, listing every issue
    twice -- and those are gitignored, so half the links would have 404'd;
  * the footer was truncated compared to every other page.
"""

import re
import sys
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent

MONTH_NAMES = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

# Only the column extract is hosted. published/*-full.pdf is gitignored, so the
# complete issues never reach GitHub Pages -- listing one gives a dead link.
EXTRACT_RE = re.compile(r'^(\d{4})-(\d{2})$')

NAV = '''      <ul class="nav-links">
        <li><a href="../articles/index.html">Articles</a></li>
        <li class="nav-dropdown">
          <a href="../catalogue/index.html">Observing Notes &#9662;</a>
          <div class="nav-dropdown-menu">
            <a href="../catalogue/index.html">Master Table</a>
            <a href="../catalogue/constellations/index.html">Browse by Constellation</a>
          </div>
        </li>
        <li><a href="../observing-lists/index.html">Observing Lists</a></li>
        <li><a href="../links.html">Links</a></li>
        <li><a href="../about.html">About</a></li>
      </ul>'''

FOOTER = '''  <footer class="site-footer">
    <div class="container">
      <p>Deep Sky Notes &mdash; Alessandro Spina</p>

      <p class="text-secondary">Finder charts produced with <a href="https://stellarium.org" target="_blank" rel="noopener">Stellarium</a>. Survey images from the <a href="https://archive.stsci.edu/cgi-bin/dss_form" target="_blank" rel="noopener">Digitized Sky Survey</a> (STScI/NASA). Object data queried from the <a href="https://simbad.u-strasbg.fr/" target="_blank" rel="noopener">SIMBAD</a> database (CDS, Strasbourg).</p>
      <p class="text-secondary">&copy; 2026 Alessandro Spina. All rights reserved.</p>
    </div>
  </footer>'''


def article_for_issue() -> dict[str, str]:
    """issue stem -> article slug, from convert_article.ISSUE_MAP.

    Guarded: convert_article imports python-docx at module level, and this
    script should still rebuild the page if that is not installed.
    """
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from convert_article import ISSUE_MAP
    except Exception as exc:                                  # pragma: no cover
        print(f"  (no article back-links: {exc})")
        return {}
    return {stem: slug for slug, (stem, *_rest) in ISSUE_MAP.items()}


def rebuild_published_index():
    pub_dir = SITE_ROOT / 'published'
    pdfs = sorted((p for p in pub_dir.glob('*.pdf') if EXTRACT_RE.match(p.stem)),
                  reverse=True)
    if not pdfs:
        print("No column extracts found in published/")
        return

    back_link = article_for_issue()

    items = []
    for pdf in pdfs:
        year, month = (int(g) for g in EXTRACT_RE.match(pdf.stem).groups())
        month_name = MONTH_NAMES.get(month, str(month))
        size_mb = pdf.stat().st_size / (1024 * 1024)
        slug = back_link.get(pdf.stem)
        read_it = (f'''
            <a class="read-online" href="../articles/{slug}.html">Read online</a>'''
                   if slug else '')
        items.append(f'''
        <div class="download-item">
          <div class="download-item-info">
            <h3>Universe &mdash; {month_name} {year}</h3>
            <span class="file-size">PDF &middot; {size_mb:.1f} MB</span>{read_it}
          </div>
          <a href="{pdf.name}" class="download-btn" download>&#8681; Download</a>
        </div>''')

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noai, noimageai">
  <title>Published Issues &mdash; Deep Sky Notes</title>
  <meta name="description" content="Wiruna Wanderings as published in Universe, the journal of the Astronomical Society of NSW">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>
  <nav class="site-nav">
    <div class="nav-inner">
      <a href="../index.html" class="nav-brand">Deep Sky Notes</a>
      <button class="nav-toggle" aria-label="Toggle navigation" onclick="document.querySelector('.nav-links').classList.toggle('open')">&#9776;</button>
{NAV}
    </div>
  </nav>
  <main class="page-content">
    <div class="container">
      <h1>Published Issues</h1>
      <p class="text-secondary"><strong>Wiruna Wanderings</strong> is a monthly column written by Alessandro Spina for <em>Universe</em>, the journal of the <a href="https://www.asnsw.com" target="_blank" rel="noopener">Astronomical Society of New South Wales</a>. Each article covers a new-moon observing weekend at the Society's dark-sky site.</p>
      <p class="text-secondary">Every one of these is also on <a href="../articles/index.html">Articles</a>, where you can read it in full and download the same PDF. This page is just the flat archive.</p>
      <div class="download-list">{''.join(items)}
      </div>
    </div>
  </main>
{FOOTER}
</body>
</html>'''

    (pub_dir / 'index.html').write_text(html, encoding='utf-8')
    print(f"Rebuilt published index ({len(items)} column extracts, "
          f"{len([i for i in pdfs if back_link.get(i.stem)])} linked to articles)")


if __name__ == '__main__':
    rebuild_published_index()
