# CLAUDE.md — Sports Analytics Dashboard

## What This Is
Interactive dashboard of 35 NCAA sports analytics and sports science degree programs. Built as a self-contained HTML/JS file with embedded data.

## Repos & Deployment
- Local: `/Users/correia/Documents/GitHub/sports_analytics_dashboard/`
- GitHub: `gu-27/sports_analytics_dashboard`
- Live: `gu-27.github.io/sports_analytics_dashboard`
- Also copied to: `correia27` portal at `/research/sports-analytics/`

## Key Files
- `index.html` — the entire dashboard (HTML + CSS + JS + embedded JSON data), ~1000 lines
- `ncaa_programs.csv` — source data (35 real programs after filtering)
- `app.py` — original Streamlit version (replaced, ignore)

## Architecture
- Pure HTML/CSS/JS, no build step, no framework
- Plotly.js loaded from CDN: `https://cdn.plot.ly/plotly-2.27.0.min.js`
- Data embedded as `const RAW_DATA = [...]` JSON in the script block
- All NaN values must be `null` in JSON (NaN is invalid JSON and breaks Safari)
- All events use `addEventListener` inside `DOMContentLoaded` — NO inline onclick

## Tabs
- Overview: stats, scatter plot, program type/public-private charts, tuition, year established
- Map & Directory: bubble map + sortable/searchable table
- Curriculum: credit hours stacked bar, donut, by institution type
- Program Explorer: single school selector → full profile with hero header, fact grid, scale bars, curriculum emphasis, credit hours bar + pie chart, partnerships, mission, problem, vision

## Known Safari Rules (critical)
- No nested `function foo(){}` inside other functions — use `const foo = function(){}`
- No inline onclick handlers — use addEventListener
- Don't inline Plotly (3.5MB breaks script execution) — always use CDN

## Updating Data
1. Edit `ncaa_programs.csv`
2. Run Python data cleaning script to regenerate JSON (convert NaN → null)
3. Replace `const RAW_DATA = [...]` in index.html
4. Test in Safari before pushing

## Deployment
Push to `main` → GitHub Pages auto-deploys. Also manually copy `index.html` to `correia27/research/sports-analytics/index.html` and push that repo too.

---

## Skills library — read before writing code

All skills live at **https://github.com/gu-27/claude-skills** (public) and are installed locally at `~/.claude/commands/`.

| Skill | Why it applies here |
|---|---|
| [`dashboard.md`](https://github.com/gu-27/claude-skills/blob/main/dashboard.md) | Tab navigation, KPI cards, filter pills, sortable tables, number formatting, section/card layout. **Note:** this project uses Plotly.js (not Chart.js) — chart-specific patterns differ, but all other UI patterns apply. |
| [`webdev.md`](https://github.com/gu-27/claude-skills/blob/main/webdev.md) | Stack conventions — plain HTML/CSS/JS, no build step, GitHub Pages from root |
| [`gonzaga-brand.md`](https://github.com/gu-27/claude-skills/blob/main/gonzaga-brand.md) | GU color palette and typography — `--navy #041E42`, `--red #C8102E`, Outfit + Libre Baskerville |

> **Collaborator note:** This project uses **Plotly.js** (not Chart.js). The `dashboard.md` skill covers Chart.js patterns — translate the concepts (destroy-before-redraw → `Plotly.purge()`, canvas sizing → layout height) but don't copy chart code verbatim.
