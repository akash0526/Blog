/* ====================================================================
   APEX PULSE — SUPABASE CLOUD CONNECTOR
   Modular REST Helper with zero external npm compilation dependencies.
   Safely manages Live Supabase Storage or falls back to Persistent Memory.
==================================================================== */

window.ApexSupabase = {
  // Configured with your secure Cloud credentials
  config() {
    return {
      url: localStorage.getItem("apex_supabase_url") || "https://qygrnvneeoxotpzgolvp.supabase.co",
      key: localStorage.getItem("apex_supabase_key") || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF5Z3Judm5lZW94b3RwemdvbHZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2MDA2MjAsImV4cCI6MjA5NzE3NjYyMH0.qRItOoiqDo2lpUo4J38T-QJyWCHDL-zVsTUWrzy0xV0",
    };
  },

  isConnected() {
    const c = this.config();
    return c.url.trim() !== "" && c.key.trim() !== "";
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
    return await this.request("articles?status=eq.published&order=published_at.desc");
  },

  /**
   * Fetch highly sensitive drafts or items currently waiting in the Human Moderation Queue
   */
  async fetchModerationQueue() {
    if (!this.isConnected()) {
      const local = window.ApexStateManager.getArticles();
      return local.filter(a => a.status === "in_review");
    }

    return await this.request("articles?status=eq.in_review&order=created_at.desc");
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
