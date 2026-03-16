import re
import json
from pathlib import Path

# ==================================================
# CONFIG
# ==================================================
# Central settings used throughout the build script.
# If the site structure changes later, this is the
# first place to check.

IMAGE_DIR = Path("images")
OUTPUT_DIR = Path("drawings")

STYLE_PATH = "../css/style.css"
VIEWER_PATH = "../js/viewer.js"

BASE_URL = "https://cskagen.github.io"

MAIN_RE = re.compile(r"^tegning_nr(\d+)\.jpg$")
SUB_RE = re.compile(r"^tegning_nr(\d+)_(\d{2})\.jpg$")


# ==================================================
# PARSE IMAGES
# ==================================================
# Reads the images folder and converts valid filenames
# into structured archive items.
#
# Accepted patterns:
#   tegning_nr852.jpg
#   tegning_nr852_01.jpg
#
# Output:
#   a list of item dictionaries
#   a list of ignored filenames

def parse_images():

    if not IMAGE_DIR.exists():
        raise SystemExit("ERROR: images/ folder not found.")

    items = []
    ignored = []
    seen_positions = set()

    for path in sorted(IMAGE_DIR.iterdir()):

        if not path.is_file():
            continue

        name = path.name

        m_main = MAIN_RE.match(name)
        m_sub = SUB_RE.match(name)

        if m_main:

            base = int(m_main.group(1))
            sub = 0
            slug = f"tegning_nr{base}"
            page_title = f"tegning nr {base} – Christian Skagen"
            visible_title = slug
            alt = f"tegning nr {base}"

        elif m_sub:

            base = int(m_sub.group(1))
            sub = int(m_sub.group(2))
            slug = f"tegning_nr{base}_{sub:02d}"
            page_title = f"tegning nr {base}, image {sub:02d} – Christian Skagen"
            visible_title = slug
            alt = f"tegning nr {base}, image {sub:02d}"

        else:
            ignored.append(name)
            continue

        key = (base, sub)

        if key in seen_positions:
            raise SystemExit(f"ERROR: Duplicate sequence position for {name}")

        seen_positions.add(key)

        items.append({
            "image_name": name,
            "base": base,
            "sub": sub,
            "slug": slug,
            "page_title": page_title,
            "visible_title": visible_title,
            "alt": alt,
            "html_name": f"{slug}.html",
            "canonical_url": f"{BASE_URL}/drawings/{slug}.html"
        })

    if not items:
        raise SystemExit("ERROR: No valid images found in images/")

    return items, ignored


# ==================================================
# VALIDATE SEQUENCE
# ==================================================
# Ensures that subordinate images are complete.
#
# Example:
#   if tegning_nr852_01 exists,
#   then tegning_nr852.jpg must also exist.
#
# Also checks that there are no missing subordinate
# numbers in a sequence.

def validate(items):

    groups = {}

    for item in items:
        groups.setdefault(item["base"], []).append(item["sub"])

    for base, subs in groups.items():

        subs = sorted(subs)

        if 0 not in subs:
            raise SystemExit(
                f"ERROR: tegning_nr{base}_01 exists but tegning_nr{base}.jpg is missing"
            )

        expected = list(range(0, max(subs) + 1))

        if subs != expected:

            missing = sorted(set(expected) - set(subs))

            raise SystemExit(
                f"ERROR: Missing subordinate image(s) for tegning_nr{base}: "
                + ", ".join(f"_{m:02d}" for m in missing if m != 0)
            )


# ==================================================
# SORT ITEMS
# ==================================================
# Sort archive items numerically by:
#   drawing number
#   subordinate image number

def sort_items(items):
    return sorted(items, key=lambda x: (x["base"], x["sub"]))


# ==================================================
# ARCHIVE REPORT
# ==================================================
# Writes two report files:
#
# 1. archive_report.txt
#    Human-readable overview
#
# 2. archive_report.json
#    Machine-readable data used by viewer.js and index

def write_archive_report(items, ignored):

    total = len(items)
    base_drawings = sum(1 for x in items if x["sub"] == 0)
    attached = total - base_drawings

    first = items[0]["slug"]
    latest = items[-1]["slug"]

    lines = []

    lines.append(f"Total items: {total}")
    lines.append(f"Base drawings: {base_drawings}")
    lines.append(f"Attached images: {attached}")
    lines.append(f"First: {first}")
    lines.append(f"Latest: {latest}")
    lines.append("")
    lines.append("Warnings:")

    if ignored:
        for name in ignored:
            lines.append(f"Ignored file: {name}")
    else:
        lines.append("None")

    lines.append("")
    lines.append("Sequence:")

    for item in items:
        lines.append(item["slug"])

    Path("archive_report.txt").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

    report = {
        "total_items": total,
        "base_drawings": base_drawings,
        "attached_images": attached,
        "first": first,
        "latest": latest,
        "ignored": ignored,
        "sequence": [item["slug"] for item in items]
    }

    Path("archive_report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )


# ==================================================
# SITEMAP
# ==================================================
# Generates sitemap.xml for search engines.
#
# Includes:
#   homepage
#   every drawing page

def write_sitemap(items):

    lines = []

    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    lines.append("  <url>")
    lines.append(f"    <loc>{BASE_URL}/</loc>")
    lines.append("  </url>")

    lines.append("  <url>")
    lines.append(f"    <loc>{BASE_URL}/archive.html</loc>")
    lines.append("  </url>")

    for item in items:
        lines.append("  <url>")
        lines.append(f"    <loc>{item['canonical_url']}</loc>")
        lines.append("  </url>")

    lines.append("</urlset>")

    Path("sitemap.xml").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )


# ==================================================
# ARCHIVE PAGE
# ==================================================
# Generates a simple master index page:
#   /archive.html
#
# This is a visible list of all drawing numbers.

def write_archive_page(items):

    lines = []

    lines.append("""<!doctype html>
<html>
<head>

<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>archive – Christian Skagen</title>
<meta name="description" content="Archive index of numbered drawings by Christian Skagen.">
<link rel="canonical" href="https://cskagen.github.io/archive.html">

<link rel="stylesheet" href="css/style.css">

<style>
.archive-list{
  width:100%;
  max-width:720px;
  margin:auto;
  text-align:left;
  font-size:16px;
  line-height:1.6;
}

.archive-list a{
  color:inherit;
  text-decoration:none;
}

.archive-list a:hover{
  text-decoration:underline;
}

@media (max-width:600px){
  .archive-list{
    font-size:14px;
  }
}
</style>

</head>

<body>

<div class="wrapper">

<h1>
<a href="/">archive</a>
</h1>

<div class="image-area" id="swipe-area">
<div class="archive-list">
""")

    for item in items:
        base = item["base"]
        sub = item["sub"]
        href = f"drawings/{item['html_name']}"

        if sub == 0:
            label = f"{base}"
        else:
            label = f"{base}_{sub:02d}"

        lines.append(f'<div><a href="{href}">{label}</a></div>')

    lines.append("""
</div>
</div>

<div class="prompt-wrap">
<span class="prompt">&gt;</span>
<input id="command" type="text" autocomplete="off" spellcheck="false">
</div>

</div>

<script src="js/viewer.js"></script>

<script>
setupViewer({
  nextPage: null,
  prevPage: null,
  latestPage: null,
  firstPage: null,
  useArchiveReport: true,
  archiveReportPath: "/archive_report.json",
  homePage: "/"
})
</script>

</body>
</html>
""")

    Path("archive.html").write_text(
        "\n".join(lines),
        encoding="utf-8"
    )


# ==================================================
# RENDER DRAWING PAGE
# ==================================================
# Generates one HTML page for each drawing.
#
# Adds:
#   title
#   meta description
#   canonical URL
#   JSON-LD structured data
#   image block
#   console input
#   viewer.js navigation config

def render_page(item, prev_html, next_html, first_html):

    image_src = f"../images/{item['image_name']}"
    page_title = item["page_title"]
    visible_title = item["visible_title"]
    alt = item["alt"]
    canonical_url = item["canonical_url"]

    meta_description = (
        f"Numbered drawing archive page for {visible_title.replace('_', ' ')} "
        f"by Christian Skagen."
    )

    structured_data = {
        "@context": "https://schema.org",
        "@type": "VisualArtwork",
        "@id": canonical_url + "#artwork",
        "url": canonical_url,
        "name": visible_title.replace("_", " "),
        "creator": {
            "@type": "Person",
            "name": "Christian Skagen",
            "url": BASE_URL + "/"
        },
        "image": BASE_URL + "/images/" + item["image_name"],
        "artform": "Drawing",
        "artMedium": "Fountain pen and ruler on paper",
        "isPartOf": {
            "@type": "WebSite",
            "@id": BASE_URL + "/#website",
            "url": BASE_URL + "/",
            "name": "Christian Skagen – drawings"
        }
    }

    structured_data_json = json.dumps(
        structured_data,
        ensure_ascii=False,
        indent=2
    )

    if next_html:
        image_block = f'''<div class="image-area" id="swipe-area">
  <a href="{next_html}">
    <img src="{image_src}" alt="{alt}">
  </a>
</div>'''
    else:
        image_block = f'''<div class="image-area" id="swipe-area">
  <img src="{image_src}" alt="{alt}">
</div>'''

    prev_js = f'"{prev_html}"' if prev_html else "null"
    next_js = f'"{next_html}"' if next_html else "null"

    return f'''<!doctype html>
<html>
<head>

<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>{page_title}</title>
<meta name="description" content="{meta_description}">
<link rel="canonical" href="{canonical_url}">
<script type="application/ld+json">
{structured_data_json}
</script>

<link rel="stylesheet" href="{STYLE_PATH}">

</head>

<body>

<div class="wrapper">

<h1>
<a href="{image_src}" target="_blank">
{visible_title}
</a>
</h1>

{image_block}

<div class="prompt-wrap">
<span class="prompt">&gt;</span>
<input id="command" type="text" autocomplete="off" spellcheck="false">
</div>

</div>

<script src="{VIEWER_PATH}"></script>

<script>

setupViewer({{
  nextPage: {next_js},
  prevPage: {prev_js},
  latestPage: "tegning_latest.html",
  firstPage: "{first_html}",
  homePage: "/",
  archiveReportPath: "/archive_report.json",
  useArchiveReport: false
}})

</script>

</body>
</html>
'''


# ==================================================
# CLEAN OUTPUT DIRECTORY
# ==================================================
# Removes previously generated drawing pages before
# rebuilding, so stale pages do not remain.

def clean_output_dir():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for path in OUTPUT_DIR.iterdir():

        if not path.is_file():
            continue

        name = path.name

        if name == "tegning_latest.html" or re.match(r"^tegning_nr\d+(?:_\d{2})?\.html$", name):
            path.unlink()


# ==================================================
# BUILD
# ==================================================
# Main build sequence.
#
# Order:
#   parse images
#   validate
#   sort
#   write reports
#   write sitemap
#   write archive page
#   clean old drawing pages
#   generate new drawing pages
#   generate tegning_latest.html

def build():

    items, ignored = parse_images()

    validate(items)

    items = sort_items(items)

    write_archive_report(items, ignored)
    write_sitemap(items)
    write_archive_page(items)

    clean_output_dir()

    first_html = items[0]["html_name"]

    for i, item in enumerate(items):

        prev_html = items[i - 1]["html_name"] if i > 0 else None
        next_html = items[i + 1]["html_name"] if i < len(items) - 1 else None

        html = render_page(
            item,
            prev_html,
            next_html,
            first_html
        )

        (OUTPUT_DIR / item["html_name"]).write_text(
            html,
            encoding="utf-8"
        )

    latest = items[-1]
    latest_prev = items[-2]["html_name"] if len(items) > 1 else None

    latest_html = render_page(
        latest,
        latest_prev,
        None,
        first_html
    )

    (OUTPUT_DIR / "tegning_latest.html").write_text(
        latest_html,
        encoding="utf-8"
    )

    print(f"Built {len(items)} pages")
    print(f"First: {items[0]['slug']}")
    print(f"Latest: {items[-1]['slug']}")


# ==================================================
# ENTRY POINT
# ==================================================
# Runs the build when the script is executed directly.

if __name__ == "__main__":
    build()
