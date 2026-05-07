import re
import json
from pathlib import Path
from html import escape

# ==================================================
# CONFIG
# ==================================================

# ==================================================
# IMAGE SOURCE (LOCAL vs CI)
# ==================================================

LOCAL_IMAGE_DIR = Path("/Volumes/kilometers/cskagen_github/drawings")
CI_IMAGE_DIR = Path("images")  # fallback for CI

if LOCAL_IMAGE_DIR.exists():
    IMAGE_DIR = LOCAL_IMAGE_DIR
else:
    IMAGE_DIR = CI_IMAGE_DIR

if not IMAGE_DIR.exists():
    raise FileNotFoundError(
        f"Image directory not found.\n"
        f"Tried: {LOCAL_IMAGE_DIR} and {CI_IMAGE_DIR}"
    )

OUTPUT_DIR = Path("drawings")
CONFIG_PATH = Path("site_config.json")

STYLE_PATH = "../css/style.css"
VIEWER_PATH = "../js/viewer.js"

BASE_URL = "https://cskagen.no"
IMAGE_BASE_URL = "https://images.cskagen.no/images"
REPLICA_IMAGE_BASE_URL = "https://images.cskagen.no/replica_images"
REPLICA_OUTPUT_DIR = Path("replica")
REPLICA_LIST_PAGE = Path("replica.html")

SITE_NAME = "Christian Skagen – drawings"
PERSON_NAME = "Christian Skagen"
DEFAULT_LOCALE = "en"

GA_MEASUREMENT_ID = "G-GLPHFCN8L0"

MAIN_RE = re.compile(r"^tegning_nr(\d+)\.jpg$")

HOME_TITLE = "Christian Skagen – drawings"
HOME_DESCRIPTION = (
    "Christian Skagen is a Norwegian visual artist working with systematic, meditative ink drawing. "
    "The drawings are constructed as linear fields through layered parallel line systems, "
    "accumulating measurable distance — often reaching kilometers of total line length — "
    "built from repeated signals (individual lines)."
)
ARCHIVE_TITLE = "archive – Christian Skagen"
ARCHIVE_DESCRIPTION = (
    "Selection of numbered ink drawings by Norwegian artist Christian Skagen, "
    "constructed as layered parallel line systems forming linear fields."
)
ABOUT_TITLE = "about – Christian Skagen"
ABOUT_DESCRIPTION = (
    "About cskagen.no and the drawing system of Christian Skagen."
)
GLOBAL_KEYWORDS = [
    "Christian Skagen",
    "Norwegian artist",
    "contemporary drawing",
    "ink drawing",
    "conceptual drawing",
    "layered line drawing",
    "parallel line drawing",
    "linear field drawing",
    "sequential archive",
    "visual art",
]

INDEX_INTRO = """Navigation:

arrow keys
swipe gestures
long tap=random

console commands:

about
random (R)
home (return or enter)
archive
print
replica
replica list
xxx (enter drawing number)"""

ABOUT_TEXT = """cskagen.no is a selected record of numbered ink drawings.

each drawing is a personal occurrence:
a remnant of presence resulting from defined systemic parameters.

the drawings are constructed as linear fields:
semi-parallel lines accumulated in layers.
through repetition and overlay, the signal line disperses into a field.

a drawing typically consists of 36 layers.
each layer is drawn by hand, line by line.

small variations in ink and direction produce gradual shifts.

the system is an evolving constant.

navigation reflects the work:
one drawing at a time.
movement is sequential or random.

the site is an emerging production surface.
selected drawings can be reproduced as a4 replicas
each replica is an instance within this system.

(> replica list).

— Christian Skagen"""

ARCHIVE_INTRO = (
    "Selected numbered ink drawings by Christian Skagen. "
    "Use the command line below or select a drawing number."
)


# ==================================================
# HELPERS
# ==================================================


def json_ld(data):
    return json.dumps(data, ensure_ascii=False, indent=2)


def html_escape(text):
    return escape(text, quote=True)


def abs_url(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if not path.startswith("/"):
        path = "/" + path
    return BASE_URL + path


def make_keywords(*extra):
    merged = GLOBAL_KEYWORDS + [x for x in extra if x]
    deduped = []
    seen = set()
    for item in merged:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return ", ".join(deduped)


def google_analytics_tag():
    if not GA_MEASUREMENT_ID:
        return ""

    return f'''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', '{GA_MEASUREMENT_ID}', {{
  'anonymize_ip': true
}});
</script>'''


def page_head(*, title, description, canonical_url, og_image=None, structured_data=None, css_path="css/style.css"):
    og_image = og_image or abs_url("/images/og-default.jpg")
    parts = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{html_escape(title)}</title>",
        f'<meta name="description" content="{html_escape(description)}">',
        f'<meta name="keywords" content="{html_escape(make_keywords())}">',
        '<meta name="robots" content="index,follow,max-image-preview:large">',
        f'<link rel="canonical" href="{html_escape(canonical_url)}">',
        f'<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{html_escape(SITE_NAME)}">',
        f'<meta property="og:locale" content="{DEFAULT_LOCALE}">',
        f'<meta property="og:title" content="{html_escape(title)}">',
        f'<meta property="og:description" content="{html_escape(description)}">',
        f'<meta property="og:url" content="{html_escape(canonical_url)}">',
        f'<meta property="og:image" content="{html_escape(og_image)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{html_escape(title)}">',
        f'<meta name="twitter:description" content="{html_escape(description)}">',
        f'<meta name="twitter:image" content="{html_escape(og_image)}">',
        f'<link rel="stylesheet" href="{html_escape(css_path)}">',
        google_analytics_tag(),
    ]
    if structured_data is not None:
        parts.insert(
            6,
            '<script type="application/ld+json">\n' + json_ld(structured_data) + '\n</script>'
        )
    return "\n".join(parts)


def website_graph(extra_nodes=None):
    graph = [
        {
            "@type": "Person",
            "@id": BASE_URL + "/#person",
            "name": PERSON_NAME,
            "url": BASE_URL + "/",
        },
        {
            "@type": "WebSite",
            "@id": BASE_URL + "/#website",
            "url": BASE_URL + "/",
            "name": SITE_NAME,
            "description": HOME_DESCRIPTION,
            "creator": {"@id": BASE_URL + "/#person"},
            "inLanguage": DEFAULT_LOCALE,
        },
    ]
    if extra_nodes:
        graph.extend(extra_nodes)
    return {"@context": "https://schema.org", "@graph": graph}


# ==================================================
# PARSE IMAGES
# ==================================================


def parse_images():
    if not IMAGE_DIR.exists():
        raise SystemExit("ERROR: images/ folder not found.")

    items = []
    ignored = []
    seen_bases = set()

    for path in sorted(IMAGE_DIR.iterdir()):
        if not path.is_file():
            continue

        name = path.name
        m_main = MAIN_RE.match(name)

        if not m_main:
            ignored.append(name)
            continue

        base = int(m_main.group(1))

        if base in seen_bases:
            raise SystemExit(f"ERROR: Duplicate base drawing for {name}")
        seen_bases.add(base)

        slug = f"tegning_nr{base}"
        visible_title = slug
        display_name = f"tegning nr {base}"
        page_title = f"tegning nr {base} – Christian Skagen"
        alt = f"Ink drawing nr {base} by Christian Skagen"

        image_url = f"{IMAGE_BASE_URL}/{name}"
        canonical_url = f"{BASE_URL}/drawings/{slug}.html"

        items.append({
            "image_name": name,
            "base": base,
            "slug": slug,
            "page_title": page_title,
            "visible_title": visible_title,
            "display_name": display_name,
            "alt": alt,
            "html_name": f"{slug}.html",
            "canonical_url": canonical_url,
            "image_url": image_url,
        })

    if not items:
        raise SystemExit("ERROR: No valid images found in images/")

    return items, ignored


# ==================================================
# VALIDATE / SORT
# ==================================================


def validate(items):
    seen_bases = set()

    for item in items:
        base = item["base"]
        if base in seen_bases:
            raise SystemExit(f"ERROR: Duplicate base drawing number: tegning_nr{base}")
        seen_bases.add(base)


def sort_items(items):
    return sorted(items, key=lambda x: x["base"])


def load_omit_set():
    if not CONFIG_PATH.exists():
        return set()

    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    omit = data.get("omit", [])

    return {int(x) for x in omit}


# ==================================================
# REPLICA HELPERS
# ==================================================


def replica_image_name(base: int) -> str:
    return f"tegning_nr{base}_a4.jpg"


def replica_image_url(base: int) -> str:
    return f"{REPLICA_IMAGE_BASE_URL}/{replica_image_name(base)}"


def replica_html_name(base: int) -> str:
    return f"tegning_nr{base}.html"


def replica_html_url(base: int) -> str:
    return f"{BASE_URL}/replica/{replica_html_name(base)}"


def replica_bases_for_v1():
    return {
            791, 792, 793, 797, 800, 801,
            802, 803, 804, 805, 806, 807,
            808, 813, 819, 821, 823, 824,
            826, 827, 828, 837, 838, 839, 
            840, 841, 842, 844, 845, 851, 
            852, 853, 854, 855, 857, 858,
            }


def render_replica_page(item):
    replica_src = replica_image_url(item["base"])
    replica_page_url = replica_html_url(item["base"])
    title = f"tegning nr {item['base']} replica – Christian Skagen"
    description = f"A4 print page for drawing nr {item['base']}."

    head = page_head(
        title=title,
        description=description,
        canonical_url=replica_page_url,
        og_image=item["image_url"],
        structured_data=None,
        css_path="../css/style.css",
    ).replace(
        '<meta name="robots" content="index,follow,max-image-preview:large">',
        '<meta name="robots" content="noindex,nofollow">'
    )

    return f'''<!doctype html>
<html>
<head>
{head}
<style>
@page {{
  size: A4;
  margin: 0;
}}

html, body {{
  margin: 0;
  padding: 0;
  background: #ffffff;
}}

body {{
  position: relative;
}}

.replica-meta-top {{
  position: absolute;
  top: 8mm;
  right: 18mm;
  text-align: right;
  font-size: 10pt;
  line-height: 1.3;
  font-family: Baskerville, "Baskerville Old Face", Georgia, serif;
  color: #000;
  white-space: pre-line;
}}

.replica-meta-bottom {{
  position: absolute;
  bottom: 8mm;
  right: 18mm;
  text-align: right;
  font-size: 10pt;
  line-height: 1.3;
  font-family: Baskerville, "Baskerville Old Face", Georgia, serif;
  color: #000;
  white-space: pre-line;
}}

.ios-clean .replica-meta-top {{
  display: none !important;
}}

.replica-print {{
  width: 210mm;
  height: 297mm;
}}

.replica-print img {{
  display: block;
  width: 210mm;
  height: 297mm;
  object-fit: contain;
}}

@media screen {{
  body {{
    background: #dcdcdc;
    display: flex;
    justify-content: center;
    align-items: flex-start;
  }}

  .replica-print {{
    width: min(100%, 210mm);
    height: auto;
    box-shadow: 0 0 0 1px rgba(0,0,0,0.08);
  }}

  .replica-print img {{
    width: 100%;
    height: auto;
  }}
}}
</style>
</head>
<body>
<div class="replica-meta-top">cskagen.no/replica/tegning_nr{item["base"]}.html</div>

<div class="replica-print">
  <img
    src="{replica_src}"
    alt="A4 replica for drawing nr {item['base']}"
    onerror="document.body.innerHTML='<div style=&quot;padding:24px;font-family:Arial,sans-serif;&quot;>Replica not available for drawing nr {item["base"]}.</div>';"
  >
</div>

<div class="replica-meta-bottom"></div>

<script>
(function () {{
  const params = new URLSearchParams(window.location.search);
  if (params.get("clean") === "1") {{
    document.documentElement.classList.add("ios-clean");
  }}
}})();

window.addEventListener("load", function () {{
  const now = new Date();
  const dd = String(now.getDate()).padStart(2, "0");
  const mm = String(now.getMonth() + 1).padStart(2, "0");
  const yyyy = now.getFullYear();
  const hh = String(now.getHours()).padStart(2, "0");
  const min = String(now.getMinutes()).padStart(2, "0");

  const timestamp = `${{dd}}/${{mm}}/${{yyyy}}, ${{hh}}:${{min}}`;
  document.querySelector(".replica-meta-bottom").textContent =
    `${{timestamp}} - > replica`;

  setTimeout(function () {{
    window.print();
  }}, 180);
}});
</script>
</body>
</html>
'''


def write_replica_list_page(items):
    lines = [
        "<!doctype html>",
        "<html>",
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>replica – Christian Skagen</title>",
        '<meta name="robots" content="noindex,nofollow">',
        '<link rel="stylesheet" href="css/style.css">',
        "<style>",
        ".replica-grid{width:100%;max-width:1400px;margin:auto;display:grid;grid-template-columns:repeat(6,1fr);gap:4px 12px;font-size:13px;line-height:1.35;}",
        ".replica-grid a{color:inherit;text-decoration:none;}",
        ".replica-grid a:hover{text-decoration:underline;}",
        ".replica-meta{width:100%;max-width:1400px;margin:0 auto 10px auto;text-align:left;font-size:14px;line-height:1.5;}",
        ".replica-item{min-width:0;word-break:break-word;}",
        "@media (max-width:900px){.replica-grid{grid-template-columns:repeat(3,1fr);}}",
        "@media (max-width:600px){.replica-grid{grid-template-columns:repeat(2,1fr);font-size:12px;}}",
        "</style>",
        "</head>",
        "<body>",
        '<div class="wrapper">',
        '<h1><a href="/">replica</a></h1>',
        '<div class="replica-meta">Available A4 replica print pages. Commands: replica, replica 851, replica 858.</div>',
        '<div class="image-area" id="swipe-area">',
        '<div class="replica-grid">',
    ]

    for item in items:
        href = f"replica/{replica_html_name(item['base'])}"
        label = f"{item['base']}"
        lines.append(f'<div class="replica-item"><a href="{href}">{label}</a></div>')

    lines.extend([
        "</div>",
        "</div>",
        '<div class="prompt-wrap">',
        '<span class="prompt">&gt;</span>',
        '<input id="command" type="text" autocomplete="off" spellcheck="false" aria-label="Command input">',
        "</div>",
        "</div>",
        '<script src="js/viewer.js"></script>',
        "<script>",
        "setupViewer({",
        "  nextPage: null,",
        "  prevPage: null,",
        "  latestPage: null,",
        "  firstPage: null,",
        "  useArchiveReport: true,",
        "  archiveReportPath: \"/archive_report.json\",",
        "  homePage: \"/\"",
        "})",
        "</script>",
        "</body>",
        "</html>",
    ])

    REPLICA_LIST_PAGE.write_text("\n".join(lines), encoding="utf-8")


# ==================================================
# REPORT / SITEMAP
# ==================================================


def write_archive_report(items, ignored):
    total = len(items)
    base_drawings = len(items)
    attached = 0

    first = items[0]["slug"]
    latest = items[-1]["slug"]

    lines = [
        f"Total items: {total}",
        f"Base drawings: {base_drawings}",
        f"Attached images: {attached}",
        f"First: {first}",
        f"Latest: {latest}",
        "",
        "Warnings:",
    ]

    if ignored:
        lines.extend(f"Ignored file: {name}" for name in ignored)
    else:
        lines.append("None")

    lines.extend(["", "Sequence:"])
    lines.extend(item["slug"] for item in items)

    Path("archive_report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = {
        "total_items": total,
        "base_drawings": base_drawings,
        "attached_images": attached,
        "first": first,
        "latest": latest,
        "ignored": ignored,
        "sequence": [item["slug"] for item in items],
    }
    Path("archive_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


def write_archive_report_page(items, ignored):
    total = len(items)
    base_drawings = len(items)
    attached = 0

    first = items[0]["slug"]
    latest = items[-1]["slug"]

    summary_entries = [
        f"Total items: {total}",
        f"Base drawings: {base_drawings}",
        f"Attached images: {attached}",
        f"First: {first}",
        f"Latest: {latest}",
        "",
        "Warnings:",
    ]

    if ignored:
        summary_entries.extend(f"Ignored file: {name}" for name in ignored)
    else:
        summary_entries.append("None")

    sequence_entries = [item["slug"] for item in items]
    summary_text = "\n".join(summary_entries)

    lines = [
        "<!doctype html>",
        "<html>",
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>archive report – Christian Skagen</title>",
        '<meta name="robots" content="noindex,nofollow,noarchive">',
        '<link rel="stylesheet" href="css/style.css">',
        "<style>",
        ".report-wrap{width:100%;max-width:1400px;margin:auto;}",
        ".report-meta{width:100%;max-width:720px;margin:0 0 16px 0;text-align:left;font-size:14px;line-height:1.5;font-family:Courier New, Courier, monospace;white-space:pre-wrap;}",
        ".report-sequence-label{width:100%;max-width:1400px;margin:0 auto 8px auto;text-align:left;font-size:14px;line-height:1.5;font-family:Courier New, Courier, monospace;}",
        ".report-grid{width:100%;max-width:1400px;margin:auto;display:grid;grid-template-columns:repeat(4,1fr);gap:4px 12px;font-size:12px;line-height:1.35;font-family:Courier New, Courier, monospace;}",
        ".report-item{min-width:0;word-break:break-word;white-space:pre-wrap;}",
        "@media (max-width:1200px){.report-grid{grid-template-columns:repeat(3,1fr);}}",
        "@media (max-width:900px){.report-grid{grid-template-columns:repeat(2,1fr);}}",
        "@media (max-width:600px){.report-grid{grid-template-columns:1fr;font-size:11px;}}",
        "</style>",
        "</head>",
        "<body>",
        '<div class="wrapper">',
        '<h1><a href="/">archive report</a></h1>',
        '<div class="image-area" id="swipe-area">',
        '<div class="report-wrap">',
        f'<div class="report-meta">{html_escape(summary_text)}</div>',
        '<div class="report-sequence-label">Sequence:</div>',
        '<div class="report-grid">',
    ]

    for entry in sequence_entries:
        lines.append(f'<div class="report-item">{html_escape(entry)}</div>')

    lines.extend([
        "</div>",
        "</div>",
        "</div>",
        '<div class="prompt-wrap">',
        '<span class="prompt">&gt;</span>',
        '<input id="command" type="text" autocomplete="off" spellcheck="false" aria-label="Command input">',
        "</div>",
        "</div>",
        '<script src="js/viewer.js"></script>',
        "<script>",
        "setupViewer({",
        "  nextPage: null,",
        "  prevPage: null,",
        "  latestPage: null,",
        "  firstPage: null,",
        "  useArchiveReport: true,",
        "  archiveReportPath: \"/archive_report.json\",",
        "  homePage: \"/\"",
        "})",
        "</script>",
        "</body>",
        "</html>",
    ])

    Path("archive_report.html").write_text("\n".join(lines), encoding="utf-8")


def write_sitemap(items):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        "  <url>",
        f"    <loc>{BASE_URL}/</loc>",
        "  </url>",
        "  <url>",
        f"    <loc>{BASE_URL}/archive.html</loc>",
        "  </url>",
        "  <url>",
        f"    <loc>{BASE_URL}/about.html</loc>",
        "  </url>",
    ]

    for item in items:
        lines.extend([
            "  <url>",
            f"    <loc>{item['canonical_url']}</loc>",
            "  </url>",
        ])

    lines.append("</urlset>")
    Path("sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ==================================================
# PAGE BUILDERS
# ==================================================


def write_home_page(items):
    first_item = items[0]
    latest_item = items[-1]

    structured = website_graph([
        {
            "@type": "CollectionPage",
            "@id": BASE_URL + "/#home",
            "url": BASE_URL + "/",
            "name": HOME_TITLE,
            "description": HOME_DESCRIPTION,
            "isPartOf": {"@id": BASE_URL + "/#website"},
            "about": {"@id": BASE_URL + "/#person"},
        }
    ])

    head = page_head(
        title=HOME_TITLE,
        description=HOME_DESCRIPTION,
        canonical_url=BASE_URL + "/",
        og_image=latest_item["image_url"],
        structured_data=structured,
        css_path="css/style.css",
    )

    html = f'''<!doctype html>
<html>
<head>
<meta name="google-site-verification" content="tyE3vdezEKc1F00i3hvjLin892w6CZbKQboJcbj_Azk">
{head}
<style>
.index-text{{
  width:100%;
  max-width:720px;
  margin:auto;
  text-align:left;
  font-size:16px;
  line-height:1.5;
  white-space:pre-line;
}}
.visually-hidden{{
  position:absolute;
  width:1px;
  height:1px;
  padding:0;
  margin:-1px;
  overflow:hidden;
  clip:rect(0,0,0,0);
  white-space:nowrap;
  border:0;
}}
@media (max-width:600px){{
  .index-text{{font-size:14px;}}
}}
</style>
</head>
<body>
<div class="wrapper">
<h1><a href="/">drawings</a></h1>
<div class="image-area" id="swipe-area">
<div class="index-text">{INDEX_INTRO}</div>
</div>
<p class="visually-hidden">{HOME_DESCRIPTION} The archive currently spans numbered drawings from {first_item['display_name']} to {latest_item['display_name']}.</p>
<div class="prompt-wrap">
<span class="prompt">&gt;</span>
<input id="command" type="text" autocomplete="off" spellcheck="false" aria-label="Command input">
</div>
</div>
<script src="js/viewer.js"></script>
<script>
setupViewer({{
  nextPage: null,
  prevPage: null,
  latestPage: null,
  firstPage: null,
  useArchiveReport: true,
  archiveReportPath: "/archive_report.json",
  homePage: "/"
}})
</script>
</body>
</html>
'''
    Path("index.html").write_text(html, encoding="utf-8")

def write_about_page():
    structured = website_graph([
        {
            "@type": "AboutPage",
            "@id": BASE_URL + "/about.html#about",
            "url": BASE_URL + "/about.html",
            "name": ABOUT_TITLE,
            "description": ABOUT_DESCRIPTION,
            "isPartOf": {"@id": BASE_URL + "/#website"},
            "about": {"@id": BASE_URL + "/#person"},
        }
    ])

    head = page_head(
        title=ABOUT_TITLE,
        description=ABOUT_DESCRIPTION,
        canonical_url=BASE_URL + "/about.html",
        structured_data=structured,
        css_path="css/style.css",
    )

    html = f'''<!doctype html>
<html>
<head>
{head}
<style>
.about-text{{
  width:100%;
  max-width:720px;
  margin:auto;
  text-align:left;
  font-size:16px;
  line-height:1.5;
  white-space:pre-line;
}}
@media (max-width:600px){{
  .about-text{{font-size:14px;}}
}}
</style>
</head>
<body>
<div class="wrapper">
<h1><a href="/">about</a></h1>
<div class="image-area" id="swipe-area">
<div class="about-text">{html_escape(ABOUT_TEXT)}</div>
</div>
<div class="prompt-wrap">
<span class="prompt">&gt;</span>
<input id="command" type="text" autocomplete="off" spellcheck="false" aria-label="Command input">
</div>
</div>
<script src="js/viewer.js"></script>
<script>
setupViewer({{
  nextPage: null,
  prevPage: null,
  latestPage: null,
  firstPage: null,
  useArchiveReport: true,
  archiveReportPath: "/archive_report.json",
  homePage: "/"
}})
</script>
</body>
</html>
'''
    Path("about.html").write_text(html, encoding="utf-8")

def write_404_page():
    head = page_head(
        title="404 – Christian Skagen",
        description="Drawing not found.",
        canonical_url=BASE_URL + "/404.html",
        structured_data=None,
        css_path="/css/style.css",
    ).replace(
        '<meta name="robots" content="index,follow,max-image-preview:large">',
        '<meta name="robots" content="noindex,nofollow">'
    )

    html = f'''<!doctype html>
<html>
<head>
{head}
<style>
.not-found-text{{
  width:100%;
  max-width:720px;
  margin:auto;
  text-align:left;
  font-size:16px;
  line-height:1.5;
  white-space:pre-line;
}}
@media (max-width:600px){{
  .not-found-text{{font-size:14px;}}
}}
</style>
</head>
<body>
<div class="wrapper">
<h1><a href="/">404</a></h1>
<div class="image-area" id="swipe-area">
<div class="not-found-text">drawing not found

the drawing may have been removed from the public sequence.

press return
or type home</div>
</div>
<div class="prompt-wrap">
<span class="prompt">&gt;</span>
<input id="command" type="text" autocomplete="off" spellcheck="false" aria-label="Command input">
</div>
</div>
<script src="/js/viewer.js"></script>
<script>
setupViewer({{
  nextPage: null,
  prevPage: null,
  latestPage: null,
  firstPage: null,
  useArchiveReport: true,
  archiveReportPath: "/archive_report.json",
  homePage: "/"
}})

document.addEventListener("keydown", function(event) {{
  if (event.key === "Enter" || event.key === "Return") {{
    const command = document.getElementById("command");
    if (!command || document.activeElement !== command) {{
      window.location.href = "/";
    }}
  }}
}});
</script>
</body>
</html>
'''
    Path("404.html").write_text(html, encoding="utf-8")

def write_archive_page(items):
    latest_item = items[-1]
    structured = website_graph([
        {
            "@type": "CollectionPage",
            "@id": BASE_URL + "/archive.html#collection",
            "url": BASE_URL + "/archive.html",
            "name": "Archive of numbered drawings",
            "description": ARCHIVE_DESCRIPTION,
            "isPartOf": {"@id": BASE_URL + "/#website"},
            "about": {"@id": BASE_URL + "/#person"},
        }
    ])

    head = page_head(
        title=ARCHIVE_TITLE,
        description=ARCHIVE_DESCRIPTION,
        canonical_url=BASE_URL + "/archive.html",
        og_image=latest_item["image_url"],
        structured_data=structured,
        css_path="css/style.css",
    )

    lines = [
        "<!doctype html>",
        "<html>",
        "<head>",
        head,
        "<style>",
        ".archive-grid{width:100%;max-width:1400px;margin:auto;display:grid;grid-template-columns:repeat(13,1fr);gap:4px 10px;font-size:13px;line-height:1.35;}",
        ".archive-grid a{color:inherit;text-decoration:none;}",
        ".archive-grid a:hover{text-decoration:underline;}",
        ".archive-meta{width:100%;max-width:1400px;margin:0 auto 10px auto;text-align:left;font-size:14px;line-height:1.5;}",
        ".archive-item{min-width:0;word-break:break-word;}",
        "@media (max-width:600px){.archive-grid{grid-template-columns:repeat(13,1fr);gap:3px 4px;font-size:11px;line-height:1.25;}}",
        "</style>",
        "</head>",
        "<body>",
        '<div class="wrapper">',
        '<h1><a href="/">archive</a></h1>',
        f'<div class="archive-meta">{html_escape(ARCHIVE_INTRO)}</div>',
        '<div class="image-area" id="swipe-area">',
        '<div class="archive-grid">',
    ]


    for item in items:
        label = str(item["base"])
        href = f'drawings/{item["html_name"]}'
        lines.append(f'<div class="archive-item"><a href="{href}">{label}</a></div>')

    lines.extend([
        "</div>",
        "</div>",
        '<div class="prompt-wrap">',
        '<span class="prompt">&gt;</span>',
        '<input id="command" type="text" autocomplete="off" spellcheck="false" aria-label="Command input">',
        "</div>",
        "</div>",
        '<script src="js/viewer.js"></script>',
        "<script>",
        "setupViewer({",
        "  nextPage: null,",
        "  prevPage: null,",
        "  latestPage: null,",
        "  firstPage: null,",
        "  useArchiveReport: true,",
        "  archiveReportPath: \"/archive_report.json\",",
        "  homePage: \"/\"",
        "})",
        "</script>",
        "</body>",
        "</html>",
    ])

    Path("archive.html").write_text("\n".join(lines), encoding="utf-8")


def artwork_structured_data(item):
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Person",
                "@id": BASE_URL + "/#person",
                "name": PERSON_NAME,
                "url": BASE_URL + "/",
            },
            {
                "@type": "WebSite",
                "@id": BASE_URL + "/#website",
                "url": BASE_URL + "/",
                "name": SITE_NAME,
            },
            {
                "@type": "VisualArtwork",
                "@id": item["canonical_url"] + "#artwork",
                "url": item["canonical_url"],
                "name": item["display_name"],
                "creator": {"@id": BASE_URL + "/#person"},
                "image": item["image_url"],
                "artform": "Drawing",
                "artMedium": "Fountain pen and ruler on paper",
                "genre": "Contemporary drawing",
                "keywords": make_keywords("systematic drawing", "numbered drawings"),
                "isPartOf": {"@id": BASE_URL + "/#website"},
            },
            {
                "@type": "ImageObject",
                "@id": item["image_url"] + "#image",
                "contentUrl": item["image_url"],
                "url": item["image_url"],
                "description": item["alt"],
                "creator": {"@id": BASE_URL + "/#person"},
                "creditText": "Christian Skagen",
                "copyrightNotice": "© Christian Skagen"
            },
            {
                "@type": "BreadcrumbList",
                "@id": item["canonical_url"] + "#breadcrumb",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "drawings",
                        "item": BASE_URL + "/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "archive",
                        "item": BASE_URL + "/archive.html",
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": item["display_name"],
                        "item": item["canonical_url"],
                    },
                ],
            },
        ],
    }


def render_page(item, prev_html, next_html, first_html):
    image_src = f"{IMAGE_BASE_URL}/{item['image_name']}"
    meta_description = (
        f"Drawing nr {item['base']}. "
        "A linear field constructed through layered parallel line systems in ink."
    )

    head = page_head(
        title=item["page_title"],
        description=meta_description,
        canonical_url=item["canonical_url"],
        og_image=item["image_url"],
        structured_data=artwork_structured_data(item),
        css_path=STYLE_PATH,
    )

    image_block = f'''<div class="image-area" id="swipe-area">
  <img src="{image_src}" alt="{html_escape(item['alt'])}" loading="eager" decoding="async">
</div>'''

    prev_js = f'"{prev_html}"' if prev_html else "null"
    next_js = f'"{next_html}"' if next_html else "null"

    return f'''<!doctype html>
<html>
<head>
{head}
</head>
<body>
<div class="wrapper">
<h1>
<a href="{image_src}" target="_blank">{html_escape(item['visible_title'])}</a>
</h1>
{image_block}
<div class="prompt-wrap">
<span class="prompt">&gt;</span>
<input id="command" type="text" autocomplete="off" spellcheck="false" aria-label="Command input">
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
# CLEAN / BUILD
# ==================================================


def clean_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in OUTPUT_DIR.iterdir():
        if not path.is_file():
            continue
        name = path.name
        if name == "tegning_latest.html" or re.match(r"^tegning_nr\d+\.html$", name):
            path.unlink()


def clean_replica_output_dir():
    REPLICA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in REPLICA_OUTPUT_DIR.iterdir():
        if not path.is_file():
            continue
        name = path.name
        if re.match(r"^tegning_nr\d+\.html$", name):
            path.unlink()


def build():
    items, ignored = parse_images()

    omit_set = load_omit_set()
    items = [item for item in items if item["base"] not in omit_set]

    validate(items)
    items = sort_items(items)

    write_archive_report(items, ignored)
    write_archive_report_page(items, ignored)
    write_sitemap(items)
    write_home_page(items)
    write_about_page()
    write_archive_page(items)
    write_404_page()

    clean_output_dir()
    clean_replica_output_dir()

    first_html = items[0]["html_name"]

    for i, item in enumerate(items):
        prev_html = items[i - 1]["html_name"] if i > 0 else None
        next_html = items[i + 1]["html_name"] if i < len(items) - 1 else None
        html = render_page(item, prev_html, next_html, first_html)
        (OUTPUT_DIR / item["html_name"]).write_text(html, encoding="utf-8")

    latest = items[-1]
    latest_prev = items[-2]["html_name"] if len(items) > 1 else None
    latest_html = render_page(latest, latest_prev, None, first_html)
    (OUTPUT_DIR / "tegning_latest.html").write_text(latest_html, encoding="utf-8")

    replica_bases = replica_bases_for_v1()
    replica_items = [item for item in items if item["base"] in replica_bases]

    for item in replica_items:
        replica_html = render_replica_page(item)
        (REPLICA_OUTPUT_DIR / replica_html_name(item["base"])).write_text(replica_html, encoding="utf-8")

    write_replica_list_page(replica_items)

    print(f"Built {len(items)} pages")
    print(f"First: {items[0]['slug']}")
    print(f"Latest: {items[-1]['slug']}")
    print(f"Replica pages: {len(replica_items)}")


if __name__ == "__main__":
    build()
