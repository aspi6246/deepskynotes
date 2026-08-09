"""Convert LaTeX object catalogue to HTML pages and JSON data."""

import json
import re
import sys
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent
CATALOGUE_DIR = SITE_ROOT.parent / "Object Catalogue" / "Private Repo"
OBJECTS_SRC = CATALOGUE_DIR / "objects_bw"
OUTPUT_DIR = SITE_ROOT / "catalogue"

GREEK = {
    r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ',
    r'\delta': 'δ', r'\epsilon': 'ε', r'\zeta': 'ζ',
    r'\eta': 'η', r'\theta': 'θ', r'\iota': 'ι',
    r'\kappa': 'κ', r'\lambda': 'λ', r'\mu': 'μ',
    r'\nu': 'ν', r'\xi': 'ξ', r'\pi': 'π',
    r'\rho': 'ρ', r'\sigma': 'σ', r'\tau': 'τ',
    r'\upsilon': 'υ', r'\phi': 'φ', r'\chi': 'χ',
    r'\psi': 'ψ', r'\omega': 'ω',
    r'\Alpha': 'Α', r'\Beta': 'Β', r'\Gamma': 'Γ',
    r'\Delta': 'Δ', r'\Omega': 'Ω',
}

TYPE_LABELS = {
    'GC': 'Globular Cluster', 'OC': 'Open Cluster', 'PN': 'Planetary Nebula',
    'EN': 'Emission Nebula', 'Gal': 'Galaxy', 'DN': 'Dark Nebula',
    'RN': 'Reflection Nebula', 'OC+N': 'Open Cluster + Nebula',
    'Interstellar': 'Interstellar', 'Cl': 'Open Cluster',
    'AGN': 'Galaxy', 'Active': 'Galaxy', 'Radio': 'Galaxy',
    'SNR': 'Supernova Remnant',
}

TYPE_CSS = {
    'Globular Cluster': 'gc', 'Open Cluster': 'oc', 'Planetary Nebula': 'pn',
    'Emission Nebula': 'en', 'Galaxy': 'gal', 'Dark Nebula': 'dn',
    'Reflection Nebula': 'en', 'Open Cluster + Nebula': 'oc',
    'Interstellar': 'en', 'Supernova Remnant': 'en',
}


def clean_latex(text: str) -> str:
    text = re.sub(r'\\textbf\{([^}]*)\}', r'<strong>\1</strong>', text)
    text = re.sub(r'\\textit\{([^}]*)\}', r'<em>\1</em>', text)
    text = re.sub(r'\\href\{([^}]*)\}\{([^}]*)\}', r'<a href="\1" target="_blank" rel="noopener">\2</a>', text)
    text = re.sub(r'\\hfill\s*<em>\(([^)]*)\)</em>', r'<span class="obs-date">(\1)</span>', text)
    for cmd, char in GREEK.items():
        text = text.replace(f'${cmd}$', char)
        text = text.replace(cmd, char)
    text = re.sub(r'\$\\sim\$', '~', text)
    text = re.sub(r'\$\\approx\$', '≈', text)
    text = re.sub(r'\$([^$]*)\$', lambda m: m.group(1), text)
    text = text.replace('\\,', ' ')
    text = text.replace('{,}', ',')
    text = text.replace('~', ' ')
    text = text.replace('---', '—')
    text = text.replace('--', '–')
    text = text.replace("``", '“')
    text = text.replace("''", '”')
    text = text.replace('\\textdegree', '°')
    text = text.replace('\\texttimes', '×')
    text = text.replace('\\times', '×')
    text = text.replace('\\%', '%')
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\(smallskip|medskip|bigskip|clearpage|par|noindent)\b', '', text)
    text = text.replace('\\\\', '<br>')
    return text.strip()


def clean_spec_field(val: str) -> str:
    val = val.strip()
    # Drop ALL math delimiters, not just the outer pair: spec strips use inline
    # maths for primes (e.g. -63°\,51$'$\,13.7$''$).
    val = val.replace('$', '')
    val = val.replace(r'\,', ' ')
    # Double prime first, else "''" is consumed as two single primes.
    val = val.replace("''", '″')
    val = val.replace("'", '′')
    val = val.replace('"', '″')
    val = val.replace(r'\textdegree', '°')
    val = val.replace(r'\times', '×')
    return val.strip()


def parse_specs_args(text: str) -> list[str]:
    args = []
    depth = 0
    current = []
    for ch in text:
        if ch == '{':
            if depth == 0:
                current = []
            else:
                current.append(ch)
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                args.append(''.join(current))
            else:
                current.append(ch)
        elif depth > 0:
            current.append(ch)
    return args


def ra_to_deg(ra_str: str) -> float | None:
    m = re.search(r'(\d+)h\s*(\d+)m\s*([\d.]+)s?', ra_str)
    if m:
        return float(m.group(1)) * 15 + float(m.group(2)) * 0.25 + float(m.group(3)) * (15/3600)
    return None


def dec_to_deg(dec_str: str) -> float | None:
    cleaned = dec_str.replace(' ', '').replace('°', ' ').replace('′', ' ').replace('″', '')
    cleaned = cleaned.replace('°', ' ').replace("'", ' ').replace('"', '')
    m = re.search(r'([+-]?\d+)\s+(\d+)\s+([\d.]+)?', cleaned)
    if m:
        d = int(m.group(1))
        minutes = int(m.group(2))
        secs = float(m.group(3)) if m.group(3) else 0.0
        sign = -1 if d < 0 or '-' in dec_str else 1
        return sign * (abs(d) + minutes / 60 + secs / 3600)
    return None


def compute_aladin_fov(size_str: str) -> float:
    if not size_str or size_str in ('–', '--', '0″'):
        return 0.25
    nums = re.findall(r'[\d.]+', size_str)
    if not nums:
        return 0.25
    max_dim = max(float(n) for n in nums)
    if '″' in size_str or '"' in size_str:
        max_dim /= 60.0
    fov = max_dim * 4.0 / 60.0
    return max(0.08, min(fov, 1.0))


def parse_mag(val: str) -> float | None:
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def parse_tex_file(path: Path) -> dict | None:
    text = path.read_text(encoding='utf-8')

    m = re.search(r'\\objectpage\{([^}]+)\}\{([^}]+)\}', text)
    if not m:
        return None
    constellation = m.group(1)
    display_name = m.group(2)

    m = re.search(r'\\specs\{', text)
    if not m:
        return None
    specs_start = m.end() - 1
    args = parse_specs_args(text[specs_start:])
    if len(args) < 9:
        return None
    ra, dec, size, mag, sb, cnt_st, obj_type, distance, chart = [clean_spec_field(a) for a in args[:9]]

    dss_source = 'DSS'
    dss_image = ''
    dss_fov = ''
    m = re.search(r'\\dssplate(?:\[([^\]]*)\])?\{([^}]+)\}\{([^}]+)\}', text)
    if m:
        dss_source = m.group(1) or 'DSS'
        dss_image = m.group(2)
        dss_fov = clean_spec_field(m.group(3))

    ultrawide_image = ''
    m = re.search(r'\\ultrawidepage\{([^}]+)\}', text)
    if m:
        ultrawide_image = m.group(1)

    wide_image = ''
    finder_image = ''
    m = re.search(r'\\wideandfinder\{([^}]+)\}\{([^}]+)\}', text)
    if m:
        wide_image = m.group(1)
        finder_image = m.group(2)

    if not wide_image:
        m = re.search(r'\\widechart\{([^}]+)\}', text)
        if m:
            wide_image = m.group(1)

    if not finder_image:
        m = re.search(r'\\finderscope\{([^}]+)\}', text)
        if m:
            finder_image = m.group(1)

    ep_image = ''
    m = re.search(r'\\eyepieceview\{([^}]+)\}', text)
    if m:
        ep_image = m.group(1)
    m2 = re.search(r'\\finderandeyepiece\{([^}]+)\}\{([^}]+)\}', text)
    if m2:
        finder_image = m2.group(1)
        ep_image = m2.group(2)

    if wide_image and 'images_bw' in wide_image and not ep_image:
        ep_image = wide_image.replace('_wide.', '_ep.')

    bg_text = ''
    m = re.search(r'\\background\s*\n(.*?)(?=\\mynotes|\\observed|\\refs|\\clearpage|$)', text, re.DOTALL)
    if m:
        bg_text = m.group(1).strip()
        bg_text = re.sub(r'%[^\n]*\n', '\n', bg_text)
        bg_text = re.sub(r'\\begin\{itemize\}.*?\\end\{itemize\}', '', bg_text, flags=re.DOTALL)

    notes_text = ''
    m = re.search(r'(?:\\mynotes|\\observed)\s*\n(.*?)(?=\\refs|\\clearpage|$)', text, re.DOTALL)
    if m:
        notes_text = m.group(1).strip()
        notes_text = re.sub(r'%[^\n]*\n', '\n', notes_text)
        notes_text = re.sub(r'\\begin\{itemize\}.*?\\end\{itemize\}', '', notes_text, flags=re.DOTALL)

    refs = []
    m = re.search(r'\\refs\s*\n.*?\\begin\{itemize\}.*?\n(.*?)\\end\{itemize\}', text, re.DOTALL)
    if m:
        for item in re.finditer(r'\\item\s+(.*?)(?=\\item|$)', m.group(1), re.DOTALL):
            refs.append(item.group(1).strip())

    obj_id = path.stem
    slug = obj_id.replace('_', '-')
    name_clean = re.match(r'^(.*?)\s*\(', display_name)
    name = name_clean.group(1) if name_clean else display_name

    return {
        'id': slug,
        'filename': path.stem,
        'name': name,
        'displayName': display_name,
        'constellation': constellation,
        'constellationSlug': constellation.lower().replace(' ', ''),
        'ra': ra,
        'dec': dec,
        'raDeg': ra_to_deg(ra),
        'decDeg': dec_to_deg(dec),
        'size': size,
        'mag': parse_mag(mag),
        'magStr': mag,
        'sb': parse_mag(sb),
        'sbStr': sb,
        'cntSt': cnt_st,
        'type': obj_type,
        'typeLabel': TYPE_LABELS.get(obj_type, obj_type),
        'typeCss': TYPE_CSS.get(TYPE_LABELS.get(obj_type, obj_type), ''),
        'distance': distance,
        'chart': chart,
        'dssSource': dss_source,
        'dssImage': dss_image,
        'dssFov': dss_fov,
        'ultrawideImage': ultrawide_image,
        'wideImage': wide_image,
        'finderImage': finder_image,
        'epImage': ep_image,
        'background': bg_text,
        'notes': notes_text,
        'refs': refs,
    }


def image_web_path(latex_path: str, constellation_slug: str) -> str:
    if not latex_path:
        return ''
    filename = Path(latex_path).stem + '.jpg'
    return f"images/{constellation_slug}/{filename}"


def format_background(bg_text: str) -> str:
    if not bg_text:
        return ''
    paragraphs = re.split(r'\n\s*\n', bg_text)
    html_parts = []
    for p in paragraphs:
        p = p.strip()
        if p:
            html_parts.append(f'<p>{clean_latex(p)}</p>')
    return '\n'.join(html_parts)


def format_notes(notes_text: str) -> str:
    if not notes_text:
        return ''
    blocks = re.split(r'\\smallskip\s*', notes_text)
    html_parts = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        paragraphs = re.split(r'\n\s*\n', block)
        for p in paragraphs:
            p = p.strip()
            if p:
                cleaned = clean_latex(p)
                cleaned = cleaned.replace('\n', ' ')
                html_parts.append(f'<p>{cleaned}</p>')
    return '\n'.join(html_parts)


def format_refs(refs: list[str]) -> str:
    if not refs:
        return ''
    items = []
    for r in refs:
        cleaned = clean_latex(r)
        items.append(f'<li>{cleaned}</li>')
    return '<ul class="references-list">\n' + '\n'.join(items) + '\n</ul>'


NAV_HTML = '''<nav class="site-nav">
    <div class="nav-inner">
      <a href="../../index.html" class="nav-brand">Deep Sky Notes</a>
      <button class="nav-toggle" aria-label="Toggle navigation" onclick="document.querySelector('.nav-links').classList.toggle('open')">&#9776;</button>
      <ul class="nav-links">
        <li><a href="../../articles/index.html">Articles</a></li>
        <li class="nav-dropdown">
          <a href="../index.html" class="active">Observing Notes &#9662;</a>
          <div class="nav-dropdown-menu">
            <a href="../index.html">Master Table</a>
            <a href="../constellations/index.html">Browse by Constellation</a>
          </div>
        </li>
        <li><a href="../../published/index.html">Published</a></li>
        <li><a href="../../links.html">Links</a></li>
        <li><a href="../../about.html">About</a></li>
      </ul>
    </div>
  </nav>'''

FOOTER_HTML = '''<footer class="site-footer">
    <div class="container">
      <p>Deep Sky Notes &mdash; Alessandro Spina</p>

      <p class="text-secondary">Finder charts produced with <a href="https://stellarium.org" target="_blank" rel="noopener">Stellarium</a>. Survey images from the <a href="https://archive.stsci.edu/cgi-bin/dss_form" target="_blank" rel="noopener">Digitized Sky Survey</a> (STScI/NASA). Object data queried from the <a href="https://simbad.u-strasbg.fr/" target="_blank" rel="noopener">SIMBAD</a> database (CDS, Strasbourg).</p>
      <p class="text-secondary">&copy; 2026 Alessandro Spina. All rights reserved.</p>
    </div>
  </footer>'''


def generate_object_page(obj: dict, prev_obj: dict | None, next_obj: dict | None) -> str:
    slug = obj['constellationSlug']
    dss_web = image_web_path(obj['dssImage'], slug)
    ultrawide_web = image_web_path(obj.get('ultrawideImage', ''), slug)
    wide_web = image_web_path(obj['wideImage'], slug)
    finder_web = image_web_path(obj['finderImage'], slug)
    ep_web = image_web_path(obj['epImage'], slug)

    bg_html = format_background(obj['background'])
    notes_html = format_notes(obj['notes'])
    refs_html = format_refs(obj['refs'])

    specs_row = ''.join(f'<td>{v}</td>' for v in [
        obj['ra'], obj['dec'], obj['size'], obj['magStr'],
        obj['sbStr'], obj['cntSt'], obj['type'], obj['distance'], obj['chart']
    ])

    dss_section = ''
    if dss_web:
        dss_section = f'''
      <div class="dss-plate">
        <img src="../{dss_web}" alt="{obj['name']} DSS plate" loading="lazy">
        <div class="dss-caption">Source: {obj['dssSource']} | Field: {obj['dssFov']}</div>
      </div>'''

    aladin_section = ''
    if obj['raDeg'] is not None and obj['decDeg'] is not None:
        fov = compute_aladin_fov(obj['size'])
        aladin_section = f'''
      <div class="aladin-viewer">
        <h2 class="object-section-title">Interactive Sky View</h2>
        <div id="aladin-lite-div" style="width: 100%; height: 350px;">
          <div class="aladin-fallback" style="display:flex;align-items:center;justify-content:center;height:100%;color:#888;font-size:0.9rem;text-align:center;padding:1rem;">
            Loading interactive sky view&hellip;
          </div>
        </div>
        <div class="aladin-caption">
          Powered by <a href="https://aladin.cds.unistra.fr/AladinLite/" target="_blank" rel="noopener">Aladin Lite</a> / CDS, Strasbourg.
          Pan, zoom, or switch surveys using the layer icon.
        </div>
        <script type="text/javascript" src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js" charset="utf-8"></script>
        <script type="text/javascript">
          (function() {{
            if (typeof A === 'undefined' || !A.init) {{
              var fb = document.querySelector('.aladin-fallback');
              if (fb) fb.textContent = 'Interactive viewer not available on this device. Try viewing on a desktop browser.';
              return;
            }}
            A.init.then(function() {{
              A.aladin('#aladin-lite-div', {{
                target: '{obj["raDeg"]:.6f} {obj["decDeg"]:.6f}',
                survey: 'P/DSS2/color',
                fov: {fov:.4f},
                showReticle: true,
                showCooGrid: false
              }});
            }}).catch(function() {{
              var fb = document.querySelector('.aladin-fallback');
              if (fb) fb.textContent = 'Interactive viewer could not load. Try viewing on a desktop browser.';
            }});
          }})();
        </script>
      </div>'''

    charts_section = ''
    parts = []
    if ultrawide_web:
        parts.append(f'''
        <div class="chart-ultrawide">
          <img src="../{ultrawide_web}" alt="{obj['name']} ultra-wide chart" loading="lazy">
          <div class="chart-caption">Ultra-wide view (~25° field)</div>
        </div>''')
    if wide_web:
        parts.append(f'''
        <div class="chart-wide">
          <img src="../{wide_web}" alt="{obj['name']} wide-field chart" loading="lazy">
          <div class="chart-caption">Wide-field view with Telrad rings (4°, 2°, 0.5°)</div>
        </div>''')
    if finder_web or ep_web:
        pair_parts = []
        if finder_web:
            pair_parts.append(f'''
          <div class="chart">
            <img src="../{finder_web}" alt="{obj['name']} finderscope view" loading="lazy">
            <div class="chart-caption">Finderscope view (9×50 RACI, ~4.4° TFOV)</div>
          </div>''')
        if ep_web:
            pair_parts.append(f'''
          <div class="chart">
            <img src="../{ep_web}" alt="{obj['name']} eyepiece view" loading="lazy">
            <div class="chart-caption">Eyepiece view — 35 mm Panoptic on 12-inch f/5 (1.6° TFOV)</div>
          </div>''')
        parts.append(f'''
        <div class="charts-pair">{''.join(pair_parts)}
        </div>''')
    if parts:
        charts_section = f'''
      <h2 class="object-section-title">Charts</h2>
      <div class="charts-grid">{''.join(parts)}
      </div>'''

    bg_section = f'''
      <h2 class="object-section-title">Background</h2>
      {bg_html}''' if bg_html else ''

    notes_section = f'''
      <h2 class="object-section-title">My Observing Notes</h2>
      <div class="observing-notes">
        {notes_html}
      </div>''' if notes_html else ''

    refs_section = f'''
      <h2 class="object-section-title">References</h2>
      {refs_html}''' if refs_html else ''

    nav_parts = []
    if prev_obj:
        nav_parts.append(f'<a href="{prev_obj["id"]}.html">&larr; {prev_obj["name"]}</a>')
    else:
        nav_parts.append('<span></span>')
    nav_parts.append(f'<a href="../constellations/{slug}.html" class="back-link">{obj["constellation"]}</a>')
    if next_obj:
        nav_parts.append(f'<a href="{next_obj["id"]}.html">{next_obj["name"]} &rarr;</a>')
    else:
        nav_parts.append('<span></span>')

    type_badge = f'<span class="type-badge {obj["typeCss"]}">{obj["typeLabel"]}</span>'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noai, noimageai">
  <title>{obj["name"]} &mdash; Deep Sky Notes</title>
  <meta name="description" content="{obj["displayName"]} in {obj["constellation"]} — finder charts, DSS plate, and observing notes">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../css/style.css">
</head>
<body>

  {NAV_HTML}

  <main class="page-content">
    <div class="container">
      <div class="breadcrumbs">
        <a href="../index.html">Catalogue</a><span class="sep">&rsaquo;</span>
        <a href="../constellations/{slug}.html">{obj["constellation"]}</a><span class="sep">&rsaquo;</span>
        {obj["name"]}
      </div>

      <div class="object-header">
        <h1 class="mt-0">{obj["displayName"]}</h1>
        <div class="object-constellation">{type_badge} in {obj["constellation"]}</div>
      </div>

      <div class="specs-table-wrap">
        <table class="specs-table">
          <thead><tr>
            <th>R.A.</th><th>Dec.</th><th>Size</th><th>Mag</th>
            <th>SB</th><th>Class</th><th>Type</th><th>Distance</th><th>Chart</th>
          </tr></thead>
          <tbody><tr>{specs_row}</tr></tbody>
        </table>
      </div>
      {dss_section}
      {aladin_section}
      {bg_section}
      {notes_section}
      {refs_section}
      {charts_section}

      <div class="object-nav">
        {nav_parts[0]}
        {nav_parts[1]}
        {nav_parts[2]}
      </div>
    </div>
  </main>

  {FOOTER_HTML}

</body>
</html>'''


def generate_constellation_page(constellation: str, slug: str, objects: list[dict]) -> str:
    nav_html = NAV_HTML.replace('href="../index.html"', 'href="../../catalogue/index.html"').replace(
        'href="../constellations/', 'href="').replace(
        'href="../../articles/', 'href="../../articles/').replace(
        'href="../../published/', 'href="../../published/').replace(
        'href="../../about.html"', 'href="../../about.html"').replace(
        'href="../../index.html"', 'href="../../index.html"')

    items = []
    for obj in objects:
        dss_thumb = f"../images/{slug}/{obj['filename']}_dss.jpg"
        type_badge = f'<span class="type-badge {obj["typeCss"]}">{obj["typeLabel"]}</span>'
        mag_str = f'Mag {obj["magStr"]}' if obj['magStr'] != '–' and obj['magStr'] != '--' else ''
        size_str = f' | Size {obj["size"]}' if obj['size'] != '–' and obj['size'] != '--' and obj['size'] != '0″' else ''
        meta = f'{type_badge} {mag_str}{size_str}'
        items.append(f'''
        <div class="object-list-item">
          <img src="{dss_thumb}" alt="{obj['name']}" loading="lazy">
          <div>
            <h4><a href="../objects/{obj['id']}.html">{obj['displayName']}</a></h4>
            <div class="item-meta">{meta}</div>
          </div>
        </div>''')

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noai, noimageai">
  <title>{constellation} &mdash; Deep Sky Notes</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../css/style.css">
</head>
<body>

  {NAV_HTML.replace('href="../../', 'href="../../')}

  <main class="page-content">
    <div class="container">
      <div class="breadcrumbs">
        <a href="../index.html">Catalogue</a><span class="sep">&rsaquo;</span>
        <a href="index.html">Constellations</a><span class="sep">&rsaquo;</span>
        {constellation}
      </div>

      <h1 class="mt-0">{constellation}</h1>
      <p class="text-secondary">{len(objects)} object{"s" if len(objects) != 1 else ""} in the catalogue</p>

      <div class="object-list">{''.join(items)}
      </div>
    </div>
  </main>

  {FOOTER_HTML}

</body>
</html>'''


def generate_constellation_index(constellations: dict[str, list[dict]]) -> str:
    cards = []
    for const in sorted(constellations):
        objs = constellations[const]
        slug = objs[0]['constellationSlug']
        count = len(objs)
        cards.append(f'''
        <div class="constellation-card">
          <h3><a href="{slug}.html">{const}</a></h3>
          <div class="obj-count">{count} object{"s" if count != 1 else ""}</div>
        </div>''')

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noai, noimageai">
  <title>Browse by Constellation &mdash; Deep Sky Notes</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../css/style.css">
</head>
<body>

  {NAV_HTML}

  <main class="page-content">
    <div class="container">
      <div class="breadcrumbs">
        <a href="../index.html">Catalogue</a><span class="sep">&rsaquo;</span>
        Constellations
      </div>

      <h1 class="mt-0">Browse by Constellation</h1>
      <p class="text-secondary">{sum(len(v) for v in constellations.values())} objects across {len(constellations)} constellations</p>

      <div class="constellation-grid">{''.join(cards)}
      </div>
    </div>
  </main>

  {FOOTER_HTML}

</body>
</html>'''


def generate_master_table_page(total: int) -> str:
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noai, noimageai">
  <title>Object Catalogue &mdash; Deep Sky Notes</title>
  <meta name="description" content="Searchable catalogue of {total} deep-sky objects observed from Wiruna dark-sky site">
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
          <a href="index.html" class="active">Observing Notes &#9662;</a>
          <div class="nav-dropdown-menu">
            <a href="index.html">Master Table</a>
            <a href="constellations/index.html">Browse by Constellation</a>
          </div>
        </li>
        <li><a href="../published/index.html">Published</a></li>
        <li><a href="../links.html">Links</a></li>
        <li><a href="../about.html">About</a></li>
      </ul>
    </div>
  </nav>

  <main class="page-content">
    <div class="container">
      <h1>Object Catalogue</h1>
      <p class="text-secondary">A searchable catalogue of deep-sky objects observed from Wiruna dark-sky site. Click any column header to sort. Use the filters to narrow the list.</p>

      <div class="catalogue-controls">
        <input type="text" class="catalogue-search" id="search" placeholder="Search by name or constellation…">
        <select class="catalogue-filter" id="filter-type">
          <option value="">All types</option>
        </select>
        <select class="catalogue-filter" id="filter-constellation">
          <option value="">All constellations</option>
        </select>
        <button class="catalogue-clear" id="clear-filters">Clear filters</button>
        <div class="catalogue-count" id="count"></div>
      </div>

      <div class="catalogue-table-wrap">
        <table class="catalogue-table" id="catalogue-table">
          <thead>
            <tr>
              <th data-sort="name">Name</th>
              <th data-sort="type">Type</th>
              <th data-sort="constellation">Constellation</th>
              <th data-sort="raDeg">RA</th>
              <th data-sort="decDeg">Dec</th>
              <th data-sort="mag">Mag</th>
              <th class="no-sort">Size</th>
              <th data-sort="sb">SB</th>
            </tr>
          </thead>
          <tbody id="table-body"></tbody>
        </table>
      </div>
    </div>
  </main>

  {FOOTER_HTML}

  <script src="../js/catalogue-table.js"></script>
</body>
</html>'''


def chapter_referenced() -> set[tuple[str, str]]:
    """(Constellation, slug) pairs actually \\input by the chapter files —
    the catalogue's source of truth. Keeps stale objects_bw leftovers
    (e.g. an orphaned mel_104 from an older build) off the website."""
    refs = set()
    const_dir = CATALOGUE_DIR / 'constellations'
    for ch in sorted(const_dir.glob('*.tex')):
        for line in ch.read_text(encoding='utf-8').splitlines():
            if line.lstrip().startswith('%'):
                continue
            m = re.search(r'objects/([^/]+)/([^}]+)\}', line)
            if m:
                refs.add((m.group(1), m.group(2)))
    return refs


def main():
    objects_dir = OBJECTS_SRC
    if len(sys.argv) > 1:
        objects_dir = Path(sys.argv[1])
    output_dir = OUTPUT_DIR
    if len(sys.argv) > 2:
        output_dir = Path(sys.argv[2])

    allowed = chapter_referenced()
    all_objects = []
    for const_dir in sorted(objects_dir.iterdir()):
        if not const_dir.is_dir():
            continue
        for tex_file in sorted(const_dir.glob('*.tex')):
            if allowed and (const_dir.name, tex_file.stem) not in allowed:
                print(f"SKIP (not in any chapter): {const_dir.name}/{tex_file.stem}")
                continue
            obj = parse_tex_file(tex_file)
            if obj:
                all_objects.append(obj)
            else:
                print(f"WARNING: Failed to parse {tex_file}")

    print(f"Parsed {len(all_objects)} objects from {objects_dir}")

    constellations: dict[str, list[dict]] = {}
    for obj in all_objects:
        constellations.setdefault(obj['constellation'], []).append(obj)

    obj_dir = output_dir / 'objects'
    obj_dir.mkdir(parents=True, exist_ok=True)
    for const, objs in constellations.items():
        for i, obj in enumerate(objs):
            prev_obj = objs[i - 1] if i > 0 else None
            next_obj = objs[i + 1] if i < len(objs) - 1 else None
            html = generate_object_page(obj, prev_obj, next_obj)
            (obj_dir / f"{obj['id']}.html").write_text(html, encoding='utf-8')
    print(f"Generated {len(all_objects)} object pages")

    const_dir = output_dir / 'constellations'
    const_dir.mkdir(parents=True, exist_ok=True)
    for const, objs in constellations.items():
        slug = objs[0]['constellationSlug']
        html = generate_constellation_page(const, slug, objs)
        (const_dir / f"{slug}.html").write_text(html, encoding='utf-8')
    print(f"Generated {len(constellations)} constellation pages")

    idx_html = generate_constellation_index(constellations)
    (const_dir / 'index.html').write_text(idx_html, encoding='utf-8')
    print("Generated constellation index")

    table_html = generate_master_table_page(len(all_objects))
    (output_dir / 'index.html').write_text(table_html, encoding='utf-8')
    print("Generated master table page")

    json_data = []
    for obj in all_objects:
        slug = obj['constellationSlug']
        json_data.append({
            'id': obj['id'],
            'name': obj['name'],
            'displayName': obj['displayName'],
            'constellation': obj['constellation'],
            'constellationSlug': slug,
            'ra': obj['ra'],
            'dec': obj['dec'],
            'raDeg': obj['raDeg'],
            'decDeg': obj['decDeg'],
            'size': obj['size'],
            'mag': obj['mag'],
            'magStr': obj['magStr'],
            'sb': obj['sb'],
            'sbStr': obj['sbStr'],
            'type': obj['type'],
            'typeLabel': obj['typeLabel'],
            'typeCss': obj['typeCss'],
            'dssThumb': f"images/{slug}/{obj['filename']}_dss.jpg",
            'url': f"objects/{obj['id']}.html",
        })

    data_dir = output_dir / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / 'objects.json').write_text(
        json.dumps(json_data, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Generated objects.json ({len(json_data)} entries)")


if __name__ == '__main__':
    main()
