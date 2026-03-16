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
