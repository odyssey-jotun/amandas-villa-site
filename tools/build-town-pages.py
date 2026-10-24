#!/usr/bin/env python3
"""Build the town pages under /projects/<town>/: one page per town where Amanda's Villa has finished work.

Run from the repo root:  python3 tools/build-town-pages.py

Each page reuses the French drain page's styles, scripts and footer, so a style change
there carries over the next time this runs. Menu and footer come from tools/site_nav.py.
Town pages stay out of the menu (Amanda's no-towns rule covers the main landing pages).

Every job on a town page is a real Amanda's Villa job Colton placed in that town
(see /job-photos/). Write only what the photos, Colton's October 5 interview and
cited public sources support. Photos live in img/projects/<town>/.
"""
import html
import importlib.util
import json
import os
import re

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE = open(os.path.join(ROOT, "hardscape", "french-drains", "index.html"), encoding="utf-8").read()
BUILD_PAGES = open(os.path.join(ROOT, "tools", "build-pages.py"), encoding="utf-8").read()

spec = importlib.util.spec_from_file_location("site_nav", os.path.join(ROOT, "tools", "site_nav.py"))
site_nav = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site_nav)

PHONE = "(870) 489-5463"
TEL = "tel:+18704895463"
P = "../../"  # every town page sits two folders deep

ICONS = ["i-cloud-rain", "i-frown", "i-house", "i-layers", "i-sprout", "i-clipboard-list", "i-ruler", "i-hammer",
         "i-footprints", "i-brick-wall", "i-flower"]


def sprite():
    out = []
    for name in ICONS:
        m = re.search(r'<symbol id="%s".*?</symbol>' % name, TEMPLATE, re.S) or \
            re.search(r'<symbol id="%s".*?</symbol>' % name, BUILD_PAGES, re.S)
        out.append(m.group(0))
    return '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">\n' + "\n".join(out) + "\n</svg>"


def head_styles():
    """The French drain page's <head> from the favicon through its last style block, minus its JSON-LD and menu CSS."""
    s = TEMPLATE[TEMPLATE.index('<link rel="icon"'):TEMPLATE.index("</head>")]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', "", s, flags=re.S)
    s = re.sub(r'\n?<style id="site-nav">.*?</style>', "", s, flags=re.S)
    return s.rstrip()


def tail():
    """Scripts and footer after </main> (the carousel script exits on pages without a carousel)."""
    return TEMPLATE[TEMPLATE.index("</main>"):]


TOWN_CSS = """<style id="town-page">
/* ---------- Town pages: one block per job, three photos each ---------- */
.jobs { display: grid; gap: var(--space-16); }
.job { padding-top: var(--space-10); border-top: 1px solid var(--line); }
.job:first-child { padding-top: 0; border-top: 0; }
.job h3 { font-size: 28px; line-height: 1.2; }
.job-text { max-width: var(--measure-text); margin-top: var(--space-2); }
.job-text .link { display: inline-block; margin-top: var(--space-4); }
.job-photos { list-style: none; margin: var(--space-6) 0 0; padding: 0; display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-4); }
.job-photos figure { margin: 0; }
.job-photos img { width: 100%; aspect-ratio: 1 / 1; object-fit: cover; border-radius: var(--radius-photo); background: var(--linen-2); }
.job-photos figcaption { margin-top: var(--space-2); font-size: 15px; line-height: 1.4; color: var(--ink-3); text-align: center; }
.svc3 h3 a { color: inherit; text-decoration: none; border-bottom: 1px solid var(--line-strong); }
.svc3 h3 a:hover { border-bottom-color: var(--clay); }
.svc3--six { row-gap: var(--space-16); }
.area .prose { margin: 0 auto; }
.area .head { text-align: center; margin-bottom: var(--space-6); }
.faq--solo { max-width: 860px; }
.job-photos .pf-open { display: block; width: 100%; padding: 0; border: 0; background: none; cursor: zoom-in; border-radius: var(--radius-photo); overflow: hidden; }
.job-photos .pf-open img { transition: transform .25s ease; }
.job-photos .pf-open:hover img { transform: scale(1.02); }
.hero-meta a.pf-open { display: inline; width: auto; color: inherit; text-decoration: underline; text-underline-offset: 4px; cursor: pointer; }
.pf-row { justify-content: center; margin-top: var(--space-16); }
.pf { width: min(1100px, 100vw - 32px); max-height: calc(100vh - 32px); padding: 0; border: 0; border-radius: var(--radius-photo); background: var(--ink); color: var(--on-forest); }
.pf::backdrop { background: rgba(20, 26, 22, .85); }
.pf-box { display: grid; grid-template-rows: minmax(0, 1fr) auto; max-height: calc(100vh - 32px); }
.pf-img { width: 100%; height: 100%; max-height: calc(100vh - 170px); object-fit: contain; background: #111; }
.pf-bar { display: flex; align-items: center; gap: var(--space-4); padding: var(--space-4); }
.pf-text { flex: 1; min-width: 0; }
.pf-job { font: 400 20px/1.3 var(--font-text-serif); }
.pf-cap { font-size: 16px; line-height: 1.4; }
.pf-count { font-size: 14px; opacity: .75; }
.pf-text p + p { margin-top: 2px; }
.pf-btn { flex: none; width: 48px; height: 48px; border-radius: 50%; border: 1px solid rgba(246, 245, 240, .5); background: transparent; color: var(--on-forest); font: 400 24px/1 var(--font-body); cursor: pointer; }
.pf-btn:hover { background: rgba(246, 245, 240, .14); }
@media (prefers-reduced-motion: reduce) { .job-photos .pf-open img { transition: none; } }
@media (max-width: 640px) {
  .pf { width: 100vw; max-width: 100vw; height: 100dvh; max-height: 100dvh; margin: 0; border-radius: 0; }
  .pf-box { height: 100%; max-height: 100dvh; }
  .pf-img { height: 100%; max-height: none; min-height: 0; }
  .pf-bar { flex-wrap: wrap; }
  .pf-text { order: -1; flex-basis: 100%; }
  .job h3 { font-size: 24px; }
  .job-photos { grid-template-columns: 1fr 1fr; gap: var(--space-2) var(--space-4); }
  .job-photos li:last-child { grid-column: 1 / -1; order: -1; }
  .job-photos li:last-child img { aspect-ratio: 4 / 3; }
  .job-photos figcaption { font-size: 14px; }
}
</style>"""


def e(t):
    return html.escape(t, quote=True)


def fn(n, suffix=""):
    return (f"<sup class='fn'><a href='#cite-{n}' id='ref-{n}{suffix}' aria-label='Citation {n}'>{n}</a></sup>")


def ctas(extra_class=""):
    return (f'<div class="btn-row{extra_class}">\n      <a class="btn btn--primary" href="{P}contact/#estimate">Request a free estimate</a>\n'
            f'      <a class="btn btn--secondary" href="{TEL}">Call {PHONE}</a>\n    </div>')


def img(town, name, w, h, alt, lazy=True):
    return (f'<img width="{w}" height="{h}" src="{P}img/projects/{town}/{name}.jpg" alt="{e(alt)}"'
            + (' loading="lazy"' if lazy else "") + ">")


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def page(t):
    slug, town = t["slug"], t["town"]
    jobs = []
    for j in t["jobs"]:
        photos = "\n".join(
            f'        <li><figure><button type="button" class="pf-open" data-pf="{pf}" aria-label="Open the {e(town)} portfolio at this photo">{img(slug, n, w, h, alt)}</button><figcaption>{e(cap)}</figcaption></figure></li>'
            for n, w, h, alt, cap, pf in j["photos"])
        more = f'\n        <a class="link" href="{P}{j["link"][0]}">{e(j["link"][1])}</a>' if j.get("link") else ""
        jobs.append(f"""    <article class="job">
      <h3>{e(j["title"])}</h3>
      <div class="job-text">
        <p>{j["text"]}</p>{more}
      </div>
      <ul class="job-photos">
{photos}
      </ul>
    </article>""")

    svc = "\n".join(f'      <div><span class="ic-badge"><svg class="ic" aria-hidden="true"><use href="#{ic}"/></svg></span>'
                    f'<h3><a href="{P}{href}">{e(title)}</a></h3><p>{text}</p></div>'
                    for ic, title, href, text in t["services"])
    value3 = "\n".join(f'      <div><span class="ic-badge"><svg class="ic" aria-hidden="true"><use href="#{ic}"/></svg></span><h3>{e(h)}</h3><p>{p}</p></div>'
                       for ic, h, p in t["value"]["points"])
    prob3 = "\n".join(f'      <div><span class="ic-badge"><svg class="ic" aria-hidden="true"><use href="#{ic}"/></svg></span><h3>{e(h)}</h3><p>{p}</p></div>'
                      for ic, h, p in t["problem"]["points"])
    steps = "\n".join(f'        <li><span class="ic-badge"><svg class="ic" aria-hidden="true"><use href="#{ic}"/></svg></span><span class="step-n" aria-hidden="true">{i}</span><h3>{e(h)}</h3><p>{p}</p></li>'
                      for i, (ic, h, p) in enumerate(t["plan"]["steps"], 1))
    faq = "\n".join(f"      <details><summary>{e(q)}</summary><div><p>{a}</p></div></details>" for q, a in t["faq"])
    cites = "\n".join(f'          <li id="cite-{i}">{c}</li>' for i, c in enumerate(t["cites"], 1))
    guide_p = "\n".join(f"        <p>{p}</p>" for p in t["guide"]["paras"])
    area_p = "\n".join(f"        <p>{p}</p>" for p in t["area"]["paras"])

    ld_service = {
        "@context": "https://schema.org", "@type": "Service",
        "name": f"Landscaping and hardscaping in {town}, Arkansas",
        "serviceType": ["Landscaping", "Hardscaping", "French drain installation"],
        "areaServed": {"@type": "City", "name": town, "containedInPlace": {"@type": "State", "name": "Arkansas"}},
        "provider": {
            "@type": "HomeAndConstructionBusiness", "name": "Amanda's Villa Landscaping and Garden Center",
            "telephone": "+1-870-489-5463",
            "address": {"@type": "PostalAddress", "streetAddress": "7901 Dollarway Road", "addressLocality": "White Hall",
                        "addressRegion": "AR", "postalCode": "71602", "addressCountry": "US"}},
    }
    ld_faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(re.sub(r"<sup.*?</sup>", "", a))}}
        for q, a in t["faq"]]}

    hero, value, prob, guide, closing = t["hero"], t["value"], t["problem"], t["guide"], t["closing"]
    pf_items = [{"src": f"{P}img/projects/{slug}/portfolio/{f}.jpg", "job": job, "cap": cap}
                for job, photos in t["portfolio"] for f, cap in photos]
    pf_label = f"Check out our {town} portfolio"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{e(t["title"])}</title>
<meta name="description" content="{e(t["description"])}">
{head_styles()}
<script type="application/ld+json">
{json.dumps(ld_service, indent=2)}
</script>
<script type="application/ld+json">
{json.dumps(ld_faq, indent=2)}
</script>
{TOWN_CSS}
</head>
<body>
{sprite()}

<header class="hero">
  <div class="hero-card">
    <picture>
      <source media="(max-width: 640px)" srcset="{P}img/projects/{slug}/{hero["tall"][0]}.jpg">
      <img width="1800" height="1125" src="{P}img/projects/{slug}/{hero["wide"][0]}.jpg" alt="{e(hero["wide"][1])}" fetchpriority="high">
    </picture>
    <nav class="nav" aria-label="Main"></nav>
    <div class="hero-copy">
      <h1>{hero["h1"]}</h1>
      <p class="hero-sub">{hero["sub"]}</p>
      <div class="hero-ctas">
        <a class="btn btn--onphoto" href="{P}contact/#estimate">Request a free estimate</a>
        <a class="btn btn--ghost" href="{TEL}">Call {PHONE}</a>
      </div>
      <p class="hero-meta"><a href="#projects" class="pf-open" data-pf="0">{e(pf_label)}</a> · Free estimates</p>
    </div>
  </div>
</header>

<main>

<!-- VALUE -->
<section class="band">
  <div class="wrap">
    <div class="split split--flip split--short">
    <figure class="split-media">
      {img(slug, value["photo"][0], 1200, 900, value["photo"][1])}
    </figure>
    <div>
      <h2>{value["h2"]}</h2>
      <div class="prose" style="margin-top: var(--space-6)">
        <p>{value["text"]}</p>
      </div>
    </div>
    </div>
    <div class="svc3">
{value3}
    </div>
  </div>
</section>

<!-- PROBLEM: one broad problem, then external, internal and philosophical -->
<section class="band band--alt">
  <div class="wrap">
    <div class="split split--short">
      <div class="split-text">
        <h2>{prob["h2"]}</h2>
        <p>{prob["lead"]}</p>
      </div>
      <figure class="split-media">
        {img(slug, prob["photo"][0], 1000, 1250, prob["photo"][1])}
      </figure>
    </div>
    <div class="svc3">
{prob3}
    </div>
    {ctas(" cta-row")}
  </div>
</section>

<!-- PROOF: every job Colton placed in this town -->
<section class="band" id="projects">
  <div class="wrap">
    <div class="head">
      <h2>{t["jobs_h2"]}</h2>
      <p>{t["jobs_intro"]}</p>
    </div>
    <div class="jobs">
{chr(10).join(jobs)}
    </div>
    <div class="btn-row cta-row pf-row">
      <button type="button" class="btn btn--primary pf-open" data-pf="0">{e(pf_label)}</button>
    </div>
  </div>
</section>

<!-- GUIDE -->
<section class="band band--alt">
  <div class="wrap split split--flip">
    <figure class="split-media">
      {img(slug, guide["photo"][0], 1000, 1250, guide["photo"][1])}
    </figure>
    <div>
      <h2>{guide["h2"]}</h2>
      <div class="prose" style="margin-top: var(--space-6)">
{guide_p}
      </div>
      <figure class="quote">
        <blockquote><p>"{guide["quote"]}"</p></blockquote>
        <figcaption>Colton, hardscape lead at Amanda's Villa</figcaption>
      </figure>
    </div>
  </div>
</section>

<!-- PLAN -->
<section class="band">
  <div class="wrap">
    <div class="plan">
      <h2>{t["plan"]["h2"]}</h2>
      <ol class="steps">
{steps}
      </ol>
      {ctas()}
    </div>
  </div>
</section>

<!-- SERVICES -->
<section class="band band--alt">
  <div class="wrap">
    <div class="head" style="text-align:center">
      <h2>{t["services_h2"]}</h2>
    </div>
    <div class="svc3 svc3--six" style="margin-top:0">
{svc}
    </div>
  </div>
</section>

<!-- EXPLANATORY PARAGRAPH -->
<section class="band area">
  <div class="wrap">
    <div class="head">
      <h2>{t["area"]["h2"]}</h2>
    </div>
    <div class="prose">
{area_p}
    </div>
  </div>
</section>

<!-- FAQ -->
<section class="band band--alt">
  <div class="wrap">
    <div class="head">
      <h2>{t["faq_h2"]}</h2>
    </div>
    <div class="faq faq--solo">
{faq}
    </div>
  </div>
</section>

<!-- CLOSING CTA -->
<section class="band closing closing--photo">
  {img(slug, closing["photo"], 1200, 900, "")}
  <div class="wrap">
    <h2>{closing["h2"]}</h2>
    <p>{closing["text"]}</p>
    {ctas()}
  </div>
</section>

<!-- CITATIONS: plain text, no links -->
<section class="cites">
  <div class="wrap">
    <details class="cites-box" id="citations">
      <summary>Citations</summary>
      <ol>
{cites}
      </ol>
    </details>
  </div>
</section>

<dialog class="pf" id="portfolio" aria-label="{e(town)} portfolio">
  <div class="pf-box">
    <img class="pf-img" alt="">
    <div class="pf-bar">
      <button type="button" class="pf-btn" data-step="-1" aria-label="Previous photo">&#8249;</button>
      <div class="pf-text"><p class="pf-job"></p><p class="pf-cap"></p><p class="pf-count"></p></div>
      <button type="button" class="pf-btn" data-step="1" aria-label="Next photo">&#8250;</button>
      <button type="button" class="pf-btn pf-close" aria-label="Close the portfolio">&#215;</button>
    </div>
  </div>
</dialog>
<script>
// {town} portfolio: every photo from every job in this town, opened by any .pf-open control
(function () {{
  var items = {json.dumps(pf_items)};
  var dlg = document.getElementById('portfolio'); if (!dlg || !dlg.showModal) return;
  var img = dlg.querySelector('.pf-img'), job = dlg.querySelector('.pf-job'), cap = dlg.querySelector('.pf-cap'), count = dlg.querySelector('.pf-count');
  var at = 0, opener = null;
  function show(i) {{
    at = (i + items.length) % items.length;
    var it = items[at];
    img.src = it.src; img.alt = it.job + ': ' + it.cap;
    job.textContent = it.job; cap.textContent = it.cap; count.textContent = 'Photo ' + (at + 1) + ' of ' + items.length;
    new Image().src = items[(at + 1) % items.length].src;
  }}
  document.querySelectorAll('.pf-open').forEach(function (b) {{
    b.addEventListener('click', function (e) {{ e.preventDefault(); opener = b; show(+b.dataset.pf || 0); dlg.showModal(); }});
  }});
  dlg.querySelectorAll('[data-step]').forEach(function (b) {{ b.addEventListener('click', function () {{ show(at + +b.dataset.step); }}); }});
  dlg.querySelector('.pf-close').addEventListener('click', function () {{ dlg.close(); }});
  dlg.addEventListener('click', function (e) {{ if (e.target === dlg) dlg.close(); }});
  dlg.addEventListener('close', function () {{ if (opener) opener.focus({{ preventScroll: true }}); }});
  document.addEventListener('keydown', function (e) {{ if (!dlg.open) return; if (e.key === 'ArrowRight') show(at + 1); if (e.key === 'ArrowLeft') show(at - 1); }});
  var x0 = null;
  img.addEventListener('touchstart', function (e) {{ x0 = e.touches[0].clientX; }}, {{ passive: true }});
  img.addEventListener('touchend', function (e) {{ if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null; if (Math.abs(dx) > 40) show(at + (dx < 0 ? 1 : -1)); }});
}})();
</script>

{tail()}"""


SC = "star-city"
STAR_CITY = {
    "slug": SC, "town": "Star City",
    "title": "Landscaping and Hardscaping in Star City, AR | Amanda's Villa",
    "description": "French drains, paver walks, flagstone paths and flower beds built by Amanda's Villa in Star City, Arkansas. Four local projects with photos. Free estimates.",
    "hero": {
        "h1": "Landscaping and Hardscaping in Star City, <em>Arkansas</em>",
        "sub": "French drains, paver walks, flagstone paths and flower beds, built and planted by Amanda's Villa for Star City homes.",
        "meta": "Four Star City projects on this page · Free estimates",
        "wide": ("hero-curved-paver-walk-picket-gate-wide", "A curved paver walk running through a white picket fence gate beside a Star City home, built by the Amanda's Villa hardscape team"),
        "tall": ("hero-curved-paver-walk-river-rock-tall",),
    },
    "value": {
        "h2": "Let's build you a Star City yard that stays dry and looks finished",
        "text": "Your project starts with a walk around your yard and a transit survey of how the ground falls, so the water, the stone and the plants each have a plan before any digging starts.",
        "photo": ("value-flower-border-brick-edging", "A border of red and purple annuals and yellow-green foliage along a brick edging at a Star City home"),
        "points": [
            ("i-layers", "A gravel base under every walk", "Your walk or patio sits on 8 to 10 inches of compacted gravel with a finer base on top, so the stone stays level through wet springs and dry summers."),
            ("i-cloud-rain", "Drainage goes in first", "Downspout lines and French drains go in before the stone and the plants, so roof water and runoff have somewhere to go."),
            ("i-sprout", "Plants from the garden center in White Hall", "Amanda chooses your shrubs and flowers from the Amanda's Villa lot, and her crew plants them."),
        ],
    },
    "problem": {
        "h2": "Star City yards hold on to the rain",
        "lead": f"Arkansas averages about 50 inches of rain a year.{fn(1)} In and around Star City, USDA soil maps show a seasonal water table within about two feet of the surface under roughly seven of every ten acres.{fn(2)} When the ground stays that wet:",
        "photo": ("problem-side-yard-dug-out-downspout-lines", "A side yard dug out along a brick house in Star City, with downspout drain pipe laid along the foundation"),
        "points": [
            ("i-cloud-rain", "Water stands where it lands", f"Low spots stay soggy for days, runoff collects along the foundation, and roots sitting in saturated soil run short of oxygen.{fn(3)}"),
            ("i-frown", "The yard turns into a chore", "Homeowners end up stepping around mud and putting off every plan they had for the space."),
            ("i-house", "A yard should be ready after a storm", "No family should have to wait days for the ground to dry before they can use their own yard."),
        ],
    },
    "jobs_h2": "Four Amanda's Villa projects in Star City",
    "jobs_intro": "Each of these was built by the Amanda's Villa hardscape teams or planted by Amanda's crew at a home in Star City.",
    "jobs": [
        {"title": "A French drain along the fence and the house",
         "text": "The team lifted the sod along the drain route, dug the trench, lined it with filter fabric and laid the pipe in gravel, with catch basins where the water collects. Then the sod went back down. From the first cut to the finished lawn, the job took four days.",
         "link": ("hardscape/french-drains/", "How a French drain is built, step by step"),
         "photos": [
             ("job-drain-1-sod-lifted", 900, 900, "Rolls of cut sod beside a curving strip of bare soil marking a French drain route across a Star City backyard", "Sod lifted along the route", 0),
             ("job-drain-2-pipe-in-fabric", 900, 900, "Blue drain pipe laid in a fabric-lined trench beside a brick house and air conditioning unit", "Pipe laid in filter fabric", 2),
             ("job-drain-3-finished-lawn", 900, 900, "A green backyard lawn along a wood privacy fence after the French drain was finished beneath it", "Lawn back in place", 5),
         ]},
        {"title": "A curved paver walk to the backyard gate",
         "text": "The strip of grass between the house and the picket fence became a curved paver walk with a two-color border and a river rock bed set into the bend. Downspout lines were run beneath the walk before the base went down.",
         "link": ("hardscape/", "Paver walkways, patios and retaining walls"),
         "photos": [
             ("job-walk-1-before", 900, 900, "Grass along a brick house and white picket fence before the paver walk", "Before", 7),
             ("job-walk-2-pavers-going-down", 900, 900, "Gray pavers being laid in a diagonal pattern with a dark border course along a side yard", "Pavers going down", 9),
             ("job-walk-3-finished", 900, 900, "A finished curved paver walk with a two-color border beside a brick house and a new bed", "Finished", 10),
         ]},
        {"title": "A flagstone front walk with a paver border",
         "text": "The front walk was dug out from the drive to the porch, filled with a gravel base, edged with pavers and finished with flagstone set in gravel.",
         "link": ("hardscape/", "Stone and paver walkways"),
         "photos": [
             ("job-flagstone-1-dug-out", 900, 900, "A curved front walk dug out across a lawn to the porch of a white brick house", "Dug out to the porch", 13),
             ("job-flagstone-2-gravel-and-border", 900, 900, "A curved walk filled with a gravel base and edged with a paver border", "Gravel base and paver border", 14),
             ("job-flagstone-3-finished", 640, 640, "A finished flagstone walk set in gravel with a dark paver border across a green lawn", "Finished", 15),
         ]},
        {"title": "Flower beds along a brick-edged drive",
         "text": "Amanda's crew planted new beds along the brick edging: rows of shrubs behind borders of seasonal flowers, a bed across the front of the sunroom and bright annuals beside the porch rail.",
         "link": ("landscaping/", "Landscape design and flower beds"),
         "photos": [
             ("job-beds-1-sunroom-bed", 900, 900, "A new bed of small shrubs and annuals across the front of a white arched sunroom on a brick house", "Bed in front of the sunroom", 16),
             ("job-beds-2-petunias-porch-rail", 900, 900, "Pink and red petunias and vinca in a brick-edged bed beside a white porch rail", "Annuals by the porch", 19),
             ("job-beds-3-shrubs-by-brick-pillar", 900, 900, "Rows of green and gold shrubs in a mulched bed beside a brick pillar wall", "Shrubs by the brick pillar", 18),
         ]},
    ],
    "portfolio": [
        ("French drain along the fence and the house", [
            ("drain-1-sod-lifted", "Sod lifted along the drain route"), ("drain-2-trench-dug", "Trench dug"),
            ("drain-3-pipe-in-fabric", "Pipe laid in a fabric-lined trench beside the house"), ("drain-4-gravel-and-catch-basin", "Gravel and a catch basin grate"),
            ("drain-5-sod-going-back", "Sod going back down along the fence"), ("drain-6-finished-along-fence", "Finished, lawn back along the fence"),
            ("drain-7-finished-beside-house", "Finished, lawn back beside the house")]),
        ("Curved paver walk to the backyard gate", [
            ("walk-1-before", "Before: grass between the house and the fence"), ("walk-2-dug-out-downspout-lines", "Walk dug out, downspout lines going in"),
            ("walk-3-pavers-going-down", "Pavers going down"), ("walk-4-finished-curve-to-gate", "Finished walk curving to the gate"),
            ("walk-5-finished-river-rock-bed", "Finished walk and the river rock bed"), ("walk-6-finished-through-gate", "Finished walk through the gate")]),
        ("Flagstone front walk with a paver border", [
            ("flagstone-1-dug-out", "Walk dug out to the porch"), ("flagstone-2-gravel-and-border", "Gravel base down, paver border set"),
            ("flagstone-3-finished", "Finished flagstone walk with the paver border")]),
        ("Flower beds along a brick-edged drive", [
            ("beds-1-sunroom-bed", "Bed across the front of the sunroom"), ("beds-2-flower-border-drive", "Flower border along the drive"),
            ("beds-3-shrubs-by-brick-pillar", "Shrubs beside the brick pillar"), ("beds-4-annuals-by-porch", "Annuals beside the porch rail")]),
    ],
    "guide": {
        "h2": "Amanda and the hardscape teams, from White Hall to Star City",
        "paras": [
            "Amanda's Villa runs its landscaping and hardscape work from its garden center on Dollarway Road in White Hall. Amanda designs the beds and her crew plants them. The hardscape teams, led by Colton, build the walks, patios, walls and drains.",
            "Every project starts the same way, with a free estimate and a transit survey of how the yard falls. Once a crew starts, it stays on that one job until it is finished, with weather the only common delay.",
        ],
        "quote": "Say you come look at our stuff, you could dissect it, and each step is going to be done correctly.",
        "photo": ("guide-crew-digging-french-drain-trench", "An Amanda's Villa crew member digging a French drain trench across a Star City backyard"),
    },
    "plan": {
        "h2": "How a Star City project works, from free estimate to finished yard",
        "steps": [
            ("i-clipboard-list", "Request a free estimate", f"Call {PHONE} or send the estimate form with a few photos of your yard."),
            ("i-ruler", "Survey and design", "A member of the hardscape team visits your Star City property, surveys it with a transit and plans the drainage and stonework, and Amanda plans the planting. You receive a custom quote."),
            ("i-hammer", "Build and plant", "One crew builds your project from start to finish, and Amanda's crew plants the beds."),
        ],
    },
    "services_h2": "What Amanda's Villa builds and plants for Star City homes",
    "services": [
        ("i-layers", "Paver patios", "hardscape/", "Patios on a compacted gravel base, with polymeric sand in the joints."),
        ("i-footprints", "Walkways", "hardscape/", "Paver, flagstone and stone walks from the drive to the door or around the house."),
        ("i-brick-wall", "Retaining walls", "hardscape/", "Structural walls for slopes and lower walls that raise a flower bed."),
        ("i-cloud-rain", "French drains", "hardscape/french-drains/", "Gravel and pipe drains that carry standing water out of the yard."),
        ("i-flower", "Landscape design and flower beds", "landscaping/", "Beds of shrubs and flowers designed by Amanda and planted by her crew."),
        ("i-sprout", "Garden center", "garden-center/", "Plants, mulch, soil and landscaping stone on the lot in White Hall."),
    ],
    "area": {
        "h2": "Landscaping and hardscaping for Star City homes",
        "paras": [
            f"Star City is the seat of Lincoln County, and Cane Creek State Park, just east of town, sits where the Delta meets the West Gulf Coastal Plain.{fn(4)} Yards in and around town range from well-drained sandy hilltops to low, flat ground where the water table rises close to the surface.{fn(2, 'b')}",
            f'Amanda\'s Villa builds <a class="link" href="{P}hardscape/french-drains/">French drains</a> and <a class="link" href="{P}hardscape/">paver walks, patios and retaining walls</a> for Star City homes, and Amanda designs and plants the <a class="link" href="{P}landscaping/">flower beds and front yards</a> around them. The <a class="link" href="{P}garden-center/">garden center</a> in White Hall sells the plants, mulch and stone.',
        ],
    },
    "faq_h2": "Star City landscaping and hardscaping questions",
    "faq": [
        ("Has Amanda's Villa done work in Star City?",
         "Yes. The French drain, paver walk, flagstone walk and flower beds on this page are all at Star City homes, and the teams work all over the state of Arkansas."),
        ("What does Star City's soil mean for a walk, patio or flower bed?",
         f"Under roughly seven of every ten acres in and around Star City, USDA soil maps show a seasonal water table within about two feet of the surface. Savannah fine sandy loam, which covers nearly three of every ten acres there, also has a dense layer called a fragipan about two feet down that slows water draining through it.{fn(2, 'c')} So every walk and patio sits on a compacted gravel base, and drainage is planned before anything is planted."),
        ("Is the estimate free?",
         "Yes. A member of the hardscape team visits the property, surveys it with a transit and provides an estimate at no cost."),
        ("How long does a project take?",
         "It depends on the project. The French drain on this page took four days from the first cut to the finished lawn. Once work begins, the crew stays on your project until it is finished, and weather is the only common delay."),
        ("Where do the plants and stone come from?",
         "Amanda chooses plants from the Amanda's Villa garden center at 7901 Dollarway Road in White Hall, which also sells mulch, soil and landscaping stone to homeowners."),
        ("Can you work with my budget?",
         "Yes. Every project is a custom quote. The team starts with the ideal design for your yard and then adjusts the scope to fit your budget."),
    ],
    "closing": {
        "h2": "Book a free estimate for your Star City yard",
        "text": "Your project starts with a walk around your yard. Schedule a free estimate, and the team will plan the drainage, stonework and planting for your Star City home.",
        "photo": "closing-dry-side-yard-after-drain",
    },
    "cites": [
        "NOAA National Centers for Environmental Information and the North Carolina Institute for Climate Studies, “Arkansas State Climate Summary,” 2022. Long-term statewide average of 50.1 inches of precipitation a year.",
        "USDA Natural Resources Conservation Service, Soil Survey Geographic Database (SSURGO), Lincoln County, Arkansas, accessed through Soil Data Access, October 2026. Of the soils mapped within about a mile of downtown Star City, the Savannah, Sawyer, Pheba and Amy soils, about 72 percent of the area, list a seasonal high water table 6 to 24 inches below the surface; Savannah fine sandy loam lists a fragipan at about 24 inches. The well-drained Smithdale and Ruston fine sandy loams cover about 17 percent.",
        "University of Arkansas Division of Agriculture Cooperative Extension Service, “Arkansas Flood Impacts.”",
        "CALS Encyclopedia of Arkansas, “Lincoln County” and “Star City (Lincoln County).”",
    ],
}

TOWNS = [STAR_CITY]


def build():
    for t in TOWNS:
        rel = f"projects/{t['slug']}/"
        os.makedirs(os.path.join(ROOT, rel), exist_ok=True)
        with open(os.path.join(ROOT, rel, "index.html"), "w", encoding="utf-8") as f:
            f.write(page(t))
        site_nav.apply(rel)
        print("built:", rel)


if __name__ == "__main__":
    build()
