/* ====================================================================
   APEX PULSE — SUPABASE CLOUD CONNECTOR
   Modular REST Helper with zero external npm compilation dependencies.
   Safely manages Live Supabase Storage or falls back to Persistent Memory.
==================================================================== */

window.ApexSupabase = {
  // Credentials are loaded from browser localStorage after the user
  // enters them via the "SEO Vault" settings panel. No hardcoded keys
  // are shipped in the source. Keep your Supabase anon / service-role
  // keys out of git at all times.
  config() {
    return {
      url: localStorage.getItem("apex_supabase_url") || "",
      key: localStorage.getItem("apex_supabase_key") || "",
    };
  },

  isConnected() {
    const c = this.config();
    return c.url.trim() !== "" && c.key.trim() !== "" && c.url.startsWith("https://");
  },

  saveCredentials(url, key) {
    try {
      const cleanUrl = url.trim().replace(/\/$/, "");
      localStorage.setItem("apex_supabase_url", cleanUrl);
      localStorage.setItem("apex_supabase_key", key.trim());
      return true;
    } catch(e) {
      return false;
    }
  },

  disconnect() {
    localStorage.removeItem("apex_supabase_url");
    localStorage.removeItem("apex_supabase_key");
  },

  /**
   * Data Transfer Object (DTO) Adapter mapping snake_case PostgreSQL rows to camelCase Frontend State
   */
  normalizeArticle(row) {
    if (!row) return null;
    return {
      id: row.id,
      slug: row.slug,
      title: row.title || "",
      metaDescription: row.meta_description || row.metaDescription || "",
      category: row.category || "Tech & AI",
      targetKeyword: row.target_keyword || row.targetKeyword || "",
      secondaryKeywords: row.secondary_keywords || row.secondaryKeywords || "",
      content: row.content || "",
      image: row.image_url || row.image || "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80",
      seoScore: row.seo_score || row.seoScore || 85,
      pageviews: row.pageviews || 1,
      status: row.status || "in_review",
      publishedAt: row.published_at || row.publishedAt || new Date().toISOString().split("T")[0],
      author: row.author || {
        name: "Alex Rivera",
        role: "Principal Systems Architect",
        avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=160&q=80"
      }
    };
  },

  /**
   * Universal REST fetch wrapper for Supabase PostgREST Endpoints
   */
  async request(path, method = "GET", body = null) {
    if (!this.isConnected()) {
      throw new Error("Supabase cloud database is not connected.");
    }

    const { url, key } = this.config();
    const endpoint = `${url}/rest/v1/${path.replace(/^\//, "")}`;
    
    const headers = {
      "apikey": key,
      "Authorization": `Bearer ${key}`,
      "Content-Type": "application/json",
      "Prefer": "return=representation"
    };

    const options = {
      method,
      headers
    };

    if (body && (method === "POST" || method === "PATCH" || method === "PUT")) {
      options.body = JSON.stringify(body);
    }

    try {
      const res = await fetch(endpoint, options);
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.message || `HTTP error ${res.status}`);
      }
      return await res.json();
    } catch(err) {
      console.error("Supabase Cloud API Error:", err);
      throw err;
    }
  },

  /**
   * Fetch live public published articles from Supabase Cloud
   */
  async fetchLiveArticles() {
    if (!this.isConnected()) {
      // Gracefully yield back to sandboxed persistent memory if offline
      return window.ApexStateManager.getArticles();
    }
    
    // Request only fully approved pieces to protect your Google Helpful Content authority
    const res = await this.request("articles?status=eq.published&order=published_at.desc");
    return Array.isArray(res) ? res.map(r => this.normalizeArticle(r)) : window.ApexStateManager.getArticles();
  },

  /**
   * Fetch highly sensitive drafts or items currently waiting in the Human Moderation Queue
   */
  async fetchModerationQueue() {
    if (!this.isConnected()) {
      const local = window.ApexStateManager.getArticles();
      return local.filter(a => a.status === "in_review");
    }

    const res = await this.request("articles?status=eq.in_review&order=created_at.desc");
    return Array.isArray(res) ? res.map(r => this.normalizeArticle(r)) : [];
  },

  /**
   * Insert or update an affiliate piece into Supabase Cloud Database
   */
  async saveArticle(articleObj) {
    if (!this.isConnected()) {
      // Run normal LocalStorage manager execution
      const list = window.ApexStateManager.getArticles();
      const existingIdx = list.findIndex(a => a.id === articleObj.id || a.slug === articleObj.slug);
      if (existingIdx >= 0) {
        list[existingIdx] = articleObj;
      } else {
        list.unshift(articleObj);
      }
      window.ApexStateManager.saveArticles(list);
      return articleObj;
    }

    // Prepare robust row object matching PostgreSQL schema
    const payload = {
      slug: articleObj.slug || window.ApexSEOEngine.generateSlug(articleObj.title),
      title: articleObj.title,
      meta_description: articleObj.metaDescription || "Affiliate technical guide piece.",
      category: articleObj.category || "Tech & AI",
      target_keyword: articleObj.targetKeyword || "Affiliate topic",
      secondary_keywords: articleObj.secondaryKeywords || "",
      content: articleObj.content,
      image_url: articleObj.image || "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80",
      seo_score: articleObj.seoScore || 85,
      pageviews: articleObj.pageviews || 1,
      status: articleObj.status || "published",
      published_at: articleObj.publishedAt || new Date().toISOString().split("T")[0]
    };

    // Upsert directly into Supabase Cloud
    const result = await this.request("articles", "POST", payload);
    return result?.[0] || articleObj;
  }
};
