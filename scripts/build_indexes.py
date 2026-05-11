"""Regenerate index pages after adding new content."""

import re
import sys
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent

MONTH_NAMES = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}


def rebuild_published_index():
    pub_dir = SITE_ROOT / 'published'
    pdfs = sorted(pub_dir.glob('*.pdf'), reverse=True)
    if not pdfs:
        print("No PDFs found")
        return

    items = []
    for pdf in pdfs:
        m = re.match(r'(\d{4})-(\d{2})', pdf.stem)
        if not m:
            continue
        year, month = int(m.group(1)), int(m.group(2))
        month_name = MONTH_NAMES.get(month, str(month))
        size_mb = pdf.stat().st_size / (1024 * 1024)
        items.append(f'''
        <div class="download-item">
          <div class="download-item-info">
            <h3>Universe &mdash; {month_name} {year}</h3>
            <span class="file-size">PDF &middot; {size_mb:.1f} MB</span>
          </div>
          <a href="{pdf.name}" class="download-btn" download>&#8681; Download</a>
        </div>''')

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Published Issues &mdash; Deep Sky Notes</title>
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
      <ul class="nav-links">
        <li><a href="../articles/index.html">Articles</a></li>
        <li class="nav-dropdown">
          <a href="../catalogue/index.html">Observing Notes &#9662;</a>
          <div class="nav-dropdown-menu">
            <a href="../catalogue/index.html">Master Table</a>
            <a href="../catalogue/constellations/index.html">Browse by Constellation</a>
          </div>
        </li>
        <li><a href="index.html" class="active">Published</a></li>
        <li><a href="../about.html">About</a></li>
      </ul>
    </div>
  </nav>
  <main class="page-content">
    <div class="container">
      <h1>Published Issues</h1>
      <p class="text-secondary">Deep Sky Notes as published in <em>Universe</em>, the journal of the Astronomical Society of NSW.</p>
      <div class="download-list">{''.join(items)}
      </div>
    </div>
  </main>
  <footer class="site-footer">
    <div class="container">
      <p>Deep Sky Notes &mdash; Alessandro Spina</p>
      <p><a href="https://www.asnsw.com" target="_blank" rel="noopener">Astronomical Society of NSW</a></p>
    </div>
  </footer>
</body>
</html>'''

    (pub_dir / 'index.html').write_text(html, encoding='utf-8')
    print(f"Rebuilt published index ({len(items)} PDFs)")


if __name__ == '__main__':
    rebuild_published_index()
