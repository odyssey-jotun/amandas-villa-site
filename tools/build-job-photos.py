"""Build /job-photos/: every Amanda's Villa job photo on file, grouped by site (property) and project (job).

    python3 tools/build-job-photos.py                 # rewrite job-photos/index.html
    python3 tools/build-job-photos.py --prep <dir>    # also copy photos in from <dir>/<source id>.jpg

Edit SITES below, then rerun. Site and project numbers are ours, for talking it through with Colton.
Images in job-photos/img/ carry no EXIF (no GPS), so nothing on the page gives away a client's address.
"""
import html, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "job-photos")

COLTON = "Colton's phone"
FB = "Amanda's Facebook page"
DRONE_VIDEO = "Facebook drone video"

# (source id, label, date, caption). Source ids are the working copies made from the originals.
SITES = [
    {
        "desc": "Brick house with a wood privacy fence",
        "when": "June 3 to 6, 2025", "from": COLTON,
        "check": "Which town? This is the job on the French drain page.",
        "projects": [("French drain along the house and the fence line", [
            ("colton-drain--IMG_1240", "IMG_1240", "Jun 3, 2025", "Sod cut and rolled back along the drain line"),
            ("colton-drain--IMG_1246", "IMG_1246", "Jun 4, 2025", "Trench dug"),
            ("colton-drain--IMG_1252", "IMG_1252", "Jun 5, 2025", "Blue drain pipe in a fabric-lined trench beside the house"),
            ("colton-drain--IMG_1260", "IMG_1260", "Jun 5, 2025", "Gravel and a catch basin grate by the generator"),
            ("colton-drain--IMG_1265", "IMG_1265", "Jun 6, 2025", "Sod going back down along the fence"),
            ("colton-drain--IMG_1273", "IMG_1273", "Jun 6, 2025", "Finished, sod back along the fence"),
            ("colton-drain--IMG_1275", "IMG_1275", "Jun 6, 2025", "Finished, sod back beside the house"),
        ])],
    },
    {
        "desc": "White painted-brick house with a tall chimney",
        "when": "June 2025", "from": COLTON,
        "check": "Which town? Is IMG_3297 the finished walk? It has no date on file.",
        "projects": [("Curved front walk: flagstone set in gravel with a paver border", [
            ("colton-oct5--IMG_1493", "IMG_1493", "Jun 20, 2025", "Walk dug out to the porch"),
            ("colton-oct5--IMG_1516", "IMG_1516", "Jun 23, 2025", "Gravel base down, paver border set"),
            ("colton-oct5--IMG_3297", "IMG_3297", "No date on file", "Finished flagstone walk with the paver border"),
        ])],
    },
    {
        "desc": "Red brick house with a white picket fence",
        "when": "August to October 2025", "from": COLTON,
        "check": "Which town?",
        "projects": [("Curved paver side walk with downspout lines and a river rock bed", [
            ("colton-oct5--IMG_2314", "IMG_2314", "Aug 29, 2025", "Before: grass between the house and the fence"),
            ("colton-oct5--IMG_2388", "IMG_2388", "Sep 7, 2025", "Walk dug out, downspout lines going in"),
            ("colton-oct5--IMG_2665", "IMG_2665", "Oct 8, 2025", "Pavers going down"),
            ("colton-oct5--IMG_2696", "IMG_2696", "Oct 17, 2025", "Finished walk curving to the gate"),
            ("colton-oct5--IMG_2697", "IMG_2697", "Oct 17, 2025", "Finished walk and the river rock bed"),
            ("colton-oct5--IMG_2700", "IMG_2700", "Oct 17, 2025", "Finished walk through the gate"),
        ])],
    },
    {
        "desc": "Black board-and-batten farmhouse on open land",
        "when": "April to May 2026", "from": COLTON,
        "check": "Which town? Is 1000004878 (no date on file) this same house?",
        "projects": [("Raised paver walk, retaining walls, steps and new beds", [
            ("colton-oct5--IMG_4635", "IMG_4635", "Apr 20, 2026", "Before: front yard and porch"),
            ("colton-oct5--IMG_4639", "IMG_4639", "Apr 20, 2026", "Before: the beds by the garage"),
            ("colton-oct5--1000004878", "1000004878", "No date on file", "Ground dug out along the front beds, layout stakes in"),
            ("colton-oct5--IMG_4680", "IMG_4680", "Apr 23, 2026", "Wall going up beside the garage"),
            ("colton-oct5--IMG_4742", "IMG_4742", "Apr 30, 2026", "Wall and steps built, gravel fill"),
            ("colton-oct5--IMG_4770", "IMG_4770", "May 6, 2026", "Paver walk turning the corner by the garage"),
            ("colton-oct5--IMG_4771", "IMG_4771", "May 6, 2026", "Paver walk along the front beds"),
            ("colton-oct5--IMG_4772", "IMG_4772", "May 6, 2026", "Steps and landing at the porch"),
            ("colton-oct5--IMG_4774", "IMG_4774", "May 6, 2026", "Landing at the porch"),
            ("colton-oct5--IMG_4849", "IMG_4849", "May 18, 2026", "Finished: walls, steps and beds from the yard"),
            ("colton-oct5--IMG_4852", "IMG_4852", "May 18, 2026", "Finished: steps up to the porch"),
            ("colton-oct5--IMG_4855", "IMG_4855", "May 18, 2026", "Finished: walk between the beds"),
            ("colton-oct5--IMG_4856", "IMG_4856", "May 18, 2026", "Finished: landing at the porch"),
            ("colton-oct5--IMG_4857", "IMG_4857", "May 18, 2026", "Finished: curved walk and bed"),
            ("colton-oct5--IMG_4858", "IMG_4858", "May 18, 2026", "Finished: steps and the boulder bed"),
            ("colton-oct5--IMG_4861", "IMG_4861", "May 18, 2026", "Finished: raised wall by the garage"),
            ("colton-oct5--IMG_4862", "IMG_4862", "May 18, 2026", "Finished: long walk out toward the driveway"),
        ])],
    },
    {
        "desc": "Backyard with a brick garage and a white arbor",
        "when": "April to June 2026", "from": COLTON,
        "check": "Which town? Are the two April photos the same yard before the job?",
        "projects": [("Herringbone brick patio and paths with new beds", [
            ("colton-oct5--IMG_4506", "IMG_4506", "Apr 7, 2026", "Before: old brick edging along the house"),
            ("colton-oct5--IMG_4519", "IMG_4519", "Apr 7, 2026", "Before: the yard and the arbor by the garage"),
            ("colton-oct5--IMG_5256", "IMG_5256", "Jun 10, 2026", "Ground cleared, skid steer on site"),
            ("colton-oct5--IMG_5277", "IMG_5277", "Jun 12, 2026", "Base compacted"),
            ("colton-oct5--IMG_5287", "IMG_5287", "Jun 15, 2026", "Herringbone path started along the house"),
            ("colton-oct5--IMG_5297", "IMG_5297", "Jun 19, 2026", "Path and border laid"),
            ("colton-oct5--IMG_5305", "IMG_5305", "Jun 22, 2026", "Patio laid"),
            ("colton-oct5--IMG_5306", "IMG_5306", "Jun 22, 2026", "Patio and path by the garage"),
            ("colton-oct5--IMG_5329", "IMG_5329", "Jun 25, 2026", "Finished: path and new beds"),
            ("colton-oct5--IMG_5330", "IMG_5330", "Jun 25, 2026", "Finished: patio with the white chairs"),
            ("colton-oct5--IMG_5333", "IMG_5333", "Jun 25, 2026", "Finished: path between the planted beds"),
        ])],
    },
    {
        "desc": "Two-story brick house on a wooded lot",
        "when": "June to August 2026", "from": COLTON,
        "check": "Which town? Are the front landing and the side walk the same house, two separate jobs?",
        "projects": [
            ("Paver landing at the front door", [
                ("colton-oct5--IMG_5337", "IMG_5337", "Jun 25, 2026", "Before: grass at the front door"),
                ("colton-oct5--IMG_5376", "IMG_5376", "Jun 30, 2026", "Finished paver landing"),
            ]),
            ("Paver walk along the side of the house", [
                ("colton-oct5--IMG_5361", "IMG_5361", "Jun 29, 2026", "Before: old path along the hedge"),
                ("colton-oct5--IMG_5364", "IMG_5364", "Jun 29, 2026", "Before: old bed torn out along the side"),
                ("colton-oct5--IMG_5742", "IMG_5742", "Aug 6, 2026", "Finished walk around the corner"),
                ("colton-oct5--IMG_5745", "IMG_5745", "Aug 6, 2026", "Finished walk along the hedge"),
                ("colton-oct5--IMG_5756", "IMG_5756", "Aug 6, 2026", "Finished walk toward the driveway"),
                ("colton-oct5--IMG_5758", "IMG_5758", "Aug 6, 2026", "Finished walk, long view"),
            ]),
        ],
    },
    {
        "desc": "Wooded hillside lot with a brick house",
        "when": "July to October 2026", "from": "Colton's phone and the drone",
        "check": "Which town? Is this the Hot Springs hillside job? Are the July and August slope photos this site?",
        "projects": [("Hillside retaining walls, block steps, patio and boulder steps", [
            ("drive-oct8--IMG_5663", "IMG_5663", "Jul 28, 2026", "Before: bare slope by the fence"),
            ("drive-oct8--IMG_5797", "IMG_5797", "Aug 20, 2026", "Excavator grading the slope"),
            ("drive-oct8--drone-20261006-170824", "DJI 0328", "Oct 6, 2026", "Drone: walls, patio and beds from above"),
            ("drive-oct8--drone-20261006-171102", "DJI 0334", "Oct 6, 2026", "Drone: patio, steps and river rock"),
            ("drive-oct8--drone-20261006-171128", "DJI 0335", "Oct 6, 2026", "Drone: curved wall and steps"),
            ("drive-oct8--drone-20261006-171146", "DJI 0336", "Oct 6, 2026", "Drone: the round wall and the bed above it"),
            ("drive-oct8--IMG_6152", "IMG_6152", "Oct 7, 2026", "Block steps between two walls"),
            ("drive-oct8--IMG_6153", "IMG_6153", "Oct 7, 2026", "Curved wall and paver patio"),
            ("drive-oct8--IMG_6156", "IMG_6156", "Oct 7, 2026", "Wall corner and gravel"),
            ("drive-oct8--IMG_6157", "IMG_6157", "Oct 7, 2026", "Wall with river rock along the drive"),
            ("drive-oct8--IMG_6162", "IMG_6162", "Oct 7, 2026", "Boulder steps through river rock"),
            ("drive-oct8--drone-20261007-133650", "DJI 0337", "Oct 7, 2026", "Drone: the round wall and steps, lower angle"),
            ("drive-oct8--drone-20261007-135156", "DJI 0366", "Oct 7, 2026", "Drone: round wall and steps with the drive behind"),
        ])],
    },
    {
        "desc": "White stone house with a round tower",
        "when": "No dates", "from": FB,
        "check": "Which town?",
        "projects": [("Front beds along the stepping-stone walk", [
            ("fb-before-after--fb-194292", "Facebook", "", "Before: bare dirt along the walk"),
            ("fb-before-after--fb-210260", "Facebook", "", "After: planted beds along the walk"),
            ("fb-general--fb-219298", "Facebook", "", "Fern urn and fountain by the front door"),
        ])],
    },
    {
        "desc": "Red brick ranch with a navy front door",
        "when": "No dates", "from": FB,
        "check": "Which town?",
        "projects": [("Bed along the curved front walk", [
            ("fb-before-after--fb-279808", "Facebook", "", "Before: lawn along the front walk"),
            ("fb-before-after--fb-285406", "Facebook", "", "After: new mulched bed with shrubs"),
        ])],
    },
    {
        "desc": "Tan-sided house with a white garage door",
        "when": "No dates", "from": FB,
        "check": "Which town?",
        "projects": [("Flagstone walk and curved bed", [
            ("fb-before-after--fb-067976", "Facebook", "", "Before: bed outline dug in bare ground"),
            ("fb-before-after--fb-071330", "Facebook", "", "After: flagstone walk around the planted bed"),
        ])],
    },
    {
        "desc": "White ranch with dark wood porch posts",
        "when": "No dates", "from": DRONE_VIDEO,
        "check": "Which town?",
        "projects": [("Front and side beds with a boulder and a Japanese maple", [
            ("fb-before-after--shot-155743", "Drone video", "", "Before: bare corner by the porch"),
            ("fb-before-after--shot-155838", "Drone video", "", "After: corner bed with the maple"),
            ("fb-before-after--shot-155856", "Drone video", "", "Before: lawn at the front porch"),
            ("fb-before-after--shot-155915", "Drone video", "", "After: front bed with the boulder"),
            ("fb-before-after--shot-155943", "Drone video", "", "Before: the whole front"),
            ("fb-before-after--shot-155931", "Drone video", "", "After: the whole front"),
        ])],
    },
    {
        "desc": "White painted-brick house with arched windows",
        "when": "No dates", "from": DRONE_VIDEO,
        "check": "Which town?",
        "projects": [("Block-edged beds and a fountain bed", [
            ("fb-before-after--shot-161913", "Drone video", "", "Before: grass strip along the drive"),
            ("fb-before-after--shot-161926", "Drone video", "", "After: block-edged bed along the drive"),
            ("fb-before-after--shot-162002", "Drone video", "", "Before: bare corner by the garage"),
            ("fb-before-after--shot-162011", "Drone video", "", "After: fountain bed by the garage"),
        ])],
    },
    {
        "desc": "Backyard pool with a wood privacy fence",
        "when": "No dates", "from": FB,
        "check": "Which town? Are both photos the same backyard?",
        "projects": [("Arborvitae row and a curved brick-edged bed", [
            ("fb-general--fb-006732", "Facebook", "", "Arborvitae and landscape lights along the fence"),
            ("fb-general--fb-010992", "Facebook", "", "Curved brick-edged bed by the patio"),
        ])],
    },
    {
        "desc": "Brick house with a white arched sunroom",
        "when": "No dates", "from": FB,
        "check": "Which town?",
        "projects": [("Beds along the brick edging and the front walk", [
            ("fb-general--fb-971544", "Facebook", "", "Shrub bed by the brick pillar"),
            ("fb-general--fb-954078", "Facebook", "", "Bed in front of the sunroom"),
            ("fb-general--fb-959728", "Facebook", "", "Flower border along the drive"),
        ])],
    },
    {
        "desc": "Brick house with white columns and a white gable",
        "when": "No date", "from": FB,
        "check": "Which town?",
        "projects": [("Curved front bed with crape myrtles", [
            ("fb-general--fb-229149", "Facebook", "", "Curved bed across the front of the house"),
        ])],
    },
    {
        "desc": "Two-story brick house with a brick mailbox",
        "when": "No date", "from": FB,
        "check": "Which town?",
        "projects": [("Flower beds along the front walk", [
            ("fb-general--fb-867741", "Facebook", "", "Beds on both sides of the front walk"),
        ])],
    },
    {
        "desc": "Round bed under a shade tree",
        "when": "No date", "from": FB,
        "check": "Which town? The house is not in the photo.",
        "projects": [("Stone-edged flower ring around a tree", [
            ("fb-general--fb-303189", "Facebook", "", "Flower ring with stone edging"),
        ])],
    },
]

MISC = {
    "desc": "Close-ups and beds with no house in view",
    "from": FB,
    "check": "Which site, if any, does each one belong to?",
    "photos": [
        ("fb-general--fb-120398", "Facebook", "", "Stone-edged bed with a birdbath"),
        ("fb-general--fb-794949", "Facebook", "", "Round bed with junipers and pansies"),
        ("fb-general--fb-050310", "Facebook", "", "Petunias by a white porch rail. Same brick edging as Site 14?"),
        ("fb-general--fb-094048", "Facebook", "", "Mixed annuals, close up"),
        ("fb-general--fb-918944", "Facebook", "", "White petunias, close up"),
        ("fb-general--fb-045138", "Facebook", "", "Celosia, likely on the garden center benches"),
    ],
}


def slug(src):
    name = src.split("--")[1].lower().replace("_", "-")
    name = name.replace("drone-2026", "dji-2026").replace("shot-", "drone-video-").replace("fb-", "facebook-")
    return name


def prep(src_dir):
    os.makedirs(f"{OUT}/img/thumb", exist_ok=True)
    for src, *_ in all_photos():
        im = Image.open(f"{src_dir}/{src}.jpg").convert("RGB")
        full = im.copy(); full.thumbnail((1200, 1200), Image.LANCZOS)
        full.save(f"{OUT}/img/{slug(src)}.jpg", quality=72, optimize=True, progressive=True)
        th = im.copy(); th.thumbnail((600, 600), Image.LANCZOS)
        th.save(f"{OUT}/img/thumb/{slug(src)}.jpg", quality=72, optimize=True, progressive=True)


def all_photos():
    for s in SITES:
        for _, photos in s["projects"]:
            yield from photos
    yield from MISC["photos"]


def esc(t):
    return html.escape(t, quote=True)


def figure(photo, where):
    src, label, date, cap = photo
    name = slug(src)
    w, h = Image.open(f"{OUT}/img/thumb/{name}.jpg").size
    meta = f"{label} · {date}" if date else label
    return (f'<li><button type="button" class="ph" data-full="img/{name}.jpg" data-where="{esc(where)}" '
            f'data-cap="{esc(cap)}" data-meta="{esc(meta)}" aria-label="Enlarge: {esc(cap)}">'
            f'<img src="img/thumb/{name}.jpg" width="{w}" height="{h}" alt="{esc(cap)}" loading="lazy" decoding="async"></button>'
            f'<p class="cap">{esc(cap)}</p><p class="meta">{esc(meta)}</p></li>')


def notes_block(key, check):
    return (f'<div class="ask"><p class="check">{esc(check)}</p>'
            f'<div class="fields"><label><span>Town</span><input type="text" data-key="{key}-town" autocomplete="off"></label>'
            f'<label><span>Notes</span><textarea data-key="{key}-notes" rows="1"></textarea></label></div></div>')


def build():
    index, body, project_no, photo_count = [], [], 0, 0
    for i, s in enumerate(SITES, 1):
        count = sum(len(p) for _, p in s["projects"])
        photo_count += count
        parts = [f'<section class="site" id="site-{i}" data-name="Site {i}" data-desc="{esc(s["desc"])}">',
                 f'<div class="site-head"><h2>Site {i}</h2><p class="desc">{esc(s["desc"])}</p>',
                 f'<p class="facts">{count} photo{"s" if count > 1 else ""} · {esc(s["when"])} · {esc(s["from"])}</p></div>']
        titles = []
        for title, photos in s["projects"]:
            project_no += 1
            titles.append(f"Project {project_no}")
            parts.append(f'<h3>Project {project_no}: {esc(title)}</h3><ul class="grid">')
            parts += [figure(p, f"Site {i}, Project {project_no}") for p in photos]
            parts.append("</ul>")
        parts.append(notes_block(f"site-{i}", s["check"]))
        parts.append("</section>")
        body.append("\n".join(parts))
        first = s["projects"][0][0]
        index.append(f'<li><a href="#site-{i}"><span class="n">Site {i}</span><span class="t">{esc(s["desc"])}</span>'
                     f'<span class="p">{" and ".join(titles)} · {count} photo{"s" if count > 1 else ""}</span></a></li>')
    m = MISC
    photo_count += len(m["photos"])
    body.append("\n".join([
        f'<section class="site" id="misc" data-name="Miscellaneous" data-desc="{esc(m["desc"])}">',
        f'<div class="site-head"><h2>Miscellaneous</h2><p class="desc">{esc(m["desc"])}</p>',
        f'<p class="facts">{len(m["photos"])} photos · No dates · {esc(m["from"])}</p></div>',
        '<ul class="grid">', *[figure(p, "Miscellaneous") for p in m["photos"]], "</ul>",
        notes_block("misc", m["check"]), "</section>"]))
    index.append(f'<li><a href="#misc"><span class="n">Miscellaneous</span><span class="t">{esc(m["desc"])}</span>'
                 f'<span class="p">{len(m["photos"])} photos</span></a></li>')

    page = TEMPLATE.replace("{{INDEX}}", "\n".join(index)).replace("{{SITES}}", "\n".join(body))
    page = page.replace("{{COUNT}}", str(photo_count)).replace("{{SITECOUNT}}", str(len(SITES))).replace("{{PROJECTCOUNT}}", str(project_no))
    with open(f"{OUT}/index.html", "w") as fh:
        fh.write(page)
    print(f"job-photos/index.html: {photo_count} photos, {len(SITES)} sites, {project_no} projects")


TEMPLATE = open(os.path.join(ROOT, "tools", "job-photos-template.html")).read()

if __name__ == "__main__":
    if "--prep" in sys.argv:
        prep(sys.argv[sys.argv.index("--prep") + 1])
    build()
