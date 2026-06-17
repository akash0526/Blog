/* ==========================================
   APEX SEO PULSE — MASTER PERSISTENT DATA
   Single source of truth: ./articles.json
============================================= */

// Fallback defaults used only if ./articles.json cannot be fetched.
const fallbackArticles = [];

const defaultKanbanCards = [
  {
    id: "k-1781286978714",
    title: "Building a Fully Autonomous AI Agent with WebSockets in 2026",
    status: "published",
    keyword: "Autonomous AI Agent",
    priority: "High",
    date: "2026-06-12"
  },
  { id: "k-1", title: "10 AI Tools Every SEO Expert Uses", status: "drafting", keyword: "AI SEO tools", priority: "High" },
  { id: "k-2", title: "Why Backlinks Still Matter in 2026", status: "drafting", keyword: "Backlink strategy", priority: "Medium" },
  { id: "k-3", title: "Migrating from WordPress to Next.js", status: "optimizing", keyword: "WordPress to Nextjs", priority: "High" },
  { id: "k-4", title: "How to Build a High Traffic Blog", status: "scheduled", keyword: "High traffic blog", priority: "High", date: "2026-06-13" },
  { id: "k-5", title: "How to Write Keyword Clusters...", status: "published", keyword: "keyword clusters", priority: "High", date: "2026-06-12" }
];

window.ApexStateManager = {
  /**
   * Load articles from localStorage if the user has edited/created any,
   * otherwise fetch the canonical ./articles.json file.
   * Returns a Promise that resolves to the article array.
   */
  async getArticles() {
    try {
      const local = localStorage.getItem("apex_articles_v1");
      if (local) {
        return JSON.parse(local);
      }
    } catch (e) {
      console.warn("Could not parse local articles; falling back to articles.json", e);
    }

    try {
      const res = await fetch("./articles.json");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return Array.isArray(data) ? data : fallbackArticles;
    } catch (e) {
      console.warn("Could not fetch articles.json; using empty fallback.", e);
      return fallbackArticles;
    }
  },

  saveArticles(articles) {
    try {
      localStorage.setItem("apex_articles_v1", JSON.stringify(articles));
    } catch (e) {
      console.warn("Failed to save articles to localStorage", e);
    }
  },

  getKanban() {
    try {
      const data = localStorage.getItem("apex_kanban_v1");
      return data ? JSON.parse(data) : defaultKanbanCards;
    } catch (e) {
      return defaultKanbanCards;
    }
  },

  saveKanban(cards) {
    try {
      localStorage.setItem("apex_kanban_v1", JSON.stringify(cards));
    } catch (e) {}
  },

  getStreakStats() {
    try {
      const data = localStorage.getItem("apex_streak_v1");
      return data ? JSON.parse(data) : {
        currentStreak: 14,
        longestStreak: 21,
        publishedThisMonth: 12,
        totalArticles: 48,
        lastPublishDate: "2026-06-12"
      };
    } catch (e) {
      return { currentStreak: 14, longestStreak: 21, publishedThisMonth: 12, totalArticles: 48, lastPublishDate: "2026-06-12" };
    }
  },

  saveStreakStats(stats) {
    try {
      localStorage.setItem("apex_streak_v1", JSON.stringify(stats));
    } catch (e) {}
  },

  recordPublishEvent() {
    const stats = this.getStreakStats();
    const today = new Date().toISOString().split("T")[0];

    if (stats.lastPublishDate !== today) {
      stats.currentStreak += 1;
      stats.publishedThisMonth += 1;
      stats.totalArticles += 1;
      if (stats.currentStreak > stats.longestStreak) {
        stats.longestStreak = stats.currentStreak;
      }
      stats.lastPublishDate = today;
      this.saveStreakStats(stats);
    }
    return stats;
  }
};
