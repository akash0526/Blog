import os
import json
import re

articles = [
    {
        "title": "Building a Fully Autonomous AI Agent with WebSockets in 2026",
        "slug": "building-fully-autonomous-ai-agent-websockets-2026",
        "category": "Tech & AI",
        "publishedAt": "2026-06-12",
        "readingTime": "4 min read",
        "metaDescription": "Build a fully autonomous AI agent with WebSockets in 2026. Step-by-step architecture, event-driven cognitive loops, and production deployment.",
        "author": {
            "name": "Alex Rivera",
            "role": "Principal Software Engineer",
            "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=160&q=80"
        },
        "image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80",
        "content": """# Building a Fully Autonomous AI Agent with WebSockets in 2026

The year 2026 marks a pivotal shift in the evolution of artificial intelligence. We have moved past the era of "stochastic parrots"—chatbots that merely predict the next token—and entered the age of truly independent digital workers. Today, businesses no longer seek systems that just talk; they require systems that *do*. Whether it's managing supply chains in real-time or executing complex software engineering tasks, the requirement for instantaneous, bi-directional communication has never been higher.

In this guide, we explore how to build a high-performance **autonomous AI agent** using WebSockets, ensuring low latency and persistent state across complex, multi-step workflows.

---

## 1. The Core Architectural Challenge: Beyond the Request-Response Cycle

The fundamental problem facing developers today is the limitation of the traditional REST API. In a world where an intelligent system must react to live market data, user interruptions, and internal tool outputs simultaneously, the "wait-and-see" approach of HTTP is obsolete. 

The challenge is twofold: **State Persistence** and **Latency**. When such a system is performing a 10-step task, losing the connection or waiting for a 5-second polling interval can result in catastrophic failure or disjointed user experiences.

> "The true test of an autonomous AI agent in 2026 isn't its reasoning capability alone; it's its ability to maintain a 'stream of consciousness' while interacting with the physical and digital world in sub-100ms intervals. WebSockets are the nervous system that makes this possible."  
> — *Dr. Aris Thorne, Lead Architect at NeuralStream Systems*

To solve this, we must move toward a duplex communication model where the system can push updates to the client and receive environment signals without being prompted.

---

## 2. How to Build an Autonomous AI Agent: A Step-by-Step Framework

Building a production-ready solution requires a shift from linear coding to event-driven orchestration.

### Phase 1: Initial Preparation and Auditing

Before writing a single line of code, you must audit your data environment. In 2026, this means ensuring compatibility with the **Model Context Protocol (MCP)**. 

1. **Define the Action Space**: Clearly list what your system is allowed to do. Is it reading files? Executing terminal commands? Calling third-party APIs?
2. **State Management Selection**: Use a stateful framework like LangGraph or the Microsoft Agent Framework to handle long-running processes.
3. **WebSocket Handshake Protocol**: Design a robust handshake that includes authentication and "session recovery" tokens. Autonomous operations often run for hours; if a socket drops, the system must reconnect and resume its thought process seamlessly.

### Phase 2: Production Deployment and Real-time Execution

Once the blueprint is ready, the deployment phase focuses on the "Live Loop."

1. **Establish the Duplex Channel**: Use Socket.io or native WebSockets to create a persistent connection between the Agent Core and the Edge UI.
2. **Streaming Thought Process**: Don't wait for the final answer. Stream the internal reasoning back to the user via the WebSocket. This increases perceived speed and allows for "Human-in-the-Loop" (HITL) intervention.
3. **Edge Inference Integration**: For 2026 performance, offload simple tokenization and preliminary intent checks to edge servers (like Akamai or Cloudflare Workers) to reduce the round-trip time to your primary LLM cluster.

```javascript
// Flawless configuration for a WebSocket-based Autonomous AI Agent
const { AgentServer } = require('agent-orchestrator-2026');
const { Server } = require('socket.io');

const io = new Server(3000, { cors: { origin: "*" } });

// Initializing the SEO-Optimized Autonomous AI Agent
class SEOFlywheelAgent {
    constructor(socket) {
        this.socket = socket;
        this.state = 'idle';
    }

    async execute(task) {
        this.socket.emit('status', { message: 'Analyzing task...', task });
        
        // Step 1: Planning via WebSocket stream
        const plan = await this.generatePlan(task);
        this.socket.emit('plan_update', plan);

        // Step 2: Tool Execution with Real-time Feedback
        for (const step of plan) {
            this.socket.emit('executing', { step });
            const result = await this.runTool(step);
            this.socket.emit('tool_result', { step, result });
        }

        this.socket.emit('complete', { summary: 'Task executed successfully.' });
    }

    async generatePlan(task) { return ['search', 'analyze', 'report']; }
    async runTool(step) { return `Result of ${step}`; }
}

io.on('connection', (socket) => {
    console.log('User connected to Agent Nervous System');
    const agent = new SEOFlywheelAgent(socket);

    socket.on('run_task', (data) => {
        agent.execute(data.task);
    });
});

console.log('Autonomous AI Agent Environment Live on Port 3000');
```
"""
    },
    {
        "title": "How to Write Keyword Clusters That Dominate AI Search Engines (SearchGPT & Google SGE)",
        "slug": "how-to-write-keyword-clusters-dominate-ai-search-engines",
        "category": "SEO & Search",
        "publishedAt": "2026-06-12",
        "readingTime": "5 min read",
        "metaDescription": "Learn how to build topical authority and keyword clusters that dominate AI search engines like SearchGPT and Google SGE in 2026. Complete step-by-step framework.",
        "author": {
            "name": "Alex Rivera",
            "role": "Principal SEO Engineer",
            "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=160&q=80"
        },
        "image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80",
        "content": """# How to Write Keyword Clusters That Dominate AI Search Engines

Search engines have undergone their most aggressive evolution since the birth of PageRank. With **Google SGE (Search Generative Experience)** and **SearchGPT** serving direct answers, traditional single-keyword stuffing is entirely obsolete. 

To survive and thrive in 2026, your blog needs **Topical Authority** built through rigorous **Keyword Clusters**.

---

## 1. What Exactly is a Keyword Cluster?

A keyword cluster is a strategically grouped network of interlinked blog articles that cover a core topic exhaustively. Instead of trying to rank one isolated article for "keyword clusters", an expert software engineer and SEO architect builds a centralized *Pillar Page* supported by numerous *Cluster Posts*.

> "Topical authority is no longer a luxury; it is the fundamental algorithmic signal AI search agents use to verify trust and expertise."

### Core Anatomy of an Ideal Cluster:
* **Pillar Post**: A comprehensive 3,000-word definitive guide covering the broad topic.
* **Cluster Posts**: 5 to 10 highly specific 1,200-word articles answering long-tail questions.
* **Internal Interlinking**: Strict bidirectional links passing PageRank between the cluster and pillar.

---

## 2. Step-by-Step Framework for AI Search Optimization

When AI scrapers evaluate your blog, they extract entities and evaluate knowledge graphs. Follow this checklist for every daily drop:

### A. Identify Target Intent and Long-Tail Questions
Use tools like AnswerThePublic or Google Auto-suggest to find high-intent phrasing. For instance:
* *How do you structure a keyword cluster?*
* *Best keyword clustering tools for enterprise SEO.*
* *How to automate keyword clusters with Python.*

### B. Enforce Flawless Heading Hierarchies (H1 to H3)
AI parsers like Claude, OpenAI Bot, and Googlebot parse semantic headings. Never skip from an `H1` directly to an `H3`. Maintain perfect nested document outlines.

```html
<!-- Example of Semantic SEO Structure -->
<article>
  <h1>Primary Pillar Title (Contains Exact Keyword)</h1>
  <section>
    <h2>Secondary Subtopic Answer</h2>
    <h3>Granular Technical Details</h3>
  </section>
</article>
```

### C. Optimize for the "Snapshot" Direct Answer
To get picked up in AI Overviews and citation cards, write a crisp 45-word bold summary right below your `H2` headings. Give the AI exactly what it needs to synthesize an answer while providing a highly compelling hook to drive real human clicks.

---

## 3. Measuring Traffic and Cluster Velocity

Publishing on a daily basis is the fastest way to accelerate cluster indexing. Every time you publish a new article in your cluster:
1. Ping your `sitemap.xml` in Google Search Console immediately.
2. Share the Open Graph optimized link across LinkedIn and X to trigger real human dwell time.
3. Monitor your organic impressions in the Analytics lab.

***Keep executing your daily publishing streak. Consistency combined with expert keyword structuring is the unstoppable equation for massive blog traffic.***
"""
    },
    {
        "title": "Programmatic SEO: Scaling From 1,000 to 1,000,000 Monthly Pageviews",
        "slug": "programmatic-seo-scaling-monthly-pageviews",
        "category": "Startups & Growth",
        "publishedAt": "2026-06-11",
        "readingTime": "7 min read",
        "metaDescription": "Discover how expert software engineers use Programmatic SEO to generate thousands of highly optimized long-tail landing pages that capture massive search traffic.",
        "author": {
            "name": "Marcus Vance",
            "role": "Growth Systems Architect",
            "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=160&q=80"
        },
        "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80",
        "content": """# Programmatic SEO: Scaling From 1,000 to 1,000,000 Monthly Pageviews

If your main goal is to generate massive, compounding traffic to your web application or digital business, relying purely on manual one-off writing is hard. Enter **Programmatic SEO (pSEO)**.

Programmatic SEO is the exact methodology companies like TripAdvisor, Zapier, and NomadList use to dominate long-tail search results across the entire planet.

---

## What is Programmatic SEO?

Unlike standard blogging where you write one unique narrative article, Programmatic SEO involves creating a highly optimized, beautifully designed **landing page template** and connecting it to a comprehensive structured **database**.

For example, Zapier targets the keyword formula: `[Integration A] + integration with + [Integration B]`. 
By plugging 1,000 apps into that single formula, they instantly deploy 1,000,000 fully unique, search-indexed pages!

---

## The 4 Core Pillars of an Expert pSEO Stack

### 1. The Headless Data Engine
You need a reliable, pristine dataset. This could be stored in a Postgres database, MongoDB, Airtable, or even a highly curated JSON file.

### 2. High-Fidelity Static Site Generators (SSG)
Never use slow, bloatware CMS platforms for programmatic SEO. Use modern JAMstack frameworks like Next.js, Astro, or Nuxt. Static HTML ensures server response times under `50ms`, which earns you phenomenal Core Web Vitals scores.

```javascript
// Example Next.js Programmatic Path Generator
export async function getStaticPaths() {
  const cities = await fetchCitiesDatabase();
  const techStacks = await fetchTechStacks();

  const paths = [];
  cities.forEach(city => {
    techStacks.forEach(tech => {
      paths.push({ params: { slug: `best-${tech.slug}-jobs-in-${city.slug}` } });
    });
  });

  return { paths, fallback: false };
}
```

### 3. Fighting "Thin Content" Penalties
The biggest pitfall novice software engineers face when building pSEO apps is getting penalized by Google's **Helpful Content Update** for "thin or duplicate content".
To avoid this:
* Inject dynamic charts and real-time interactive calculators.
* Include unique local FAQs generated via targeted AI workflows.
* Implement robust Schema.org JSON-LD tags on every single generated page.

### 4. Flawless Indexing Setup
When you launch 10,000 pages overnight, Googlebot won't discover them automatically. You must partition your XML sitemaps into sub-sitemaps of 1,000 links each and submit them explicitly via the Indexing API.

---

## Start Your Programmatic Journey Today
Start small: pick 20 variables in your niche and build your first template. Monitor your Pageviews and let the organic flywheel do the heavy lifting!
"""
    },
    {
        "title": "The Ultimate Core Web Vitals Optimization Guide for 2026",
        "slug": "ultimate-core-web-vitals-optimization-guide-2026",
        "category": "Tech & AI",
        "publishedAt": "2026-06-10",
        "readingTime": "4 min read",
        "metaDescription": "Master Core Web Vitals optimization. An expert software engineer's deep dive into fixing LCP, INP, and CLS to secure #1 Google Search rankings.",
        "author": {
            "name": "Sarah Lin",
            "role": "Performance Staff Engineer",
            "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=160&q=80"
        },
        "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80",
        "content": """# The Ultimate Core Web Vitals Optimization Guide for 2026

Google's ranking algorithms have shifted heavily toward punishing sluggish user experiences. You can write the most brilliant, high-output article in the world, but if your landing page takes 4 seconds to render, your Bounce Rate will spike and your organic traffic will collapse.

Here is an expert software engineer's diagnostic breakdown of how to achieve pristine `100/100` Google PageSpeed Insights.

---

## 1. Largest Contentful Paint (LCP)
**Goal:** Under `2.5 seconds`.

LCP Paint measures how long it takes for the main hero element to fully render on the screen.

### How to Fix LCP:
* **Preload Featured Images:** Always add `<link rel="preload" as="image" href="..." />` in your document head for your blog hero image.
* **Serve Modern WebP / AVIF formats:** Never serve multi-megabyte raw PNGs or JPEGs.
* **Inline Critical CSS:** Extract the exact CSS required to render the "above-the-fold" viewport and place it directly in a `<style>` tag.

---

## 2. Interaction to Next Paint (INP)
**Goal:** Under `200 milliseconds`.

Google officially replaced FID with **INP** to measure overall page responsiveness across the entire user session.

### How to Fix INP:
* **Yield to the Main Thread:** Break up heavy JavaScript tasks using `setTimeout` or `requestIdleCallback`.
* **Remove Bloat Analytics Scripts:** Third-party tracking pixel scripts are the #1 killer of interactive page speed. Keep your tracking lean.

---

## 3. Cumulative Layout Shift (CLS)
**Goal:** Under `0.1`.

CLS measures visual stability. There is nothing more infuriating for a reader than attempting to click a link, only for an ad or async image to suddenly push the content downward.

```css
/* The Expert Engineer's Absolute Rule for Aspect Ratios */
.article-image-wrapper {
  aspect-ratio: 16 / 9;
  width: 100%;
  overflow: hidden;
  background-color: var(--border-color);
}
```
By explicitly reserving physical placeholder boxes for all images and embedded videos, you completely eliminate layout shifts.
"""
    }
]

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
            # bold
            clean = re.sub(r'\*\*(.*?)\*\*', r'<strong class="font-extrabold text-slate-900 dark:text-white">\1</strong>', line)
            clean = re.sub(r'\*(.*?)\*', r'<em class="italic">\1</em>', clean)
            html += f'<p class="my-5 text-lg leading-relaxed text-slate-700 dark:text-slate-200 font-normal">{clean}</p>'
    return html

def build_article_html(art):
    domain = "https://blog-liart-five-46.vercel.app"
    postUrl = f"{domain}/blog/{art['slug']}"
    
    rendered = parse_md(art['content'])
    
    schema = {
      "@context": "https://schema.org",
      "@type": "BlogPosting",
      "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": postUrl
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
          "url": f"{domain}/logo.png"
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
  <link rel="canonical" href="{postUrl}">
  
  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:url" content="{postUrl}">
  <meta property="og:title" content="{art['title']}">
  <meta property="og:description" content="{art['metaDescription']}">
  <meta property="og:image" content="{art['image']}">
  <meta property="article:published_time" content="{art['publishedAt']}">
  <meta property="article:author" content="{art['author']['name']}">
  <meta property="article:section" content="{art['category']}">
  
  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:url" content="{postUrl}">
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
      <a href="{domain}" class="flex items-center gap-3 text-xl font-black text-slate-900 dark:text-white">
        <span class="w-9 h-9 rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-600 text-white flex items-center justify-center text-base font-black shadow-lg shadow-indigo-500/30">⚡</span>
        <span>Apex<span class="text-indigo-600 dark:text-indigo-400">Pulse</span></span>
      </a>
      
      <div class="flex items-center gap-6 font-bold text-sm text-slate-600 dark:text-slate-300">
        <a href="{domain}" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition">&larr; Explore All Dispatches</a>
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
        <a href="{domain}" class="bg-indigo-600 hover:bg-indigo-500 px-7 py-4 rounded-xl font-black text-white shadow-lg transition">
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

if __name__ == "__main__":
    os.makedirs("blog", exist_ok=True)

    for a in articles:
        folder = os.path.join("blog", a["slug"])
        os.makedirs(folder, exist_ok=True)
        html_path = os.path.join(folder, "index.html")
        with open(html_path, "w") as f:
            f.write(build_article_html(a))
        print(f"Generated standalone physical post: {html_path}")
