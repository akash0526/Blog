# Apex Pulse — SEO & Publishing Platform

Apex Pulse is a high-output technical publishing platform with a CMS-like writing studio, real-time SEO audit, Kanban editorial calendar, and a static export engine. It can run entirely in the browser using localStorage or sync live articles to a Supabase PostgreSQL backend.

---

## ⚠️ Security Notice — Rotate Your Supabase Key

If you previously cloned or viewed this repository before the security cleanup, the Supabase **anon key** and **project URL** were hardcoded in the source and are visible in the public git history.

**You must rotate this key immediately** in your Supabase project:

1. Open your Supabase dashboard → Project Settings → API.
2. Click **Generate a new JWT secret** or create a new API key.
3. Delete the old key.
4. Update your GitHub repository secrets (`SUPABASE_URL`, `SUPABASE_KEY`) and any local `.env` files.

Never commit keys, tokens, or secrets to git. The project now ships with:

- `.gitignore` that excludes `.env` and secrets.
- `.env.example` as a template for local development.
- GitHub Actions workflow that reads only from repository secrets.
- Frontend Supabase connector that loads credentials from `localStorage` after the user enters them in the **SEO Vault** panel — no hardcoded defaults remain.

---

## Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy the environment template and fill in your real values
cp .env.example .env

# 3. Run the static blog generator (optional, generates /blog/* pages)
python generate_static_blog.py

# 4. Serve the static files (e.g., with Python's built-in server)
python -m http.server 8000
```

Open `http://localhost:8000` to view the app.

---

## Supabase Setup

1. Create a new Supabase project.
2. Run the SQL in `supabase_schema.sql` in the SQL Editor to create the `articles` and `authors` tables.
3. Configure Row Level Security (RLS) policies for your use case (the schema includes starter policies).
4. Copy your **Project URL** and **anon key** into the frontend via the **SEO Vault → Supabase Connect** panel.
5. For the autopilot worker, add `SUPABASE_URL` and `SUPABASE_KEY` as GitHub repository secrets (Settings → Secrets and variables → Actions).

---

## Project Structure

```
.
├── .github/workflows/autopilot.yml   # Nightly autopilot content worker
├── articles.json                     # Canonical source for seed articles
├── .env.example                      # Local environment template
├── .gitignore                        # Secrets & build ignores
├── autopilot_worker.py               # Python worker for scheduled content
├── generate_static_blog.py           # Static HTML page generator
├── index.html                        # Main SPA (CMS + blog frontend)
├── dispatches.html                   # Magazine-style landing page
├── supabase_schema.sql               # PostgreSQL schema
├── src/
│   ├── app.js                        # Main application logic
│   ├── data.js                       # Default articles + localStorage manager
│   ├── seo.js                        # Real-time SEO scoring engine
│   ├── supabaseClient.js             # Supabase REST connector (no hardcoded keys)
│   ├── exporter.js                   # Sitemap, robots, and HTML export helpers
│   ├── icons.js                      # SVG icon collection
│   └── styles.css                    # Enterprise design system
└── blog/                             # Generated standalone article pages
```

---

## Autopilot Worker

`autopilot_worker.py` runs on a schedule to draft new technical articles for your review queue. It now follows a much higher-quality pipeline:

1. **Scrapes real GitHub trending data** for Python repositories.
2. **Generates a draft article** using:
   - OpenAI GPT-4o-mini if `OPENAI_API_KEY` is set, OR
   - Anthropic Claude 3.5 Sonnet if `CLAUDE_API_KEY` is set, OR
   - A clean, high-quality template fallback if no LLM key is available.
3. **Saves the draft as `in_review`** in Supabase so you can review, edit, and humanize it before publishing.

The generated content is designed to be genuinely helpful: it explains the technology, provides a working code example, covers trade-offs, and avoids affiliate spam, fake benchmarks, and clichés.

To run locally:

```bash
cp .env.example .env
# fill in SUPABASE_URL, SUPABASE_KEY, and optionally OPENAI_API_KEY
python autopilot_worker.py
```

---

## Build & Deploy

### 1. Generate the static site

```bash
# Generates:
#   - blog/<slug>/index.html   (standalone article pages)
#   - blog/index.html          (magazine listing)
#   - dispatches.html          (root magazine listing)
#   - sitemap.xml              (fresh, auto-generated)
#   - robots.txt               (points to the current domain)
python generate_static_blog.py
```

The static generator reads `articles.json` and writes all output files. To use a custom domain, set the `APEX_DOMAIN` environment variable:

```bash
APEX_DOMAIN=https://your-domain.com python generate_static_blog.py
```

### 2. Deploy to Vercel

This project is designed to deploy as a static site on Vercel:

1. Push to a GitHub repository.
2. Import the repository into Vercel.
3. Set framework preset to **Other** (no build command required).
4. Vercel will use `vercel.json` for clean URLs and SPA rewrites.
5. Add `SUPABASE_URL` and `SUPABASE_KEY` as Vercel environment variables only if you intend to run the autopilot worker there.

**Important routing note:** `vercel.json` now uses `cleanUrls: true` so static files like `/blog/<slug>` and `/blog` are served directly without a trailing slash. The remaining rewrites only handle dynamic SPA routes (`/categories/*` and `/daily`).

### 3. Local testing

Python's built-in server does not support Vercel's `cleanUrls` behavior, so you will see trailing-slash redirects locally. Use these URLs for local testing:

```bash
python3 -m http.server 8000
# http://localhost:8000/           → SPA homepage
# http://localhost:8000/blog/      → magazine listing
# http://localhost:8000/blog/<slug>/ → article page
# http://localhost:8000/dispatches.html → root magazine listing
# http://localhost:8000/sitemap.xml
# http://localhost:8000/robots.txt
```

---

## License

This is a personal project. Use at your own risk and rotate all cloud credentials before production use.
