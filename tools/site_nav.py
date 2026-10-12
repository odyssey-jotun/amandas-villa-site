#!/usr/bin/env python3
"""One menu and footer for every built page.

Run from the repo root:  python3 tools/site_nav.py
(tools/build-pages.py also runs it after generating its pages.)

To add a page to the Garden Center dropdown once it's built, add it to
GARDEN_CENTER below and run this script. Under-construction pages stay out
of the menu on purpose.
"""
import os
import re

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

PHONE = "(870) 489-5463"
TEL = "tel:+18704895463"

# Folder paths, relative to the site root
TOP = [("landscaping/", "Landscaping"), ("hardscape/", "Hardscape"), ("garden-center/", "Garden Center"),
       ("about/", "About"), ("contact/", "Contact")]
GARDEN_CENTER = [
    ("garden-center/plants-shrubs-trees/", "Plants, shrubs and trees"),
    ("garden-center/landscaping-stone/", "Landscaping stone"),
    ("garden-center/pottery-decor/", "Pottery and garden decor"),
    ("garden-center/produce/", "Arkansas produce"),
]

# Every page that carries the full menu
PAGES = ["", "landscaping/", "hardscape/", "garden-center/", "about/", "contact/"] + [u for u, _ in GARDEN_CENTER]

CSS = """<style id="site-nav">
/* Menu: Garden Center dropdown, Contact tab, phone menu sub-items, four-column footer.
   Written by tools/site_nav.py; edit there, not here. */
.nav-links .nav-drop { display: block; position: relative; }
.nav-links a, .nav-drop summary, .nav .btn--onphoto, .nav .wordmark span { white-space: nowrap; }
.nav-drop summary { list-style: none; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; color: var(--on-forest); font: 600 13px/1 var(--font-body); letter-spacing: .2em; text-transform: uppercase; padding: 4px 0; }
.nav-drop summary::-webkit-details-marker { display: none; }
.nav-drop summary::after { content: ""; width: 6px; height: 6px; border-right: 1.5px solid currentColor; border-bottom: 1.5px solid currentColor; transform: translateY(-2px) rotate(45deg); transition: transform .15s; }
.nav-drop[open] summary::after { transform: translateY(1px) rotate(-135deg); }
.nav-drop summary:hover { color: #fff; }
.nav-drop.is-current summary { border-bottom: 1px solid var(--clay-light); padding-bottom: 4px; }
.nav-drop ul { position: absolute; top: calc(100% + 16px); left: 50%; transform: translateX(-50%); z-index: 5; list-style: none; margin: 0; padding: 8px 0; min-width: 260px; background: var(--linen); border-radius: 14px; box-shadow: 0 20px 44px -20px rgba(14,22,18,.6); }
.nav-drop ul li + li { margin-top: 0; }
.nav-drop ul li:first-child { border-bottom: 1px solid var(--line); margin-bottom: 6px; padding-bottom: 6px; }
.nav-links .nav-drop ul a { display: block; padding: 10px 22px; color: var(--ink); font: 600 16px/1.3 var(--font-body); letter-spacing: 0; text-transform: none; border: 0; }
.nav-links .nav-drop ul a:hover { background: var(--sage-pale); color: var(--forest-deep); }
.nav-links .nav-drop ul a[aria-current] { color: var(--forest); background: var(--sage-pale); padding-bottom: 10px; }
.nav details ul a.sub { padding-left: 16px; font-weight: 400; }
.foot-grid { grid-template-columns: 1.4fr 1fr 1fr 1fr; }
.foot ul { align-content: start; }
@media (max-width: 1440px) { .nav-links { gap: 28px; } }
/* The full row needs about 1250px; below that, the Menu button takes over and Call stays visible */
@media (max-width: 1279px) {
  .nav-links { display: none; }
  .nav details { display: block; position: relative; }
  .nav summary { list-style: none; cursor: pointer; font: 600 13px/1 var(--font-body); letter-spacing: .2em; text-transform: uppercase; padding: 12px 0 12px 12px; }
  .nav summary::-webkit-details-marker { display: none; }
  .nav details ul { position: absolute; right: 0; top: 100%; z-index: 3; list-style: none; margin: 0; padding: var(--space-4); background: var(--linen); border-radius: var(--radius-sm); min-width: 240px; display: grid; gap: var(--space-2); }
  .nav details a { color: var(--ink); text-decoration: none; font-weight: 600; display: block; padding: 8px 0; }
  .nav { gap: var(--space-4); }
  .nav .btn--onphoto { margin-left: auto; }
}
@media (max-width: 900px) { .foot-grid { grid-template-columns: 1fr; } }
</style>"""

JS = """<script id="site-nav-js">
// Close the Garden Center dropdown on an outside click or Escape.
(function () {
  var drops = document.querySelectorAll('.nav-drop');
  document.addEventListener('click', function (e) {
    drops.forEach(function (d) { if (d.open && !d.contains(e.target)) d.open = false; });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') drops.forEach(function (d) { if (d.open) { d.open = false; d.querySelector('summary').focus(); } });
  });
})();
</script>"""


def prefix_for(page):
    depth = page.count("/")
    return "../" * depth


def nav_html(page):
    p = prefix_for(page)
    home = p or "./"
    cur = ' aria-current="page"'
    in_gc = page.startswith("garden-center/")

    links = []
    for u, t in TOP:
        if u == "garden-center/":
            items = [(u, "Garden Center overview")] + GARDEN_CENTER
            sub = "\n".join(
                f'            <li><a href="{p}{su}"{cur if su == page else ""}>{st}</a></li>' for su, st in items)
            links.append(f"""        <li>
          <details class="nav-drop{' is-current' if in_gc else ''}">
            <summary>Garden Center</summary>
            <ul>
{sub}
            </ul>
          </details>
        </li>""")
        else:
            links.append(f'        <li><a href="{p}{u}"{cur if u == page else ""}>{t}</a></li>')

    menu = []
    for u, t in TOP:
        menu.append(f'          <li><a href="{p}{u}">{t}</a></li>')
        if u == "garden-center/":
            menu += [f'          <li><a class="sub" href="{p}{su}">{st}</a></li>' for su, st in GARDEN_CENTER]
    menu.append(f'          <li><a href="{TEL}">Call {PHONE}</a></li>')

    links_s = "\n".join(links)
    menu_s = "\n".join(menu)
    return f"""<nav class="nav" aria-label="Main">
      <a class="wordmark" href="{home}"{cur if page == "" else ""}><b>Amanda's Villa</b><span>Landscaping · Hardscape · Garden Center</span></a>
      <ul class="nav-links">
{links_s}
      </ul>
      <a class="btn btn--onphoto" href="{TEL}">Call {PHONE}</a>
      <details>
        <summary>Menu</summary>
        <ul>
{menu_s}
        </ul>
      </details>
    </nav>"""


def footer_html(page):
    p = prefix_for(page)
    home = p or "./"
    site = "\n".join(f'        <li><a href="{p}{u}">{t}</a></li>' for u, t in TOP)
    gc = "\n".join(f'        <li><a href="{p}{u}">{t}</a></li>' for u, t in GARDEN_CENTER)
    return f"""<footer class="foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="wordmark" href="{home}"><b>Amanda's Villa</b><span>Landscaping · Hardscape · Garden Center · White Hall, Arkansas</span></a>
        <p class="foot-tag">Together, plant the space your yard deserves.</p>
      </div>
      <ul>
{site}
      </ul>
      <ul>
{gc}
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


def apply(page):
    path = os.path.join(ROOT, page, "index.html")
    s = open(path, encoding="utf-8").read()
    s, n1 = re.subn(r'<nav class="nav" aria-label="Main">.*?</nav>', lambda m: nav_html(page), s, count=1, flags=re.S)
    s, n2 = re.subn(r'<footer class="foot">.*?</footer>', lambda m: footer_html(page), s, count=1, flags=re.S)
    s = re.sub(r'\n?<style id="site-nav">.*?</style>', "", s, flags=re.S)
    s = re.sub(r'\n?<script id="site-nav-js">.*?</script>', "", s, flags=re.S)
    s = s.replace("</head>", CSS + "\n</head>", 1)
    s = s.replace("</body>", JS + "\n</body>", 1)
    if not (n1 and n2):
        raise SystemExit(f"{page or 'home'}: menu or footer not found")
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)


def apply_all():
    for page in PAGES:
        apply(page)
        print("menu:", page or "home")


if __name__ == "__main__":
    apply_all()
