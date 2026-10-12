#!/usr/bin/env python3
"""Build the Contact page and the garden center category pages.

Run from the repo root:  python3 tools/build-pages.py

Each page reuses the Garden Center page's <head> styles and icon sprite, so a
style change made on /garden-center/ carries over the next time this runs.
Pages still waiting on Amanda (mulch, soil, compost, houseplants, hanging
baskets) stay under construction in tools/build-under-construction.py.
"""
import html
import json
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = open(os.path.join(ROOT, "garden-center", "index.html"), encoding="utf-8").read()

# Everything from <meta charset> through </style>, minus the title and description
HEAD_STYLE = SRC[SRC.index("<link rel=\"icon\""):SRC.index("</style>") + len("</style>")]
SPRITE = SRC[SRC.index("<svg width=\"0\""):SRC.index("</svg>\n\n<header")]

EXTRA_ICONS = """
<symbol id="i-phone" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></symbol>
<symbol id="i-map-pin" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/></g></symbol>
<symbol id="i-sun" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></g></symbol>
<symbol id="i-mountain" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="m8 3 4 8 5-5 5 15H2L8 3z"/></symbol>
<symbol id="i-heart" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></symbol>
<symbol id="i-cloud-rain" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M4 14.9A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.24M16 14v6M8 14v6M12 16v6"/></symbol>
<symbol id="i-hammer" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="m15 12-8.373 8.373a1 1 0 1 1-3-3L12 9M18 15l4-4M21.5 11.5l-1.914-1.914A2 2 0 0 1 19 8.172V7l-2.26-2.26a6 6 0 0 0-4.202-1.756L9 2.96l.92.82A6.18 6.18 0 0 1 12 8.4V10l2 2h1.172a2 2 0 0 1 1.414.586L18.5 14.5"/></symbol>
<symbol id="i-clipboard" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="8" height="4" x="8" y="2" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2M12 11h4M12 16h4M8 11h.01M8 16h.01"/></g></symbol>
"""

PHONE = "(870) 489-5463"
TEL = "tel:+18704895463"

REVIEWS = [
    ("Shop here before anywhere else. They have it all with fair prices and a very helpful staff.", "Carl C."),
    ("Great selection of healthy plants and shrubs at reasonable prices. Bulk mulch and other landscaping supplies. Friendly and helpful personnel. Worth visiting.", "C. C."),
    ("Amanda went above and beyond to help me work something out for my Mother's day gift all the way from Texas. So so so helpful! My mother said she had great plant choices.", "C. F."),
    ("Amanda always has the best variety and most reasonable prices around. I love going there!!", "Sara M."),
]

LOCAL_BUSINESS = {
    "@context": "https://schema.org",
    "@type": "GardenStore",
    "name": "Amanda's Villa Landscaping and Garden Center",
    "telephone": "+1-870-489-5463",
    "address": {"@type": "PostalAddress", "streetAddress": "7901 Dollarway Road", "addressLocality": "White Hall", "addressRegion": "AR", "postalCode": "71602", "addressCountry": "US"},
    "areaServed": "Arkansas",
}


def esc(s):
    return html.escape(s, quote=True)


def icon(name):
    return f'<span class="ic-badge"><svg class="ic" aria-hidden="true"><use href="#i-{name}"/></svg></span>'


def img(p, src, alt, w, h, cls="", lazy=True):
    c = f' class="{cls}"' if cls else ""
    l = ' loading="lazy"' if lazy else ""
    return f'<img width="{w}" height="{h}"{c} src="{p}img/{src}" alt="{esc(alt)}"{l}>'


def cta_row(p, primary, extra_cls=" cta-row"):
    label, href = primary
    return (f'<div class="btn-row{extra_cls}">\n'
            f'      <a class="btn btn--primary" href="{href.replace("~/", p)}">{label}</a>\n'
            f'      <a class="btn btn--secondary" href="{TEL}">Call {PHONE}</a>\n'
            f'    </div>')


def nav(p, current):
    items = [("landscaping/", "Landscaping"), ("hardscape/", "Hardscape"), ("garden-center/", "Garden Center"), ("about/", "About")]
    cur = ' aria-current="page"'
    links = "\n".join(
        f'        <li><a href="{p}{u}"{cur if u == current else ""}>{t}</a></li>' for u, t in items)
    menu = "\n".join(f'          <li><a href="{p}{u}">{t}</a></li>' for u, t in items)
    return f"""    <nav class="nav" aria-label="Main">
      <a class="wordmark" href="{p}"><b>Amanda's Villa</b><span>Landscaping · Hardscape · Garden Center</span></a>
      <ul class="nav-links">
{links}
      </ul>
      <a class="btn btn--onphoto" href="{TEL}">Call {PHONE}</a>
      <details>
        <summary>Menu</summary>
        <ul>
{menu}
          <li><a href="{TEL}">Call {PHONE}</a></li>
        </ul>
      </details>
    </nav>"""


def footer(p):
    return f"""<footer class="foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="wordmark" href="{p}"><b>Amanda's Villa</b><span>Landscaping · Hardscape · Garden Center · White Hall, Arkansas</span></a>
        <p class="foot-tag">Together, plant the space your yard deserves.</p>
      </div>
      <ul>
        <li><a href="{p}landscaping/">Landscaping</a></li>
        <li><a href="{p}hardscape/">Hardscape</a></li>
        <li><a href="{p}garden-center/">Garden Center</a></li>
        <li><a href="{p}about/">About</a></li>
      </ul>
      <ul>
        <li>7901 Dollarway Road<br>White Hall, AR 71602</li>
        <li><a href="{TEL}">{PHONE}</a></li>
        <li><span class="todo">Hours</span></li>
      </ul>
    </div>
    <small>© 2026 Amanda's Villa Landscaping and Garden Center.</small>
  </div>
</footer>"""


def faq_ld(faqs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}}
            for q, a in faqs
        ],
    }


def reviews_section(heading):
    figs = "\n".join(
        f'      <figure class="review">\n        <blockquote><p>"{esc(t)}"</p></blockquote>\n        <figcaption>{n}, Google review</figcaption>\n      </figure>'
        for t, n in REVIEWS)
    return f"""<!-- REVIEWS: verbatim Google reviews, first name and last initial only -->
<section class="band">
  <div class="wrap">
    <div class="head">
      <h2>{heading}</h2>
    </div>
    <div class="reviews">
{figs}
    </div>
  </div>
</section>"""


def page(d):
    p = d["prefix"]
    faqs = d["faqs"]
    faq_html = "\n".join(f"      <details><summary>{esc(q)}</summary><div><p>{a}</p></div></details>" for q, a in faqs)
    lds = [LOCAL_BUSINESS, faq_ld([(q, a) for q, a in faqs if "todo" not in a])]
    ld_html = "\n".join(f'<script type="application/ld+json">\n{json.dumps(x, indent=2, ensure_ascii=False)}\n</script>' for x in lds)
    hero = d["hero"]
    body = "\n\n".join(s(p) if callable(s) else s for s in d["sections"])
    return alternate_bands(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{esc(d["title"])}</title>
<meta name="description" content="{esc(d["description"])}">
{HEAD_STYLE}
{ld_html}
</head>
<body>
{SPRITE}{EXTRA_ICONS}</svg>

<header class="hero">
  <div class="hero-card">
    <picture>
      <source media="(max-width: 640px)" srcset="{p}img/{hero["img"]}-tall.jpg">
      <img width="1600" height="900" src="{p}img/{hero["img"]}-wide.jpg" alt="{esc(hero["alt"])}" fetchpriority="high">
    </picture>
{nav(p, d["current"])}
    <div class="hero-copy">
      <h1>{hero["h1"]}</h1>
      <p class="hero-sub">{hero["sub"]}</p>
      <div class="hero-ctas">
        <a class="btn btn--onphoto" href="{hero["cta"][1].replace("~/", p)}">{hero["cta"][0]}</a>
        <a class="btn btn--ghost" href="{TEL}">Call {PHONE}</a>
      </div>
      <p class="hero-meta">7901 Dollarway Road, White Hall · <span class="todo">Hours</span></p>
    </div>
    <p class="standin">Stand-in photo. {hero["standin"]}</p>
  </div>
</header>

<main>

{body}

<!-- FAQ -->
<section class="band">
  <div class="wrap">
    <div class="head">
      <h2>{d["faq_heading"]}</h2>
    </div>
    <div class="split split--top">
    <div class="faq">
{faq_html}
    </div>
    <figure class="split-media">
      {img(p, *d["faq_img"])}
    </figure>
    </div>
  </div>
</section>

<!-- CLOSING CTA -->
<section class="band closing closing--photo">
  {img(p, d["closing"]["img"], "", 2000, 1250)}
  <div class="wrap">
    <h2>{d["closing"]["h2"]}</h2>
    <p>7901 Dollarway Road, White Hall, Arkansas · {PHONE} · <span class="todo">Hours</span></p>
    {cta_row(p, d["closing"]["cta"], "")}
  </div>
</section>

</main>

{footer(p)}

</body>
</html>
""")


def alternate_bands(doc):
    """Give every content band an alternating background, plain first, so removing
    or reordering a section never leaves two of the same shade side by side."""
    n = [0]

    def swap(m):
        n[0] += 1
        return '<section class="band band--alt"' if n[0] % 2 == 0 else '<section class="band"'
    return re.sub(r'<section class="band(?: band--alt)?"', swap, doc)


# ---------- shared section builders ----------

def guide(h2, para, photo, proof):
    def f(p):
        items = "\n".join(f"        <li>{icon(i)}<span>{t}</span></li>" for i, t in proof)
        return f"""<!-- GUIDE -->
<section class="band band--alt">
  <div class="wrap split split--flip">
    <figure class="split-media">
      {img(p, *photo)}
    </figure>
    <div>
      <h2>{h2}</h2>
      <div class="prose" style="margin-top: var(--space-6)">
        <p>{para}</p>
      </div>
      <ul class="proof">
{items}
      </ul>
    </div>
  </div>
</section>"""
    return f


def lot(h2, intro, items, note, photos, alt=True):
    def f(p):
        lis = "\n".join(
            f"        <li><b>{n}</b>{f'<i>{l}</i>' if l else ''}<span>{s}</span></li>" for n, l, s in items)
        figs = "\n".join(f"      <figure>{img(p, src, a, w, h)}<figcaption>{c}</figcaption></figure>" for src, a, w, h, c in photos)
        return f"""<!-- ON THE LOT -->
<section class="band{' band--alt' if alt else ''}">
  <div class="wrap">
    <div class="split split--top">
      <div>
        <h2>{h2}</h2>
        <div class="prose" style="margin-top: var(--space-6)"><p>{intro}</p></div>
      </div>
      <div>
        <ul class="plantlist">
{lis}
        </ul>
        <p class="note">{note}</p>
      </div>
    </div>
    <div class="lot-grid">
{figs}
    </div>
  </div>
</section>"""
    return f


def plan(h2, photo, steps, cta):
    def f(p):
        lis = "\n".join(
            f'        <li>{icon(i)}<span class="step-n" aria-hidden="true">{n}</span><h3>{t}</h3><p>{b}</p></li>'
            for n, (i, t, b) in enumerate(steps, 1))
        return f"""<!-- PLAN -->
<section class="band">
  <div class="wrap">
    <div class="plan">
      <h2>{h2}</h2>
      {img(p, *photo, cls="plan-photo")}
      <ol class="steps">
{lis}
      </ol>
      {cta_row(p, cta, "")}
    </div>
  </div>
</section>"""
    return f


def split_prose(comment, h2, paras, photo, alt, flip):
    def f(p):
        ps = "\n".join(f"        <p>{x}</p>" for x in paras)
        fig = f"""    <figure class="split-media">
      {img(p, *photo)}
    </figure>"""
        txt = f"""    <div>
      <h2>{h2}</h2>
      <div class="prose" style="margin-top: var(--space-6)">
{ps}
      </div>
    </div>"""
        inner = f"{fig}\n{txt}" if flip else f"{txt}\n{fig}"
        return f"""<!-- {comment} -->
<section class="band{' band--alt' if alt else ''}">
  <div class="wrap split{' split--flip' if flip else ''}">
{inner}
  </div>
</section>"""
    return f


VISIT = ("Visit the garden center", "~/contact/#directions")
GC = "garden-center/"

# ---------- pages ----------

PAGES = {}

PAGES["garden-center/plants-shrubs-trees"] = dict(
    prefix="../../", current=GC,
    title="Shrubs, Trees and Shade and Full Sun Plants in Arkansas | Amanda's Villa",
    description="Japanese maples, Italian cypress, shrubs, mums and seasonal color at Amanda's Villa in White Hall, with help choosing plants for shade or full sun.",
    hero=dict(
        img="garden-center/hero-shopper-walking-shrub-nursery-rows",
        alt="A shopper walking between rows of potted shrubs and trees in a plant nursery",
        h1="Shrubs, Trees and Plants That Grow Where They're <em>Planted</em>",
        sub="Japanese maples, Italian cypress, shrubs, mums and seasonal color, chosen for the light in each spot.",
        cta=VISIT,
        standin="The final hero shows a customer choosing shrubs on the lot, still to be shot."),
    sections=[
        guide(
            "A plant nursery where every sale starts with the spot",
            "Amanda designs and plants landscapes all over Arkansas, so the people on the lot know which plants live in shade, which need full sun, and which handle Arkansas clay. Before anything goes on the cart, someone asks where it's going.",
            ("plants-coleus-mums-amandas-villa.jpg", "Bright coleus, mums and ornamental grasses in a fall plant display at Amanda's Villa Garden Center", 1100, 1375),
            [("store", "Shrubs and trees from small starts to large specimen trees, sized by pot"),
             ("sun", "Plants for shade, part shade and full sun"),
             ("shovel", "Amanda's crew can plant what you buy"),
             ("truck", "Landscapers and contractors buy their plants here")]),
        lot(
            "Japanese maples, Italian cypress and seasonal color on the lot",
            "A few of the plants in the nursery yard this season. Stock changes with the season, so call ahead for something specific.",
            [("Japanese maple", "Acer palmatum", "Specimen trees for a front bed or a shady corner."),
             ("Italian cypress", "Cupressus sempervirens", "Tall, narrow evergreens for a formal line along a drive or a fence."),
             ("Coleus", "Plectranthus scutellarioides", "Bright leaves for shade and part shade."),
             ("Garden mums", "Chrysanthemum", "Potted fall mums in rows across the nursery yard."),
             ("Pansies and violas", "Viola", "Cool-season color for fall beds and planters."),
             ("Banana plants and elephant ears", "Musa, Colocasia", "Big tropical leaves for a bold summer bed.")],
            "Ask on the lot what's in for your light: shade, part shade or full sun.",
            [("home/garden-center-celosia-and-annuals.jpg", "Red celosia and bright annuals on the Amanda's Villa lot", 900, 1125, "Celosia and seasonal color"),
             ("success-pansies-amandas-villa.jpg", "Tables of pansies and violas for fall planting at Amanda's Villa Garden Center", 1100, 1375, "Pansies and violas"),
             ("lot-banana-plants-and-elephant-ears-under-pergola-amandas-villa.jpg", "Banana plants and elephant ears under the pergola at Amanda's Villa", 1065, 1420, "Banana plants and elephant ears")]),
        lambda p: reviews_section("What customers say about the plants"),
        plan(
            "How to bring home shrubs and trees that will grow",
            ("plan-fall-planters-amandas-villa.jpg", "Potted lantana, pansies, ornamental kale and peppers ready to take home at Amanda's Villa Garden Center", 1500, 643),
            [("store", "Come visit", "Stop by the lot at 7901 Dollarway Road in White Hall. Someone will greet you on the way in."),
             ("sun", "Describe the spot", "Say how much sun it has, or show a photo, and someone will lay out a few plants that will live there."),
             ("shovel", "Plant it, or have it planted", "Take your plants home, or have Amanda's crew plant them for you.")],
            VISIT),
        split_prose(
            "SUCCESS AND FAILURE",
            "A yard that fills in a little more every year",
            ["Picture a Japanese maple turning red by the front walk, a row of cypress along the drive, and beds that are still green in August. Every plant was chosen for the light it has, so the yard keeps growing.",
             "Without that match, too many yards stay stuck: bare beds, a dead shrub pulled every spring, and money spent on plants that never had a chance."],
            ("landscaping/after-ranch-maple.jpg", "A Japanese maple in a new mulched bed in front of a ranch house, planted by Amanda's Villa", 1100, 825),
            alt=True, flip=False),
        split_prose(
            "EXPLANATORY PARAGRAPH",
            "Shade plants, full sun plants, shrubs and trees for Arkansas yards",
            ["Many Arkansas homeowners want a yard that looks full and healthy, but it's hard to know which shrubs and trees will live in each spot. Amanda's Villa runs a plant nursery on Dollarway Road in White Hall with shrubs, trees, shade plants and full sun plants, and every sale starts with a question about the light.",
             "Come by, describe the spot, and leave with plants chosen to grow there. Amanda's crew can plant them, too."],
            ("landscaping/gallery-01.jpg", "A round bed of bright annuals around a shade tree, planted by Amanda's Villa", 821, 1026),
            alt=False, flip=True),
    ],
    faq_heading="Questions about plants, shrubs and trees",
    faqs=[
        ("Can you help me choose plants for shade?", "Yes. Say how many hours of sun the spot has, or bring a photo, and someone on the lot will lay out plants for shade, part shade or full sun."),
        ("How big are the trees?", "Shrubs and trees run from small starts to large specimen trees, sized by pot."),
        ("Can Amanda's crew plant what I buy?", "Yes. Buy the plants and take them home, or have Amanda's crew plant them for you."),
        ("My plant is dying. Can you help?", "Usually. Bring a photo, or the plant. The staff will ask about sun, watering, ants and whether water is standing in the hole, which covers many of the usual causes."),
        ("Can you order a plant you don't have?", "Usually. If it isn't on the lot, Amanda will try to find it."),
        ("What are your hours?", '<span class="todo">Hours.</span> The garden center is at 7901 Dollarway Road, White Hall.'),
    ],
    faq_img=("landscaping/service-flower-bed-design.jpg", "A planted bed of shrubs and annuals along a brick house, designed by Amanda's Villa", 900, 1125),
    closing=dict(img="hero-storefront-amandas-villa.jpg", h2="Describe the spot. Leave with plants that will grow there.", cta=VISIT),
)

PAGES["garden-center/landscaping-stone"] = dict(
    prefix="../../", current=GC,
    title="Landscaping Rocks, River Rock, Flagstone and Boulders in Arkansas | Amanda's Villa",
    description="River rock, fieldstone, flagstone, boulders, granite and Ozark Mountain rock by the piece or by the pile at Amanda's Villa in White Hall.",
    hero=dict(
        img="garden-center/hero-couple-crossing-natural-stone-steps",
        alt="A couple holding hands while stepping across natural stone steps in a garden",
        h1="Landscaping Rocks, River Rock and Boulders for Arkansas <em>Yards</em>",
        sub="River rock, fieldstone, flagstone, boulders, granite and Ozark Mountain rock, by the piece or by the pile.",
        cta=VISIT,
        standin="The final hero shows a customer choosing stone on the lot, still to be shot."),
    sections=[
        guide(
            "A stone yard run by people who build with stone",
            "Amanda's Villa sells natural stone to homeowners and contractors, and its hardscape teams build patios, walkways and retaining walls from it. So the help on the lot comes from people who know how each stone sets, stacks and drains.",
            ("hardscape/service-retaining-wall.jpg", "A dark block retaining wall and planted bed built by an Amanda's Villa hardscape team", 900, 1125),
            [("store", "Stone by the piece or by the pile"),
             ("hand-heart", "If the lot doesn't have the stone a project calls for, Amanda will try to track it down"),
             ("hammer", "The hardscape teams build patios, walkways and walls from it"),
             ("truck", "Landscapers and contractors load it for their jobs")]),
        lot(
            "River rock, fieldstone, flagstone and landscape boulders",
            "Homeowners take stone home for a border or a path, and contractors load it for jobs. What's on the lot changes, so call ahead for a large order.",
            [("River rock", "", "Smooth, rounded stone for beds, borders and around plantings."),
             ("Fieldstone", "", "Rough, flat-sided pieces for borders and low stacked edges."),
             ("Flagstone", "", "Flat slabs for stepping stones, paths and patios."),
             ("Landscape boulders", "", "Large accent stones for a bed, a corner or a hillside."),
             ("Granite and Ozark Mountain rock", "", "Arkansas stone for borders, accents and walls."),
             ("Pavers", "", "For a patio or a walkway, or ask the hardscape teams to lay them.")],
            "Not sure how much stone a bed or path takes? Bring the measurements and ask on the lot.",
            [("stone-river-rock-amandas-villa.jpg", "Close-up of smooth gray river rock sold for landscaping at Amanda's Villa", 1000, 1000, "River rock"),
             ("landscaping/after-flagstone-walk.jpg", "A flagstone walk curving past a new planted bed, laid by Amanda's Villa", 1080, 810, "Flagstone"),
             ("landscaping/after-porch-boulder.jpg", "A landscape boulder set in a new bed beside a front porch, by Amanda's Villa", 1100, 825, "Landscape boulders")]),
        split_prose(
            "WHAT IT BECOMES",
            "From the stone yard to a finished hillside",
            ['The same stone on the lot goes into the jobs the hardscape teams build: boulder steps, curved retaining walls and paver patios. For a project bigger than a weekend, the <a class="link" href="../../hardscape/">hardscape page</a> shows the work and how to ask for a free estimate.'],
            ("about/colton-boulder-steps-river-rock.jpg", "Boulder steps with river rock beds built by the Amanda's Villa hardscape team", 900, 900),
            alt=False, flip=True),
        lambda p: reviews_section("What customers say about Amanda's Villa"),
        plan(
            "How to bring home the right stone",
            ("stone-fieldstone-amandas-villa.jpg", "Rough gray fieldstone pieces stacked for landscaping at Amanda's Villa", 1000, 1000),
            [("store", "Come see the stone", "Stop by 7901 Dollarway Road in White Hall and walk the stone yard."),
             ("clipboard", "Pick it out", "Choose by the piece or by the pile. Bring the size of the bed or path and someone will help you work out how much."),
             ("hammer", "Set it, or have it built", "Take it home for a weekend project, or have the hardscape teams build with it.")],
            VISIT),
        split_prose(
            "SUCCESS AND FAILURE",
            "Beds with clean edges and paths that stay dry",
            ["Picture river rock along the foundation, flagstone stepping stones to the back gate and a boulder anchoring the corner bed. After the next storm, everything is still where it was.",
             "Without stone, too many yards go through the same cycle every spring: washed-out beds, muddy paths and another weekend spent putting the dirt back."],
            ("hardscape/gallery-07.jpg", "A curved paver walkway with a river rock bed beside it, built by an Amanda's Villa hardscape team", 900, 1125),
            alt=True, flip=False),
        split_prose(
            "EXPLANATORY PARAGRAPH",
            "Landscape rock, river rock and flagstone in one stone yard",
            ["Many Arkansas homeowners want beds and paths that hold up to clay soil and hard rain, but finding the right landscaping rocks in one place is hard. Amanda's Villa sells river rock, fieldstone, flagstone, landscape boulders, granite and Ozark Mountain rock on Dollarway Road in White Hall, by the piece or by the pile.",
             "Pick out the stone, take it home or have the hardscape teams build with it, and enjoy a yard that stays put."],
            ("about/colton-curved-wall-paver-patio.jpg", "A curved natural stone wall around a paver patio, built by an Amanda's Villa hardscape team", 900, 900),
            alt=False, flip=True),
    ],
    faq_heading="Questions about landscaping stone",
    faqs=[
        ("Can I buy just a few pieces?", "Yes. Stone sells by the piece or by the pile."),
        ("Can you find a stone you don't have?", "Usually. If the lot doesn't have the stone a project calls for, Amanda will try to track it down."),
        ("Do you sell stone to contractors?", "Yes. Landscapers and contractors load stone here for their jobs."),
        ("Can your crew build with the stone?", 'Yes. The hardscape teams build patios, walkways and retaining walls, and the estimate is free. See the <a class="link" href="../../hardscape/">hardscape page</a>.'),
        ("What are your hours?", '<span class="todo">Hours.</span> The stone yard is at 7901 Dollarway Road, White Hall.'),
    ],
    faq_img=("hardscape/area-farmhouse-walls-and-steps.jpg", "Block walls, steps and a boulder accent in front of a farmhouse, built by an Amanda's Villa hardscape team", 1200, 900),
    closing=dict(img="hero-storefront-amandas-villa.jpg", h2="Pick out the stone. Build a yard that stays put.", cta=VISIT),
)

PAGES["garden-center/pottery-decor"] = dict(
    prefix="../../", current=GC,
    title="Flower Pots, Talavera Pottery, Statues and Garden Decor in Arkansas | Amanda's Villa",
    description="About two hundred flower pots at a time, plus concrete planters, bird baths, fountains, garden statues and seasonal decor at Amanda's Villa in White Hall.",
    hero=dict(
        img="garden-center/hero-woman-holding-terracotta-pot",
        alt="A smiling woman holding a plant in a terracotta pot",
        h1="Flower Pots, Planters and Garden <em>Decor</em>",
        sub="Clay, ceramic, glazed, Talavera and aluminum pots, from a three-inch windowsill pot to one big enough for a hotel lobby.",
        cta=VISIT,
        standin="The final hero shows a customer choosing a pot on the lot, still to be shot."),
    sections=[
        guide(
            "Around two hundred pots on the lot at any time",
            "Amanda's Villa keeps a full pottery yard beside the plants, so a pot and the plant for it can be chosen together. The people on the lot will help match the size, the color and the light.",
            ("garden-center/talavera-and-ceramic-pottery-aisle-amandas-villa.jpg", "An aisle of Talavera and ceramic pottery lined with blooming annuals at Amanda's Villa Garden Center", 1100, 825),
            [("store", "Clay, ceramic, glazed, Talavera and aluminum pots"),
             ("leaf", "Plants for the pot are a few steps away"),
             ("star", "Concrete planters, bird baths, fountains and garden statues"),
             ("hand-heart", "Help matching a pot to the plant, the porch and the light")]),
        lot(
            "Talavera pottery, large outdoor planters and garden statues",
            "A few of the things in the pottery yard. Decor changes with the season, so the lot looks different every visit.",
            [("Clay and glazed ceramic pots", "", "From a three-inch pot for a windowsill up to large outdoor planters."),
             ("Talavera pottery", "", "Hand-painted pots and pieces in bright colors."),
             ("Aluminum planters", "", "Light, weatherproof planters for a porch or patio."),
             ("Concrete urns and planters", "", "Heavy, classic planters for an entry or a garden bed."),
             ("Bird baths and fountains", "", "A focal point for a bed, and a stop for the birds."),
             ("Garden statues and yard art", "", "Statues, metal frogs and butterflies, hummingbird feeders, Razorback signs and seasonal decor.")],
            "Call ahead if you need a particular size or a matching pair.",
            [("pottery-talavera-pumpkin-amandas-villa.jpg", "A hand-painted Talavera ceramic pumpkin among fall decor at Amanda's Villa Garden Center", 1100, 1375, "Talavera pottery"),
             ("garden-center/concrete-garden-statue-amandas-villa.jpg", "A concrete garden statue among pansies and pumpkins at Amanda's Villa Garden Center", 1031, 1375, "Garden statues"),
             ("pottery-frogs-planters-amandas-villa.jpg", "Painted metal frog garden ornaments beside purple and blue ceramic planters at Amanda's Villa Garden Center", 1100, 1375, "Yard art and planters")]),
        lambda p: reviews_section("What customers say about Amanda's Villa"),
        plan(
            "How to dress up the porch in one trip",
            ("plan-fall-planters-amandas-villa.jpg", "Potted lantana, pansies, ornamental kale and peppers ready to take home at Amanda's Villa Garden Center", 1500, 643),
            [("store", "Come visit", "Stop by the lot at 7901 Dollarway Road in White Hall. Bring a photo of the porch or patio."),
             ("leaf", "Pick a pot and a plant", "Choose them together, so the size, color and light all match."),
             ("house", "Set it out", "Put it by the door and enjoy a porch that looks lived in.")],
            VISIT),
        split_prose(
            "SUCCESS AND FAILURE",
            "A front porch that welcomes people home",
            ["Picture a pair of glazed pots by the front door, a bird bath in the bed and a Talavera piece on the patio table. Guests notice, and coming home feels better.",
             "Without it, too many porches stay bare, with a nursery pot or two that never made it into anything nicer."],
            ("landscaping/faq-stone-house-fern-urn.jpg", "A Boston fern in a tall black urn beside a front door, planted by Amanda's Villa", 900, 1200),
            alt=True, flip=False),
        split_prose(
            "EXPLANATORY PARAGRAPH",
            "Flower pots, bird baths and garden decor for Arkansas homes",
            ["Many Arkansas homeowners want a porch and patio that feel finished, but finding the right flower pots and garden decor in one place is hard. Amanda's Villa keeps about two hundred pots on Dollarway Road in White Hall, with Talavera pottery, large outdoor planters, bird baths, fountains and garden statues beside them.",
             "Pick a pot and a plant together, set them out, and enjoy a home that welcomes people at the door."],
            ("landscaping/after-fountain-bed.jpg", "A tiered fountain in a new bed by a front entry, planted by Amanda's Villa", 1100, 825),
            alt=False, flip=True),
    ],
    faq_heading="Questions about pottery and garden decor",
    faqs=[
        ("How big are the pots?", "They run from a three-inch pot for a windowsill to one big enough for a hotel lobby."),
        ("How many pots do you carry?", "Around two hundred are on the lot at any time."),
        ("Do you sell bird baths and fountains?", "Yes, along with concrete planters, garden statues, hummingbird feeders and seasonal decor."),
        ("Can you help me pick a plant for the pot?", "Yes. Say where the pot is going, and someone on the lot will suggest plants for that light."),
        ("What are your hours?", '<span class="todo">Hours.</span> The garden center is at 7901 Dollarway Road, White Hall.'),
    ],
    faq_img=("landscaping/service-flower-bed-edging.jpg", "A bird bath in an edged flower bed, planted by Amanda's Villa", 807, 1008),
    closing=dict(img="hero-storefront-amandas-villa.jpg", h2="Pick the pot and the plant together.", cta=VISIT),
)

PAGES["garden-center/produce"] = dict(
    prefix="../../", current=GC,
    title="Arkansas Produce Stand: Tomatoes, Local Honey and Amish Jams | Amanda's Villa",
    description="Farm-raised Arkansas tomatoes and seasonal produce, local honey, and jams, jellies and chow-chow from an Amish family, at Amanda's Villa in White Hall.",
    hero=dict(
        img="garden-center/hero-woman-holding-fresh-tomatoes",
        alt="A woman holding fresh red tomatoes at a produce stand",
        h1="Arkansas Produce, Local Honey and Amish <em>Preserves</em>",
        sub="Farm-raised tomatoes and seasonal produce from Arkansas farms, with local honey and jams, jellies and chow-chow made without preservatives.",
        cta=("Visit the produce stand", "~/contact/#directions"),
        standin="The final hero shows a customer at the Amanda's Villa produce stand, still to be shot."),
    sections=[
        guide(
            "A produce stand stocked from Arkansas farms first",
            "The produce at Amanda's Villa is farm-raised and grown in the ground, from Arkansas farms as long as the season allows and out of state only when it has to be. Cut one of these tomatoes open and it's red all the way through.",
            ("produce-tomatoes-amandas-villa.jpg", "Baskets of fresh red tomatoes on a wooden table at the Amanda's Villa produce stand", 1400, 1050),
            [("sprout", "Farm-raised and grown in the ground"),
             ("heart", "Jams, jellies, chow-chow and desserts from Ozark Mountain, an Amish family that uses no preservatives"),
             ("store", "Honey from an Arkansas beekeeper and salsa made by a local cook"),
             ("hand-heart", "Every purchase keeps money in Arkansas")]),
        lot(
            "Fresh tomatoes, seasonal produce and Amish jams",
            "What's on the stand changes with the season. In early fall it held all of this at once.",
            [("Tomatoes", "", "Farm-raised and red all the way through, sold by the basket."),
             ("Watermelons", "", "On the produce table while the season lasts."),
             ("Onions and pickling cucumbers", "", "Yellow onions by the pile and pickling cucumbers kept cold."),
             ("Pumpkins and winter squash", "", "Heirloom pumpkins, blue Hubbard, butternut and gourds every fall."),
             ("Local honey", "", "Jars from an Arkansas beekeeper."),
             ("Jams, jellies and chow-chow", "", "From Ozark Mountain, an Amish family in north-central Arkansas, made with no preservatives.")],
            "Call ahead to ask what came in this week.",
            [("garden-center/jams-jellies-and-preserves-shelves-amandas-villa.jpg", "Shelves of jams, jellies and preserves at the Amanda's Villa produce stand", 1100, 825, "Jams, jellies and chow-chow"),
             ("produce-honey-amandas-villa.jpg", "Jars of local honey at the Amanda's Villa produce stand", 1100, 825, "Local honey"),
             ("garden-center/yellow-onions-amandas-villa.jpg", "A pile of yellow onions for sale at the Amanda's Villa produce stand", 1031, 1375, "Yellow onions")]),
        plan(
            "How to stock the kitchen with Arkansas food",
            ("garden-center/fresh-tomatoes-by-the-basket-amandas-villa.jpg", "Baskets of fresh red tomatoes on a wooden table at the Amanda's Villa produce stand", 1100, 825),
            [("store", "Stop by the stand", "Come to 7901 Dollarway Road in White Hall. The produce stand sits beside the garden center."),
             ("leaf", "Pick what's in season", "Tomatoes, melons, squash or whatever came in this week, plus honey and preserves."),
             ("house", "Bring it home to the table", "Cook something that tastes like Arkansas.")],
            ("Visit the produce stand", "~/contact/#directions")),
        split_prose(
            "SUCCESS AND FAILURE",
            "Tomatoes that taste like a summer garden",
            ["Picture a tomato sandwich with slices that are red all the way through, chow-chow on the beans and honey on a warm biscuit. Every jar and basket came from Arkansas hands.",
             "Without a stand like this, too many kitchens settle for produce picked early and shipped a long way."],
            ("guide-cash-register-amandas-villa.jpg", "An antique brass cash register at the Amanda's Villa produce stand", 1100, 1375),
            alt=True, flip=False),
        split_prose(
            "EXPLANATORY PARAGRAPH",
            "A farm stand with Arkansas produce, local honey and chow-chow",
            ["Many Arkansas families want produce that tastes fresh, but too much of what's in the grocery store was picked early and shipped in. Amanda's Villa runs a produce stand on Dollarway Road in White Hall with farm-raised Arkansas tomatoes and seasonal produce, local honey, and Amish jams, jellies and chow-chow.",
             "Stop by, pick what's in season, and bring home food that keeps money in Arkansas."],
            ("produce-preserves-amandas-villa.jpg", "Jars of preserves above fresh tomatoes at the Amanda's Villa produce stand", 1100, 825),
            alt=False, flip=True),
    ],
    faq_heading="Questions about the produce stand",
    faqs=[
        ("Is the produce local?", "As local as the season allows. It's farm-raised, grown in the ground, from Arkansas farms first and out of state only when it has to be."),
        ("What's in season right now?", "It changes every few weeks. In early fall the stand had tomatoes, watermelons, onions, pickling cucumbers, pumpkins and winter squash. Call to ask what came in this week."),
        ("Who makes the jams and chow-chow?", "Ozark Mountain, an Amish family in north-central Arkansas that uses no preservatives."),
        ("Do you sell local honey?", "Yes. The honey comes from an Arkansas beekeeper."),
        ("What are your hours?", '<span class="todo">Hours.</span> The produce stand is at 7901 Dollarway Road, White Hall.'),
    ],
    faq_img=("fall-heirloom-pumpkins-amandas-villa.jpg", "Heirloom pumpkins and gourds on straw at Amanda's Villa", 1100, 1375),
    closing=dict(img="hero-storefront-amandas-villa.jpg", h2="Pick what's in season. Bring Arkansas home to the table.", cta=("Visit the produce stand", "~/contact/#directions")),
)


def contact_ways(p):
    return f"""<!-- WAYS TO REACH AMANDA'S VILLA -->
<section class="band">
  <div class="wrap">
    <div class="head">
      <h2>Call, come by, or ask for a visit</h2>
    </div>
    <div class="svc3">
      <div>{icon("phone")}<h3>Call</h3><p><a class="link" href="{TEL}">{PHONE}</a>. Ask about a landscaping design, a hardscape estimate, or whether something is on the lot.</p></div>
      <div>{icon("map-pin")}<h3>Visit the garden center</h3><p>7901 Dollarway Road, White Hall, AR 71602. Plants, pottery, stone, mulch and Arkansas produce.</p></div>
      <div>{icon("clipboard")}<h3>Ask for a visit to your yard</h3><p>Amanda measures and designs landscaping jobs herself, and the hardscape teams give free estimates, all over Arkansas.</p></div>
    </div>
    {cta_row(p, ("Call " + PHONE, TEL)).replace(f'<a class="btn btn--secondary" href="{TEL}">Call {PHONE}</a>', f'<a class="btn btn--secondary" href="#directions">Directions</a>')}
  </div>
</section>"""


def contact_directions(p):
    return f"""<!-- DIRECTIONS -->
<section class="band band--alt" id="directions">
  <div class="wrap split split--flip">
    <figure class="split-media">
      {img(p, "contact/roadside-sign-with-butterflies-amandas-villa.jpg", "The Amanda's Villa Landscaping and Garden Center roadside sign with metal butterfly ornaments", 1100, 825)}
    </figure>
    <div>
      <h2>Find the garden center on Dollarway Road</h2>
      <div class="prose" style="margin-top: var(--space-6)">
        <p>Amanda's Villa Landscaping and Garden Center<br>7901 Dollarway Road<br>White Hall, AR 71602</p>
        <p>Look for the Amanda's Villa sign out front.</p>
        <p><span class="todo">Hours</span></p>
      </div>
    </div>
  </div>
</section>"""


PAGES["contact"] = dict(
    prefix="../", current=None,
    title="Contact Amanda's Villa Landscaping and Garden Center | White Hall, Arkansas",
    description="Call (870) 489-5463 or visit 7901 Dollarway Road in White Hall for landscaping design, a free hardscape estimate, or the garden center.",
    hero=dict(
        img="contact/hero-garden-center-staff-helping-customer",
        alt="A garden center worker in an apron talking with a customer among plants in a greenhouse",
        h1="Call or Visit Amanda's <em>Villa</em>",
        sub="Landscaping design, free hardscape estimates and a full garden center at 7901 Dollarway Road in White Hall.",
        cta=("Directions", "#directions"),
        standin="The final hero shows Amanda or the garden center staff with a customer, still to be shot."),
    sections=[
        contact_ways,
        contact_directions,
        plan(
            "What to have ready when you call",
            ("hero-pergola-wide-amandas-villa.jpg", "Banana plants and elephant ears under the pergola at Amanda's Villa Garden Center", 1065, 666),
            [("camera", "For landscaping", "A phone photo of the space, and a picture of a yard you love if you have one. Amanda will come measure."),
             ("hammer", "For a patio, wall or drain", "Just the yard. The hardscape team surveys it with a transit and gives the estimate free."),
             ("leaf", "For the garden center", "A photo of the spot, or the plant itself if it's struggling.")],
            ("Directions", "#directions")),
    ],
    faq_heading="Questions people ask before they call",
    faqs=[
        ("Is the hardscape estimate free?", "Yes. The hardscape team comes out, surveys the yard with a transit and gives an estimate at no charge."),
        ("Does Amanda come out herself?", "Yes. She measures and designs every landscaping job personally."),
        ("How far do you travel?", "Landscaping and hardscape jobs are all over the state of Arkansas."),
        ("Do I need an appointment for the garden center?", "No. Come by the lot at 7901 Dollarway Road in White Hall, and someone will greet you on the way in."),
        ("What are your hours?", '<span class="todo">Hours.</span>'),
    ],
    faq_img=("home/garden-center-celosia-and-annuals.jpg", "Red celosia and bright annuals on the Amanda's Villa lot", 900, 1125),
    closing=dict(img="hero-storefront-amandas-villa.jpg", h2="Together, plant the space your yard deserves.", cta=("Directions", "#directions")),
)


if __name__ == "__main__":
    for path, d in PAGES.items():
        out = os.path.join(ROOT, path, "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(page(d))
        print("wrote", path)
