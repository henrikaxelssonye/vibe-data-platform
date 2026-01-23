// Observable Framework configuration
// See: https://observablehq.com/framework/config

export default {
  title: "Vibe Data Platform",

  pages: [
    { name: "Overview", path: "/" },
    { name: "Customers", path: "/customers" },
    { name: "Sales", path: "/sales" },
    { name: "Weather", path: "/weather" }
  ],

  // Page header
  head: `
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>">
    <meta name="description" content="Vibe Data Platform - Analytics Dashboard">
  `,

  // Header and footer
  header: `
    <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 1.2rem;">
      <span>📊</span>
      <a href="/" style="text-decoration: none; color: inherit; font-weight: bold;">Vibe Data Platform</a>
    </div>
  `,

  footer: `Built with Observable Framework | Data powered by dbt + DuckDB`,

  // Source root
  root: "src",

  // Enable table of contents
  toc: true,

  // Enable pager navigation
  pager: true,

  // Search
  search: true,

  // Build output directory for GitHub Pages
  output: "dist",

  // Base path for GitHub Pages (will be set by environment variable)
  base: process.env.BASE_PATH || "/"
};
