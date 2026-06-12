/* ==========================================
   APEX SEO PULSE - PRODUCTION EXPORT ENGINE
   Static HTML generator, XML Sitemap & Robots.txt setup
============================================= */

window.ApexExporter = {
  /**
   * Generates a fully contained, pristine standalone HTML page for an article
   * Includes complete Open Graph meta tags, Schema JSON-LD, clean typography, and responsive styling.
   */
  generateStandaloneArticleHtml(article) {
    const { title, slug, category, metaDescription, publishedAt, readingTime, author, image, content } = article;
    const domain = "https://apexpulse.com";
    const postUrl = `${domain}/blog/${slug}`;
    const schemaJson = window.ApexSEOEngine.generateSchema(article);
    
    // Parse Markdown to simple HTML for standalone export
    const renderedContent = this.parseSimpleMarkdown(content);

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  
  <!-- Technical SEO Premium Meta Tags -->
  <title>${title} | ApexSEO Pulse Platform</title>
  <meta name="description" content="${metaDescription}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <link rel="canonical" href="${postUrl}">
  
  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="article">
  <meta property="og:url" content="${postUrl}">
  <meta property="og:title" content="${title}">
  <meta property="og:description" content="${metaDescription}">
  <meta property="og:image" content="${image}">
  <meta property="article:published_time" content="${publishedAt}">
  <meta property="article:author" content="${author?.name || 'Alex Rivera'}">
  <meta property="article:section" content="${category}">
  
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:url" content="${postUrl}">
  <meta name="twitter:title" content="${title}">
  <meta name="twitter:description" content="${metaDescription}">
  <meta name="twitter:image" content="${image}">
  
  <!-- Embedded Typography & Modern Styling -->
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #0f172a; }
    .prose { max-width: 800px; margin: 0 auto; font-size: 1.125rem; line-height: 1.8; }
    .prose h1 { font-size: 2.75rem; font-weight: 800; line-height: 1.2; margin-bottom: 1.5rem; }
    .prose h2 { font-size: 1.85rem; font-weight: 700; margin-top: 2.5rem; margin-bottom: 1rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; }
    .prose h3 { font-size: 1.35rem; font-weight: 700; margin-top: 2rem; margin-bottom: 0.75rem; }
    .prose p { margin-bottom: 1.5rem; }
    .prose a { color: #4f46e5; text-decoration: underline; font-weight: 600; }
    .prose blockquote { border-left: 4px solid #4f46e5; padding-left: 1.25rem; font-style: italic; color: #64748b; margin: 2rem 0; background-color: #e0e7ff; padding: 1rem 1.25rem; border-radius: 0 0.5rem 0.5rem 0; }
    .prose pre { background-color: #0f172a; color: #f8fafc; padding: 1.25rem; border-radius: 0.75rem; overflow-x: auto; font-family: monospace; font-size: 0.95rem; margin: 1.5rem 0; }
    .prose img { width: 100%; border-radius: 1rem; margin: 2rem 0; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
  </style>
  
  <!-- Structured Data JSON-LD -->
  <script type="application/ld+json">
    ${schemaJson}
  </script>
</head>
<body class="min-h-screen flex flex-col">

  <!-- Minimal Expert Header -->
  <header class="bg-white border-b border-slate-200 sticky top-0 z-30">
    <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
      <a href="${domain}" class="flex items-center gap-3 text-xl font-extrabold text-slate-900">
        <span class="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-black">⚡</span>
        <span>ApexSEO <span class="text-indigo-600">Pulse</span></span>
      </a>
      <div class="flex items-center gap-6 font-semibold text-slate-600">
        <a href="${domain}" class="hover:text-indigo-600">Explore Blog</a>
        <a href="${domain}/daily" class="hover:text-indigo-600">Daily Dispatch</a>
      </div>
    </div>
  </header>

  <!-- Main Article Body -->
  <main class="flex-1 py-16 px-6">
    <article class="max-w-4xl mx-auto bg-white rounded-3xl border border-slate-200 shadow-xl p-8 sm:p-14">
      
      <!-- Article Metadata -->
      <div class="flex items-center gap-3 text-sm font-bold uppercase tracking-wider text-indigo-600 mb-6">
        <span class="bg-indigo-50 px-3 py-1 rounded-full">${category}</span>
        <span class="text-slate-400">•</span>
        <span class="text-slate-500">${publishedAt}</span>
        <span class="text-slate-400">•</span>
        <span class="text-slate-500">${readingTime}</span>
      </div>
      
      <h1 class="text-3xl sm:text-5xl font-black text-slate-900 leading-tight mb-8">${title}</h1>
      
      <!-- Author Card -->
      <div class="flex items-center gap-4 py-6 border-y border-slate-100 mb-10 bg-slate-50 px-6 rounded-2xl">
        <img src="${author?.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=160&q=80'}" alt="${author?.name}" class="w-14 h-14 rounded-full object-cover shadow-md">
        <div>
          <div class="font-extrabold text-slate-900">${author?.name || 'Alex Rivera'}</div>
          <div class="text-sm font-semibold text-indigo-600">${author?.role || 'Principal Software Engineer'}</div>
        </div>
        <div class="ml-auto text-xs font-bold text-slate-500 bg-white px-3 py-1.5 rounded-xl border border-slate-200 shadow-sm">
          ⚡ Daily Publisher
        </div>
      </div>
      
      <!-- Hero Image -->
      ${image ? `<img src="${image}" alt="${title}" class="w-full h-[400px] object-cover rounded-3xl mb-12 shadow-xl">` : ''}
      
      <!-- Prose Written Content -->
      <div class="prose">
        ${renderedContent}
      </div>

      <!-- Article End Footer CTA -->
      <div class="mt-16 pt-10 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-6 bg-indigo-950 text-white p-8 rounded-3xl shadow-lg">
        <div>
          <div class="text-xl font-black mb-1">Loved this daily technical breakdown?</div>
          <div class="text-sm text-indigo-200">Join 45,000+ software engineers getting our high-traffic daily pieces.</div>
        </div>
        <a href="${domain}/newsletter" class="bg-indigo-600 hover:bg-indigo-500 px-6 py-3 rounded-xl font-bold text-white shadow-md transition transform hover:-translate-y-0.5">
          Subscribe to Daily Drop
        </a>
      </div>

    </article>
  </main>

  <!-- Production Footer -->
  <footer class="bg-slate-900 text-slate-400 py-12 px-6 mt-20 border-t border-slate-800">
    <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
      <div class="flex items-center gap-3 text-white font-extrabold">
        ⚡ ApexSEO Pulse Production Platform
      </div>
      <div class="text-sm">
        © 2026 ApexSEO Pulse. Optimized for maximum page speed and Google crawling.
      </div>
    </div>
  </footer>

</body>
</html>`;
  },

  /**
   * Complete standard XML Sitemap Generator
   */
  generateSitemapXml(articles) {
    const domain = "https://apexpulse.com";
    let urls = `<url>
    <loc>${domain}</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>${domain}/categories</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>`;

    articles.forEach(art => {
      urls += `\n  <url>
    <loc>${domain}/blog/${art.slug}</loc>
    <lastmod>${art.publishedAt || new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>`;
    });

    return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  ${urls}
</urlset>`;
  },

  /**
   * Enterprise Robots.txt Generator
   */
  generateRobotsTxt() {
    return `# ========================================================
# Enterprise Robots.txt for ApexSEO Pulse Platform
# Configured for instant indexing & AI scraper management
# ========================================================

User-agent: *
Allow: /
Disallow: /admin/
Disallow: /private-drafts/
Disallow: /api/

# Explicit instructions for AI web crawlers
User-agent: GPTBot
Allow: /blog/

User-agent: ClaudeBot
Allow: /blog/

# XML Sitemap Directive
Sitemap: https://apexpulse.com/sitemap.xml`;
  },

  /**
   * Helper to parse simple markdown to clean HTML tags
   */
  parseSimpleMarkdown(md) {
    if (!md) return "";
    let html = md
      .replace(/^### (.*$)/gim, (match, p1) => `<h3 id="${window.ApexSEOEngine.generateSlug(p1.trim())}">${p1}</h3>`)
      .replace(/^## (.*$)/gim, (match, p1) => `<h2 id="${window.ApexSEOEngine.generateSlug(p1.trim())}">${p1}</h2>`)
      .replace(/^# (.*$)/gim, (match, p1) => `<h1 id="${window.ApexSEOEngine.generateSlug(p1.trim())}">${p1}</h1>`)
      .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
      .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/gim, '<em>$1</em>')
      .replace(/\[(.*?)\]\((.*?)\)/gim, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
      .replace(/\n\n/gim, '</p><p>');

    // Handle code blocks
    html = html.replace(/```(?:\w+)?\n([\s\S]*?)```/gm, (match, code) => {
      return `<pre><code>${this.escapeHtml(code.trim())}</code></pre>`;
    });

    return `<p>${html}</p>`;
  },

  escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  },

  downloadFile(filename, content, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 200);
  }
};
