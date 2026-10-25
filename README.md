<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#25134D">
<meta name="description" content="Idea Man — Every big idea needs a sidekick. Free creative-director plugin for Claude and Codex, plus the official brand kit.">
<title>Idea Man — Creative Director Plugin &amp; Studio Brand Kit</title>
<style>
:root {
  --yellow: #F6F43C;
  --cyan: #26D9E6;
  --coral: #FF5878;
  --electric: #4B39F2;
  --ink: #25134D;
  --paper: #FFFEF4;
  --lavender: #EEEAFA;
  --line: #D8D2DF;
  --muted: #665775;
  --display: 'Arial Black', 'Segoe UI Black', Impact, Arial, sans-serif;
  --body: 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif;
  --mono: ui-monospace, 'Cascadia Code', 'Segoe UI Mono', Consolas, monospace;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; scroll-padding-top: 84px; }
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font: 17px/1.55 var(--body);
  -webkit-font-smoothing: antialiased;
}
a { color: inherit; text-underline-offset: 4px; }
button, a { -webkit-tap-highlight-color: transparent; }
button { font: inherit; cursor: pointer; }
a:focus-visible, button:focus-visible, summary:focus-visible {
  outline: 3px solid var(--electric);
  outline-offset: 4px;
}
img { max-width: 100%; display: block; }
h1, h2, h3, h4, p, figure, pre { margin: 0; }
h1, h2, h3 { line-height: 1.03; letter-spacing: -0.045em; }
h2 { font-family: var(--display); font-weight: 900; font-size: clamp(34px, 4.3vw, 62px); }
h3 { font-size: 26px; font-weight: 850; }
code, pre { font-family: var(--mono); }

.wrap { width: min(1280px, calc(100% - 80px)); margin: auto; }
.eyebrow {
  font: 800 12px/1.4 var(--body);
  letter-spacing: 0.16em;
  text-transform: uppercase;
}
.small { font-size: 14px; line-height: 1.5; }
.muted { color: var(--muted); }

.skip {
  position: absolute;
  left: 20px;
  top: -80px;
  z-index: 100;
  padding: 12px 20px;
  background: var(--yellow);
  color: var(--ink);
  font-weight: 800;
}
.skip:focus { top: 10px; }

/* TOPBAR */
.topbar {
  position: sticky;
  top: 0;
  z-index: 40;
  background: var(--ink);
  color: var(--paper);
  border-bottom: 2px solid #3c2473;
}
.nav {
  min-height: 68px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}
.brand {
  font-family: var(--display);
  font-weight: 950;
  letter-spacing: -0.05em;
  text-decoration: none;
  font-size: 22px;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 12px;
}
.brand-badge {
  font: 700 11px/1 var(--body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  background: var(--electric);
  color: #fff;
  padding: 6px 10px;
  border-radius: 100px;
}
.navlinks {
  display: flex;
  align-items: center;
  gap: 22px;
  font-size: 13px;
  font-weight: 750;
}
.navlinks a { text-decoration: none; transition: color 0.15s; }
.navlinks a:hover { color: var(--cyan); }
.nav-cta {
  background: var(--yellow);
  color: var(--ink);
  border: 0;
  border-radius: 100px;
  padding: 9px 16px;
  font-size: 12px;
  font-weight: 850;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  text-decoration: none;
  transition: transform 0.12s, background 0.12s;
}
.nav-cta:hover { background: var(--cyan); color: var(--ink); transform: translateY(-1px); }
.topbar a:focus-visible, .topbar button:focus-visible { outline-color: var(--yellow); }

/* HERO */
.hero {
  background: var(--yellow);
  padding: 32px 0 0;
  border-bottom: 2px solid var(--ink);
}
.hero-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--ink);
}
.wordmark {
  font-family: var(--display);
  font-weight: 950;
  font-size: clamp(72px, 15.8vw, 220px);
  letter-spacing: -0.085em;
  line-height: 0.96;
  white-space: nowrap;
  margin: 18px 0 12px;
  color: var(--ink);
}
.hero-sub {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 20px;
  margin: 0 0 28px;
  padding: 0 3px;
}
.hero-sub .tagline {
  font-size: clamp(22px, 2.6vw, 36px);
  font-weight: 850;
  letter-spacing: -0.035em;
}
.hero-sub .subtitle {
  font-size: clamp(18px, 1.8vw, 24px);
  font-weight: 850;
  letter-spacing: -0.02em;
  background: var(--ink);
  color: var(--yellow);
  padding: 8px 16px;
  border-radius: 100px;
}

/* HERO STUDIO GRID */
.hero-grid {
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  gap: 24px;
  align-items: stretch;
}
.duo {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}
.character-card {
  display: flex;
  flex-direction: column;
}
.character-image {
  position: relative;
  border: 2px solid var(--ink);
  border-radius: 16px;
  overflow: hidden;
  background: #ff0;
}
.character-image img {
  width: 100%;
  height: auto;
  aspect-ratio: 1;
  object-fit: contain;
}
.character-number {
  position: absolute;
  top: 14px;
  left: 14px;
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--ink);
  color: var(--yellow);
  font-weight: 850;
  font-size: 13px;
}
.character-caption {
  display: flex;
  gap: 12px;
  justify-content: space-between;
  align-items: flex-start;
  padding: 14px 2px 22px;
}
.character-caption h2 {
  font-family: var(--body);
  font-size: 22px;
  font-weight: 850;
  letter-spacing: -0.03em;
}
.character-caption p { font-size: 13.5px; margin-top: 4px; }
.approval {
  font: 800 10px var(--body);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  white-space: nowrap;
  border: 1.5px solid var(--ink);
  padding: 6px 10px;
  border-radius: 100px;
}

/* HERO BRIEF CARD */
.hero-pitch {
  background: var(--paper);
  border: 2px solid var(--ink);
  border-radius: 16px;
  padding: 28px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 22px;
}
.pitch-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font: 800 11px/1 var(--body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 8px 12px;
  border-radius: 100px;
  border: 1.5px solid var(--ink);
}
.badge-cyan { background: var(--cyan); color: var(--ink); }
.badge-coral { background: var(--coral); color: var(--ink); }
.badge-electric { background: var(--electric); color: #fff; }
.badge-ink { background: var(--ink); color: var(--yellow); }

.hero-pitch h2 {
  font-size: clamp(28px, 3vw, 42px);
  line-height: 1.02;
  margin-top: 4px;
}
.hero-pitch .lead {
  font-size: 17.5px;
  line-height: 1.55;
  font-weight: 600;
}
.hero-command-box {
  background: var(--ink);
  color: var(--paper);
  border-radius: 12px;
  padding: 16px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}
.hero-command-box code {
  font-size: 14px;
  color: var(--yellow);
  font-weight: 700;
  overflow-x: auto;
  white-space: nowrap;
}
.copy-pill {
  background: var(--cyan);
  color: var(--ink);
  border: 0;
  border-radius: 100px;
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 850;
  white-space: nowrap;
  flex-shrink: 0;
}
.copy-pill:hover { background: var(--yellow); }

.hero-bottom {
  border-top: 1.5px solid #25134d45;
  padding: 16px 0 22px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  font-size: 14px;
  font-weight: 650;
}
.hero-links {
  display: flex;
  gap: 22px;
  flex-wrap: wrap;
}
.hero-links a { font-weight: 800; }

/* SECTIONS */
.section { padding: 85px 0; }
.section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 40px;
  margin-bottom: 40px;
}
.section-head .eyebrow { margin-bottom: 14px; }
.section-head > p { max-width: 390px; padding-top: 26px; font-weight: 600; }

/* THE PROMISE & 7+ CRITIC (DEEP VIOLET) */
.purpose {
  background: var(--ink);
  color: var(--paper);
}
.purpose-grid {
  display: grid;
  grid-template-columns: 1fr 1.1fr;
  gap: 64px;
  align-items: start;
}
.purpose h2 {
  color: var(--yellow);
  font-size: clamp(44px, 5.4vw, 76px);
  margin-top: 14px;
}
.purpose-copy > p {
  font-size: 20px;
  line-height: 1.55;
  margin-top: 22px;
}
.journey {
  margin-top: 28px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  list-style: none;
  padding: 0;
  font-size: 14px;
  font-weight: 850;
}
.journey li {
  background: #331c68;
  border: 1px solid #5838a1;
  padding: 8px 14px;
  border-radius: 100px;
}
.journey li:not(:last-child)::after {
  content: '→';
  color: var(--cyan);
  margin-left: 10px;
}
.purpose-note {
  margin-top: 20px;
  color: #d7cde6;
  font-size: 15px;
}

/* BLIND CRITIC PIPELINE BOARD */
.critic-board {
  background: #1B0D3B;
  border: 2px solid var(--cyan);
  border-radius: 18px;
  padding: 28px;
}
.critic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding-bottom: 18px;
  border-bottom: 1px solid #ffffff26;
  margin-bottom: 20px;
}
.critic-steps {
  display: grid;
  gap: 14px;
}
.critic-step {
  background: #25134D;
  border: 1.5px solid #482c85;
  border-radius: 12px;
  padding: 16px 18px;
  display: grid;
  grid-template-columns: 42px 1fr auto;
  align-items: center;
  gap: 14px;
}
.critic-step.highlight-gate {
  border-color: var(--coral);
  background: #311559;
}
.critic-step.highlight-survivor {
  border-color: var(--yellow);
  background: #2C195A;
}
.step-num {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-weight: 900;
  font-size: 13px;
  background: var(--yellow);
  color: var(--ink);
}
.highlight-gate .step-num { background: var(--coral); color: var(--ink); }
.highlight-survivor .step-num { background: var(--cyan); color: var(--ink); }
.critic-step h3 { font-size: 18px; color: #fff; margin-bottom: 3px; }
.critic-step p { font-size: 13.5px; color: #d7cde6; }
.step-tag {
  font: 800 11px var(--mono);
  padding: 6px 10px;
  border-radius: 8px;
  background: #170a30;
  color: var(--yellow);
  white-space: nowrap;
}

/* INSTALL SECTION */
.install-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}
.install-card {
  background: #fff;
  border: 2px solid var(--ink);
  border-radius: 16px;
  padding: 28px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 20px;
  box-shadow: 0 6px 0 var(--ink);
}
.install-card-top .platform-tag {
  display: inline-block;
  font: 850 11px var(--body);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 6px 11px;
  border-radius: 100px;
  margin-bottom: 14px;
}
.tag-claude { background: var(--yellow); color: var(--ink); }
.tag-cowork { background: var(--coral); color: var(--ink); }
.tag-codex { background: var(--cyan); color: var(--ink); }

.install-card h3 { font-size: 26px; margin-bottom: 10px; }
.code-block {
  background: var(--ink);
  color: var(--paper);
  border-radius: 12px;
  padding: 16px;
  font-size: 13px;
  line-height: 1.65;
  overflow-x: auto;
  position: relative;
}
.code-block code { color: var(--yellow); display: block; }
.code-block .comment { color: var(--cyan); font-weight: 700; }
.install-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding-top: 14px;
  border-top: 1px solid var(--line);
  font-size: 13.5px;
}
.btn-action {
  background: var(--ink);
  color: #fff;
  border: 0;
  border-radius: 100px;
  padding: 10px 18px;
  font-size: 13px;
  font-weight: 800;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.btn-action:hover { background: var(--electric); }

/* MODES SECTION */
.modes-section {
  background: var(--lavender);
  border-top: 2px solid var(--ink);
  border-bottom: 2px solid var(--ink);
}
.modes-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 18px;
}
.mode-card {
  background: var(--paper);
  border: 2px solid var(--ink);
  border-radius: 16px;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 24px;
  transition: transform 0.15s, background 0.15s;
}
.mode-card:hover {
  transform: translateY(-4px);
  background: var(--yellow);
}
.mode-num {
  font: 850 12px var(--mono);
  color: var(--electric);
  display: block;
  margin-bottom: 10px;
}
.mode-card h3 {
  font-family: var(--display);
  font-size: 28px;
  margin-bottom: 10px;
}
.mode-card p {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.45;
}
.mode-cmd {
  font: 700 12px var(--mono);
  background: var(--ink);
  color: var(--paper);
  padding: 8px 10px;
  border-radius: 8px;
  text-align: left;
  border: 0;
  width: 100%;
}
.mode-cmd:hover { background: var(--electric); }

/* 11 SKILLS ENGINE */
.skills-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 28px;
}
.filter-btn {
  border: 1.5px solid var(--ink);
  background: var(--paper);
  color: var(--ink);
  border-radius: 100px;
  padding: 9px 18px;
  font-weight: 800;
  font-size: 13px;
}
.filter-btn[aria-pressed="true"] {
  background: var(--ink);
  color: var(--yellow);
}
.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 18px;
}
.skill-card {
  border: 1.5px solid var(--ink);
  border-radius: 14px;
  padding: 20px;
  background: #fff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 14px;
}
.skill-card[ hidden ] { display: none; }
.skill-stage {
  font: 800 11px var(--body);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--electric);
}
.skill-name {
  font: 800 17px var(--mono);
  background: var(--yellow);
  color: var(--ink);
  padding: 6px 10px;
  border-radius: 8px;
  display: inline-block;
  margin-top: 6px;
}
.skill-copy-btn {
  align-self: flex-start;
  border: 1px solid var(--line);
  background: var(--paper);
  border-radius: 100px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 750;
}
.skill-copy-btn:hover { border-color: var(--ink); background: var(--cyan); }

/* VOICE SECTION (CYAN) */
.voice {
  background: var(--cyan);
  border-top: 2px solid var(--ink);
  border-bottom: 2px solid var(--ink);
}
.voice-grid {
  display: grid;
  grid-template-columns: 0.85fr 1.15fr;
  gap: 70px;
}
.voice h2 { margin: 15px 0 22px; }
.voice-intro { max-width: 390px; font-weight: 600; }
.voice-examples { list-style: none; padding: 0; margin: 0; }
.voice-examples li {
  border-bottom: 1.5px solid #25134d55;
  padding: 22px 0;
}
.voice-examples li:first-child { padding-top: 0; }
.voice-examples li:last-child { border: 0; padding-bottom: 0; }
.voice-examples span {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 850;
  display: block;
  margin-bottom: 7px;
}
.voice-examples p {
  font-size: clamp(20px, 2vw, 27px);
  font-weight: 800;
  line-height: 1.3;
  letter-spacing: -0.025em;
}
.voice-footnote { font-size: 14px; margin-top: 27px; font-weight: 650; }

/* CHARACTER SYSTEM & TOOLKIT */
.usage {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 55px;
}
.usage h3 { margin-bottom: 13px; }
.usage .tag {
  display: inline-block;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 14px;
  color: var(--electric);
}
.usage ul { padding-left: 20px; margin: 16px 0 20px; font-size: 15px; }
.usage li { margin: 7px 0; }
.text-link {
  display: inline-flex;
  gap: 9px;
  align-items: center;
  font-weight: 800;
  font-size: 14px;
  min-height: 44px;
}
.rule-strip {
  margin-top: 36px;
  border-top: 1px solid var(--line);
  padding-top: 22px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 55px;
}
.rule-strip strong { display: block; margin-bottom: 5px; }
.rule-strip p { font-size: 14px; }

/* PALETTE & TYPE */
.palette-section { background: var(--lavender); border-top: 2px solid var(--ink); }
.palette {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr 1fr 1fr;
  gap: 0;
  border: 2px solid var(--ink);
  border-radius: 16px;
  overflow: hidden;
}
.swatch {
  border: 0;
  border-right: 1.5px solid #25134d35;
  text-align: left;
  padding: 24px 20px;
  min-height: 205px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 38px;
  color: var(--ink);
}
.swatch:last-child { border: 0; }
.swatch strong { font-weight: 850; display: block; font-size: 17px; line-height: 1.2; }
.swatch code { font: 700 14px var(--mono); display: block; margin-top: 9px; }
.swatch small { font-size: 12px; font-weight: 750; }
.swatch:hover small { text-decoration: underline; }
.swatch-yellow { background: var(--yellow); }
.swatch-cyan { background: var(--cyan); }
.swatch-coral { background: var(--coral); }
.swatch-electric { background: var(--electric); color: #fff; }
.swatch-ink { background: var(--ink); color: #fff; }

.color-note {
  display: flex;
  gap: 40px;
  justify-content: space-between;
  margin-top: 20px;
  font-size: 14px;
}
.color-note p { max-width: 590px; }
.type-specimen {
  margin-top: 55px;
  border-top: 1.5px solid #25134d40;
  padding-top: 35px;
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 65px;
}
.specimen {
  font: 950 clamp(36px, 5vw, 70px)/0.98 var(--display);
  letter-spacing: -0.065em;
  margin: 16px 0;
}
.type-notes h3 { font-size: 23px; margin-bottom: 15px; }
.type-notes p { font-size: 15px; margin-bottom: 14px; }
.type-sizes {
  display: flex;
  gap: 18px;
  flex-wrap: wrap;
  font-size: 12px;
  font-weight: 750;
  margin-top: 22px;
}

/* MARKETPLACE LISTING STUDY & ICON SCALES */
.preview-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 22px;
}
.switcher {
  display: flex;
  gap: 5px;
  background: #ece7f4;
  padding: 5px;
  border-radius: 100px;
  border: 1.5px solid var(--ink);
}
.switcher button {
  border: 0;
  background: transparent;
  color: var(--ink);
  border-radius: 100px;
  padding: 10px 18px;
  font-weight: 800;
  font-size: 14px;
  min-height: 44px;
}
.switcher button[aria-pressed="true"] { background: var(--ink); color: #fff; }
.mockups { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.preview-stage {
  padding: 24px;
  background: #f0eef4;
  border: 1.5px solid #ded9e7;
  border-radius: 18px;
  min-width: 0;
}
.stage-label {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  margin-bottom: 20px;
}
.listing {
  padding: 24px;
  background: #fff;
  border: 1.5px solid #e5e1eb;
  border-radius: 15px;
}
.listing-top { display: flex; gap: 18px; align-items: center; }
.listing img {
  width: 76px;
  height: 76px;
  flex-shrink: 0;
  border-radius: 18px;
  object-fit: contain;
  background: var(--yellow);
}
.listing h3 { font-size: 25px; letter-spacing: -0.035em; }
.listing-sub { font-size: 13px; margin-top: 6px; color: #62596e; }
.listing-description { font-size: 15px; margin-top: 21px; line-height: 1.6; }
.listing-footer {
  border-top: 1px solid #e4dfea;
  margin-top: 22px;
  padding-top: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
}
.sample-button {
  display: inline-block;
  border: 1px solid #dad5e3;
  border-radius: 100px;
  padding: 8px 14px;
  font-weight: 750;
}
.dark-stage { background: #171320; color: #f8f6fc; border-color: #32283e; }
.dark-stage .listing { background: #262030; border-color: #41374d; }
.dark-stage .listing-sub { color: #cac1d6; }
.dark-stage .listing-footer { border-color: #4f435b; }
.dark-stage .sample-button { background: #f5f1fa; color: var(--ink); border-color: #f5f1fa; }

.scale-block {
  display: grid;
  grid-template-columns: 0.8fr 1.2fr;
  align-items: center;
  gap: 35px;
  margin-top: 35px;
}
.scale-copy h3 { font-size: 24px; margin-bottom: 10px; }
.scale-copy p { max-width: 380px; font-size: 14px; }
.scales {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  border-bottom: 1px solid var(--line);
  padding-bottom: 15px;
}
.scale { text-align: center; flex-shrink: 0; }
.scale img { margin: 0 auto 12px; border-radius: 22%; background: var(--yellow); }
.scale span { font: 600 12px var(--mono); }

/* REPO LAYOUT & README MARKDOWN EXPORT */
.repo-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
}
.repo-card {
  border: 2px solid var(--ink);
  border-radius: 16px;
  padding: 28px;
  background: #fff;
}
.repo-tree {
  background: var(--ink);
  color: var(--paper);
  padding: 20px;
  border-radius: 12px;
  font: 600 13.5px/1.7 var(--mono);
  margin-top: 16px;
}
.repo-tree .dir { color: var(--yellow); font-weight: 800; }
.repo-tree .desc { color: var(--cyan); }

.readme-drawer {
  margin-top: 28px;
  border: 2px solid var(--ink);
  border-radius: 16px;
  background: var(--yellow);
  padding: 22px 28px;
}
.readme-drawer summary {
  cursor: pointer;
  font-weight: 850;
  font-size: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.readme-raw-box {
  margin-top: 18px;
  background: var(--ink);
  color: var(--paper);
  padding: 20px;
  border-radius: 12px;
  max-height: 420px;
  overflow: auto;
  font: 12.5px/1.6 var(--mono);
  white-space: pre-wrap;
}

/* FOOTER & TOAST */
.footer {
  padding: 36px 0;
  background: var(--ink);
  color: #e1d8ec;
  font-size: 13.5px;
}
.footer-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 25px;
}
.footer details {
  max-width: 880px;
  margin-top: 23px;
  border-top: 1px solid #ffffff30;
  padding-top: 17px;
}
.footer summary { cursor: pointer; font-weight: 700; min-height: 32px; }
.footer details p { margin: 12px 0; }
.footer .sources { display: flex; flex-wrap: wrap; gap: 12px 24px; }

.toast {
  position: fixed;
  bottom: 22px;
  left: 50%;
  transform: translate(-50%, 15px);
  background: var(--ink);
  color: #fff;
  border: 2px solid var(--cyan);
  border-radius: 12px;
  padding: 12px 22px;
  box-shadow: 0 8px 28px #25134d40;
  z-index: 90;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s, transform 0.15s;
  font-size: 14px;
  font-weight: 750;
  max-width: calc(100% - 40px);
  text-align: center;
}
.toast.show { opacity: 1; transform: translate(-50%, 0); }

@media (max-width: 1060px) {
  .wrap { width: calc(100% - 48px); }
  .hero-grid, .purpose-grid, .install-grid, .voice-grid, .usage, .type-specimen, .repo-grid {
    grid-template-columns: 1fr;
  }
  .modes-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 720px) {
  .wrap { width: calc(100% - 32px); }
  .nav { padding: 12px 0; flex-wrap: wrap; }
  .navlinks { width: 100%; justify-content: space-between; overflow-x: auto; padding-bottom: 4px; }
  .hero-sub { display: block; }
  .hero-sub .subtitle { display: inline-block; margin-top: 10px; }
  .duo, .mockups, .scale-block, .modes-grid, .rule-strip { grid-template-columns: 1fr; }
  .palette { grid-template-columns: repeat(6, 1fr); }
  .swatch { grid-column: span 2; min-height: 160px; }
  .swatch:nth-child(4), .swatch:nth-child(5) { grid-column: span 3; }
  .section { padding: 55px 0; }
  .section-head { display: block; }
  .section-head > p { padding-top: 14px; max-width: none; }
}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>

<header class="topbar">
  <nav class="nav wrap" aria-label="Idea Man Studio Navigation">
    <a class="brand" href="#top">
      IDEA MAN
      <span class="brand-badge">Claude &amp; Codex Plugin</span>
    </a>
    <div class="navlinks">
      <a href="#promise">The Promise</a>
      <a href="#install">Install</a>
      <a href="#modes">Modes</a>
      <a href="#skills">11 Skills</a>
      <a href="#voice">Voice</a>
      <a href="#brand-kit">Brand Kit</a>
      <button type="button" class="nav-cta" id="copy-readme-btn">Copy README.md</button>
    </div>
  </nav>
</header>

<main id="main">
  <!-- HERO SECTION -->
  <section class="hero" id="top" aria-labelledby="brand-title">
    <div class="wrap">
      <div class="hero-meta eyebrow">
        <span>A creative studio with a sidekick spirit</span>
        <span>Two characters. One Idea Man.</span>
      </div>

      <h1 class="wordmark" id="brand-title">IDEA MAN</h1>

      <div class="hero-sub">
        <p class="tagline">Every big idea needs a sidekick.</p>
        <p class="subtitle">Brainstorm. Sharpen. Create.</p>
      </div>

      <div class="hero-grid">
        <!-- SUPPLIED FULL-SQUARE ARTWORK DUO -->
        <div class="duo">
          <figure class="character-card">
            <div class="character-image">
              <span class="character-number" aria-hidden="true">01</span>
              <img
                src="plugins/idea-man/assets/lightbulb-hero-1024.webp"
                onerror="this.onerror=null;this.src='idea-man-lightbulb-hero.png';"
                width="1024"
                height="1024"
                alt="Lightbulb Hero: a faceless blue bulb wearing round violet glasses and a coral cape, with hands on hips and violet boots."
                fetchpriority="high">
            </div>
            <figcaption class="character-caption">
              <div>
                <h2>Lightbulb Hero</h2>
                <p>A bright thought, ready to move.</p>
              </div>
              <span class="approval">Approved</span>
            </figcaption>
          </figure>

          <figure class="character-card">
            <div class="character-image">
              <span class="character-number" aria-hidden="true">02</span>
              <img
                src="idea-man-invisible-nerd.png"
                onerror="this.onerror=null;this.src='plugins/idea-man/assets/lightbulb-hero-1024.webp';"
                width="1254"
                height="1254"
                alt="Invisible Nerd: floating round cyan glasses and a coral cape with violet lining, against bright yellow."
                fetchpriority="high">
            </div>
            <figcaption class="character-caption">
              <div>
                <h2>Invisible Nerd</h2>
                <p>Curiosity, with a cape.</p>
              </div>
              <span class="approval">Approved</span>
            </figcaption>
          </figure>
        </div>

        <!-- STUDIO README PITCH CARD -->
        <div class="hero-pitch">
          <div>
            <div class="pitch-badges">
              <span class="badge badge-ink">Free Plugin</span>
              <span class="badge badge-cyan">Blind Critic 7+</span>
              <span class="badge badge-coral">5 Modes · 11 Skills</span>
              <span class="badge badge-electric">MIT License</span>
            </div>
            <h2 style="margin-top:18px;">BIG IDEA.<br>NEXT MOVE.</h2>
            <p class="lead" style="margin-top:14px;">
              <strong>Idea Man</strong> is a free creative-director plugin for Claude and Codex. It finds the insight first, then generates far past the obvious with methods drawn from real master thinkers. A blind critic scores every idea, and you only see the ones that score 7+, with their risks and the cheapest test.
            </p>
          </div>

          <div>
            <p class="eyebrow" style="margin-bottom:8px;">Quick invoke in Claude Code</p>
            <div class="hero-command-box">
              <code>/idea-man:creative-director &lt;brief&gt;</code>
              <button type="button" class="copy-pill" data-copy="/idea-man:creative-director ">Copy command</button>
            </div>
          </div>
        </div>
      </div>

      <div class="hero-bottom">
        <p>Find distinct directions. Sharpen the strongest. Turn it into something you can make.</p>
        <div class="hero-links">
          <a href="https://sergey9519546.github.io/idea-man/" target="_blank" rel="noopener">Live Site: sergey9519546.github.io/idea-man ↗</a>
          <a href="https://github.com/sergey9519546/idea-man/releases/latest" target="_blank" rel="noopener">Latest Release (v1.2.1) ↗</a>
        </div>
      </div>
    </div>
  </section>

  <!-- THE PROMISE & THE 7+ BLIND CRITIC -->
  <section class="section purpose" id="promise" aria-labelledby="promise-title">
    <div class="wrap purpose-grid">
      <div>
        <p class="eyebrow" style="color:var(--cyan);">The promise</p>
        <h2 id="promise-title">Brainstorm.<br>Sharpen.<br>Create.</h2>
        <div class="purpose-copy">
          <p>Bring a half-formed thought, a rough draft, or a direction you already love. Idea Man helps you find the next useful step—and carry the idea further.</p>
          <ol class="journey" aria-label="Creative studio journey">
            <li>Understand</li>
            <li>Explore</li>
            <li>Critique</li>
            <li>Develop</li>
            <li>Make</li>
          </ol>
          <p class="purpose-note">A complete creative studio, from first directions to production briefs and execution with the tools available in your workspace. Save project decisions when you want to pick up later.</p>
        </div>
      </div>

      <!-- THE 7+ CRITIC PIPELINE -->
      <div class="critic-board" aria-label="How the Blind Critic pipeline works">
        <div class="critic-header">
          <span class="eyebrow" style="color:var(--yellow);">Inside the Full Mode Engine</span>
          <span class="badge badge-coral">Only 7+ Ideas Survive</span>
        </div>
        <div class="critic-steps">
          <div class="critic-step">
            <span class="step-num">01</span>
            <div>
              <h3>Diagnose &amp; Find the Insight First</h3>
              <p>Looks past surface requests to uncover the real tension before generating.</p>
            </div>
            <span class="step-tag">INSIGHT</span>
          </div>
          <div class="critic-step">
            <span class="step-num">02</span>
            <div>
              <h3>Generate Past the Obvious</h3>
              <p>Applies lateral methods drawn from real master thinkers—changing the idea, not just the wording.</p>
            </div>
            <span class="step-tag">DIVERGE</span>
          </div>
          <div class="critic-step highlight-gate">
            <span class="step-num">03</span>
            <div>
              <h3>The Blind Critic Scores Every Idea</h3>
              <p>An independent critic evaluates every candidate cold. Anything scoring below 7 is killed.</p>
            </div>
            <span class="step-tag">7+ GATE</span>
          </div>
          <div class="critic-step highlight-survivor">
            <span class="step-num">04</span>
            <div>
              <h3>Risks &amp; The Cheapest Test</h3>
              <p>You only see the 7+ winners—paired with their core risks and the cheapest test to validate them.</p>
            </div>
            <span class="step-tag">PRESENT</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- INSTALL SECTION -->
  <section class="section" id="install" aria-labelledby="install-title">
    <div class="wrap">
      <div class="section-head">
        <div>
          <p class="eyebrow">01 / Install</p>
          <h2 id="install-title">Ready in your<br>workspace.</h2>
        </div>
        <p>Install Idea Man in Claude Code, Claude.ai, Cowork, or OpenAI Codex.</p>
      </div>

      <div class="install-grid">
        <!-- CLAUDE CODE -->
        <article class="install-card">
          <div class="install-card-top">
            <span class="platform-tag tag-claude">Claude Code</span>
            <h3>Claude Code CLI</h3>
            <p class="small muted" style="margin-bottom:16px;">Add the marketplace, install the plugin, and run the creative director on any brief.</p>
            <div class="code-block">
              <code>claude plugin marketplace add sergey9519546/idea-man</code>
              <code>claude plugin install idea-man@idea-man-marketplace</code>
              <code class="comment" style="margin-top:8px;"># Then run:</code>
              <code>/idea-man:creative-director &lt;brief&gt;</code>
            </div>
          </div>
          <div class="install-footer">
            <span class="small muted">2 commands</span>
            <button type="button" class="btn-action" data-copy="claude plugin marketplace add sergey9519546/idea-man&#10;claude plugin install idea-man@idea-man-marketplace">Copy CLI Install</button>
          </div>
        </article>

        <!-- CLAUDE.AI / COWORK -->
        <article class="install-card">
          <div class="install-card-top">
            <span class="platform-tag tag-cowork">Claude.ai / Cowork</span>
            <h3>Web &amp; Desktop Upload</h3>
            <p class="small muted" style="margin-bottom:16px;">Upload the release package directly into Claude.ai or Cowork.</p>
            <div class="code-block">
              <code class="comment">1. Open Claude settings:</code>
              <code>Customize → Plugins → Add → Upload plugin</code>
              <code class="comment" style="margin-top:8px;">2. Choose release archive:</code>
              <code>idea-man-1.2.1.zip</code>
            </div>
          </div>
          <div class="install-footer">
            <span class="small muted">Latest GitHub release</span>
            <a class="btn-action" href="https://github.com/sergey9519546/idea-man/releases/latest" target="_blank" rel="noopener">Get idea-man-1.2.1.zip ↗</a>
          </div>
        </article>

        <!-- CODEX -->
        <article class="install-card">
          <div class="install-card-top">
            <span class="platform-tag tag-codex">Codex</span>
            <h3>OpenAI Codex</h3>
            <p class="small muted" style="margin-bottom:16px;">Install from the main branch. The Codex plugin directory listing is pending review.</p>
            <div class="code-block">
              <code>codex plugin marketplace add sergey9519546/idea-man --ref main</code>
            </div>
          </div>
          <div class="install-footer">
            <span class="small muted">Direct git install</span>
            <button type="button" class="btn-action" data-copy="codex plugin marketplace add sergey9519546/idea-man --ref main">Copy Codex Command</button>
          </div>
        </article>
      </div>
    </div>
  </section>

  <!-- FIVE MODES -->
  <section class="section modes-section" id="modes" aria-labelledby="modes-title">
    <div class="wrap">
      <div class="section-head">
        <div>
          <p class="eyebrow">02 / Modes</p>
          <h2 id="modes-title">Five ways to<br>run the room.</h2>
        </div>
        <p>Pick the mode that fits your stage—from a full insight-to-critic run to a rapid spark or a ruthless critique.</p>
      </div>

      <div class="modes-grid">
        <article class="mode-card">
          <div>
            <span class="mode-num">MODE 01</span>
            <h3>Full</h3>
            <p>Diagnose, insight, generate, critique, present.</p>
          </div>
          <button type="button" class="mode-cmd" data-copy="/idea-man:creative-director [Full] ">Copy Full trigger ↗</button>
        </article>

        <article class="mode-card">
          <div>
            <span class="mode-num">MODE 02</span>
            <h3>Spark</h3>
            <p>A quick burst of ideas.</p>
          </div>
          <button type="button" class="mode-cmd" data-copy="/idea-man:creative-director [Spark] ">Copy Spark trigger ↗</button>
        </article>

        <article class="mode-card">
          <div>
            <span class="mode-num">MODE 03</span>
            <h3>Critique</h3>
            <p>Rate, compare or kill an existing idea.</p>
          </div>
          <button type="button" class="mode-cmd" data-copy="/idea-man:creative-director [Critique] ">Copy Critique trigger ↗</button>
        </article>

        <article class="mode-card">
          <div>
            <span class="mode-num">MODE 04</span>
            <h3>Unstick</h3>
            <p>Get moving on a stuck problem.</p>
          </div>
          <button type="button" class="mode-cmd" data-copy="/idea-man:creative-director [Unstick] ">Copy Unstick trigger ↗</button>
        </article>

        <article class="mode-card">
          <div>
            <span class="mode-num">MODE 05</span>
            <h3>Room</h3>
            <p>Parallel thinkers plus a blind critic.</p>
          </div>
          <button type="button" class="mode-cmd" data-copy="/idea-man:creative-director [Room] ">Copy Room trigger ↗</button>
        </article>
      </div>
    </div>
  </section>

  <!-- 11 SKILLS -->
  <section class="section" id="skills" aria-labelledby="skills-title">
    <div class="wrap">
      <div class="section-head">
        <div>
          <p class="eyebrow">03 / Skills</p>
          <h2 id="skills-title">11 specialized<br>studio skills.</h2>
        </div>
        <p>Filter the 11 skills across the creative studio journey or click any skill to copy its identifier.</p>
      </div>

      <div class="skills-filter" role="group" aria-label="Filter skills by studio stage">
        <button type="button" class="filter-btn" data-filter="all" aria-pressed="true">All 11 Skills</button>
        <button type="button" class="filter-btn" data-filter="understand" aria-pressed="false">Understand</button>
        <button type="button" class="filter-btn" data-filter="explore" aria-pressed="false">Explore</button>
        <button type="button" class="filter-btn" data-filter="critique" aria-pressed="false">Critique</button>
        <button type="button" class="filter-btn" data-filter="develop" aria-pressed="false">Develop</button>
        <button type="button" class="filter-btn" data-filter="make" aria-pressed="false">Make</button>
      </div>

      <div class="skills-grid" id="skills-grid">
        <article class="skill-card" data-stage="understand">
          <div>
            <span class="skill-stage">Understand · Orchestrator</span><br>
            <code class="skill-name">creative-director</code>
          </div>
          <button type="button" class="skill-copy-btn" data-copy="creative-director">Copy skill name</button>
        </article>

        <article class="skill-card" data-stage="understand">
          <div>
            <span class="skill-stage">Understand · Framing</span><br>
            <code class="skill-name">creative-brief</code>
          </div>
          <button type="button" class="skill-copy-btn" data-copy="creative-brief">Copy skill name</button>
        </article>

        <article class="skill-card" data-stage="explore">
          <div>
            <span class="skill-stage">Explore · Divergence</span><br>
            <code class="skill-name">concept-variations</code>
          </div>
          <button type="button" class="skill-copy-btn" data-copy="concept-variations">Copy skill name</button>
        </article>

        <article class="skill-card" data-stage="develop">
          <div>
            <span class="skill-stage">Develop · Shaping</span><br>
            <code class="skill-name">concept-development</code>
          </div>
          <button type="button" class="skill-copy-btn" data-copy="concept-development">Copy skill name</button>
        </article>

        <article class="skill-card" data-stage="critique">
          <div>
            <span class="skill-stage">Critique · 7+ Blind Critic</span><br>
            <code class="skill-name">creative-review</code>
          </div>
          <button type="button" class="skill-copy-btn" data-copy="creative-review">Copy skill name</button>
        </article>

        <article class="skill-card" data-stage="critique">
          <div>
            <span class="skill-stage">Critique · Craft Bar</span><br>
            <code class="skill-name">artifact-quality</code>
          </div>
          <button type="button" class="skill-copy-btn" data-copy="artifact-quality">Copy skill name</button>
        </article>

        <article class="skill-card" data-stage="understand">
          <div>
            <span class="skill-stage">Understand · Synthesis</span><br>
            <code class="skill-name">research-and-writing</code>
          </div>
          <button type="button" class="skill-copy-btn" data-copy="research-and-writing">Copy skill name</button>
        </article>

        <article class="skill-card" data-stage="understand">
          <div>
            <span class="skill-stage">Understand · Direction</span><br>
            <code class="skill-name">innovation-strategy</code>
          </div>
          <button type="button" class="skill-copy-btn" data-copy="innovation-strategy">Copy skill name</button>
        </article>

        <article class="skill-card" data-stage="develop">
          <div>
            <span class="skill-stage">Develop · Memory</span><br>
            <code class="skill-name">creative-learning</code>
          </div>
          <button type="button" class="skill-copy-btn" data-copy="creative-learning">Copy skill name</button>
        </article>

        <article class="skill-card" data-stage="make">
          <div>
            <span class="skill-stage">Make · Ship &amp; Test</span><br>
            <code class="skill-name">execution-handoff</code>
          </div>
          <button type="button" class="skill-copy-btn" data-copy="execution-handoff">Copy skill name</button>
        </article>

        <article class="skill-card" data-stage="explore">
          <div>
            <span class="skill-stage">Explore · Studio Flow</span><br>
            <code class="skill-name">creative-project</code>
          </div>
          <button type="button" class="skill-copy-btn" data-copy="creative-project">Copy skill name</button>
        </article>
      </div>
    </div>
  </section>

  <!-- VOICE SECTION -->
  <section class="section voice" id="voice" aria-labelledby="voice-title">
    <div class="wrap voice-grid">
      <div>
        <p class="eyebrow">04 / Voice</p>
        <h2 id="voice-title">Curious.<br>Candid.<br>Useful.</h2>
        <p class="voice-intro">A sharp creative partner with a sense of play. Ask the question that matters. Explain the choice. Give the person something they can use.</p>
        <p class="voice-footnote">Keep the superhero spirit in the imagery. In conversation, use plain language and honest judgments.</p>
      </div>
      <ol class="voice-examples">
        <li><span>Invitation</span><p>“Give me the rough version.”</p></li>
        <li><span>Exploration</span><p>“Six directions. Each changes the idea, not just the wording.”</p></li>
        <li><span>Critique</span><p>“The hook works. The payoff needs a clearer turn.”</p></li>
        <li><span>Development</span><p>“Keep the part you love. Let's build the next piece around it.”</p></li>
      </ol>
    </div>
  </section>

  <!-- BRAND & CHARACTER SYSTEM -->
  <section class="section" id="brand-kit" aria-labelledby="characters-title">
    <div class="wrap">
      <div class="section-head">
        <div>
          <p class="eyebrow">05 / Character system</p>
          <h2 id="characters-title">Same mind.<br>Two ways to show up.</h2>
        </div>
        <p>Both characters are approved peers. Pick the silhouette that best fits the composition; their roles are flexible.</p>
      </div>

      <div class="usage">
        <article>
          <span class="tag">Invisible Nerd</span>
          <h3>Let curiosity lead.</h3>
          <p>The empty glasses make room for the person with the idea. A compact, unusual silhouette for discovery, conversation, and the plugin icon.</p>
          <ul>
            <li>Round cyan glasses with violet depth; empty lenses.</li>
            <li>Coral cape, violet lining, and cyan clasp.</li>
            <li>No head, face, body, hands, or feet.</li>
          </ul>
          <a class="text-link" href="idea-man-invisible-nerd.png" download>Download Invisible Nerd PNG ↓</a>
        </article>

        <article>
          <span class="tag">Lightbulb Hero</span>
          <h3>Give the idea presence.</h3>
          <p>The confident pose makes a natural companion for demonstrations, studio guides, and moments when a direction starts taking shape.</p>
          <ul>
            <li>Plain cyan-blue bulb and round violet glasses.</li>
            <li>Coral cape, violet screw base, hands on hips, and boots.</li>
            <li>No eyes, eyebrows, mouth, filament, or light rays.</li>
          </ul>
          <a class="text-link" href="idea-man-lightbulb-hero.png" download>Download Lightbulb Hero PNG ↓</a>
        </article>
      </div>

      <div class="rule-strip">
        <p><strong>Give the silhouette space.</strong>Use the supplied full-square artwork. Keep both lenses and the cape visible. Avoid stretching, extra props, or placing copy over the character.</p>
        <p><strong>Make one character the focal point.</strong>Show the duo in brand introductions. For a small listing icon, choose one. These mascots identify Idea Man; the user's project keeps its own identity.</p>
      </div>

      <!-- INTERACTIVE MARKETPLACE LISTING PREVIEW -->
      <div style="margin-top:65px;">
        <div class="preview-controls">
          <div class="switcher" role="group" aria-label="Choose the character used in the previews">
            <button type="button" data-character="nerd" aria-pressed="true">Invisible Nerd</button>
            <button type="button" data-character="hero" aria-pressed="false">Lightbulb Hero</button>
          </div>
          <p class="small muted">Character switch updates both marketplace listings and all icon sizes.</p>
        </div>

        <div class="mockups">
          <div class="preview-stage">
            <p class="stage-label">Light surface / Listing study</p>
            <article class="listing" aria-label="Light listing mockup">
              <div class="listing-top">
                <img class="preview-character" src="idea-man-invisible-nerd.png" onerror="this.onerror=null;this.src='plugins/idea-man/assets/lightbulb-hero-1024.webp';" width="76" height="76" alt="Invisible Nerd icon">
                <div>
                  <h3>Idea Man</h3>
                  <p class="listing-sub">Brainstorm. Sharpen. Create.</p>
                </div>
              </div>
              <p class="listing-description">Find distinct directions. Sharpen the strongest. Turn it into something you can make.</p>
              <div class="listing-footer">
                <span>Creative studio</span>
                <span class="sample-button">Open studio ↗</span>
              </div>
            </article>
          </div>

          <div class="preview-stage dark-stage">
            <p class="stage-label">Dark surface / Listing study</p>
            <article class="listing" aria-label="Dark listing mockup">
              <div class="listing-top">
                <img class="preview-character" src="idea-man-invisible-nerd.png" onerror="this.onerror=null;this.src='plugins/idea-man/assets/lightbulb-hero-1024.webp';" width="76" height="76" alt="Invisible Nerd icon">
                <div>
                  <h3>Idea Man</h3>
                  <p class="listing-sub">Brainstorm. Sharpen. Create.</p>
                </div>
              </div>
              <p class="listing-description">Find distinct directions. Sharpen the strongest. Turn it into something you can make.</p>
              <div class="listing-footer">
                <span>Creative studio</span>
                <span class="sample-button">Open studio ↗</span>
              </div>
            </article>
          </div>
        </div>

        <div class="scale-block">
          <div class="scale-copy">
            <h3>The small-size check.</h3>
            <p>At 32 px, judge the glasses-and-cape silhouette, not texture. Use one complete character with a yellow field. Never squeeze the duo or the wordmark into a tiny icon.</p>
          </div>
          <div class="scales" aria-label="Icon scale previews">
            <div class="scale"><img class="preview-character" src="idea-man-invisible-nerd.png" onerror="this.onerror=null;this.src='plugins/idea-man/assets/lightbulb-hero-1024.webp';" width="32" height="32" alt="Character at 32 pixels"><span>32 px</span></div>
            <div class="scale"><img class="preview-character" src="idea-man-invisible-nerd.png" onerror="this.onerror=null;this.src='plugins/idea-man/assets/lightbulb-hero-1024.webp';" width="48" height="48" alt="Character at 48 pixels"><span>48 px</span></div>
            <div class="scale"><img class="preview-character" src="idea-man-invisible-nerd.png" onerror="this.onerror=null;this.src='plugins/idea-man/assets/lightbulb-hero-1024.webp';" width="64" height="64" alt="Character at 64 pixels"><span>64 px</span></div>
            <div class="scale"><img class="preview-character" src="idea-man-invisible-nerd.png" onerror="this.onerror=null;this.src='plugins/idea-man/assets/lightbulb-hero-1024.webp';" width="96" height="96" alt="Character at 96 pixels"><span>96 px</span></div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- COLOR & TYPOGRAPHY -->
  <section class="section palette-section" id="toolkit" aria-labelledby="toolkit-title">
    <div class="wrap">
      <div class="section-head">
        <div>
          <p class="eyebrow">06 / Color &amp; typography</p>
          <h2 id="toolkit-title">Turn the volume up.<br>Keep the message clear.</h2>
        </div>
        <p>Yellow sets the stage. Deep violet carries the words. Cyan and coral bring the characters to life.</p>
      </div>

      <div class="palette" aria-label="Brand palette; select a color to copy its hex code">
        <button class="swatch swatch-yellow" data-copy="#F6F43C" aria-label="Copy Solar yellow, hex F6F43C">
          <span><strong>Solar yellow</strong><code>#F6F43C</code></span>
          <small>Signature field · Copy hex ↗</small>
        </button>
        <button class="swatch swatch-cyan" data-copy="#26D9E6" aria-label="Copy Cyan, hex 26D9E6">
          <span><strong>Cyan</strong><code>#26D9E6</code></span>
          <small>Curiosity · Copy hex ↗</small>
        </button>
        <button class="swatch swatch-coral" data-copy="#FF5878" aria-label="Copy Coral, hex FF5878">
          <span><strong>Coral</strong><code>#FF5878</code></span>
          <small>Energy · Copy hex ↗</small>
        </button>
        <button class="swatch swatch-electric" data-copy="#4B39F2" aria-label="Copy Electric violet, hex 4B39F2">
          <span><strong>Electric violet</strong><code>#4B39F2</code></span>
          <small>Accent · Copy hex ↗</small>
        </button>
        <button class="swatch swatch-ink" data-copy="#25134D" aria-label="Copy Deep violet, hex 25134D">
          <span><strong>Deep violet</strong><code>#25134D</code></span>
          <small>Type &amp; depth · Copy hex ↗</small>
        </button>
      </div>

      <div class="color-note">
        <p>Use deep violet for text on yellow, cyan, coral, and light neutral surfaces. Use white on electric or deep violet. Keep electric violet and coral away from small text on each other.</p>
        <p>The artwork contains its own luminous yellow and shading. Keep the supplied pixels intact.</p>
      </div>

      <div class="type-specimen">
        <div>
          <p class="eyebrow">Display voice / Loud, compact, confident</p>
          <p class="specimen">BIG IDEA.<br>NEXT MOVE.</p>
          <div class="type-sizes">
            <span>Display 56–120 px</span>
            <span>Section 32–64 px</span>
            <span>Body 16–20 px</span>
          </div>
        </div>
        <div class="type-notes">
          <h3>Bold type. Room to think.</h3>
          <p><strong>Headlines:</strong> Arial Black, with Segoe UI Black and a heavy sans-serif fallback. Short phrases, tight tracking, generous surrounding space.</p>
          <p><strong>Reading:</strong> Segoe UI, then Arial or a system sans-serif. Sentence case, comfortable line spacing, and short paragraphs.</p>
          <p><strong>Brand name:</strong> <span style="font-weight:900">IDEA MAN</span> for the display wordmark; <strong>Idea Man</strong> in prose. Keep “Brainstorm. Sharpen. Create.” as the product subtitle.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- REPOSITORY LAYOUT & RAW GITHUB README DRAWER -->
  <section class="section" id="repo" aria-labelledby="repo-title">
    <div class="wrap">
      <div class="section-head">
        <div>
          <p class="eyebrow">07 / Repository &amp; Build</p>
          <h2 id="repo-title">Repository layout.</h2>
        </div>
        <p>Clean separation between the plugin, static landing-page generator, and test suite.</p>
      </div>

      <div class="repo-grid">
        <div class="repo-card">
          <h3>Directory Structure</h3>
          <div class="repo-tree">
            <div><span class="dir">plugins/idea-man/</span> &nbsp;<span class="desc"># the plugin</span></div>
            <div><span class="dir">site/</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="desc"># landing-page source</span></div>
            <div><span class="dir">docs/</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="desc"># compiled output for GitHub Pages</span></div>
            <div><span class="dir">tests/</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="desc"># Python tests</span></div>
          </div>
        </div>

        <div class="repo-card">
          <h3>Build &amp; Validate Landing Page</h3>
          <p class="small muted" style="margin-top:6px;">Compile <code>site/</code> into <code>docs/</code> for GitHub Pages and verify integrity:</p>
          <div class="code-block" style="margin-top:16px;">
            <code>node site/build.mjs</code>
            <code>node site/validate.mjs</code>
          </div>
          <div style="margin-top:16px;">
            <button type="button" class="btn-action" data-copy="node site/build.mjs && node site/validate.mjs">Copy Build Commands</button>
          </div>
        </div>
      </div>

      <!-- RAW GITHUB README.MD DRAWER -->
      <details class="readme-drawer">
        <summary>
          <span>📄 View / Copy Raw GitHub README.md (Drop-in Markdown + Brand Kit HTML)</span>
          <button type="button" class="btn-action" id="drawer-copy-readme">Copy Raw README.md</button>
        </summary>
        <pre class="readme-raw-box" id="raw-readme-source">&lt;div align="center"&gt;

&lt;p&gt;&lt;b&gt;A CREATIVE STUDIO WITH A SIDEKICK SPIRIT &amp;nbsp;·&amp;nbsp; TWO CHARACTERS. ONE IDEA MAN.&lt;/b&gt;&lt;/p&gt;

&lt;a href="https://sergey9519546.github.io/idea-man/"&gt;
  &lt;img src="plugins/idea-man/assets/lightbulb-hero-1024.webp" alt="Idea Man: a faceless cyan lightbulb in round violet glasses and a coral cape" width="360"&gt;
&lt;/a&gt;

# IDEA MAN

### **Every big idea needs a sidekick.**
**Brainstorm. Sharpen. Create.**

&lt;p align="center"&gt;Find distinct directions. Sharpen the strongest. Turn it into something you can make.&lt;/p&gt;

[![Site](https://img.shields.io/badge/IDEA_MAN-STUDIO_SITE-F6F43C?style=for-the-badge&amp;labelColor=25134D)](https://sergey9519546.github.io/idea-man/)
[![Claude](https://img.shields.io/badge/CLAUDE-PLUGIN-4B39F2?style=for-the-badge&amp;labelColor=25134D)](#install)
[![Codex](https://img.shields.io/badge/CODEX-PLUGIN-26D9E6?style=for-the-badge&amp;labelColor=25134D)](#install)
[![Release](https://img.shields.io/github/v/release/sergey9519546/idea-man?style=for-the-badge&amp;label=RELEASE&amp;color=FF5878&amp;labelColor=25134D)](https://github.com/sergey9519546/idea-man/releases/latest)
[![License: MIT](https://img.shields.io/badge/LICENSE-MIT-F6F43C?style=for-the-badge&amp;labelColor=25134D)](#license)

&lt;/div&gt;

---

## The Promise: Brainstorm. Sharpen. Create.

**Idea Man** is a free creative-director plugin for Claude and Codex. It finds the insight first, then generates far past the obvious with methods drawn from real master thinkers. A blind critic scores every idea, and you only see the ones that score 7+, with their risks and the cheapest test.

Bring a half-formed thought, a rough draft, or a direction you already love. Idea Man helps you find the next useful step—and carry the idea further.

&lt;p align="center"&gt;
  &lt;code&gt;&lt;b&gt;Understand&lt;/b&gt;&lt;/code&gt; &amp;nbsp;→&amp;nbsp; &lt;code&gt;&lt;b&gt;Explore&lt;/b&gt;&lt;/code&gt; &amp;nbsp;→&amp;nbsp; &lt;code&gt;&lt;b&gt;Critique (7+)&lt;/b&gt;&lt;/code&gt; &amp;nbsp;→&amp;nbsp; &lt;code&gt;&lt;b&gt;Develop&lt;/b&gt;&lt;/code&gt; &amp;nbsp;→&amp;nbsp; &lt;code&gt;&lt;b&gt;Make&lt;/b&gt;&lt;/code&gt;
&lt;/p&gt;

Site: https://sergey9519546.github.io/idea-man/

---

## Install

**Claude Code**

```bash
claude plugin marketplace add sergey9519546/idea-man
claude plugin install idea-man@idea-man-marketplace
