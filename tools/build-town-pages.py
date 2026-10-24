#!/usr/bin/env python3
"""Build the town portfolio pages under /projects/<town>/: one page per town where Amanda's Villa has finished work.

Run from the repo root:  python3 tools/build-town-pages.py

A town page is a portfolio first: its main content is the jobs Colton placed in that town
(see /job-photos/), grouped by category (Hardscape, Landscaping), each job with its own
carousel of every photo. Around the work sit one short sales section with the town's soil
facts, links to the service pages, a short FAQ and the closing call. Keep the shared copy
small so each page is mostly its own town's work.

Styles, scripts and the footer come from the French drain page; the menu and footer from
tools/site_nav.py. Town pages stay out of the menu. Write only what the photos, Colton's
October 5 interview and cited public sources support.

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
@media (max-width: 640px) {
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
    cards = []
    for i, (f, cap) in enumerate(job["photos"]):
        w, h = Image.open(os.path.join(ROOT, "img", "projects", slug, "portfolio", f + ".jpg")).size
        alt = f"{job['title']}: {cap}"
        cards.append(f'        <figure class="cf-card" data-i="{i}" data-title="{e(cap)}"><img draggable="false" width="{w}" height="{h}" '
                     f'src="{P}img/projects/{slug}/portfolio/{f}.jpg" alt="{e(alt)}" loading="lazy"></figure>')
    n = len(cards)
    return f"""      <div class="cf cf--steps cf--work" tabindex="0" role="region" aria-roledescription="carousel" aria-label="{e(job['title'])}, {n} photos">
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
    "description": "Four Amanda's Villa projects in Star City, Arkansas, photographed from start to finish: a French drain, a curved paver walk, a flagstone walk and new flower beds.",
    "hero": {
        "h1": "Landscaping and Hardscaping Projects in Star City, <em>Arkansas</em>",
        "sub": "A French drain, two new walks and a set of flower beds, built and planted by Amanda's Villa for Star City homes.",
        "wide": ("hero-curved-paver-walk-picket-gate-wide", "A curved paver walk running through a white picket fence gate beside a Star City home, built by the Amanda's Villa hardscape team"),
        "tall": ("hero-curved-paver-walk-river-rock-tall",),
    },
    "work_h2": "Examples of our work in Star City",
    "work_intro": "Each of these was built by the Amanda's Villa hardscape teams or planted by Amanda's crew at a home in Star City. Use the arrows to walk through each job from start to finish.",
    "tiers": [
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
    ],
    "sales": {
        "h2": "Let's build you a Star City yard that stays dry and looks finished",
        "paras": [
            f"Star City is the seat of Lincoln County, which Bayou Bartholomew splits between the Delta and the West Gulf Coastal Plain.{fn(3)} Under roughly seven of every ten acres in and around town, USDA soil maps show a seasonal water table within about two feet of the surface,{fn(2)} and Arkansas averages about 50 inches of rain a year.{fn(1)}",
            "So your project starts with a free estimate and a transit survey of how your ground falls, and the drainage is planned before the stone and the plants.",
        ],
        "photo": ("problem-side-yard-dug-out-downspout-lines", "A side yard dug out along a brick house in Star City, with downspout drain pipe laid along the foundation"),
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
         "Yes. The French drain, paver walk, flagstone walk and flower beds on this page are all at Star City homes, and the teams work all over the state of Arkansas."),
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
        "photo": "closing-dry-side-yard-after-drain",
    },
    "cites": [
        "NOAA National Centers for Environmental Information and the North Carolina Institute for Climate Studies, “Arkansas State Climate Summary,” 2022. Long-term statewide average of 50.1 inches of precipitation a year.",
        "USDA Natural Resources Conservation Service, Soil Survey Geographic Database (SSURGO), Lincoln County, Arkansas, accessed through Soil Data Access, October 2026. Of the soils mapped within about a mile of downtown Star City, the Savannah, Sawyer, Pheba and Amy soils, about 72 percent of the area, list a seasonal high water table 6 to 24 inches below the surface; Savannah fine sandy loam, about 29 percent, lists a fragipan at about 24 inches. The well-drained Smithdale and Ruston fine sandy loams cover about 17 percent.",
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
