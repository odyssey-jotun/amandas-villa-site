#!/usr/bin/env python3
"""Build the town portfolio pages under /projects/<town>/: one page per town where Amanda's Villa has finished work.

Run from the repo root:  python3 tools/build-town-pages.py

A town page is a portfolio first: its main content is the jobs Colton placed in that town
(see /job-photos/), grouped by category (Hardscape, Landscaping), each job with its own
carousel of every photo. Around the work sit one short sales section with the town's soil
facts, links to the service pages, a short FAQ and the closing call. Keep the shared copy
small so each page is mostly its own town's work.

Styles, scripts and the footer come from the French drain page; the menu and footer from
tools/site_nav.py. Town pages sit under Our Work in the menu (PROJECTS in site_nav.py), and
the hub at /projects/ links to every one of them. To add a town: add its dict to TOWNS here,
its card to HUB_CARDS and its page to PROJECTS in site_nav.py. Write only what the photos,
Colton's October 5 interview and cited public sources support.

Photos: img/projects/<town>/ (hero, sales and closing photos) and img/projects/<town>/portfolio/
(every job photo, house numbers removed, EXIF stripped).
"""
import html
import importlib.util
import json
import os
import re

from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE = open(os.path.join(ROOT, "hardscape", "french-drains", "index.html"), encoding="utf-8").read()
BUILD_PAGES = open(os.path.join(ROOT, "tools", "build-pages.py"), encoding="utf-8").read()

spec = importlib.util.spec_from_file_location("site_nav", os.path.join(ROOT, "tools", "site_nav.py"))
site_nav = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site_nav)

PHONE = "(870) 489-5463"
TEL = "tel:+18704895463"
P = "../../"  # every town page sits two folders deep

ICONS = ["i-cloud-rain", "i-layers", "i-sprout", "i-footprints", "i-brick-wall", "i-flower"]


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
    """Scripts and footer after </main>, minus the French drain page's single-carousel script."""
    s = TEMPLATE[TEMPLATE.index("</main>"):]
    s, n = re.subn(r"<script>\n\(function \(\) \{\n  var root = document\.querySelector\('\.cf'\).*?</script>\n", "", s, flags=re.S)
    if n != 1:
        raise SystemExit("French drain carousel script not found; update tail()")
    return s


TOWN_CSS = """<style id="town-page">
/* ---------- Town portfolio pages: work grouped by category, one carousel per job ---------- */
.tier { margin-top: var(--space-16); }
.tier-head { padding-bottom: var(--space-4); border-bottom: 1px solid var(--line-strong); }
.tier-head h3 { font: 400 32px/1.15 var(--font-display); }
.tier-head p { margin-top: var(--space-2); max-width: var(--measure-text); }
.tier-head .link { display: inline-block; margin-top: var(--space-2); }
.job { margin-top: var(--space-10); }
.job + .job { padding-top: var(--space-10); border-top: 1px solid var(--line); }
.job h4 { margin: 0; font: 400 24px/1.25 var(--font-text-serif); color: var(--ink); text-wrap: balance; }
.job-text { max-width: var(--measure-text); margin-top: var(--space-2); }
.job .cf { margin-top: var(--space-6); }
.cf--work .cf-caption { margin-top: var(--space-4); }
.cf--work .cf-title { font-size: 22px; }
.svc3 h3 a { color: inherit; text-decoration: none; border-bottom: 1px solid var(--line-strong); }
.svc3 h3 a:hover { border-bottom-color: var(--clay); }
.svc3--six { row-gap: var(--space-16); }
.hero-meta a { color: inherit; text-decoration: underline; text-underline-offset: 4px; }
.faq--solo { max-width: 860px; }
.job-photo { margin: var(--space-6) 0 0; max-width: 760px; }
.job-photo img { width: 100%; height: auto; display: block; border-radius: var(--radius-photo); }
.job-photo figcaption { margin-top: var(--space-2); }
.town-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-16) var(--space-10); }
.town-card a { color: inherit; text-decoration: none; display: block; }
.town-card img { width: 100%; height: auto; aspect-ratio: 4 / 3; object-fit: cover; display: block; border-radius: var(--radius-photo); }
.town-card h3 { margin-top: var(--space-4); font: 400 28px/1.15 var(--font-display); }
.town-card p { margin-top: var(--space-2); }
.town-card .link { display: inline-block; margin-top: var(--space-2); border-bottom: 1px solid var(--line-strong); }
.town-card a:hover .link { border-bottom-color: var(--clay); }
@media (max-width: 1000px) { .town-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) {
  .cf--many .cf-dots { display: none; }  /* more than 9 dots wrap on a phone; the count above says where you are */
  .town-grid { grid-template-columns: 1fr; }
  .town-card h3 { font-size: 25px; }
  .tier { margin-top: var(--space-10); }
  .tier-head h3 { font-size: 27px; }
  .job h4 { font-size: 21px; }
  .cf--work .cf-title { font-size: 19px; }
}
</style>"""

CAROUSEL_JS = """<script>
// One carousel per job. Each starts over at photo 1 when it scrolls into view and only advances while on screen.
document.querySelectorAll('.cf').forEach(function (root) {
  var cards = Array.prototype.slice.call(root.querySelectorAll('.cf-card'));
  var dotsBox = root.querySelector('.cf-dots'), title = root.querySelector('.cf-title'), count = root.querySelector('.cf-count');
  var n = cards.length, cur = 0, timer = null;
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var dots = cards.map(function (_, i) {
    var d = document.createElement('button'); d.type = 'button'; d.className = 'cf-dot';
    d.setAttribute('aria-label', 'Show photo ' + (i + 1)); d.addEventListener('click', function () { go(i); });
    dotsBox.appendChild(d); return d;
  });
  function render() {
    cards.forEach(function (c, i) {
      var off = (i - cur + n) % n; if (off > n / 2) off -= n;
      c.setAttribute('data-pos', Math.abs(off) <= 2 ? String(off) : 'x');
      c.setAttribute('aria-hidden', off === 0 ? 'false' : 'true');
    });
    dots.forEach(function (d, i) { d.setAttribute('aria-current', i === cur ? 'true' : 'false'); });
    count.textContent = (cur + 1) + ' / ' + n;
    title.textContent = cards[cur].getAttribute('data-title');
  }
  function go(i) { cur = (i + n) % n; render(); }
  function step(d) { go(cur + d); }
  cards.forEach(function (c, i) { c.addEventListener('click', function () { if (i !== cur) go(i); }); });
  root.querySelectorAll('.cf-btn').forEach(function (b) { b.addEventListener('click', function () { step(+b.getAttribute('data-dir')); }); });
  root.addEventListener('keydown', function (e) { if (e.key === 'ArrowLeft') { step(-1); e.preventDefault(); } if (e.key === 'ArrowRight') { step(1); e.preventDefault(); } });
  var x0 = null;
  root.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  root.addEventListener('touchend', function (e) { if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 40) step(dx < 0 ? 1 : -1); x0 = null; });
  function play() { if (still || timer || n < 2) return; timer = setInterval(function () { step(1); }, 6500); }
  function pause() { clearInterval(timer); timer = null; }
  root.addEventListener('mouseenter', pause); root.addEventListener('mouseleave', play);
  root.addEventListener('focusin', pause); root.addEventListener('focusout', play);
  render();
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { pause(); go(0); play(); } else { pause(); } });
    }, { threshold: 0.3 }).observe(root);
  } else { play(); }
});
</script>
"""

ARROW_L = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>'
ARROW_R = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>'


def e(t):
    return html.escape(t, quote=True)


def fn(n, suffix=""):
    return f"<sup class='fn'><a href='#cite-{n}' id='ref-{n}{suffix}' aria-label='Citation {n}'>{n}</a></sup>"


def ctas(extra_class=""):
    return (f'<div class="btn-row{extra_class}">\n      <a class="btn btn--primary" href="{P}contact/#estimate">Request a free estimate</a>\n'
            f'      <a class="btn btn--secondary" href="{TEL}">Call {PHONE}</a>\n    </div>')


def img(town, name, w, h, alt, lazy=True):
    return (f'<img width="{w}" height="{h}" src="{P}img/projects/{town}/{name}.jpg" alt="{e(alt)}"'
            + (' loading="lazy"' if lazy else "") + ">")


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def carousel(slug, job):
    if len(job["photos"]) == 1:  # one photo on file: a plain figure, no carousel controls
        f, cap = job["photos"][0]
        w, h = Image.open(os.path.join(ROOT, "img", "projects", slug, "portfolio", f + ".jpg")).size
        return (f'      <figure class="job-photo"><img width="{w}" height="{h}" src="{P}img/projects/{slug}/portfolio/{f}.jpg" '
                f'alt="{e(job["title"] + ": " + cap)}" loading="lazy"><figcaption>{e(cap)}</figcaption></figure>')
    cards = []
    for i, (f, cap) in enumerate(job["photos"]):
        w, h = Image.open(os.path.join(ROOT, "img", "projects", slug, "portfolio", f + ".jpg")).size
        alt = f"{job['title']}: {cap}"
        cards.append(f'        <figure class="cf-card" data-i="{i}" data-title="{e(cap)}"><img draggable="false" width="{w}" height="{h}" '
                     f'src="{P}img/projects/{slug}/portfolio/{f}.jpg" alt="{e(alt)}" loading="lazy"></figure>')
    n = len(cards)
    return f"""      <div class="cf cf--steps cf--work{' cf--many' if n > 9 else ''}" tabindex="0" role="region" aria-roledescription="carousel" aria-label="{e(job['title'])}, {n} photos">
        <div class="cf-bar cf-bar--top">
          <button class="cf-btn" type="button" data-dir="-1" aria-label="Previous photo">{ARROW_L}</button>
          <span class="cf-count" aria-hidden="true">1 / {n}</span>
          <button class="cf-btn" type="button" data-dir="1" aria-label="Next photo">{ARROW_R}</button>
        </div>
        <div class="cf-stage">
{chr(10).join(cards)}
        </div>
        <div class="cf-caption" aria-live="polite"><p class="cf-title">{e(job['photos'][0][1])}</p></div>
        <div class="cf-bar">
          <button class="cf-btn" type="button" data-dir="-1" aria-label="Previous photo">{ARROW_L}</button>
          <div class="cf-dots"></div>
          <button class="cf-btn" type="button" data-dir="1" aria-label="Next photo">{ARROW_R}</button>
        </div>
      </div>"""


def page(t):
    slug, town = t["slug"], t["town"]

    tiers = []
    for tier in t["tiers"]:
        jobs = "\n".join(f"""    <article class="job">
      <h4>{e(j["title"])}</h4>
      <div class="job-text"><p>{j["text"]}</p></div>
{carousel(slug, j)}
    </article>""" for j in tier["jobs"])
        tiers.append(f"""  <div class="tier">
    <div class="tier-head">
      <h3>{e(tier["title"])}</h3>
      <p>{tier["text"]}</p>
      <a class="link" href="{P}{tier["link"][0]}">{e(tier["link"][1])}</a>
    </div>
{jobs}
  </div>""")

    sales = t["sales"]
    sales3 = "\n".join(f'      <div><span class="ic-badge"><svg class="ic" aria-hidden="true"><use href="#{ic}"/></svg></span><h3>{e(h)}</h3><p>{p}</p></div>'
                       for ic, h, p in sales["points"])
    sales_p = "\n".join(f"        <p>{p}</p>" for p in sales["paras"])
    svc = "\n".join(f'      <div><span class="ic-badge"><svg class="ic" aria-hidden="true"><use href="#{ic}"/></svg></span>'
                    f'<h3><a href="{P}{href}">{e(title)}</a></h3><p>{text}</p></div>'
                    for ic, title, href, text in t["services"])
    faq = "\n".join(f"      <details><summary>{e(q)}</summary><div><p>{a}</p></div></details>" for q, a in t["faq"])
    cites = "\n".join(f'          <li id="cite-{i}">{c}</li>' for i, c in enumerate(t["cites"], 1))

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

    hero, closing = t["hero"], t["closing"]
    return f"""<!doctype html>
<html lang="en">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-YDMETHXQC0"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', 'G-YDMETHXQC0');
</script>
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
      <p class="hero-meta"><a href="#projects">{e(t["work_h2"])}</a> · Free estimates</p>
    </div>
  </div>
</header>

<main>

<!-- THE WORK: every job Colton placed in this town, grouped by category -->
<section class="band" id="projects">
  <div class="wrap">
    <div class="head">
      <h2>{e(t["work_h2"])}</h2>
      <p>{t["work_intro"]}</p>
    </div>
{chr(10).join(tiers)}
  </div>
</section>

<!-- SALES: the town's ground, and how the teams build for it -->
<section class="band band--alt">
  <div class="wrap">
    <div class="split split--short">
      <div class="split-text">
        <h2>{sales["h2"]}</h2>
        <div class="prose" style="margin-top: var(--space-6)">
{sales_p}
        </div>
      </div>
      <figure class="split-media">
        {img(slug, sales["photo"][0], 1000, 1250, sales["photo"][1])}
      </figure>
    </div>
    <div class="svc3">
{sales3}
    </div>
    {ctas(" cta-row")}
  </div>
</section>

<!-- SERVICES -->
<section class="band">
  <div class="wrap">
    <div class="head" style="text-align:center">
      <h2>{e(t["services_h2"])}</h2>
    </div>
    <div class="svc3 svc3--six" style="margin-top:0">
{svc}
    </div>
  </div>
</section>

<!-- FAQ -->
<section class="band band--alt">
  <div class="wrap">
    <div class="head">
      <h2>{e(t["faq_h2"])}</h2>
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

{CAROUSEL_JS}
{tail()}"""


STAR_CITY = {
    "slug": "star-city", "town": "Star City",
    "title": "Landscaping and Hardscaping Projects in Star City, AR | Amanda's Villa",
    "description": "Four Amanda's Villa projects in Star City, Arkansas, photographed from start to finish: new flower beds, a curved paver walk, a flagstone walk and a French drain.",
    "hero": {
        "h1": "Landscaping and Hardscaping Projects in Star City, <em>Arkansas</em>",
        "sub": "New flower beds, two new walks and a French drain, planted and built by Amanda's Villa for Star City homes.",
        "wide": ("hero-curved-paver-walk-picket-gate-wide", "A curved paver walk running through a white picket fence gate beside a Star City home, built by the Amanda's Villa hardscape team"),
        "tall": ("hero-curved-paver-walk-river-rock-tall",),
    },
    "work_h2": "Examples of our work in Star City",
    "work_intro": "Each of these was planted by Amanda's crew or built by the Amanda's Villa hardscape teams at a home in Star City. Use the arrows to walk through each job from start to finish.",
    "tiers": [
        {"title": "Landscaping",
         "text": "Beds of shrubs and flowers, designed by Amanda and planted by her crew.",
         "link": ("landscaping/", "More about landscaping at Amanda's Villa"),
         "jobs": [
             {"title": "Flower beds along a brick-edged drive",
              "text": "Amanda's crew planted new beds along the brick edging: rows of shrubs behind borders of seasonal flowers, a bed across the front of the sunroom and bright annuals beside the porch rail.",
              "photos": [
                  ("beds-1-sunroom-bed", "Bed across the front of the sunroom"), ("beds-2-flower-border-drive", "Flower border along the drive"),
                  ("beds-3-shrubs-by-brick-pillar", "Shrubs beside the brick pillar"), ("beds-4-annuals-by-porch", "Annuals beside the porch rail")]},
         ]},
        {"title": "Hardscape and drainage",
         "text": "Drains, walks and stonework, built by the hardscape teams led by Colton.",
         "link": ("hardscape/", "More about hardscape at Amanda's Villa"),
         "jobs": [
             {"title": "A French drain along the fence and the house",
              "text": "The team lifted the sod along the drain route, dug the trench, lined it with filter fabric and laid the pipe in gravel, with catch basins where the water collects. Then the sod went back down. From the first cut to the finished lawn, the job took four days.",
              "photos": [
                  ("drain-1-sod-lifted", "Sod lifted along the drain route"), ("drain-2-trench-dug", "Trench dug"),
                  ("drain-3-pipe-in-fabric", "Pipe laid in a fabric-lined trench beside the house"), ("drain-4-gravel-and-catch-basin", "Gravel and a catch basin grate"),
                  ("drain-5-sod-going-back", "Sod going back down along the fence"), ("drain-6-finished-along-fence", "Finished, lawn back along the fence"),
                  ("drain-7-finished-beside-house", "Finished, lawn back beside the house")]},
             {"title": "A curved paver walk to the backyard gate",
              "text": "The strip of grass between the house and the picket fence became a curved paver walk with a two-color border and a river rock bed set into the bend. Downspout lines were run beneath the walk before the base went down.",
              "photos": [
                  ("walk-1-before", "Before: grass between the house and the fence"), ("walk-2-dug-out-downspout-lines", "Walk dug out, downspout lines going in"),
                  ("walk-3-pavers-going-down", "Pavers going down"), ("walk-4-finished-curve-to-gate", "Finished walk curving to the gate"),
                  ("walk-5-finished-river-rock-bed", "Finished walk and the river rock bed"), ("walk-6-finished-through-gate", "Finished walk through the gate")]},
             {"title": "A flagstone front walk with a paver border",
              "text": "The front walk was dug out from the drive to the porch, filled with a gravel base, edged with pavers and finished with flagstone set in gravel.",
              "photos": [
                  ("flagstone-1-dug-out", "Walk dug out to the porch"), ("flagstone-2-gravel-and-border", "Gravel base down, paver border set"),
                  ("flagstone-3-finished", "Finished flagstone walk with the paver border")]},
         ]},
    ],
    "sales": {
        "h2": "Let's build you a Star City yard that stays dry and looks finished",
        "paras": [
            f"Star City is the seat of Lincoln County, which Bayou Bartholomew splits between the Delta and the West Gulf Coastal Plain.{fn(3)} Under roughly seven of every ten acres in and around town, USDA soil maps show a seasonal water table within about two feet of the surface,{fn(2)} and Arkansas averages about 50 inches of rain a year.{fn(1)}",
            "So your project starts with a free estimate and a transit survey of how your ground falls, and the drainage is planned before the stone and the plants.",
        ],
        "photo": ("sales-shrub-and-flower-bed-by-sunroom", "A finished bed of boxwoods, gold shrubs and seasonal flowers inside a brick edge, in front of the white arched sunroom of a Star City home"),
        "points": [
            ("i-layers", "A gravel base under every walk", "Your walk or patio sits on 8 to 10 inches of compacted gravel with a finer base on top, so the stone stays level through wet springs and dry summers."),
            ("i-cloud-rain", "Drainage goes in first", "Downspout lines and French drains go in before the stone and the plants, so roof water and runoff have somewhere to go."),
            ("i-sprout", "Plants from the garden center in White Hall", "Amanda chooses your shrubs and flowers from the Amanda's Villa lot, and her crew plants them."),
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
    "faq_h2": "Star City landscaping and hardscaping questions",
    "faq": [
        ("Has Amanda's Villa done work in Star City?",
         "Yes. The flower beds, paver walk, flagstone walk and French drain on this page are all at Star City homes, and the teams work all over the state of Arkansas."),
        ("What does Star City's soil mean for a walk, patio or flower bed?",
         f"Under roughly seven of every ten acres in and around Star City, USDA soil maps show a seasonal water table within about two feet of the surface. Savannah fine sandy loam, which covers nearly three of every ten acres there, also has a dense layer called a fragipan about two feet down that slows water draining through it.{fn(2, 'b')} So every walk and patio sits on a compacted gravel base, and drainage is planned before anything is planted."),
        ("How long does a project take?",
         "It depends on the project. The French drain on this page took four days from the first cut to the finished lawn. Once work begins, the crew stays on your project until it is finished, and weather is the only common delay."),
        ("Is the estimate free?",
         "Yes. A member of the hardscape team visits the property, surveys it with a transit and provides an estimate at no cost. Every project is a custom quote."),
    ],
    "closing": {
        "h2": "Book a free estimate for your Star City yard",
        "text": "Your project starts with a walk around your yard. Schedule a free estimate, and the team will plan the drainage, stonework and planting for your Star City home.",
        "photo": "closing-curved-paver-walk-river-rock",
    },
    "cites": [
        "NOAA National Centers for Environmental Information and the North Carolina Institute for Climate Studies, “Arkansas State Climate Summary,” 2022. Long-term statewide average of 50.1 inches of precipitation a year.",
        "USDA Natural Resources Conservation Service, Soil Survey Geographic Database (SSURGO), Lincoln County, Arkansas, accessed through Soil Data Access, October 2026. Of the soils mapped within about a mile of downtown Star City, the Savannah, Sawyer, Pheba and Amy soils, about 72 percent of the area, list a seasonal high water table 6 to 24 inches below the surface; Savannah fine sandy loam, about 29 percent, lists a fragipan at about 24 inches. The well-drained Smithdale and Ruston fine sandy loams cover about 17 percent.",
        "CALS Encyclopedia of Arkansas, “Lincoln County” and “Star City (Lincoln County).”",
    ],
}

NOAA_CITE = STAR_CITY["cites"][0]
SERVICES = STAR_CITY["services"]
STANDARD_POINTS = STAR_CITY["sales"]["points"]


def ask_free_estimate():
    return ("Is the estimate free?",
            "Yes. A member of the hardscape team visits the property, surveys it with a transit and provides an estimate at no cost. Every project is a custom quote.")


WHITE_HALL = {
    "slug": "white-hall", "town": "White Hall",
    "title": "Landscaping Projects in White Hall, AR | Amanda's Villa",
    "description": "Four sets of new flower beds Amanda's Villa planted at White Hall, Arkansas homes, near the garden center on Dollarway Road.",
    "hero": {
        "h1": "Landscaping Projects in White Hall, <em>Arkansas</em>",
        "sub": "Four sets of new flower beds, designed by Amanda and planted by her crew for White Hall homes, close to the Amanda's Villa garden center on Dollarway Road.",
        "wide": ("hero-flower-beds-front-walk-wide", "Two curved flower beds framing the front walk of a red brick White Hall home, each with a small tree ringed by seasonal flowers, planted by Amanda's Villa"),
        "tall": ("hero-flower-beds-front-walk-tall",),
    },
    "work_h2": "Examples of our work in White Hall",
    "work_intro": "Each of these was designed by Amanda and planted by her crew at a home in White Hall. Use the arrows to compare each yard before and after.",
    "tiers": [
        {"title": "Landscaping",
         "text": "Beds of shrubs and flowers, designed by Amanda and planted by her crew.",
         "link": ("landscaping/", "More about landscaping at Amanda's Villa"),
         "jobs": [
             {"title": "Planted beds along a stepping-stone walk",
              "text": "At a new white stone house with a round tower, the walk to the front door ran through bare dirt. Amanda's crew planted beds along the house on both sides of the walk: shrubs, flowers and black mulch, up to a fern urn and a fountain at the front door.",
              "photos": [
                  ("walk-beds-1-before", "Before: bare dirt along the walk"), ("walk-beds-2-after", "After: planted beds along the walk"),
                  ("walk-beds-3-fern-urn-fountain", "Fern urn and fountain by the front door")]},
             {"title": "Block-edged beds along the drive and a fountain bed",
              "text": "A strip of grass along the drive of a white brick house became a bed edged in block and planted with shrubs and flowers. Around the corner by the garage, a bare patch became a matching bed with a fountain in the middle.",
              "photos": [
                  ("drive-beds-1-before", "Before: grass strip along the drive"), ("drive-beds-2-after", "After: block-edged bed along the drive"),
                  ("drive-beds-3-corner-before", "Before: bare corner by the garage"), ("drive-beds-4-fountain-bed", "After: fountain bed by the garage")]},
             {"title": "Flower beds on both sides of the front walk",
              "text": "Two curved beds frame the front walk where it meets the street, each with a small tree ringed by seasonal flowers inside a block edge.",
              "photos": [("mailbox-beds", "Beds on both sides of the front walk")]},
             {"title": "A flower ring under a shade tree",
              "text": "A ring of seasonal flowers, inside stone edging, around the trunk of a big shade tree in the front lawn.",
              "photos": [("flower-ring", "Flower ring with stone edging")]},
         ]},
    ],
    "sales": {
        "h2": "Let's plant you a White Hall yard that stays dry and looks finished",
        "paras": [
            f"The Amanda's Villa garden center sits on Dollarway Road, which the Encyclopedia of Arkansas calls the first concrete road in Arkansas.{fn(3)} Under roughly eight of every ten acres within a mile of the center of White Hall, USDA soil maps show a seasonal water table within about two feet of the surface, and under about six of every ten, a dense layer called a fragipan two to two and a half feet down slows water draining through it.{fn(2)} Arkansas averages about 50 inches of rain a year.{fn(1)}",
            "So your project starts with a free estimate, and the drainage is planned before the stone and the plants.",
        ],
        "photo": ("sales-planted-beds-along-stepping-stone-walk", "New beds of shrubs and flowers along a stepping-stone walk beside a white stone house with a round tower in White Hall"),
        "points": [
            ("i-sprout", "Plants from the lot on Dollarway Road", "Amanda chooses your shrubs and flowers from the Amanda's Villa garden center in White Hall, and her crew plants them."),
            STANDARD_POINTS[1],
            STANDARD_POINTS[0],
        ],
    },
    "services_h2": "What Amanda's Villa builds and plants for White Hall homes",
    "services": SERVICES,
    "faq_h2": "White Hall landscaping questions",
    "faq": [
        ("Has Amanda's Villa done work in White Hall?",
         "Yes. The garden center is on Dollarway Road in White Hall, and the four sets of flower beds on this page are all at White Hall homes. The teams work all over the state of Arkansas."),
        ("What does White Hall's soil mean for a flower bed or a walk?",
         f"Under roughly eight of every ten acres within a mile of the center of White Hall, USDA soil maps show a seasonal water table within about two feet of the surface. Savannah and Pheba soils, which cover about six of every ten acres there, also have a fragipan two to two and a half feet down that slows water draining through it.{fn(2, 'b')} So every walk and patio sits on a compacted gravel base, and drainage is planned before anything is planted."),
        ("How long does a project take?",
         "It depends on the project. Once work begins, the crew stays on your project until it is finished, and weather is the only common delay."),
        ask_free_estimate(),
    ],
    "closing": {
        "h2": "Book a free estimate for your White Hall yard",
        "text": "Your project starts with a walk around your yard. Schedule a free estimate, and Amanda's Villa will plan the planting, stonework and drainage for your White Hall home.",
        "photo": "closing-block-edged-bed-along-drive",
    },
    "cites": [
        NOAA_CITE,
        "USDA Natural Resources Conservation Service, Soil Survey Geographic Database (SSURGO), Jefferson County, Arkansas, accessed through Soil Data Access, October 2026. Of the soils mapped within about a mile of the center of White Hall, the Savannah, Pheba, Sawyer and Amy soils, about 83 percent of the area, list a seasonal high water table 6 to 24 inches below the surface. Savannah fine sandy loam, about 36 percent, lists a fragipan at about 24 inches, and Pheba silt loam, about 26 percent, at about 29 inches.",
        "CALS Encyclopedia of Arkansas, “White Hall (Jefferson County).” Act 164 of 1913 let Jefferson County levy a special tax to build the Dollarway Road, “the first concrete road in Arkansas.”",
    ],
}

WOODLAWN = {
    "slug": "woodlawn", "town": "Woodlawn",
    "title": "Landscaping and Hardscaping Projects in Woodlawn, AR | Amanda's Villa",
    "description": "Two Amanda's Villa projects in Woodlawn, Arkansas, photographed from start to finish: a curved bed with a flagstone walk, and a farmhouse front with block walls, steps and a paver walk.",
    "hero": {
        "h1": "Landscaping and Hardscaping Projects in Woodlawn, <em>Arkansas</em>",
        "sub": "A curved bed with a flagstone walk, and a farmhouse front with block walls, wide steps and a paver walk, built and planted by Amanda's Villa for Woodlawn homes.",
        "wide": ("hero-farmhouse-walls-steps-walk-wide", "A black board-and-batten farmhouse in Woodlawn with a new block retaining wall, wide block steps, a paver landing and planted beds, built by Amanda's Villa"),
        "tall": ("hero-farmhouse-curved-walk-tall",),
    },
    "work_h2": "Examples of our work in Woodlawn",
    "work_intro": "Each of these was planted by Amanda's crew or built by the Amanda's Villa hardscape teams at a home in Woodlawn. Use the arrows to walk through each job from start to finish.",
    "tiers": [
        {"title": "Landscaping",
         "text": "Beds of shrubs and flowers, designed by Amanda and planted by her crew.",
         "link": ("landscaping/", "More about landscaping at Amanda's Villa"),
         "jobs": [
             {"title": "A curved bed with a flagstone walk around it",
              "text": "Beside a tan-sided house, a curved bed was cut into bare ground, edged and planted with shrubs. Then a flagstone walk was laid around the curve of the bed to the drive.",
              "photos": [("bed-1-before", "Before: bed outline dug in bare ground"), ("bed-2-after", "After: flagstone walk around the planted bed")]},
         ]},
        {"title": "Hardscape",
         "text": "Walls, steps and walks, built by the Amanda's Villa hardscape teams.",
         "link": ("hardscape/", "More about hardscape at Amanda's Villa"),
         "jobs": [
             {"title": "Block walls, steps and a paver walk across a farmhouse front",
              "text": "The front of a black farmhouse sat a step above open lawn. The hardscape team built a block retaining wall along the front beds and beside the garage, wide block steps up to a paver landing at the porch, and a paver walk with a dark border that curves between new beds out toward the drive. The beds were planted with shrubs and grasses, with boulders set in the mulch.",
              "photos": [
                  ("farmhouse-01-before-front-yard", "Before: front yard and porch"), ("farmhouse-02-before-beds-by-garage", "Before: the beds by the garage"),
                  ("farmhouse-03-dug-out-front-beds", "Ground dug out along the front beds, layout stakes in"), ("farmhouse-04-wall-going-up", "Wall going up beside the garage"),
                  ("farmhouse-05-wall-and-steps-built", "Wall and steps built, gravel fill"), ("farmhouse-06-walk-turning-corner", "Paver walk turning the corner by the garage"),
                  ("farmhouse-07-walk-along-beds", "Paver walk along the front beds"), ("farmhouse-08-steps-and-landing", "Steps and landing at the porch"),
                  ("farmhouse-09-landing-at-porch", "Landing at the porch"), ("farmhouse-10-finished-from-yard", "Finished: walls, steps and beds from the yard"),
                  ("farmhouse-11-finished-steps-to-porch", "Finished: steps up to the porch"), ("farmhouse-12-finished-walk-between-beds", "Finished: walk between the beds"),
                  ("farmhouse-13-finished-landing", "Finished: landing at the porch"), ("farmhouse-14-finished-curved-walk", "Finished: curved walk and bed"),
                  ("farmhouse-15-finished-steps-boulder-bed", "Finished: steps and the boulder bed"), ("farmhouse-16-finished-raised-wall", "Finished: raised wall by the garage"),
                  ("farmhouse-17-finished-long-walk", "Finished: long walk out toward the driveway")]},
         ]},
    ],
    "sales": {
        "h2": "Let's build you a Woodlawn yard that stays dry and looks finished",
        "paras": [
            f"Woodlawn sits in Cleveland County, which the Saline River crosses from near its northwest corner to near its southeast corner.{fn(3)} Under nearly eight of every ten acres within a mile of Woodlawn, USDA soil maps show a seasonal water table within about two feet of the surface, and nearly one acre in five is floodplain that floods often.{fn(2)} Arkansas averages about 50 inches of rain a year.{fn(1)}",
            "So your project starts with a free estimate and a transit survey of how your ground falls, and the drainage is planned before the stone and the plants.",
        ],
        "photo": ("sales-curved-paver-walk-new-beds", "A curved paver walk with a dark border between new beds of shrubs, grasses and a boulder at a Woodlawn farmhouse"),
        "points": STANDARD_POINTS,
    },
    "services_h2": "What Amanda's Villa builds and plants for Woodlawn homes",
    "services": SERVICES,
    "faq_h2": "Woodlawn landscaping and hardscaping questions",
    "faq": [
        ("Has Amanda's Villa done work in Woodlawn?",
         "Yes. The curved bed and flagstone walk and the farmhouse walls, steps and walk on this page are both at Woodlawn homes, and the teams work all over the state of Arkansas."),
        ("What does Woodlawn's soil mean for a walk, patio or flower bed?",
         f"Under nearly eight of every ten acres within a mile of Woodlawn, USDA soil maps show a seasonal water table within about two feet of the surface.{fn(2, 'b')} So every walk and patio sits on a compacted gravel base, and drainage is planned before anything is planted."),
        ("How long does a project take?",
         "It depends on the project. At the farmhouse on this page, the first wall was going up in late April, and the finished photos were taken in mid-May. Once work begins, the crew stays on your project until it is finished, and weather is the only common delay."),
        ask_free_estimate(),
    ],
    "closing": {
        "h2": "Book a free estimate for your Woodlawn yard",
        "text": "Your project starts with a walk around your yard. Schedule a free estimate, and the team will plan the drainage, stonework and planting for your Woodlawn home.",
        "photo": "closing-steps-and-boulder-bed",
    },
    "cites": [
        NOAA_CITE,
        "USDA Natural Resources Conservation Service, Soil Survey Geographic Database (SSURGO), Cleveland County, Arkansas, accessed through Soil Data Access, October 2026. Of the soils mapped within about a mile of Woodlawn, the Wehadkee, Savannah, Tippah, Caddo, Pheba, Prentiss, Weston and Stough soils, about 79 percent of the area, list a seasonal high water table 6 to 24 inches below the surface. Wehadkee soils and Udifluvents, about 18 percent, are frequently flooded.",
        "CALS Encyclopedia of Arkansas, “Cleveland County.”",
    ],
}

HOT_SPRINGS = {
    "slug": "hot-springs", "town": "Hot Springs",
    "title": "Hillside Retaining Wall Project in Hot Springs, AR | Amanda's Villa",
    "description": "A bare Hot Springs, Arkansas hillside built into levels by Amanda's Villa: curved block retaining walls, block steps, a round raised terrace and boulder steps.",
    "hero": {
        "h1": "Hillside Retaining Walls in Hot Springs, <em>Arkansas</em>",
        "sub": "A bare hillside built into levels with curved block retaining walls, block steps, a round raised terrace and boulder steps, by the Amanda's Villa hardscape teams.",
        "wide": ("hero-hillside-round-wall-steps-wide", "A round block retaining wall with steps cut into it on a wooded Hot Springs hillside, with planted beds on the level above, built by Amanda's Villa"),
        "tall": ("hero-hillside-block-steps-tall",),
    },
    "work_h2": "Examples of our work in Hot Springs",
    "work_intro": "This hillside was built by the Amanda's Villa hardscape teams at a home in Hot Springs. Use the arrows to go from the bare slope to the finished walls, from the ground and from the air.",
    "tiers": [
        {"title": "Hardscape",
         "text": "Walls, steps and patios, built by the Amanda's Villa hardscape teams.",
         "link": ("hardscape/", "More about hardscape at Amanda's Villa"),
         "jobs": [
             {"title": "Retaining walls, block steps, a patio and boulder steps on a wooded hillside",
              "text": "The slope beside the house was bare red dirt. An excavator graded it into levels, and the hardscape team built curved block retaining walls to hold each level, block steps between the walls, a round raised terrace, a paver patio along a curved wall and boulder steps through a bed of river rock. Planted beds sit on the levels above the walls.",
              "photos": [
                  ("hillside-01-before-bare-slope", "Before: bare slope by the fence"), ("hillside-02-excavator-grading", "Excavator grading the slope"),
                  ("hillside-03-drone-walls-patio-beds", "Drone: walls, terrace and beds from above"), ("hillside-04-drone-patio-steps-river-rock", "Drone: terrace, steps and river rock"),
                  ("hillside-05-drone-curved-wall-steps", "Drone: curved wall and steps"), ("hillside-06-drone-round-wall", "Drone: the round wall and the bed above it"),
                  ("hillside-07-block-steps-between-walls", "Block steps between two walls"), ("hillside-08-curved-wall-paver-patio", "Curved wall and paver patio"),
                  ("hillside-09-wall-corner-gravel", "Wall corner and gravel"), ("hillside-10-wall-river-rock-drive", "Wall with river rock along the drive"),
                  ("hillside-11-boulder-steps", "Boulder steps through river rock"), ("hillside-12-drone-round-wall-steps-low", "Drone: the round wall and steps, lower angle"),
                  ("hillside-13-drone-round-wall-drive", "Drone: round wall and steps with the drive behind")]},
         ]},
    ],
    "sales": {
        "h2": "Let's build you a Hot Springs yard that holds its slope and looks finished",
        "paras": [
            f"Hot Springs sits along the Ouachita River in the Central Ouachita Mountains.{fn(3)} Within about a mile of downtown, USDA soil maps show roughly seven of every ten acres sloping 8 percent or more, about six of every ten mapped as stony and bedrock within about three feet of the surface under more than eight of every ten.{fn(2)} Arkansas averages about 50 inches of rain a year.{fn(1)}",
            "So a hillside yard there is built in levels. Walls hold the slope back, steps join one level to the next, and your project starts with a free estimate and a transit survey of how the ground falls.",
        ],
        "photo": ("sales-boulder-steps-river-rock", "Boulder steps climbing through a bed of river rock between block retaining walls on a Hot Springs hillside"),
        "points": [
            ("i-brick-wall", "Walls that hold the slope", "Structural retaining walls hold the hillside back in levels, so the ground between them is flat enough to use."),
            ("i-layers", "A gravel base under every patio", "Your patio or walk sits on 8 to 10 inches of compacted gravel with a finer base on top, so the stone stays level through wet springs and dry summers."),
            ("i-footprints", "Steps between the levels", "Block or boulder steps join each level, so the whole hillside is a yard you can walk."),
        ],
    },
    "services_h2": "What Amanda's Villa builds and plants for Hot Springs homes",
    "services": SERVICES,
    "faq_h2": "Hot Springs hardscaping questions",
    "faq": [
        ("Has Amanda's Villa done work in Hot Springs?",
         "Yes. The hillside walls, steps and terrace on this page are at a Hot Springs home, and the teams work all over the state of Arkansas."),
        ("What does Hot Springs ground mean for a wall or a patio?",
         f"Within about a mile of downtown Hot Springs, USDA soil maps show roughly seven of every ten acres sloping 8 percent or more, and more than eight of every ten with bedrock within about three feet of the surface.{fn(2, 'b')} So a sloped yard is built in levels behind structural retaining walls, and every walk and patio sits on a compacted gravel base."),
        ("How long does a project take?",
         "It depends on the project. On the hillside on this page, the excavator was grading the slope in late August, and the finished drone photos were taken in early October. Once work begins, the crew stays on your project until it is finished, and weather is the only common delay."),
        ask_free_estimate(),
    ],
    "closing": {
        "h2": "Book a free estimate for your Hot Springs yard",
        "text": "Your project starts with a walk around your yard. Schedule a free estimate, and the team will plan the walls, steps and drainage for your Hot Springs home.",
        "photo": "closing-round-wall-from-above",
    },
    "cites": [
        NOAA_CITE,
        "USDA Natural Resources Conservation Service, Soil Survey Geographic Database (SSURGO), Garland County, Arkansas, accessed through Soil Data Access, October 2026. Of the soils mapped within about a mile of downtown Hot Springs, about 69 percent of the area has a representative slope of 8 percent or more. The Bismarck-Sherless-Clebit and Bismarck-Clebit-Sherless complexes, about 62 percent, are mapped as stony or very stony and list soft bedrock at about 16 inches; in all, about 85 percent list bedrock within about 36 inches.",
        "CALS Encyclopedia of Arkansas, “Hot Springs (Garland County).”",
    ],
}

PINE_BLUFF = {
    "slug": "pine-bluff", "town": "Pine Bluff",
    "title": "Herringbone Brick Patio Project in Pine Bluff, AR | Amanda's Villa",
    "description": "A herringbone brick path and patio with new beds, built by Amanda's Villa behind a Pine Bluff, Arkansas home and photographed from bare ground to finished.",
    "hero": {
        "h1": "A Herringbone Brick Patio in Pine Bluff, <em>Arkansas</em>",
        "sub": "A herringbone brick path and patio with new beds on both sides, built and planted by Amanda's Villa behind a Pine Bluff home.",
        "wide": ("hero-herringbone-patio-chairs-wide", "A red brick herringbone patio with white metal chairs, a gray border and new planted beds behind a Pine Bluff home, built by Amanda's Villa"),
        "tall": ("hero-herringbone-path-tall",),
    },
    "work_h2": "Examples of our work in Pine Bluff",
    "work_intro": "This patio was built by the Amanda's Villa hardscape teams at a home in Pine Bluff. Use the arrows to walk through the job from the old yard to the finished patio.",
    "tiers": [
        {"title": "Hardscape",
         "text": "Patios, walks and stonework, built by the Amanda's Villa hardscape teams.",
         "link": ("hardscape/", "More about hardscape at Amanda's Villa"),
         "jobs": [
             {"title": "A herringbone brick path and patio with new beds",
              "text": "Behind the house, an old brick edging and a worn path ran through a bare yard between the house, a brick garage and a white arbor. The team cleared the ground, compacted the base and laid red brick pavers in a herringbone pattern with a gray border: a path along the house that opens into a patio by the garage. New beds of shrubs and flowers were planted on both sides. From the cleared ground to the finished patio took about two weeks.",
              "photos": [
                  ("patio-01-before-edging-along-house", "Before: old brick edging along the house"), ("patio-02-before-yard-and-arbor", "Before: the yard and the arbor by the garage"),
                  ("patio-03-ground-cleared", "Ground cleared, skid steer on site"), ("patio-04-base-compacted", "Base compacted"),
                  ("patio-05-path-started", "Herringbone path started along the house"), ("patio-06-path-and-border", "Path and border laid"),
                  ("patio-07-patio-laid", "Patio laid"), ("patio-08-patio-and-path-by-garage", "Patio and path by the garage"),
                  ("patio-09-finished-path-new-beds", "Finished: path and new beds"), ("patio-10-finished-patio-chairs", "Finished: patio with the white chairs"),
                  ("patio-11-finished-path-between-beds", "Finished: path between the planted beds")]},
         ]},
    ],
    "sales": {
        "h2": "Let's build you a Pine Bluff yard that stays dry and looks finished",
        "paras": [
            f"Pine Bluff grew from a cabin built in 1819 on a “high bluff covered with pine trees” on the south bank of the Arkansas River.{fn(3)} Under about three of every four acres of land within a mile of downtown, USDA soil maps show a seasonal water table within about two feet of the surface, rising to about a foot under more than half, over a dense fragipan layer two and a half to three feet down.{fn(2)} Arkansas averages about 50 inches of rain a year.{fn(1)}",
            "So your project starts with a free estimate and a transit survey of how your ground falls, and the drainage is planned before the stone and the plants.",
        ],
        "photo": ("sales-herringbone-path-new-beds", "A herringbone brick path with a gray border turning between new mulched beds behind a Pine Bluff home"),
        "points": STANDARD_POINTS,
    },
    "services_h2": "What Amanda's Villa builds and plants for Pine Bluff homes",
    "services": SERVICES,
    "faq_h2": "Pine Bluff hardscaping and landscaping questions",
    "faq": [
        ("Has Amanda's Villa done work in Pine Bluff?",
         "Yes. The herringbone path, patio and beds on this page are at a Pine Bluff home, and the teams work all over the state of Arkansas."),
        ("What does Pine Bluff's soil mean for a patio, walk or flower bed?",
         f"Under about three of every four acres of land within a mile of downtown Pine Bluff, USDA soil maps show a seasonal water table within about two feet of the surface, with a dense fragipan layer two and a half to three feet down that slows water draining through it.{fn(2, 'b')} So every walk and patio sits on a compacted gravel base, and drainage is planned before anything is planted."),
        ("How long does a project take?",
         "It depends on the project. The patio on this page took about two weeks from the cleared ground to the finished brick. Once work begins, the crew stays on your project until it is finished, and weather is the only common delay."),
        ask_free_estimate(),
    ],
    "closing": {
        "h2": "Book a free estimate for your Pine Bluff yard",
        "text": "Your project starts with a walk around your yard. Schedule a free estimate, and the team will plan the drainage, stonework and planting for your Pine Bluff home.",
        "photo": "closing-herringbone-patio",
    },
    "cites": [
        NOAA_CITE,
        "USDA Natural Resources Conservation Service, Soil Survey Geographic Database (SSURGO), Jefferson County, Arkansas, accessed through Soil Data Access, October 2026. Of the land mapped within about a mile of downtown Pine Bluff, open water left out, the Calloway, Grenada and Amy soils, about 77 percent, list a seasonal high water table 6 to 24 inches below the surface. Calloway-Urban land complex, about 59 percent, lists it at about 12 inches and a fragipan at about 37 inches; Grenada-Urban land complex, about 18 percent, lists a fragipan at about 29 inches.",
        "CALS Encyclopedia of Arkansas, “Pine Bluff (Jefferson County).”",
    ],
}

SHERIDAN = {
    "slug": "sheridan", "town": "Sheridan",
    "title": "Paver Walk and Landing Projects in Sheridan, AR | Amanda's Villa",
    "description": "A paver landing at the front door and a paver walk around the side of the house, built by Amanda's Villa at a Sheridan, Arkansas home.",
    "hero": {
        "h1": "Paver Walk and Landing Projects in Sheridan, <em>Arkansas</em>",
        "sub": "A paver landing at the front door and a paver walk around the side of the house, built by the Amanda's Villa hardscape teams for a Sheridan home.",
        "wide": ("hero-paver-walk-around-corner-wide", "A new paver walk with a dark border turning the corner of a brick house toward a green Sheridan lawn, built by Amanda's Villa"),
        "tall": ("hero-paver-walk-long-view-tall",),
    },
    "work_h2": "Examples of our work in Sheridan",
    "work_intro": "Both of these were built by the Amanda's Villa hardscape teams at one home in Sheridan. Use the arrows to compare each before and after.",
    "tiers": [
        {"title": "Hardscape",
         "text": "Walks, landings and stonework, built by the Amanda's Villa hardscape teams.",
         "link": ("hardscape/", "More about hardscape at Amanda's Villa"),
         "jobs": [
             {"title": "A paver landing at the front door",
              "text": "The patch of worn grass in front of the concrete stoop became a paver landing with a dark border.",
              "photos": [("landing-1-before", "Before: grass at the front door"), ("landing-2-finished", "Finished paver landing")]},
             {"title": "A paver walk around the side of the house",
              "text": "An old path along the hedge and a torn-out bed along the side of the house were replaced by a paver walk with a dark border, set on gravel, that turns the corner of the house toward the driveway.",
              "photos": [
                  ("side-walk-1-before-old-path", "Before: old path along the hedge"), ("side-walk-2-before-bed-torn-out", "Before: old bed torn out along the side"),
                  ("side-walk-3-finished-around-corner", "Finished walk around the corner"), ("side-walk-4-finished-along-hedge", "Finished walk along the hedge"),
                  ("side-walk-5-finished-toward-drive", "Finished walk toward the driveway"), ("side-walk-6-finished-long-view", "Finished walk, long view")]},
         ]},
    ],
    "sales": {
        "h2": "Let's build you a Sheridan yard that stays dry and looks finished",
        "paras": [
            f"Sheridan is the county seat of Grant County, which is known for its timber industry.{fn(3)} About four of every ten acres within a mile of downtown are Sacul soils, a sandy loam over a subsoil that is about half clay from roughly seven inches down, and about one acre in five is floodplain that floods often.{fn(2)} Arkansas averages about 50 inches of rain a year.{fn(1)}",
            "So your project starts with a free estimate and a transit survey of how your ground falls, and the drainage is planned before the stone and the plants.",
        ],
        "photo": ("sales-paver-walk-along-brick-house", "A paver walk with a dark border running along a brick house past a hedge at a Sheridan home"),
        "points": STANDARD_POINTS,
    },
    "services_h2": "What Amanda's Villa builds and plants for Sheridan homes",
    "services": SERVICES,
    "faq_h2": "Sheridan hardscaping questions",
    "faq": [
        ("Has Amanda's Villa done work in Sheridan?",
         "Yes. The paver landing and the side walk on this page are at a Sheridan home, and the teams work all over the state of Arkansas."),
        ("What does Sheridan's soil mean for a walk or patio?",
         f"About four of every ten acres within a mile of downtown Sheridan are Sacul soils, with a subsoil that is about half clay from roughly seven inches down.{fn(2, 'b')} So every walk and patio sits on a compacted gravel base, and drainage is planned before anything is planted."),
        ("How long does a project take?",
         "It depends on the project. The front landing on this page was finished five days after its before photo. Once work begins, the crew stays on your project until it is finished, and weather is the only common delay."),
        ask_free_estimate(),
    ],
    "closing": {
        "h2": "Book a free estimate for your Sheridan yard",
        "text": "Your project starts with a walk around your yard. Schedule a free estimate, and the team will plan the drainage, stonework and planting for your Sheridan home.",
        "photo": "closing-paver-landing-front-door",
    },
    "cites": [
        NOAA_CITE,
        "USDA Natural Resources Conservation Service, Soil Survey Geographic Database (SSURGO), Grant County, Arkansas, accessed through Soil Data Access, October 2026. Of the soils mapped within about a mile of downtown Sheridan, Sacul gravelly fine sandy loam and Sacul fine sandy loam, about 43 percent of the area, list a subsoil of about 50 percent clay from about 7 to 31 inches. The frequently flooded Ouachita, Guyton, Bibb and Sardis soils cover about 21 percent.",
        "CALS Encyclopedia of Arkansas, “Sheridan (Grant County).”",
    ],
}

TOWNS = [STAR_CITY, WHITE_HALL, WOODLAWN, HOT_SPRINGS, PINE_BLUFF, SHERIDAN]

# The /projects/ hub: one card per town, in alphabetical order. (slug, town, card photo, alt, what's there)
HUB_CARDS = [
    ("hot-springs", "Hot Springs", "A round block retaining wall and steps on a wooded Hot Springs hillside",
     "Curved retaining walls, block steps, a raised terrace and boulder steps on a hillside."),
    ("pine-bluff", "Pine Bluff", "A red brick herringbone path between new planted beds in Pine Bluff",
     "A herringbone brick path and patio with new beds on both sides."),
    ("sheridan", "Sheridan", "A paver walk with a dark border along a brick house in Sheridan",
     "A paver landing at the front door and a paver walk around the house."),
    ("star-city", "Star City", "A curved paver walk with a river rock bed beside a Star City home",
     "New flower beds, a curved paver walk, a flagstone walk and a French drain."),
    ("white-hall", "White Hall", "Two curved flower beds framing the front walk of a White Hall home",
     "Four sets of new flower beds, close to the garden center."),
    ("woodlawn", "Woodlawn", "Block walls, wide steps and planted beds across a Woodlawn farmhouse front",
     "A curved bed with a flagstone walk, and farmhouse walls, steps and a paver walk."),
]


def hub():
    cards = "\n".join(f"""      <article class="town-card">
        <a href="{slug}/">
          <img width="800" height="600" src="../img/projects/{slug}/card.jpg" alt="{e(alt)}" loading="lazy">
          <h3>{e(town)}</h3>
          <p>{e(text)}</p>
          <span class="link">See the work in {e(town)}</span>
        </a>
      </article>""" for slug, town, alt, text in HUB_CARDS)
    p = "../"
    head = head_styles().replace("../../", "../")  # the hub sits one folder deep, not two
    foot = tail().replace("../../", "../")
    return f"""<!doctype html>
<html lang="en">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-YDMETHXQC0"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', 'G-YDMETHXQC0');
</script>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Our Work: Landscaping and Hardscaping Projects Across Arkansas | Amanda's Villa</title>
<meta name="description" content="Finished Amanda's Villa projects, town by town: flower beds, paver and flagstone walks, patios, retaining walls and French drains, each photographed from start to finish.">
{head}
{TOWN_CSS}
</head>
<body>

<header class="hero">
  <div class="hero-card">
    <picture>
      <source media="(max-width: 640px)" srcset="{p}img/projects/hero-our-work-tall.jpg">
      <img width="1800" height="1125" src="{p}img/projects/hero-our-work-wide.jpg" alt="Wide block steps rising to a paver landing at a farmhouse porch, between a curved block wall and planted beds, built by Amanda's Villa" fetchpriority="high">
    </picture>
    <nav class="nav" aria-label="Main"></nav>
    <div class="hero-copy">
      <h1>Landscaping and Hardscaping Projects Across <em>Arkansas</em></h1>
      <p class="hero-sub">Flower beds, walks, patios, retaining walls and French drains, planted and built by Amanda's Villa for homes all over the state.</p>
      <div class="hero-ctas">
        <a class="btn btn--onphoto" href="{p}contact/#estimate">Request a free estimate</a>
        <a class="btn btn--ghost" href="{TEL}">Call {PHONE}</a>
      </div>
      <p class="hero-meta"><a href="#towns">Our work, town by town</a> · Free estimates</p>
    </div>
  </div>
</header>

<main>

<section class="band" id="towns">
  <div class="wrap">
    <div class="head">
      <h2>Our work, town by town</h2>
      <p>Every job here was photographed by the Amanda's Villa teams, from the first day to the finished yard. Pick a town to walk through each one.</p>
    </div>
    <div class="town-grid">
{cards}
    </div>
  </div>
</section>

<section class="band closing closing--photo">
  <img width="1200" height="900" src="{p}img/projects/closing-our-work.jpg" alt="" loading="lazy">
  <div class="wrap">
    <h2>Book a free estimate for your yard</h2>
    <p>Your project starts with a walk around your yard. Schedule a free estimate, and Amanda's Villa will plan the drainage, stonework and planting for your home.</p>
    {ctas().replace(P, p)}
  </div>
</section>

{foot}"""


def build():
    with open(os.path.join(ROOT, "projects", "index.html"), "w", encoding="utf-8") as f:
        f.write(hub())
    site_nav.apply("projects/")
    print("built: projects/")
    for t in TOWNS:
        rel = f"projects/{t['slug']}/"
        os.makedirs(os.path.join(ROOT, rel), exist_ok=True)
        with open(os.path.join(ROOT, rel, "index.html"), "w", encoding="utf-8") as f:
            f.write(page(t))
        site_nav.apply(rel)
        print("built:", rel)


if __name__ == "__main__":
    build()
