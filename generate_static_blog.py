import os
import json
import re
import shutil
from datetime import date

# ========================================================
# APEX PULSE — STATIC SITE GENERATOR
# Reads the canonical ./articles.json file and renders:
#   - Standalone SEO-ready article pages under ./blog/<slug>/
#   - A magazine listing page at ./blog/index.html
#   - A magazine listing page at ./dispatches.html
#   - An up-to-date sitemap.xml
# ========================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLES_PATH = os.path.join(SCRIPT_DIR, "articles.json")
BLOG_DIR = os.path.join(SCRIPT_DIR, "blog")
DOMAIN = os.environ.get("APEX_DOMAIN", "https://blog-liart-five-46.vercel.app").rstrip("/")


def load_articles():
    """Load the canonical article list from articles.json."""
    if not os.path.exists(ARTICLES_PATH):
        raise FileNotFoundError(f"articles.json not found at {ARTICLES_PATH}")
    with open(ARTICLES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("articles.json must contain a JSON array")
    return data


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def parse_md(md):
    lines = md.split('\n')
    html = ''
    in_code = False
    code_block = ''
    for line in lines:
        if line.startswith('```'):
            if in_code:
                html += f'<pre class="bg-slate-950 text-indigo-300 p-5 rounded-2xl font-mono text-sm my-6 overflow-x-auto border border-slate-800"><code>{code_block.strip()}</code></pre>'
                code_block = ''
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_block += line + '\n'
            continue

        if line.startswith('### '):
            text = line.replace('### ', '').strip()
            html += f'<h3 id="{slugify(text)}" class="text-xl font-black text-slate-900 dark:text-white mt-8 mb-3">{text}</h3>'
        elif line.startswith('## '):
            text = line.replace('## ', '').strip()
            html += f'<h2 id="{slugify(text)}" class="text-2xl font-black text-slate-900 dark:text-white mt-12 mb-4 pb-2 border-b border-slate-200 dark:border-slate-800">{text}</h2>'
        elif line.startswith('# '):
            continue
        elif line.startswith('> '):
            text = line.replace('> ', '')
            html += f'<blockquote class="border-l-4 border-indigo-600 pl-5 py-2 my-8 font-serif italic text-lg text-slate-600 dark:text-slate-300 bg-indigo-50/50 dark:bg-indigo-950/40 rounded-r-2xl">{text}</blockquote>'
        elif line.strip() == '---':
            html += '<hr class="my-10 border-slate-200 dark:border-slate-800">'
        elif line.strip():
            clean = re.sub(r'\*\*(.*?)\*\*', r'<strong class="font-extrabold text-slate-900 dark:text-white">\1</strong>', line)
            clean = re.sub(r'\*(.*?)\*', r'<em class="italic">\1</em>', clean)
            html += f'<p class="my-5 text-lg leading-relaxed text-slate-700 dark:text-slate-200 font-normal">{clean}</p>'
    return html


def build_article_html(art):
    post_url = f"{DOMAIN}/blog/{art['slug']}"
    rendered = parse_md(art['content'])

    schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": post_url
        },
        "headline": art['title'],
        "description": art['metaDescription'],
        "image": art['image'],
        "author": {
            "@type": "Person",
            "name": art['author']['name'],
            "jobTitle": art['author']['role']
        },
        "publisher": {
            "@type": "Organization",
            "name": "Apex Pulse Platform",
            "logo": {
                "@type": "ImageObject",
                "url": f"{DOMAIN}/logo.png"
            }
        },
        "datePublished": art['publishedAt'],
        "dateModified": art['publishedAt']
    }

    schema_json = json.dumps(schema, indent=2)

    return f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <title>{art['title']} | Apex Pulse</title>
  <meta name="description" content="{art['metaDescription']}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <link rel="canonical" href="{post_url}">

  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:url" content="{post_url}">
  <meta property="og:title" content="{art['title']}">
  <meta property="og:description" content="{art['metaDescription']}">
  <meta property="og:image" content="{art['image']}">
  <meta property="article:published_time" content="{art['publishedAt']}">
  <meta property="article:author" content="{art['author']['name']}">
  <meta property="article:section" content="{art['category']}">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:url" content="{post_url}">
  <meta name="twitter:title" content="{art['title']}">
  <meta name="twitter:description" content="{art['metaDescription']}">
  <meta name="twitter:image" content="{art['image']}">

  <!-- Fonts & Tailwind -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['Inter', 'sans-serif'],
          }}
        }}
      }}
    }}
  </script>

  <script type="application/ld+json">
    {schema_json}
  </script>
</head>
<body class="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 min-h-screen flex flex-col antialiased">

  <!-- Header -->
  <header class="h-20 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-50 transition">
    <div class="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
      <a href="{DOMAIN}" class="flex items-center gap-3 text-xl font-black text-slate-900 dark:text-white">
        <span class="w-9 h-9 rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-600 text-white flex items-center justify-center text-base font-black shadow-lg shadow-indigo-500/30">⚡</span>
        <span>Apex<span class="text-indigo-600 dark:text-indigo-400">Pulse</span></span>
      </a>

      <div class="flex items-center gap-6 font-bold text-sm text-slate-600 dark:text-slate-300">
        <a href="{DOMAIN}" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition">&larr; Explore All Dispatches</a>
        <button id="btn-theme" class="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">🌙</button>
      </div>
    </div>
  </header>

  <!-- Full Article Main -->
  <main class="flex-1 py-12 px-6 max-w-5xl mx-auto w-full">
    <article class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-8 sm:p-16 shadow-2xl transition">

      <div class="flex items-center gap-3 text-xs font-black uppercase tracking-wider text-indigo-600 dark:text-indigo-400 mb-6 flex-wrap">
        <span class="bg-indigo-50 dark:bg-indigo-950 px-3.5 py-1.5 rounded-full">{art['category']}</span>
        <span class="text-slate-300 dark:text-slate-700">•</span>
        <span class="text-slate-500 font-semibold">{art['publishedAt']}</span>
        <span class="text-slate-300 dark:text-slate-700">•</span>
        <span class="text-slate-500 font-semibold">{art['readingTime']}</span>
      </div>

      <h1 class="text-3xl sm:text-5xl font-black text-slate-900 dark:text-white leading-tight mb-10 tracking-tight">
        {art['title']}
      </h1>

      <div class="flex items-center gap-4 py-6 border-y border-slate-100 dark:border-slate-800 mb-12 bg-slate-50 dark:bg-slate-800/60 px-8 rounded-2xl">
        <img src="{art['author']['avatar']}" alt="{art['author']['name']}" width="56" height="56" class="w-14 h-14 rounded-full object-cover shadow-md border-2 border-white dark:border-slate-700 flex-shrink-0">
        <div>
          <div class="font-black text-slate-900 dark:text-white text-base">{art['author']['name']}</div>
          <div class="text-xs font-bold text-indigo-600 dark:text-indigo-400">{art['author']['role']}</div>
        </div>
        <div class="ml-auto text-xs font-extrabold text-slate-500 dark:text-slate-400 bg-white dark:bg-slate-900 px-3.5 py-2 rounded-xl border border-slate-200/80 dark:border-slate-800 shadow-sm flex items-center gap-1.5">
          Verified Publisher
        </div>
      </div>

      <img src="{art['image']}" alt="{art['title']}" class="w-full h-[380px] sm:h-[450px] object-cover rounded-3xl mb-14 shadow-2xl border border-slate-100 dark:border-slate-800">

      <div class="prose max-w-none text-slate-800 dark:text-slate-200 leading-relaxed">
        {rendered}
      </div>

      <div class="mt-20 pt-10 border-t border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-6 bg-gradient-to-br from-indigo-950 to-slate-900 text-white p-10 rounded-3xl shadow-xl">
        <div>
          <div class="text-xl font-black mb-1">Loved this technical deep dive?</div>
          <div class="text-xs text-indigo-200 font-medium">Join 45,000+ expert engineers getting our high-output pieces.</div>
        </div>
        <a href="{DOMAIN}" class="bg-indigo-600 hover:bg-indigo-500 px-7 py-4 rounded-xl font-black text-white shadow-lg transition">
          Subscribe Live &rarr;
        </a>
      </div>

    </article>
  </main>

  <footer class="py-12 bg-slate-900 text-slate-500 text-center text-xs mt-16 border-t border-slate-800">
    © 2026 Apex Pulse Platform. Built by Principal Software Engineers.
  </footer>

  <script>
    document.getElementById("btn-theme")?.addEventListener("click", () => {{
      document.documentElement.classList.toggle("dark");
      document.getElementById("btn-theme").innerHTML = document.documentElement.classList.contains("dark") ? "☀️" : "🌙";
    }});
  </script>
</body>
</html>"""


def build_sitemap_xml(articles):
    """Generate a sitemap.xml containing the home page, listing pages, and every article."""
    today = date.today().isoformat()
    urls = [
        f"""  <url>
    <loc>{DOMAIN}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""",
        f"""  <url>
    <loc>{DOMAIN}/blog</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>""",
        f"""  <url>
    <loc>{DOMAIN}/dispatches</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""",
    ]

    for art in articles:
        urls.append(f"""  <url>
    <loc>{DOMAIN}/blog/{art['slug']}</loc>
    <lastmod>{art.get('publishedAt', today)}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>
"""


def _article_card_html(art, post_url):
    """HTML for one article card on the magazine listing pages."""
    return f"""<div class="bg-slate-800/50 border border-slate-800 rounded-3xl overflow-hidden flex flex-col h-full hover:border-indigo-500 transition duration-300 shadow-xl group">
          <div class="h-60 bg-cover bg-center relative overflow-hidden" style="background-image: url('{art['image']}');">
            <div class="absolute top-4 left-4 bg-slate-900/90 backdrop-blur-md px-3 py-1 rounded-full text-[10px] font-black uppercase text-indigo-400 tracking-wider">
              {art['category']}
            </div>
          </div>

          <div class="p-8 flex flex-col flex-1 justify-between space-y-6">
            <div>
              <div class="flex items-center gap-2 text-[11px] font-mono font-bold text-slate-400 mb-2">
                <span>{art['publishedAt']}</span> • <span>{art['readingTime']}</span> • <span class="text-indigo-400">{(art.get('pageviews') or 0):,} hits</span>
              </div>
              <h4 class="text-2xl font-black text-white leading-snug group-hover:text-indigo-400 transition duration-200">
                {art['title']}
              </h4>
              <p class="text-slate-300 text-sm leading-relaxed mt-3 font-normal line-clamp-3">
                {art['metaDescription']}
              </p>
            </div>

            <div class="pt-6 border-t border-slate-800 flex items-center justify-between">
              <span class="text-xs font-extrabold text-slate-400">{art['author']['name']}</span>
              <a href="{post_url}" class="inline-flex items-center gap-1.5 text-xs font-black text-indigo-400 group-hover:underline">
                Read Dispatch &rarr;
              </a>
            </div>
          </div>
        </div>"""


def _magazine_listing_html(articles, base_path, title, logo_subtext, cta_text):
    """
    Build a magazine-style listing page.
    base_path is the relative path from the generated file to the project root.
    """
    home_url = f"{base_path}index.html"
    cms_url = f"{base_path}index.html#cms"

    if articles:
        featured = articles[0]
        rest = articles[1:]
    else:
        featured = None
        rest = []

    featured_section = ""
    if featured:
        featured_section = f"""<section id="featured" class="py-12 px-6 max-w-7xl mx-auto">
      <div class="mb-6 flex items-center justify-between border-b border-slate-800 pb-4">
        <span class="text-xs font-black text-indigo-400 uppercase tracking-widest flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-indigo-400 animate-ping"></span> EDITORIAL SPOTLIGHT
        </span>
        <span class="text-xs font-bold text-slate-500 font-mono">{date.today().strftime('%B %d, %Y')}</span>
      </div>

      <div class="relative bg-gradient-to-br from-slate-800 via-slate-900 to-indigo-950 rounded-3xl border border-slate-700/80 overflow-hidden shadow-2xl grid grid-cols-1 lg:grid-cols-12 gap-0 group transition duration-500 hover:border-indigo-500/80">
        <div class="lg:col-span-7 h-[400px] lg:h-[540px] bg-cover bg-center relative overflow-hidden" style="background-image: url('{featured['image']}');">
          <div class="absolute inset-0 bg-gradient-to-t lg:bg-gradient-to-r from-slate-900 lg:from-slate-900/40 via-transparent to-transparent"></div>
          <div class="absolute top-6 left-6 bg-indigo-600 text-white text-[11px] font-black px-4 py-1.5 rounded-full uppercase tracking-widest shadow-lg">
            ⚡ {featured['category']}
          </div>
        </div>

        <div class="lg:col-span-5 p-8 lg:p-12 flex flex-col justify-between flex-1 z-10 bg-slate-900/90 lg:bg-transparent">
          <div>
            <div class="flex items-center gap-3 text-xs font-bold text-slate-400 mb-4 font-mono">
              <span>{featured['publishedAt']}</span>
              <span>•</span>
              <span class="text-indigo-300 font-bold flex items-center gap-1">👁️ {(featured.get('pageviews') or 0):,} Verified Reads</span>
            </div>

            <h2 class="text-3xl lg:text-4xl font-black text-white leading-tight tracking-tight mb-6 group-hover:text-indigo-400 transition duration-300">
              {featured['title']}
            </h2>

            <p class="text-slate-300 text-sm lg:text-base leading-relaxed mb-8 line-clamp-4 font-normal">
              {featured['metaDescription']}
            </p>
          </div>

          <div class="pt-6 border-t border-slate-800/80 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <img src="{featured['author']['avatar']}" class="w-10 h-10 rounded-full object-cover border-2 border-indigo-500">
              <div>
                <div class="text-xs font-black text-white">{featured['author']['name']}</div>
                <div class="text-[10px] text-indigo-400 font-bold">{featured['author']['role']}</div>
              </div>
            </div>
            <a href="{base_path}blog/{featured['slug']}/index.html" class="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-black px-5 py-3 rounded-xl transition transform hover:translate-x-1 shadow-md cursor-pointer">
              Read Deep Dive &rarr;
            </a>
          </div>
        </div>
      </div>
    </section>"""

    grid_cards = "\n        ".join(
        _article_card_html(art, f"{base_path}blog/{art['slug']}/index.html") for art in rest
    ) if rest else '<div class="text-slate-400 text-sm font-bold col-span-full text-center py-12">More dispatches coming soon.</div>'

    return f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <title>{title}</title>
  <meta name="description" content="An elite developer magazine and highly authoritative publication covering autonomous AI loops, real-time WebSockets, programmatic JAMstack velocity, and PageRank engineering.">
  <meta name="robots" content="index, follow, max-image-preview:large">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['Inter', 'sans-serif'],
          }}
        }}
      }}
    }}
  </script>

  <link rel="stylesheet" href="{base_path}src/styles.css">
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen flex flex-col font-sans selection:bg-indigo-500 selection:text-white antialiased">

  <!-- Magazine Navigation -->
  <header class="h-24 border-b border-slate-800 bg-slate-900/90 backdrop-blur-xl sticky top-0 z-50 transition">
    <div class="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">

      <a href="{home_url}" class="flex items-center gap-3 text-2xl font-black tracking-tight text-white group cursor-pointer">
        <span class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 text-white flex items-center justify-center text-lg font-black shadow-lg shadow-indigo-500/30 group-hover:scale-105 transition duration-300">⚡</span>
        <span>Apex<span class="text-indigo-400">{logo_subtext}</span></span>
      </a>

      <div class="flex items-center gap-4">
        <a href="{cms_url}" class="inline-flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-black px-4 py-3 rounded-xl border border-slate-700 transition shadow-sm cursor-pointer">
          ⚙️ Switch to CMS Padlock
        </a>
      </div>

    </div>
  </header>

  <main class="flex-1 pb-24">
    {featured_section}

    <section id="editorial-grid" class="py-16 px-6 max-w-7xl mx-auto">
      <div class="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-slate-800 pb-6">
        <div>
          <h3 class="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            <span>📚 Technical Dispatches Vault</span>
          </h3>
          <p class="text-slate-400 text-sm mt-1 font-medium">Exhaustive software engineering frameworks, Jamstack site speed benchmarks, and long-tail SEO execution models.</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
        {grid_cards}
      </div>
    </section>

    <section class="py-16 px-6 max-w-5xl mx-auto">
      <div class="bg-gradient-to-br from-indigo-950 via-slate-900 to-purple-950 rounded-3xl p-10 sm:p-16 border border-slate-800 shadow-2xl text-center relative overflow-hidden">
        <div class="absolute -left-20 -top-20 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl"></div>
        <div class="max-w-xl mx-auto relative z-10 space-y-6">
          <span class="bg-indigo-500/20 text-indigo-300 font-extrabold text-xs px-3.5 py-1.5 rounded-full border border-indigo-500/30 uppercase tracking-widest inline-block">
            ⚡ Definitive Industry Intelligence
          </span>
          <h3 class="text-3xl sm:text-5xl font-black tracking-tight text-white">Subscribe to Magazine Drops</h3>
          <p class="text-slate-300 text-sm sm:text-base leading-relaxed">
            Get our latest long-form technical breakdowns and high-traffic JAMstack methodologies delivered to your inbox every Friday.
          </p>
          <form class="flex flex-col sm:flex-row gap-3 max-w-md mx-auto pt-2">
            <input type="email" placeholder="software.engineer@example.com" required class="input px-5 py-3.5 rounded-2xl bg-white/10 border-slate-700 text-white placeholder-slate-400 focus:border-indigo-500 font-bold text-sm">
            <button type="submit" class="bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-3.5 rounded-2xl font-black whitespace-nowrap shadow-lg transition">
              {cta_text}
            </button>
          </form>
          <div class="text-[11px] font-bold text-slate-500">Zero spam. Pure architectural signal.</div>
        </div>
      </div>
    </section>
  </main>

  <footer class="py-12 bg-slate-950 border-t border-slate-800/80 text-center text-xs font-bold text-slate-500">
    <div class="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-2 text-white font-black text-sm">
        <span>⚡ Apex Pulse Technical Magazine</span>
      </div>
      <div>
        © 2026 Apex Pulse Platform. Built with absolute JAMstack rigour.
      </div>
    </div>
  </footer>

</body>
</html>"""


def build_blog_index_html(articles):
    """Generate the dark magazine listing page at ./blog/index.html."""
    return _magazine_listing_html(
        articles,
        base_path="../",
        title="Apex Pulse Magazine — Elite Engineering & Technical Dispatches",
        logo_subtext="Dispatches",
        cta_text="Subscribe Payout"
    )


def build_dispatches_html(articles):
    """Generate the dark magazine listing page at ./dispatches.html."""
    return _magazine_listing_html(
        articles,
        base_path="./",
        title="Apex Pulse Magazine — Elite Engineering & Technical Dispatches",
        logo_subtext="Magazine",
        cta_text="Subscribe Payout"
    )


def build_robots_txt():
    """Generate robots.txt with the current domain and sitemap directive."""
    return f"""# ========================================================\n# Apex Pulse robots.txt\n# ========================================================\n\nUser-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /private-drafts/\nDisallow: /api/\n\n# AI crawlers are welcome to read published articles\nUser-agent: GPTBot\nAllow: /blog/\n\nUser-agent: ClaudeBot\nAllow: /blog/\n\nSitemap: {DOMAIN}/sitemap.xml\n"""


def clean_blog_output(articles, blog_dir):
    """Remove generated article folders that are no longer in articles.json.
    Preserves blog/index.html and any non-folder contents."""
    if not os.path.isdir(blog_dir):
        return

    valid_slugs = {a["slug"] for a in articles}

    for entry in os.listdir(blog_dir):
        entry_path = os.path.join(blog_dir, entry)
        if os.path.isdir(entry_path) and entry not in valid_slugs:
            shutil.rmtree(entry_path)
            print(f"Removed stale article folder: {entry_path}")


if __name__ == "__main__":
    articles = load_articles()
    os.makedirs(BLOG_DIR, exist_ok=True)

    # 1. Remove article folders that no longer exist in articles.json
    clean_blog_output(articles, BLOG_DIR)

    # 2. Generate standalone article pages
    for article in articles:
        folder = os.path.join(BLOG_DIR, article["slug"])
        os.makedirs(folder, exist_ok=True)
        html_path = os.path.join(folder, "index.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(build_article_html(article))
        print(f"Generated standalone post: {html_path}")

    # 3. Generate listing pages
    blog_index_path = os.path.join(BLOG_DIR, "index.html")
    with open(blog_index_path, "w", encoding="utf-8") as f:
        f.write(build_blog_index_html(articles))
    print(f"Generated magazine listing: {blog_index_path}")

    dispatches_path = os.path.join(SCRIPT_DIR, "dispatches.html")
    with open(dispatches_path, "w", encoding="utf-8") as f:
        f.write(build_dispatches_html(articles))
    print(f"Generated dispatches page: {dispatches_path}")

    # 4. Generate sitemap.xml
    sitemap_path = os.path.join(SCRIPT_DIR, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(build_sitemap_xml(articles))
    print(f"Generated sitemap: {sitemap_path}")

    # 5. Generate robots.txt
    robots_path = os.path.join(SCRIPT_DIR, "robots.txt")
    with open(robots_path, "w", encoding="utf-8") as f:
        f.write(build_robots_txt())
    print(f"Generated robots.txt: {robots_path}")

    print(f"\n✅ Build complete: {len(articles)} articles, 2 listing pages, 1 sitemap, 1 robots.txt")
