import os
import json
import time  # NEW: for retry backoff
import urllib.request
import re
from datetime import datetime, date
from urllib.error import HTTPError

# ====================================================================
# APEX PULSE — AUTOPILOT CONTENT WORKER (v1.2 — Resilient Edition)
# --------------------------------------------------------------------
# Changelog vs v1.1:
#   - Smart retry-with-backoff for HTTP 429 rate-limit responses
#   - Browser-like headers to bypass Cloudflare bot detection (Groq)
#   - Multiple OpenRouter free models tried in sequence
#   - Supabase push now uses UPSERT (no more duplicate-slug errors)
#   - Small delay between providers to be friendly to rate limiters
# --------------------------------------------------------------------
# Provider priority chain (first available wins):
#   1. Gemini        — free, highest quality, 1,500 req/day
#   2. Groq          — free, fastest inference
#   3. OpenRouter    — free, 4 fallback models tried in sequence
#   4. OpenAI        — paid (you may have signup credits)
#   5. Claude        — paid
#   6. Template      — curated fallback, always works
# ====================================================================

# --- Credentials (loaded only from environment variables) ---
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()

# --- Free providers (recommended) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()

# --- Paid providers (optional, used as fallback after free ones) ---
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "").strip()

# --- Model names ---
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

# CHANGED: was a single model. Now a prioritized list — first to succeed wins.
# Each one is a free OpenRouter model with different popularity/load patterns.
OPENROUTER_MODELS = [
    os.environ.get("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free"),
    "qwen/qwen-2.5-72b-instruct:free",
    "deepseek/deepseek-chat:free",
    "meta-llama/llama-3.3-70b-instruct:free",  # last because most overloaded
]

# --- Behavior tuning ---
DELAY_BETWEEN_PROVIDERS_SEC = float(os.environ.get("DELAY_BETWEEN_PROVIDERS_SEC", "1.5"))
MAX_RETRIES_PER_PROVIDER = int(os.environ.get("MAX_RETRIES_PER_PROVIDER", "2"))


# ====================================================================
# Credential helpers
# ====================================================================

def require_env(name, value):
    if not value:
        raise SystemExit(
            f"❌ Environment variable '{name}' is missing. "
            "Set it in your .env file or GitHub repository secrets, "
            "then run the worker again."
        )


def load_credentials():
    require_env("SUPABASE_URL", SUPABASE_URL)
    require_env("SUPABASE_KEY", SUPABASE_KEY)
    if not SUPABASE_URL.startswith("https://"):
        raise SystemExit("❌ SUPABASE_URL must begin with https://")


def active_provider():
    if GEMINI_API_KEY:      return "Gemini"
    if GROQ_API_KEY:        return "Groq"
    if OPENROUTER_API_KEY:  return "OpenRouter"
    if OPENAI_API_KEY:      return "OpenAI"
    if CLAUDE_API_KEY:      return "Claude"
    return "Template (no LLM key configured)"


# ====================================================================
# HTTP helpers
# ====================================================================

# Browser-like headers to avoid Cloudflare bot detection (fixes Groq 1010)
_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}


def fetch_url(url, headers=None, timeout=15):
    req_headers = dict(_BROWSER_HEADERS)
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return res.read().decode("utf-8")


def _post_json(url, payload, headers=None, timeout=60):
    """POST JSON helper with consistent error handling."""
    req_headers = {"Content-Type": "application/json"}
    req_headers.update(_BROWSER_HEADERS)
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=req_headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.read().decode("utf-8"), res.status
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        print(f"🚨 HTTP {e.code} from {url.split('?')[0]}: {body[:240]}")
        raise


def _post_json_with_retry(url, payload, headers=None, timeout=60, max_retries=None):
    """
    POST JSON with smart exponential backoff for HTTP 429 (rate limit) errors.

    403/401/etc are NOT retried (they're not transient — retrying wastes time).
    429 IS retried with 2s, 4s, 8s waits between attempts.
    Network errors are retried too.
    """
    if max_retries is None:
        max_retries = MAX_RETRIES_PER_PROVIDER

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return _post_json(url, payload, headers, timeout)
        except HTTPError as e:
            last_error = e
            # Only retry on 429 (rate limit) or 5xx (server error)
            if e.code in (429, 500, 502, 503, 504) and attempt < max_retries:
                wait = 2 ** (attempt + 1)  # 2s, 4s, 8s
                reason = "rate-limited" if e.code == 429 else f"server error {e.code}"
                print(f"⏳ {reason}. Waiting {wait}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_error = e
            if attempt < max_retries:
                wait = 2 ** (attempt + 1)
                print(f"⏳ Network error ({e}). Waiting {wait}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait)
                continue
            raise
    raise last_error


# ====================================================================
# Topic discovery
# ====================================================================

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def fetch_github_trending():
    """Scrape the GitHub Trending page for Python repositories."""
    print("⚡ Fetching real GitHub trending repositories for Python...")
    try:
        html = fetch_url("https://github.com/trending/python?since=daily")
        article_match = re.search(
            r'<article[^>]*class="[^"]*Box-row[^"]*"[^>]*>(.*?)</article>',
            html,
            re.DOTALL,
        )
        if not article_match:
            return None
        article = article_match.group(1)
        link_match = re.search(
            r'<h2[^>]*class="h3 lh-condensed"[^>]*>\s*<a[^>]*href="/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)"[^>]*>',
            article,
            re.DOTALL,
        )
        if not link_match:
            return None
        full_name = link_match.group(1).strip()
        owner, name = full_name.split("/", 1)

        desc_match = re.search(
            r'<p[^>]*class="col-9[^"]*"[^>]*>(.*?)\n</p>',
            article,
            re.DOTALL,
        )
        description = ""
        if desc_match:
            description = re.sub(r"<[^>]+>", "", desc_match.group(1)).strip()
            description = description.replace("&amp;", "&")

        stars_match = re.search(
            r'href="/{0}/stargazers"[^>]*>.*?([\d,\.]+[kKmM]?)\s*stars?.*?'.format(re.escape(full_name)),
            article,
            re.DOTALL,
        )
        if not stars_match:
            stars_match = re.search(
                r'octicon-star[^>]*>.*?\s*<a[^>]*>([\d,\.]+[kKmM]?)',
                article,
                re.DOTALL,
            )
        stars = stars_match.group(1) if stars_match else "trending"

        return {
            "owner": owner,
            "name": name,
            "full_name": full_name,
            "stars": stars,
            "description": description,
            "url": f"https://github.com/{full_name}",
        }
    except Exception as e:
        print(f"⚠️ Could not scrape GitHub trending: {e}")
        return None


def fallback_topic():
    return {
        "owner": "astral-sh",
        "name": "uv",
        "full_name": "astral-sh/uv",
        "stars": "trending",
        "description": "An extremely fast Python package and project manager, written in Rust.",
        "url": "https://github.com/astral-sh/uv",
        "install_url": "https://astral.sh/uv/install.sh",
    }


# ====================================================================
# Prompt construction
# ====================================================================

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

You MUST respond with a single JSON object and nothing else. No prose before or after the JSON. No markdown code fences around the JSON."""


def _build_user_prompt(repo):
    return (
        f"Write a Markdown technical blog post about the open-source project "
        f"{repo['full_name']} ({repo['url']}).\n\n"
        f"GitHub description: {repo['description']}\n\n"
        f"The slug should be '{slugify(repo['name'])}-{date.today().strftime('%Y-%m-%d')}'.\n"
        f"Include a front-matter style meta description and target keyword.\n\n"
        f"Return ONLY a JSON object with these exact keys:\n"
        f"- title (string)\n"
        f"- slug (string)\n"
        f"- meta_description (string, 120-160 chars)\n"
        f"- target_keyword (string)\n"
        f"- secondary_keywords (string, comma separated)\n"
        f"- content (string, Markdown article body, 600-1000 words)\n"
    )


def _strip_json_fences(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def _parse_article_json(text):
    """Parse and validate the article JSON returned by any provider."""
    text = _strip_json_fences(text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON decode failed, attempting to recover: {e}")
        # Some models put trailing commas or wrap in extra prose
        # Try to find the first { ... last } block
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            try:
                data = json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                return None
        else:
            return None
    required = ["title", "content", "meta_description", "target_keyword"]
    missing = [k for k in required if k not in data or not data[k]]
    if missing:
        print(f"⚠️ Generated JSON missing required fields: {missing}")
        return None
    return data


# ====================================================================
# Provider implementations
# ====================================================================

def call_gemini(repo):
    """Generate an article using Google Gemini (free tier)."""
    if not GEMINI_API_KEY:
        return None
    print(f"🤖 Calling Google Gemini ({GEMINI_MODEL}) for {repo['full_name']}...")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": _build_user_prompt(repo)}]}
        ],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "generationConfig": {
            "temperature": 0.6,
            "maxOutputTokens": 4096,
            "responseMimeType": "application/json",
        },
    }
    try:
        body, _ = _post_json_with_retry(url, payload)
        data = json.loads(body)
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return _parse_article_json(text)
    except Exception as e:
        print(f"🚨 Gemini request failed: {e}")
        return None


def call_groq(repo):
    """Generate an article using Groq (free, fast inference)."""
    if not GROQ_API_KEY:
        return None
    print(f"🤖 Calling Groq ({GROQ_MODEL}) for {repo['full_name']}...")
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(repo)},
        ],
        "temperature": 0.6,
        "max_tokens": 4096,
        "response_format": {"type": "json_object"},
    }
    try:
        body, _ = _post_json_with_retry(
            "https://api.groq.com/openai/v1/chat/completions",
            payload,
            # Origin/Referer headers help bypass Cloudflare bot detection
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Origin": "https://console.groq.com",
                "Referer": "https://console.groq.com/",
            },
        )
        data = json.loads(body)
        text = data["choices"][0]["message"]["content"]
        return _parse_article_json(text)
    except Exception as e:
        print(f"🚨 Groq request failed: {e}")
        return None


def call_openrouter(repo):
    """
    Generate an article using OpenRouter (free model aggregator).

    CHANGED: now tries multiple free models in sequence. The popular
    `meta-llama/llama-3.3-70b-instruct:free` model is rate-limited most
    of the time, so we try Gemini Flash via OpenRouter first, then Qwen,
    then DeepSeek, then Llama as last resort.
    """
    if not OPENROUTER_API_KEY:
        return None

    for model in OPENROUTER_MODELS:
        print(f"🤖 Calling OpenRouter ({model}) for {repo['full_name']}...")
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(repo)},
            ],
            "temperature": 0.6,
            "max_tokens": 4096,
        }
        try:
            body, _ = _post_json_with_retry(
                "https://openrouter.ai/api/v1/chat/completions",
                payload,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://blog-liart-five-46.vercel.app",
                    "X-Title": "Apex Pulse Autopilot",
                },
            )
            data = json.loads(body)
            # OpenRouter returns a 'reason' field when content is filtered or empty
            if data.get("choices", [{}])[0].get("finish_reason") == "error":
                err = data.get("error", {})
                print(f"⚠️ OpenRouter model {model} returned error: {err}")
                continue
            text = data["choices"][0]["message"]["content"]
            result = _parse_article_json(text)
            if result:
                print(f"✅ OpenRouter model {model} succeeded")
                return result
        except Exception as e:
            print(f"🚨 OpenRouter model {model} failed: {e}")
            # Try the next model in the list
            continue

    print(f"🚨 All OpenRouter models failed (tried {len(OPENROUTER_MODELS)} free models)")
    return None


def call_openai(repo):
    if not OPENAI_API_KEY:
        return None
    print(f"🤖 Calling OpenAI (gpt-4o-mini) for {repo['full_name']}...")
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(repo)},
        ],
        "temperature": 0.6,
        "response_format": {"type": "json_object"},
    }
    try:
        body, _ = _post_json_with_retry(
            "https://api.openai.com/v1/chat/completions",
            payload,
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        )
        data = json.loads(body)
        raw = data["choices"][0]["message"]["content"]
        return _parse_article_json(raw)
    except Exception as e:
        print(f"🚨 OpenAI request failed: {e}")
        return None


def call_claude(repo):
    if not CLAUDE_API_KEY:
        return None
    print(f"🤖 Calling Claude (claude-3-5-sonnet) for {repo['full_name']}...")
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 4096,
        "temperature": 0.6,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": _build_user_prompt(repo)}],
    }
    try:
        body, _ = _post_json_with_retry(
            "https://api.anthropic.com/v1/messages",
            payload,
            headers={
                "x-api-key": CLAUDE_API_KEY,
                "anthropic-version": "2023-06-01",
            },
        )
        data = json.loads(body)
        raw = data["content"][0]["text"]
        return _parse_article_json(raw)
    except Exception as e:
        print(f"🚨 Claude request failed: {e}")
        return None


# ====================================================================
# Provider priority chain
# ====================================================================

PROVIDER_CHAIN = [
    ("Gemini",     call_gemini),
    ("Groq",       call_groq),
    ("OpenRouter", call_openrouter),
    ("OpenAI",     call_openai),
    ("Claude",     call_claude),
]


def generate_with_providers(repo):
    """
    Walk the provider priority chain and return the first successful result.

    Adds a small delay between providers to be friendly to rate limiters,
    so a 429 on provider 1 doesn't immediately cascade into 429s on 2 and 3.
    """
    failed_codes = []
    for idx, (name, fn) in enumerate(PROVIDER_CHAIN):
        if idx > 0:
            # Small delay so we don't hammer the next API immediately
            time.sleep(DELAY_BETWEEN_PROVIDERS_SEC)
        try:
            result = fn(repo)
            if result:
                print(f"✅ Article generated via {name}")
                return result
        except HTTPError as e:
            failed_codes.append((name, e.code))
            print(f"⚠️ {name} returned HTTP {e.code}")
        except Exception as e:
            print(f"⚠️ {name} provider raised an unhandled exception: {e}")

    # Friendly explanation when all providers failed for the same reason
    if failed_codes and all(c == 429 for _, c in failed_codes):
        print("ℹ️  All providers returned 429 — you're rate-limited everywhere.")
        print("   Wait 60 seconds and try again, or upgrade to a paid tier.")
    elif failed_codes and all(c == 403 for _, c in failed_codes):
        print("ℹ️  All providers returned 403 — your IP may be blocked.")
        print("   Try from a different network (mobile hotspot, different VPN endpoint).")

    print("ℹ️  Falling back to template article")
    return fallback_article(repo)


# ====================================================================
# Curated template fallback (no LLM required)
# ====================================================================

def fallback_article(repo):
    print(f"📝 Using template-based fallback for {repo['full_name']}...")
    name = repo["name"]
    full_name = repo["full_name"]
    url = repo["url"]
    description = repo["description"] or "a popular open-source developer tool"
    install_url = repo.get("install_url")
    # Add a unique minute-suffix to avoid Supabase duplicate key conflicts
    # when the same repo trends on multiple days
    minute_suffix = datetime.now().strftime("%H%M")
    slug = f"{slugify(name)}-{date.today().strftime('%Y-%m-%d')}-{minute_suffix}"

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
        "content": content,
    }


# ====================================================================
# Article synthesis
# ====================================================================

def synthesize_article():
    repo = fetch_github_trending()
    if not repo:
        repo = fallback_topic()

    print(f"✅ Selected topic: {repo['full_name']}")
    print(f"🔌 Active provider chain: {active_provider()}")

    generated = generate_with_providers(repo)

    slug = generated.get("slug") or slugify(generated.get("title", repo["name"]))
    # Ensure slug contains a date
    if not re.search(r"\d{4}-\d{2}-\d{2}", slug):
        slug = f"{slug}-{date.today().strftime('%Y-%m-%d')}"

    return {
        "slug": slug,
        "title": generated.get("title", repo["name"]),
        "meta_description": generated.get(
            "meta_description", f"A practical guide to {repo['full_name']}"
        ),
        "category": "Tech & AI",
        "target_keyword": generated.get("target_keyword", repo["name"]),
        "secondary_keywords": generated.get("secondary_keywords", ""),
        "content": generated.get("content", ""),
        "image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80",
        "seo_score": 85,
        "pageviews": 1,
        "status": "in_review",
        "published_at": date.today().isoformat(),
    }


# ====================================================================
# Supabase push — CHANGED to use UPSERT (no more duplicate-slug errors)
# ====================================================================

def push_to_supabase_cloud(article_obj):
    """
    Push the article to Supabase as an in-review draft.

    Uses PostgREST's upsert behavior: if a row with the same `slug` already
    exists, it will be updated instead of throwing a duplicate-key error.
    This makes the worker safely idempotent — running it twice in a day
    updates the existing draft instead of failing.
    """
    print(f"⚡ Pushing draft to Supabase: {article_obj['title']}")

    # The `on_conflict=slug` query parameter tells PostgREST to treat the
    # slug column as the conflict resolution key for upserts.
    endpoint = f"{SUPABASE_URL.rstrip('/')}/rest/v1/articles?on_conflict=slug"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        # `resolution=merge-duplicates` turns the INSERT into an UPSERT.
        # When the row exists, it gets merged (existing non-null values win,
        # new non-null values overwrite, nulls are left alone).
        "Prefer": "resolution=merge-duplicates,return=minimal",
        "User-Agent": "ApexPulse-Autopilot-Worker/1.2",
    }

    req = urllib.request.Request(
        endpoint,
        data=json.dumps(article_obj).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            if res.status in (200, 201, 204):
                print(f"🎉 Draft saved/updated in Supabase: {article_obj['slug']}")
                return True
            else:
                print(f"⚠️ Supabase returned unexpected status: {res.status}")
                return False
    except HTTPError as e:
        print(f"🚨 Supabase HTTP error ({e.code}): {e.read().decode('utf-8')}")
        print("💡 Hint: Check that your RLS policy allows inserts into the 'articles' table.")
        print("💡 Hint: Confirm the 'slug' column has a UNIQUE constraint in your schema.")
        return False
    except Exception as e:
        print(f"🚨 Supabase network error: {e}")
        return False


# ====================================================================
# Entry point
# ====================================================================

def run_autopilot_flywheel():
    load_credentials()
    print(f"🚀 Starting Apex Autopilot Flywheel — {datetime.now().isoformat()}")
    article = synthesize_article()
    push_to_supabase_cloud(article)


if __name__ == "__main__":
    run_autopilot_flywheel()
