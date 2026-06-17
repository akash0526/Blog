import os
import json
import urllib.request
import re
from datetime import datetime, date
from urllib.error import HTTPError

# ====================================================================
# APEX PULSE — AUTOPILOT CONTENT WORKER
# Generates a genuine, helpful technical article from a trending open-source
# repository and pushes it to Supabase as an in-review draft for human approval.
# ====================================================================

<<<<<<< HEAD
# ====================================================================
# SECURITY NOTE
# These credentials are intentionally loaded ONLY from environment
# variables. Never hardcode keys here or commit them to git. The
# project ships a .env.example template; copy it to .env for local
# development, and set repository secrets for GitHub Actions.
# ====================================================================
=======
# --- Credentials (loaded only from environment variables) ---
>>>>>>> 8d0cda5 (changes)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "").strip()
<<<<<<< HEAD


def require_env(name, value):
    """Abort early if a required environment variable is missing."""
    if not value:
        raise SystemExit(
            f"❌ Environment variable '{name}' is missing. "
            "Set it in your .env file or GitHub repository secrets, "
            "then run the worker again."
        )


def load_credentials():
    """Validate required cloud credentials before any network call."""
    require_env("SUPABASE_URL", SUPABASE_URL)
    require_env("SUPABASE_KEY", SUPABASE_KEY)
    if not SUPABASE_URL.startswith("https://"):
        raise SystemExit("❌ SUPABASE_URL must begin with https://")
=======
>>>>>>> 8d0cda5 (changes)


def require_env(name, value):
    """Abort early if a required environment variable is missing."""
    if not value:
        raise SystemExit(
            f"❌ Environment variable '{name}' is missing. "
            "Set it in your .env file or GitHub repository secrets, "
            "then run the worker again."
        )


def load_credentials():
    """Validate required cloud credentials before any network call."""
    require_env("SUPABASE_URL", SUPABASE_URL)
    require_env("SUPABASE_KEY", SUPABASE_KEY)
    if not SUPABASE_URL.startswith("https://"):
        raise SystemExit("❌ SUPABASE_URL must begin with https://")


# --- Helpers ---

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def fetch_url(url, headers=None, timeout=15):
    """Simple GET helper with a custom user-agent."""
    req_headers = {
        "User-Agent": "ApexPulse-Autopilot-Worker/1.0 (Educational Content Bot)"
    }
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return res.read().decode("utf-8")


def fetch_github_trending():
    """
    Scrape the GitHub Trending page for Python repositories.
    Returns the top repo as a dict, or None if scraping fails.
    """
    print("⚡ Fetching real GitHub trending repositories for Python...")
    try:
        html = fetch_url("https://github.com/trending/python?since=daily")

        # Extract the first repository <article> block.
        article_match = re.search(
            r'<article[^>]*class="[^"]*Box-row[^"]*"[^>]*>(.*?)</article>',
            html,
            re.DOTALL
        )
        if not article_match:
            return None
        article = article_match.group(1)

        # Repo link: the first <a> inside the h2 block.
        link_match = re.search(
            r'<h2[^>]*class="h3 lh-condensed"[^>]*>\s*<a[^>]*href="/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)"[^>]*>',
            article,
            re.DOTALL
        )
        if not link_match:
            return None
        full_name = link_match.group(1).strip()
        owner, name = full_name.split("/", 1)

        # Description
        desc_match = re.search(
            r'<p[^>]*class="col-9[^"]*"[^>]*>(.*?)</p>',
            article,
            re.DOTALL
        )
        description = ""
        if desc_match:
            description = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip()
            description = description.replace('&amp;', '&')

        # Star count
        stars_match = re.search(
            r'<a[^>]*href="/{0}/stargazers"[^>]*>.*?([\d,\.]+[kKmM]?)\s*stars?.*?</a>'.format(re.escape(full_name)),
            article,
            re.DOTALL
        )
        if not stars_match:
            stars_match = re.search(
                r'<svg[^>]*octicon-star[^>]*>.*?</svg>\s*<span[^>]*>([\d,\.]+[kKmM]?)</span>',
                article,
                re.DOTALL
            )
        stars = stars_match.group(1) if stars_match else "trending"

        return {
            "owner": owner,
            "name": name,
            "full_name": full_name,
            "stars": stars,
            "description": description,
            "url": f"https://github.com/{full_name}"
        }
    except Exception as e:
        print(f"⚠️ Could not scrape GitHub trending: {e}")
        return None


def fallback_topic():
    """Curated fallback topic when live scraping is unavailable."""
    return {
        "owner": "astral-sh",
        "name": "uv",
        "full_name": "astral-sh/uv",
        "stars": "trending",
        "description": "An extremely fast Python package and project manager, written in Rust.",
        "url": "https://github.com/astral-sh/uv",
        "install_url": "https://astral.sh/uv/install.sh"
    }


# --- Content generation ---

SYSTEM_PROMPT = """You are a senior software engineer writing a practical, no-fluff technical blog post for an audience of experienced developers.

Rules:
1. Start with a clear, concrete explanation of the technology.
2. Include a real, working code example that a reader can run.
3. Explain *why* a team would adopt this tool and what problem it solves.
4. Mention one or two genuine trade-offs or gotchas.
5. Do NOT use clichés like "in today's fast-paced world" or "in conclusion".
6. Do NOT invent fake benchmarks, star counts, or expert quotes.
7. Do NOT include affiliate links or undisclosed promotions.
8. Keep the tone direct, technical, and honest.
9. Format the article in Markdown with an H1 title, H2 sections, and H3 subsections where appropriate.
10. The article should be 600-1,000 words.
"""


def _strip_json_fences(text):
    """Remove markdown code fences if the LLM wrapped JSON in them."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def call_openai(repo):
    """Generate an article using OpenAI's chat completions API."""
    print(f"🤖 Calling OpenAI GPT-4o-mini for {repo['full_name']}...")
    user_prompt = (
        f"Write a Markdown technical blog post about the open-source project "
        f"{repo['full_name']} ({repo['url']}).\n\n"
        f"GitHub description: {repo['description']}\n\n"
        f"The slug should be '{slugify(repo['name'])}-{date.today().strftime('%Y-%m-%d')}'.\n"
        f"Include a front-matter style meta description and target keyword.\n\n"
        f"Return ONLY a JSON object with these keys:\n"
        f"- title (string)\n"
        f"- slug (string)\n"
        f"- meta_description (string, 120-160 chars)\n"
        f"- target_keyword (string)\n"
        f"- secondary_keywords (string, comma separated)\n"
        f"- content (string, Markdown article body)\n"
    )

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.6,
        "response_format": {"type": "json_object"}
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            data = json.loads(res.read().decode("utf-8"))
            raw = _strip_json_fences(data["choices"][0]["message"]["content"])
            return json.loads(raw)
    except HTTPError as e:
        print(f"🚨 OpenAI API error: {e.code} {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"🚨 OpenAI request failed: {e}")
        return None


def call_claude(repo):
    """Generate an article using Anthropic's Messages API."""
    print(f"🤖 Calling Claude 3.5 Sonnet for {repo['full_name']}...")
    user_prompt = (
        f"Write a Markdown technical blog post about the open-source project "
        f"{repo['full_name']} ({repo['url']}).\n\n"
        f"GitHub description: {repo['description']}\n\n"
        f"The slug should be '{slugify(repo['name'])}-{date.today().strftime('%Y-%m-%d')}'.\n"
        f"Return ONLY a JSON object with these keys: title, slug, meta_description, target_keyword, secondary_keywords, content. "
        f"The content field must contain the full Markdown article body. "
        f"Do not wrap the JSON in markdown code fences."
    )

    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 2048,
        "temperature": 0.6,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_prompt}]
    }

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            data = json.loads(res.read().decode("utf-8"))
            raw = _strip_json_fences(data["content"][0]["text"])
            return json.loads(raw)
    except HTTPError as e:
        print(f"🚨 Claude API error: {e.code} {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"🚨 Claude request failed: {e}")
        return None


def fallback_article(repo):
    """
    High-quality template-based fallback when no LLM API key is available.
    No affiliate links, no fake claims, no keyword stuffing.
    """
    print(f"📝 Using template-based fallback for {repo['full_name']}...")
    name = repo['name']
    full_name = repo['full_name']
    url = repo['url']
    description = repo['description'] or "a popular open-source developer tool"
    install_url = repo.get("install_url")
    slug = f"{slugify(name)}-{date.today().strftime('%Y-%m-%d')}"

    if install_url:
        install_cmd = f"curl -LsSf {install_url} | sh"
    else:
        install_cmd = f"# Install instructions are available at {url}"

    title = f"A Practical Look at {name}: What {full_name} Does and Why It Matters"
    meta = f"A hands-on guide to {full_name}. Learn what {name} does, how to install it, and when it belongs in your workflow."
    keywords = f"{name}, {full_name}, developer tools"

    content = f"""# {title}

{full_name} is gaining attention among developers. {description}. In this post we look at what problem it solves, how to get started, and where it fits in a modern engineering workflow.

---

## 1. The Problem {name} Solves

Most Python projects accumulate tooling over time: a package manager, a lock-file generator, a virtual-environment manager, a task runner, and a linter. Keeping these tools aligned and fast is a real maintenance burden. {name} aims to consolidate several of those responsibilities into one fast, consistent interface.

The key idea is simple: replace multiple slow shell commands with one tool that can resolve, install, and run Python code quickly. By doing so, it reduces both local development friction and CI pipeline time.

---

## 2. Getting Started

You can install {name} directly. Because it is distributed as a single static binary, setup is usually a one-liner:

```bash
# Follow the official installation instructions at {url}
# This is a common one-liner — verify the exact URL in the docs before running:
{install_cmd}
```

After installation, verify the binary is available:

```bash
{name} --version
```

A typical first step is to create a project lock file and a virtual environment:

```bash
{name} init
{name} sync
```

`init` writes the project metadata, and `sync` ensures the exact dependency versions described in the lock file are installed.

---

## 3. A Concrete Workflow Example

Imagine you are joining a repository that already uses {name}. Instead of reading a long `README` section about Python versions and `pip` flags, you run one command and the project is ready:

```bash
{name} run python src/main.py
```

This command:

1. Activates the correct virtual environment automatically.
2. Installs any missing dependencies from the lock file.
3. Runs the script in a reproducible environment.

For CI pipelines, the same lock file guarantees that the build environment matches the one on your local machine. That reproducibility is the main reason teams adopt tools like {name}.

---

## 4. Trade-offs to Consider

{name} is not a universal replacement for every project. Keep these points in mind:

* **Adoption cost:** Existing projects with complex `Makefile` or `tox` setups need a migration plan.
* **Ecosystem maturity:** Some integrations may still be catching up. Check the official issue tracker before betting a critical workflow on a brand-new feature.
* **Learning curve:** While the CLI is small, the mental model (unified package + project management) differs from traditional `pip`/`venv` workflows.

---

## 5. Should You Use It?

If your team is starting a new Python service or wants to cut CI minutes, {name} is worth a two-week evaluation. The unified model reduces the number of files and commands new contributors must learn, and the speed improvements are often measurable within a few builds.

For the latest features and installation instructions, refer to the official repository: {url}.

---

*This article was generated by the Apex Pulse autopilot worker and is awaiting human review before publication.*
"""

    return {
        "title": title,
        "slug": slug,
        "meta_description": meta,
        "target_keyword": name,
        "secondary_keywords": keywords,
        "content": content
    }


def synthesize_article():
    """Pick a trending topic and generate a genuine technical article."""
    repo = fetch_github_trending()
    if not repo:
        repo = fallback_topic()

    print(f"✅ Selected topic: {repo['full_name']}")

    generated = None
    if OPENAI_API_KEY:
        generated = call_openai(repo)
    elif CLAUDE_API_KEY:
        generated = call_claude(repo)

    if not generated:
        generated = fallback_article(repo)

    # Normalize the generated object to the Supabase schema
    slug = generated.get("slug") or slugify(generated.get("title", repo["name"]))
    if not re.search(r"\d{4}-\d{2}-\d{2}", slug):
        slug = f"{slug}-{date.today().strftime('%Y-%m-%d')}"

    return {
        "slug": slug,
        "title": generated.get("title", repo["name"]),
        "meta_description": generated.get("meta_description", f"A practical guide to {repo['full_name']}"),
        "category": "Tech & AI",
        "target_keyword": generated.get("target_keyword", repo["name"]),
        "secondary_keywords": generated.get("secondary_keywords", ""),
        "content": generated.get("content", ""),
        "image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80",
        "seo_score": 85,
        "pageviews": 1,
        "status": "in_review",
        "published_at": date.today().isoformat()
    }


# --- Supabase push ---

def push_to_supabase_cloud(article_obj):
    """Push the article to Supabase as an in-review draft."""
    print(f"⚡ Pushing draft to Supabase: {article_obj['title']}")

    endpoint = f"{SUPABASE_URL.rstrip('/')}/rest/v1/articles"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
        "User-Agent": "ApexPulse-Autopilot-Worker/1.0"
    }

    req = urllib.request.Request(
        endpoint,
        data=json.dumps(article_obj).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            if res.status in [200, 201, 204]:
                print(f"🎉 Draft saved to Supabase moderation queue: {article_obj['slug']}")
                return True
            else:
                print(f"⚠️ Supabase returned unexpected status: {res.status}")
                return False
    except HTTPError as e:
        print(f"🚨 Supabase HTTP error ({e.code}): {e.read().decode('utf-8')}")
        print("💡 Hint: Check that your RLS policy allows inserts into the 'articles' table.")
        return False
    except Exception as e:
        print(f"🚨 Supabase network error: {e}")
        return False


def run_autopilot_flywheel():
    load_credentials()
<<<<<<< HEAD
    print(f"🚀 Starting Apex Autopilot Flywheel — Issue Date: {datetime.now().isoformat()}...")
    trending_trend = scrape_github_trending_tech()
    affiliate_article = synthesize_helpful_affiliate_content(trending_trend)
    push_to_supabase_cloud(affiliate_article)
=======
    print(f"🚀 Starting Apex Autopilot Flywheel — {datetime.now().isoformat()}")
    article = synthesize_article()
    push_to_supabase_cloud(article)

>>>>>>> 8d0cda5 (changes)

if __name__ == "__main__":
    run_autopilot_flywheel()
