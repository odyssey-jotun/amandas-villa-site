# Amanda's Villa: working notes for Claude

## The client and the site
Amanda's Villa Landscaping and Garden Center in White Hall, Arkansas (owners Amanda and Colton). Built by Outset Web Design (Joe Green, technical; Marc Gray, copy, brand and SEO). See README.md for the page list and how Marc's build scripts work.

## Stack
Plain HTML/CSS/JS. One folder per URL, all paths relative. Site files live at the repo root, not in `public/`, because the scripts in `tools/` are run from the root and write pages in place.

## Hosting
- Cloudflare Worker `amandas-villa-site` in the Outset business Cloudflare account, connected to this repo.
- `wrangler.jsonc` publishes the repo root; `.assetsignore` keeps README.md, CLAUDE.md, wrangler.jsonc, tools/, CREDITS.md files and dotfiles off the website. Add any new non-site file there.
- Live: `https://amandas-villa-site.jmgreen1361.workers.dev` (until the domain is connected)
- Preview: `https://develop-amandas-villa-site.jmgreen1361.workers.dev`
- Domain: amandasvilla.com, registered through Cloudflare in the business account. No email on the domain yet; Zoho Mail is planned later, which will need MX/SPF/DKIM records in Cloudflare DNS.

## Branches
- `main` is the live site; `develop` is the preview.
- Work on `develop`. Changes reach `main` only through a pull request, and only when Joe says so.
- Marc also pushes: pull before starting work.

## Token
`CLOUDFLARE_API_TOKEN` lives in `.env` (gitignored). Joe pastes it himself; never print it or ask for it in chat.

## Going-live checklist (do on develop, check the preview, then merge)
1. Remove `<meta name="robots" content="noindex, nofollow">` from every page, only after Amanda says yes, and add a `robots.txt` allowing all.
2. Connect and test any forms.
3. Set `"workers_dev": false`, then confirm the develop preview still loads.
4. Load https://amandasvilla.com and https://www.amandasvilla.com and confirm.

## Working with Joe
Explain things in plain terms. Ask before anything that affects the live site, the domain or DNS, or can't be undone.
