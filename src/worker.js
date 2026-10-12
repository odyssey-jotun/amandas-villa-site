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

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const isPublic = PUBLIC_HOSTS.includes(url.hostname);
    const forced = url.searchParams.has("coming-soon");

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
