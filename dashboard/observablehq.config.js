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

  // Dark theme inspired by Dark Horse Analytics
  theme: ["midnight", "alt"],

  // Custom stylesheets
  style: "style.css",

  // Page header with Google Fonts
  head: `
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>">
    <meta name="description" content="Vibe Data Platform - Analytics Dashboard">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@500;600;700;800&display=swap" rel="stylesheet">
  `,

  // Header and footer
  header: `
    <div style="display: flex; align-items: center; gap: 0.75rem;">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#c6b356" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 3v18h18"/>
        <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
      </svg>
      <a href="/" style="text-decoration: none; color: #f1f1ef; font-family: 'Montserrat', sans-serif; font-weight: 700; font-size: 1.1rem; letter-spacing: -0.02em;">VIBE DATA</a>
    </div>
  `,

  footer: `
    <div style="text-align: center; color: #6b7a8c; font-size: 0.75rem; padding: 1rem;">
      Built with Observable Framework | Data powered by dbt + DuckDB | Styled with Dark Horse Analytics aesthetics
    </div>
  `,

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
