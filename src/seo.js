/* ==========================================
   APEX SEO PULSE - CORE SEO & AI ENGINE
   Expert Real-Time Live Scoring & Technical Builders
============================================= */

window.ApexSEOEngine = {
  /**
   * Analyzes an article's raw content, title, and metadata against industry standard SEO practices
   * Returns a detailed 100-point scorecard with granular checklist criteria.
   */
  analyze(article) {
    const { title = "", targetKeyword = "", metaDescription = "", content = "" } = article;
    
    // Normalize target keyword
    const kw = targetKeyword.trim().toLowerCase();
    const cleanContent = this.stripMarkdownAndHtml(content);
    const words = cleanContent.split(/\s+/).filter(w => w.length > 0);
    const wordCount = words.length;
    
    const checklist = [];
    let totalScore = 0;
    const weights = {
      titleKw: 15,
      titleLen: 10,
      metaKw: 10,
      metaLen: 10,
      first100Words: 15,
      density: 15,
      h2Kw: 10,
      links: 5,
      altTags: 5,
      wordCount: 5
    };

    // 1. Title Keyword Check
    if (!kw) {
      checklist.push({ metric: "Target Keyword", passed: false, text: "No target keyword specified. Enter a primary keyword to start real-time scoring." });
    } else {
      const titleHasKw = title.toLowerCase().includes(kw);
      checklist.push({
        metric: "Title Keyword Match",
        passed: titleHasKw,
        text: titleHasKw ? `Exact target keyword "${kw}" found in article title.` : `Target keyword "${kw}" is missing from your title.`
      });
      if (titleHasKw) totalScore += weights.titleKw;
    }

    // 2. Title Length Check
    const titleLen = title.length;
    const titleLenPassed = titleLen >= 40 && titleLen <= 65;
    checklist.push({
      metric: "Title Length",
      passed: titleLenPassed,
      text: titleLenPassed ? `Title length is perfect (${titleLen} characters). Optimal is 40-65.` : `Title has ${titleLen} characters. Recommendation: keep between 40-65 characters to avoid truncation in Google SERPs.`
    });
    if (titleLenPassed) totalScore += weights.titleLen;

    // 3. Meta Description Keyword
    if (kw && metaDescription) {
      const metaHasKw = metaDescription.toLowerCase().includes(kw);
      checklist.push({
        metric: "Meta Description Keyword",
        passed: metaHasKw,
        text: metaHasKw ? `Target keyword found in meta description.` : `Target keyword missing from meta description.`
      });
      if (metaHasKw) totalScore += weights.metaKw;
    } else {
      checklist.push({ metric: "Meta Description Keyword", passed: false, text: "Add a meta description containing your keyword." });
    }

    // 4. Meta Description Length
    const metaLen = metaDescription.length;
    const metaLenPassed = metaLen >= 120 && metaLen <= 165;
    checklist.push({
      metric: "Meta Description Length",
      passed: metaLenPassed,
      text: metaLenPassed ? `Meta description length is excellent (${metaLen} characters).` : `Meta description has ${metaLen} chars. Optimal SEO snippet range is 120-165 characters.`
    });
    if (metaLenPassed) totalScore += weights.metaLen;

    // 5. Keyword in First 100 Words
    if (kw && words.length > 0) {
      const first100 = words.slice(0, 100).join(" ").toLowerCase();
      const inFirst100 = first100.includes(kw);
      checklist.push({
        metric: "Keyword in First 100 Words",
        passed: inFirst100,
        text: inFirst100 ? `Excellent: Target keyword appears within the introductory paragraph.` : `Target keyword should appear within the first 100 words to establish instant semantic intent.`
      });
      if (inFirst100) totalScore += weights.first100Words;
    } else {
      checklist.push({ metric: "Keyword in First 100 Words", passed: false, text: "Write introductory content." });
    }

    // 6. Keyword Density Meter
    if (kw && wordCount > 0) {
      // regex to find keyword occurrences
      const regex = new RegExp(kw.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'), 'gi');
      const matches = cleanContent.match(regex);
      const kwCount = matches ? matches.length : 0;
      const kwWords = kw.split(/\s+/).length;
      const density = ((kwCount * kwWords) / wordCount) * 100;
      
      const isOptimalDensity = density >= 0.8 && density <= 3.0;
      checklist.push({
        metric: "Keyword Density",
        passed: isOptimalDensity,
        text: isOptimalDensity 
          ? `Perfect keyword density: ${density.toFixed(2)}% (${kwCount} occurrences). Optimal is 0.8% - 3%.` 
          : (density < 0.8 
              ? `Low keyword density: ${density.toFixed(2)}%. Include your keyword more naturally.` 
              : `High keyword density: ${density.toFixed(2)}%. Warning: Risk of Google algorithmic penalty for keyword stuffing!`)
      });
      if (isOptimalDensity) totalScore += weights.density;
    } else {
      checklist.push({ metric: "Keyword Density", passed: false, text: "Insufficient word count to calculate density." });
    }

    // 7. Heading (H2/H3) Keyword Match
    if (kw && content) {
      const hMatches = content.match(/^(#{2,3}|<h2>|<h3>).*$/gm);
      let headingHasKw = false;
      if (hMatches) {
        headingHasKw = hMatches.some(h => h.toLowerCase().includes(kw));
      }
      checklist.push({
        metric: "Subheading (H2/H3) Optimization",
        passed: headingHasKw,
        text: headingHasKw ? `Target keyword embedded seamlessly inside H2/H3 subheadings.` : `Add your primary target keyword to at least one H2 or H3 heading.`
      });
      if (headingHasKw) totalScore += weights.h2Kw;
    } else {
      checklist.push({ metric: "Subheading (H2/H3) Optimization", passed: false, text: "No subheadings found." });
    }

    // 8. Links Counter (Internal & External)
    const links = content.match(/\[.*?\]\(.*?\)|<a href=".*?">/g) || [];
    const internalLinks = links.filter(l => l.includes("apexpulse") || l.includes("post-") || l.startsWith("[") && !l.includes("http"));
    const externalLinks = links.filter(l => l.includes("http") && !l.includes("apexpulse"));
    const linksPassed = links.length >= 2;
    checklist.push({
      metric: "Link Strategy",
      passed: linksPassed,
      text: linksPassed ? `Flawless internal (${internalLinks.length}) & external (${externalLinks.length}) interlinking.` : `Include at least 2 relevant outbound or internal links to boost domain trust.`
    });
    if (linksPassed) totalScore += weights.links;

    // 9. Image Alt Tags
    const images = content.match(/!\[.*?\]\(.*?\)|<img.*?>/g) || [];
    let altPassed = true;
    if (images.length > 0) {
      altPassed = images.every(img => img.includes("![") && !img.startsWith("![]") || img.includes("alt=") && !img.includes('alt=""'));
    } else {
      altPassed = false;
    }
    checklist.push({
      metric: "Image Alt Attributes",
      passed: altPassed,
      text: images.length === 0 ? `No rich media found. Embed at least one high-quality image with descriptive ALT text.` : (altPassed ? `All embedded media files have rich SEO descriptive ALT tags.` : `Warning: Some embedded images are missing ALT text.`)
    });
    if (altPassed && images.length > 0) totalScore += weights.altTags;

    // 10. Word Count for Pillar SEO
    const wordCountPassed = wordCount >= 500;
    checklist.push({
      metric: "Exhaustive Content (Word Count)",
      passed: wordCountPassed,
      text: wordCountPassed ? `Comprehensive piece (${wordCount} words). High topical authority.` : `Article has ${wordCount} words. Expert SEO guides generally require > 500 words to outperform core competitors.`
    });
    if (wordCountPassed) totalScore += weights.wordCount;

    // Estimate Readability
    const readability = this.calculateReadability(cleanContent);

    // Give a bonus if target keyword is not specified to not discourage initial drafting
    if (!kw) totalScore = Math.min(65, totalScore + 30);

    return {
      score: Math.min(100, Math.max(12, totalScore)),
      wordCount,
      readingTime: Math.ceil(wordCount / 200) + " min read",
      readability,
      checklist
    };
  },

  stripMarkdownAndHtml(text) {
    if (!text) return "";
    return text
      .replace(/<[^>]*>?/gm, '') // HTML tags
      .replace(/([#*>`~_-])/g, '') // Markdown chars
      .replace(/\[(.*?)\]\(.*?\)/g, '$1') // Markdown links
      .replace(/\n+/g, ' ')
      .trim();
  },

  calculateReadability(text) {
    if (!text) return { score: 100, label: "Simple" };
    const words = text.split(/\s+/).filter(w => w.length > 0);
    const sentences = text.split(/[\.\?!]\s+/).filter(s => s.length > 0);
    
    if (words.length === 0 || sentences.length === 0) return { score: 100, label: "Simple" };

    const avgWordsPerSentence = words.length / sentences.length;
    // Simple rough estimation of syllables
    const syllables = words.reduce((acc, word) => {
      acc += Math.max(1, word.replace(/(?:[^laeiouy]|ed|es|e)$/eme, '').match(/[aeiouy]{1,2}/gi)?.length || 1);
      return acc;
    }, 0);
    const avgSyllablesPerWord = syllables / words.length;

    // Flesch Reading Ease Formula
    const flesch = 206.835 - (1.015 * avgWordsPerSentence) - (84.6 * avgSyllablesPerWord);
    const score = Math.max(0, Math.min(100, Math.round(flesch)));

    let label = "Standard (Optimal for Web)";
    if (score > 80) label = "Easy (Conversational)";
    else if (score < 50) label = "Advanced / Academic";

    return { score, label };
  },

  /**
   * Auto-slug generator removing English stop words for ultra-clean SERP slugs
   */
  generateSlug(title) {
    const stopWords = ["a", "an", "the", "and", "or", "but", "in", "on", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once"];
    const cleaned = title
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .split(/\s+/)
      .filter(w => !stopWords.includes(w) && w.length > 0)
      .join("-");
    return cleaned || "daily-article";
  },

  /**
   * Builds Google Search JSON-LD structured data script
   */
  generateSchema(article) {
    const { title, metaDescription, publishedAt, author, image } = article;
    const schema = {
      "@context": "https://schema.org",
      "@type": "BlogPosting",
      "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": `https://apexpulse.com/blog/${article.slug}`
      },
      "headline": title || "Apex Pulse Daily Dispatch",
      "description": metaDescription || "Expert software engineering and professional blog post.",
      "image": image || "https://apexpulse.com/og-default.jpg",
      "author": {
        "@type": "Person",
        "name": author?.name || "Alex Rivera",
        "jobTitle": author?.role || "Principal Software Engineer"
      },
      "publisher": {
        "@type": "Organization",
        "name": "ApexSEO Pulse Studio",
        "logo": {
          "@type": "ImageObject",
          "url": "https://apexpulse.com/logo.png"
        }
      },
      "datePublished": publishedAt || new Date().toISOString().split('T')[0],
      "dateModified": publishedAt || new Date().toISOString().split('T')[0]
    };

    return JSON.stringify(schema, null, 2);
  },

  /**
   * AI Idea & Keyword Generator interactive helper
   */
  brainstormTopics(niche) {
    const defaultIdeas = {
      "Tech & AI": [
        { title: "Building a Fully Autonomous AI Agent with WebSockets in 2026", kw: "Autonomous AI Agent", intent: "Transactional / High Value" },
        { title: "SearchGPT vs Google SGE: An Architectural Performance Benchmark", kw: "SearchGPT benchmark", intent: "Informational" },
        { title: "Rust vs Go for High-Concurrency Microservices: 1M Requests/Sec Test", kw: "Rust vs Go microservices", intent: "Technical Expert" }
      ],
      "SEO & Marketing": [
        { title: "15 Zero-Volume Click Keywords That Generated $100k in Pipeline", kw: "Zero volume keywords", intent: "Viral Growth" },
        { title: "How to Recover From Google's Helpful Content Penalty in 7 Days", kw: "Helpful content recovery", intent: "High Emergency Intent" },
        { title: "The Enterprise Internal Linking Checklist Built by Principal Engineers", kw: "Enterprise internal linking", intent: "B2B Authority" }
      ],
      "Startups & Growth": [
        { title: "How We Built a 30-Day Daily Publishing Streak That Tripled Our MRR", kw: "Daily publishing streak", intent: "Case Study" },
        { title: "Bootstrapping to $1M ARR With Programmatic Jamstack SEO", kw: "Bootstrapping programmatic SEO", intent: "Founder Intent" },
        { title: "The Open Source Community Flywheel: GitHub Stars to Paid Customers", kw: "Open source customer flywheel", intent: "Growth Hacker" }
      ]
    };

    return defaultIdeas[niche] || defaultIdeas["Tech & AI"];
  }
};
