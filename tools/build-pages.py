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
<symbol id="i-amphora" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2v5.632c0 .424-.272.795-.653.982A6 6 0 0 0 6 14c.006 4 3 7 5 8" /> <path d="M10 5H8a2 2 0 0 0 0 4h.68" /> <path d="M14 2v5.632c0 .424.272.795.652.982A6 6 0 0 1 18 14c0 4-3 7-5 8" /> <path d="M14 5h2a2 2 0 0 1 0 4h-.68" /> <path d="M18 22H6" /> <path d="M9 2h6" /></g></symbol>
<symbol id="i-bird" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 7h.01" /> <path d="M3.4 18H12a8 8 0 0 0 8-8V7a4 4 0 0 0-7.28-2.3L2 20" /> <path d="m20 7 2 .5-2 .5" /> <path d="M10 18v3" /> <path d="M14 17.75V21" /> <path d="M7 18a6 6 0 0 0 3.84-10.61" /></g></symbol>
<symbol id="i-brick-wall" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" /> <path d="M12 9v6" /> <path d="M16 15v6" /> <path d="M16 3v6" /> <path d="M3 15h18" /> <path d="M3 9h18" /> <path d="M8 15v6" /> <path d="M8 3v6" /></g></symbol>
<symbol id="i-carrot" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 16a1 1 0 0 0-7-7q-4 4-5.987 12.385a.5.5 0 0 0 .602.602Q11 20 15 16l-3-3" /> <path d="M15 9q4 4 7 0-3-4-7 0 4-4 0-7-4 3 0 7" /> <path d="m8 15-2.58-2.58" /></g></symbol>
<symbol id="i-cherry" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 17a5 5 0 0 0 10 0c0-2.76-2.5-5-5-3-2.5-2-5 .24-5 3Z" /> <path d="M12 17a5 5 0 0 0 10 0c0-2.76-2.5-5-5-3-2.5-2-5 .24-5 3Z" /> <path d="M7 14c3.22-2.91 4.29-8.75 5-12 1.66 2.38 4.94 9 5 12" /> <path d="M22 9c-4.29 0-7.14-2.33-10-7 5.71 0 10 4.67 10 7Z" /></g></symbol>
<symbol id="i-citrus" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.66 17.67a1.08 1.08 0 0 1-.04 1.6A12 12 0 0 1 4.73 2.38a1.1 1.1 0 0 1 1.61-.04z" /> <path d="M19.65 15.66A8 8 0 0 1 8.35 4.34" /> <path d="m14 10-5.5 5.5" /> <path d="M14 17.85V10H6.15" /></g></symbol>
<symbol id="i-cooking-pot" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h20" /> <path d="M20 12v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8" /> <path d="m4 8 16-4" /> <path d="m8.86 6.78-.45-1.81a2 2 0 0 1 1.45-2.43l1.94-.48a2 2 0 0 1 2.43 1.46l.45 1.8" /></g></symbol>
<symbol id="i-feather" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.086 18.412A2 2 0 0112.67 19H5v-7.672a2 2 0 01.586-1.414L11.75 3.75a6 6 0 118.49 8.49z" /> <path d="M16 8 2 22" /> <path d="M17.488 15H9" /></g></symbol>
<symbol id="i-flower" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3" /> <path d="M12 16.5A4.5 4.5 0 1 1 7.5 12 4.5 4.5 0 1 1 12 7.5a4.5 4.5 0 1 1 4.5 4.5 4.5 4.5 0 1 1-4.5 4.5" /> <path d="M12 7.5V9" /> <path d="M7.5 12H9" /> <path d="M16.5 12H15" /> <path d="M12 16.5V15" /> <path d="m8 8 1.88 1.88" /> <path d="M14.12 9.88 16 8" /> <path d="m8 16 1.88-1.88" /> <path d="M14.12 14.12 16 16" /></g></symbol>
<symbol id="i-flower-2" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5a3 3 0 1 1 3 3m-3-3a3 3 0 1 0-3 3m3-3v1M9 8a3 3 0 1 0 3 3M9 8h1m5 0a3 3 0 1 1-3 3m3-3h-1m-2 3v-1" /> <circle cx="12" cy="8" r="2" /> <path d="M12 10v12" /> <path d="M12 22c4.2 0 7-1.667 7-5-4.2 0-7 1.667-7 5Z" /> <path d="M12 22c-4.2 0-7-1.667-7-5 4.2 0 7 1.667 7 5Z" /></g></symbol>
<symbol id="i-footprints" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 16v-2.38C4 11.5 2.97 10.5 3 8c.03-2.72 1.49-6 4.5-6C9.37 2 10 3.8 10 5.5c0 3.11-2 5.66-2 8.68V16a2 2 0 1 1-4 0Z" /> <path d="M20 20v-2.38c0-2.12 1.03-3.12 1-5.62-.03-2.72-1.49-6-4.5-6C14.63 6 14 7.8 14 9.5c0 3.11 2 5.66 2 8.68V20a2 2 0 1 0 4 0Z" /> <path d="M16 17h4" /> <path d="M4 13h4" /></g></symbol>
<symbol id="i-hexagon" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" /></g></symbol>
<symbol id="i-layers" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z" /> <path d="M2 12a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 12" /> <path d="M2 17a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 17" /></g></symbol>
<symbol id="i-mountain-snow" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m8 3 4 8 5-5 5 15H2L8 3z" /> <path d="M4.14 15.08c2.62-1.57 5.24-1.43 7.86.42 2.74 1.94 5.49 2 8.23.19" /></g></symbol>
<symbol id="i-palette" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22a1 1 0 0 1 0-20 10 9 0 0 1 10 9 5 5 0 0 1-5 5h-2.25a1.75 1.75 0 0 0-1.4 2.8l.3.4a1.75 1.75 0 0 1-1.4 2.8z" /> <circle cx="13.5" cy="6.5" r=".5" fill="currentColor" /> <circle cx="17.5" cy="10.5" r=".5" fill="currentColor" /> <circle cx="6.5" cy="12.5" r=".5" fill="currentColor" /> <circle cx="8.5" cy="7.5" r=".5" fill="currentColor" /></g></symbol>
<symbol id="i-shapes" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.3 10a.7.7 0 0 1-.626-1.079L11.4 3a.7.7 0 0 1 1.198-.043L16.3 8.9a.7.7 0 0 1-.572 1.1Z" /> <rect x="3" y="14" width="7" height="7" rx="1" /> <circle cx="17.5" cy="17.5" r="3.5" /></g></symbol>
<symbol id="i-tree-deciduous" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 19a4 4 0 0 1-2.24-7.32A3.5 3.5 0 0 1 9 6.03V6a3 3 0 1 1 6 0v.04a3.5 3.5 0 0 1 3.24 5.65A4 4 0 0 1 16 19Z" /> <path d="M12 19v3" /></g></symbol>
<symbol id="i-tree-palm" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 8c0-2.76-2.46-5-5.5-5S2 5.24 2 8h2l1-1 1 1h4" /> <path d="M13 7.14A5.82 5.82 0 0 1 16.5 6c3.04 0 5.5 2.24 5.5 5h-3l-1-1-1 1h-3" /> <path d="M5.89 9.71c-2.15 2.15-2.3 5.47-.35 7.43l4.24-4.25.7-.7.71-.71 2.12-2.12c-1.95-1.96-5.27-1.8-7.42.35" /> <path d="M11 15.5c.5 2.5-.17 4.5-1 6.5h4c2-5.5-.5-12-1-14" /></g></symbol>
<symbol id="i-tree-pine" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m17 14 3 3.3a1 1 0 0 1-.7 1.7H4.7a1 1 0 0 1-.7-1.7L7 14h-.3a1 1 0 0 1-.7-1.7L9 9h-.2A1 1 0 0 1 8 7.3L12 3l4 4.3a1 1 0 0 1-.8 1.7H15l3 3.3a1 1 0 0 1-.7 1.7H17Z" /> <path d="M12 22v-3" /></g></symbol>
<symbol id="i-waves" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12q2.5 2 5 0t5 0 5 0 5 0" /> <path d="M2 19q2.5 2 5 0t5 0 5 0 5 0" /> <path d="M2 5q2.5 2 5 0t5 0 5 0 5 0" /></g></symbol>
<symbol id="i-wheat" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 22 16 8" /> <path d="M3.47 12.53 5 11l1.53 1.53a3.5 3.5 0 0 1 0 4.94L5 19l-1.53-1.53a3.5 3.5 0 0 1 0-4.94Z" /> <path d="M7.47 8.53 9 7l1.53 1.53a3.5 3.5 0 0 1 0 4.94L9 15l-1.53-1.53a3.5 3.5 0 0 1 0-4.94Z" /> <path d="M11.47 4.53 13 3l1.53 1.53a3.5 3.5 0 0 1 0 4.94L13 11l-1.53-1.53a3.5 3.5 0 0 1 0-4.94Z" /> <path d="M20 2h2v2a4 4 0 0 1-4 4h-2V6a4 4 0 0 1 4-4Z" /> <path d="M11.47 17.47 13 19l-1.53 1.53a3.5 3.5 0 0 1-4.94 0L5 19l1.53-1.53a3.5 3.5 0 0 1 4.94 0Z" /> <path d="M15.47 13.47 17 15l-1.53 1.53a3.5 3.5 0 0 1-4.94 0L9 15l1.53-1.53a3.5 3.5 0 0 1 4.94 0Z" /> <path d="M19.47 9.47 21 11l-1.53 1.53a3.5 3.5 0 0 1-4.94 0L13 11l1.53-1.53a3.5 3.5 0 0 1 4.94 0Z" /></g></symbol>
"""

LOT_CSS = """<style id="lot-items">
/* What's on the lot: icon cards, three across, two across on phones */
.head--center { text-align: center; }
.head--center p { margin-left: auto; margin-right: auto; }
.lot-items { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-10) var(--space-6); }
.lot-items li { display: flex; flex-direction: column; align-items: center; text-align: center; gap: 6px; }
.lot-items .ic-badge { width: 64px; height: 64px; margin-bottom: var(--space-2); }
.lot-items .ic { width: 28px; height: 28px; }
.lot-items h3 { font: 400 22px/1.25 var(--font-text-serif); color: var(--ink); margin: 0; }
.lot-items i { font: italic 400 17px/1.35 var(--font-text-serif); color: var(--stone); }
.lot-items p { margin: 0; max-width: 30ch; color: var(--ink-3); font-size: 16px; line-height: 1.5; }
.note--center { text-align: center; margin-top: var(--space-10); }
@media (max-width: 640px) {
  .lot-items { grid-template-columns: 1fr 1fr; gap: var(--space-10) var(--space-4); }
  .lot-items .ic-badge { width: 56px; height: 56px; }
  .lot-items .ic { width: 24px; height: 24px; }
  .lot-items h3 { font-size: 19px; }
  .lot-items i { font-size: 15px; }
  .lot-items p { font-size: 15px; }
}
</style>"""


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


SPLIT_HERO_CSS = '<style>\n/* ---------- Hero: copy on the green panel beside the photo on desktop, below it on phones ---------- */\n@media (min-width: 641px) {\n  .hero-card { background: var(--forest-deep); }\n  .hero-card > picture { left: auto; right: 0; width: 62%; }\n  .hero-card > picture img { object-position: {pos}; -webkit-mask-image: linear-gradient(90deg, transparent 0%, #000 28%); mask-image: linear-gradient(90deg, transparent 0%, #000 28%); }\n  .hero-card::before { background: linear-gradient(180deg, rgba(14,22,18,.55) 0%, rgba(14,22,18,0) 20%); }\n  .hero-copy { align-items: flex-start; text-align: left; justify-content: center; width: 50%; padding: var(--space-10) var(--space-10) var(--space-16) calc(var(--space-10) + var(--space-6)); }\n  .hero h1 { font-size: 54px; max-width: 10.5em; }\n  .hero-sub { max-width: 24em; }\n  .hero-meta { max-width: 28em; line-height: 1.7; }\n  .hero-ctas .btn--onphoto { background: var(--on-forest); color: var(--forest-deep); border-color: var(--on-forest); }\n  .hero-ctas .btn--onphoto:hover { background: #fff; border-color: #fff; }\n}\n@media (max-width: 640px) {\n  .hero-card { min-height: 0; background: var(--forest-deep); }\n  .hero-card > picture { position: relative; inset: auto; display: block; aspect-ratio: 4 / 5; }\n  .hero-card > picture img { object-position: center 30%; -webkit-mask-image: linear-gradient(180deg, #000 78%, transparent); mask-image: linear-gradient(180deg, #000 78%, transparent); }\n  .hero-card .nav { position: absolute; top: 0; left: 0; right: 0; z-index: 2; }\n  .hero-card::before { background: linear-gradient(180deg, rgba(14,22,18,.55) 0%, rgba(14,22,18,0) 14%); }\n  .hero-copy { margin-top: -48px; padding-top: 0; }\n  .hero-card .btn--onphoto { background: var(--on-forest); color: var(--forest-deep); border-color: var(--on-forest); }\n}\n</style>'


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
<title>{esc(d["title"])}</title>
<meta name="description" content="{esc(d["description"])}">
{HEAD_STYLE}
{LOT_CSS}
{SPLIT_HERO_CSS.replace("{pos}", hero["split"]) if hero.get("split") else ""}
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
        cards = "\n".join(
            f"      <li>{icon(i)}<h3>{n}</h3>{f'<i>{l}</i>' if l else ''}<p>{d}</p></li>" for i, n, l, d in items)
        figs = "\n".join(f"      <figure>{img(p, src, a, w, h)}<figcaption>{c}</figcaption></figure>" for src, a, w, h, c in photos)
        return f"""<!-- ON THE LOT -->
<section class="band{' band--alt' if alt else ''}">
  <div class="wrap">
    <div class="head head--center">
      <h2>{h2}</h2>
      <p>{intro}</p>
    </div>
    <ul class="lot-items">
{cards}
    </ul>
    <p class="note note--center">{note}</p>
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
            [("tree-deciduous", "Japanese maple", "Acer palmatum", "Specimen trees for a front bed or a shady corner."),
             ("tree-pine", "Italian cypress", "Cupressus sempervirens", "Tall, narrow evergreens for a formal line along a drive or a fence."),
             ("leaf", "Coleus", "Plectranthus scutellarioides", "Bright leaves for shade and part shade."),
             ("flower", "Garden mums", "Chrysanthemum", "Potted fall mums in rows across the nursery yard."),
             ("flower-2", "Pansies and violas", "Viola", "Cool-season color for fall beds and planters."),
             ("tree-palm", "Banana plants and elephant ears", "Musa, Colocasia", "Big tropical leaves for a bold summer bed.")],
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
             ("shovel", "Plant it", "Take your plants home, or have Amanda's crew plant them for you.")],
            VISIT),
        split_prose(
            "SUCCESS AND FAILURE",
            "A yard that fills in a little more every year",
            ["Picture a Japanese maple turning red by the front walk, a row of cypress along the drive, and beds that are still green in August. Every plant was chosen for the light it has, so the yard keeps growing.",
             "Each spring the yard has a little more to show. Shrubs fill out the space they were planted for, the evergreens hold their color through winter, and pansies and mums brighten the beds when the summer flowers fade.",
             "Before long the front yard is the first thing friends mention when they visit, and the back porch is the favorite seat on a warm evening.",
             "Choosing for the light from the start is what keeps a yard growing year after year, with fewer plants to replace each spring."],
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
            [("waves", "River rock", "", "Smooth, rounded stone for beds, borders and around plantings."),
             ("layers", "Fieldstone", "", "Rough, flat-sided pieces for borders and low stacked edges."),
             ("footprints", "Flagstone", "", "Flat slabs for stepping stones, paths and patios."),
             ("mountain", "Landscape boulders", "", "Large accent stones for a bed, a corner or a hillside."),
             ("mountain-snow", "Granite and Ozark Mountain rock", "", "Arkansas stone for borders, accents and walls."),
             ("brick-wall", "Pavers", "", "For a patio or a walkway, or ask the hardscape teams to lay them.")],
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
        img="garden-center/hero-woman-choosing-terracotta-pot",
        alt="A woman choosing a terracotta pot from the shelves of a garden center",
        split="88% center",
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
            [("flower-2", "Clay and glazed ceramic pots", "", "From a three-inch pot for a windowsill up to large outdoor planters."),
             ("palette", "Talavera pottery", "", "Hand-painted pots and pieces in bright colors."),
             ("feather", "Aluminum planters", "", "Light, weatherproof planters for a porch or patio."),
             ("amphora", "Concrete urns and planters", "", "Heavy, classic planters for an entry or a garden bed."),
             ("bird", "Bird baths and fountains", "", "A focal point for a bed, and a stop for the birds."),
             ("shapes", "Garden statues and yard art", "", "Statues, metal frogs and butterflies, hummingbird feeders, Razorback signs and seasonal decor.")],
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
        img="garden-center/hero-couple-shopping-gourds-at-market",
        alt="A smiling couple choosing squash at a covered produce stand",
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
            [("cherry", "Tomatoes", "", "Farm-raised and red all the way through, sold by the basket."),
             ("citrus", "Watermelons", "", "On the produce table while the season lasts."),
             ("carrot", "Onions and pickling cucumbers", "", "Yellow onions by the pile and pickling cucumbers kept cold."),
             ("wheat", "Pumpkins and winter squash", "", "Heirloom pumpkins, blue Hubbard, butternut and gourds every fall."),
             ("hexagon", "Local honey", "", "Jars from an Arkansas beekeeper."),
             ("cooking-pot", "Jams, jellies and chow-chow", "", "From Ozark Mountain, an Amish family in north-central Arkansas, made with no preservatives.")],
            "Call ahead to ask what came in this week.",
            [("garden-center/jams-jellies-and-preserves-shelves-amandas-villa.jpg", "Shelves of jams, jellies and preserves at the Amanda's Villa produce stand", 1100, 825, "Jams, jellies and chow-chow"),
             ("produce-honey-amandas-villa.jpg", "Jars of local honey at the Amanda's Villa produce stand", 1100, 825, "Local honey"),
             ("garden-center/yellow-onions-amandas-villa.jpg", "A pile of yellow onions for sale at the Amanda's Villa produce stand", 1031, 1375, "Yellow onions")]),
        plan(
            "How to stock the kitchen with Arkansas food",
            ("garden-center/cash-register-produce-stand-wide-amandas-villa.jpg", "The antique brass cash register on the counter of the Amanda's Villa produce stand", 1100, 825),
            [("store", "Stop by the stand", "Come to 7901 Dollarway Road in White Hall. The produce stand sits beside the garden center."),
             ("leaf", "Pick what's in season", "Tomatoes, melons, squash or whatever came in this week, plus honey and preserves."),
             ("house", "Bring it home to the table", "Cook something that tastes like Arkansas.")],
            ("Visit the produce stand", "~/contact/#directions")),
        split_prose(
            "SUCCESS AND FAILURE",
            "Tomatoes that taste like a summer garden",
            ["Picture a tomato sandwich with slices that are red all the way through, chow-chow on the beans and honey on a warm biscuit. Every jar and basket came from Arkansas hands.",
             "Without a stand like this, too many kitchens settle for produce picked early and shipped a long way."],
            ("garden-center/preserves-above-fresh-tomatoes-amandas-villa.jpg", "Jars of Ozark Mountain preserves on wooden shelves above fresh tomatoes at the Amanda's Villa produce stand", 1100, 1375),
            alt=True, flip=False),
        split_prose(
            "EXPLANATORY PARAGRAPH",
            "A farm stand with Arkansas produce, local honey and chow-chow",
            ["Many Arkansas families want produce that tastes fresh, but too much of what's in the grocery store was picked early and shipped in. Amanda's Villa runs a produce stand on Dollarway Road in White Hall with farm-raised Arkansas tomatoes and seasonal produce, local honey, and Amish jams, jellies and chow-chow.",
             "Stop by, pick what's in season, and bring home food that keeps money in Arkansas."],
            ("garden-center/blue-hubbard-squash-and-gourds-amandas-villa.jpg", "Blue Hubbard squash, butternut and ornamental gourds on straw at the Amanda's Villa produce stand", 1100, 825),
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
    import site_nav  # same folder; keeps the menu and footer in step with every other page
    site_nav.apply_all()
