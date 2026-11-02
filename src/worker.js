// Coming-soon switch for Amanda's Villa.
//
// Visitors to amandasvilla.com and www.amandasvilla.com see the coming-soon
// page on every address. The workers.dev test address and the develop
// preview still show the full site, so Amanda and Marc can review it.
// Add ?coming-soon to any preview address to see what the public sees.
//
// To launch: set COMING_SOON to false (or remove this file, "main" and
// "run_worker_first" from wrangler.jsonc).

const COMING_SOON = true;
const PUBLIC_HOSTS = ["amandasvilla.com", "www.amandasvilla.com"];

// The estimate form on /contact/ posts here. Each request is emailed to Amanda
// through SendGrid, the same way the Outset site's contact form works.
// Worker secrets (set them in Cloudflare, never in this file):
//   SENDGRID_API_KEY    SendGrid key with mail.send permission
//   CONTACT_TO_EMAIL    where requests land (Amanda's email)
//   CONTACT_FROM_EMAIL  optional; a sender verified in SendGrid
const SENDGRID = "https://api.sendgrid.com/v3/mail/send";
const MAX_PHOTOS = 3;
const MAX_PHOTO_B64 = 3_000_000; // about 2.2 MB per photo once decoded; the page shrinks them first

const json = (body, status) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

const esc = (s) =>
  String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

const clean = (s, max) => String(s ?? "").trim().slice(0, max);

async function handleEstimate(request, env, isPublic) {
  let v;
  try {
    v = await request.json();
  } catch {
    return json({ error: "Malformed request." }, 400);
  }

  // Honeypot: people never see this field, so anything in it is a bot.
  // Answer as though it worked so the bot doesn't retry.
  if (v.company) return json({ ok: true }, 200);

  const f = {
    name: clean(v.name, 120),
    phone: clean(v.phone, 40),
    email: clean(v.email, 200),
    town: clean(v.town, 200),
    needs: (Array.isArray(v.needs) ? v.needs : []).map((n) => clean(n, 80)).slice(0, 6),
    message: clean(v.message, 4000),
  };
  const errors = {};
  if (!f.name) errors.name = "Please add your name.";
  if (!f.phone && !f.email) errors.phone = "Please add a phone number or an email address.";
  if (f.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.email)) errors.email = "That email address doesn't look right.";
  if (Object.keys(errors).length) return json({ errors }, 422);

  const photos = (Array.isArray(v.photos) ? v.photos : [])
    .slice(0, MAX_PHOTOS)
    .filter((p) => typeof p?.data === "string" && p.data.length < MAX_PHOTO_B64 && /^[A-Za-z0-9+/=]+$/.test(p.data))
    .map((p, i) => ({ content: p.data, filename: `yard-photo-${i + 1}.jpg`, type: "image/jpeg", disposition: "attachment" }));

  if (!env.SENDGRID_API_KEY || !env.CONTACT_TO_EMAIL) {
    console.error("Estimate form not configured: set SENDGRID_API_KEY and CONTACT_TO_EMAIL.");
    return json({ error: "The form is not set up yet." }, 500);
  }

  // Anything sent from a preview says so, so a test is never mistaken for a customer.
  const test = isPublic ? "" : "[TEST] ";
  const rows = [
    ["Name", esc(f.name)],
    ["Phone", f.phone ? `<a href="tel:${esc(f.phone)}">${esc(f.phone)}</a>` : "not given"],
    ["Email", f.email ? `<a href="mailto:${esc(f.email)}">${esc(f.email)}</a>` : "not given"],
    ["Town or address", f.town ? esc(f.town) : "not given"],
    ["Looking for", f.needs.length ? esc(f.needs.join(", ")) : "not given"],
    ["Photos", photos.length ? `${photos.length} attached` : "none"],
  ];
  const html =
    `<div style="font:15px/1.5 Helvetica,Arial,sans-serif;color:#1c241f;max-width:560px">` +
    (test ? `<p style="background:#fdf3e3;border:1px solid #e8c88f;padding:8px 12px;border-radius:6px"><b>This came from the preview site. It is a test.</b></p>` : "") +
    `<h2 style="font-weight:400;margin:0 0 12px">New estimate request from the website</h2><table cellpadding="0" cellspacing="0">` +
    rows.map(([k, val]) => `<tr><td style="padding:4px 14px 4px 0;color:#5f6862;white-space:nowrap;vertical-align:top"><b>${k}</b></td><td style="padding:4px 0">${val}</td></tr>`).join("") +
    `</table>` +
    (f.message ? `<div style="margin-top:16px;padding:12px 14px;background:#ecebe4;border-radius:8px">${esc(f.message).replace(/\r?\n/g, "<br>")}</div>` : "") +
    `<p style="color:#5f6862;font-size:13px;margin-top:18px">${f.email ? "Reply to this email and it goes straight to them." : "They left no email, so call them back."}</p></div>`;
  const text =
    `${test}New estimate request from the website\n\n` +
    rows.map(([k, val]) => `${k}: ${val.replace(/<[^>]+>/g, "")}`).join("\n") +
    (f.message ? `\n\n${f.message}` : "") + "\n";

  const mail = {
    personalizations: [{ to: [{ email: env.CONTACT_TO_EMAIL }] }],
    from: { email: env.CONTACT_FROM_EMAIL || "website@outsetsites.com", name: "Amanda's Villa website" },
    subject: `${test}Estimate request from ${f.name}${f.town ? ` in ${f.town}` : ""}`,
    content: [{ type: "text/plain", value: text }, { type: "text/html", value: html }],
  };
  if (f.email) mail.reply_to = { email: f.email, name: f.name };
  if (photos.length) mail.attachments = photos;

  const sent = await fetch(SENDGRID, {
    method: "POST",
    headers: { authorization: `Bearer ${env.SENDGRID_API_KEY}`, "content-type": "application/json" },
    body: JSON.stringify(mail),
  });
  if (!sent.ok) {
    console.error("SendGrid rejected the estimate request", sent.status, await sent.text());
    return json({ error: "Could not send the request." }, 502);
  }
  return json({ ok: true }, 200);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const isPublic = PUBLIC_HOSTS.includes(url.hostname);
    const forced = url.searchParams.has("coming-soon");
    // Google Search Console's verification file has to load on the real domain.
    const isVerification = /^\/google[0-9a-f]+\.html$/.test(url.pathname);

    if (url.pathname === "/api/estimate") {
      if (request.method !== "POST") return json({ error: "Method not allowed." }, 405);
      return handleEstimate(request, env, isPublic);
    }

    // Serve it at the exact .html address; Cloudflare would otherwise redirect
    // it to the address without .html, and Google's check expects a 200.
    if (isVerification) {
      return env.ASSETS.fetch(new URL(url.pathname.replace(/\.html$/, ""), url));
    }

    if (COMING_SOON && (isPublic || forced)) {
      const page = await env.ASSETS.fetch(new URL("/coming-soon/", url));
      return new Response(page.body, {
        status: 200,
        headers: {
          "content-type": "text/html; charset=utf-8",
          "cache-control": "no-store",
          "x-robots-tag": "noindex",
        },
      });
    }

    return env.ASSETS.fetch(request);
  },
};
