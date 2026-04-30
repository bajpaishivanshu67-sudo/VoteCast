<div align="center">
  <img src="https://via.placeholder.com/150x150/005A9C/FFFFFF?text=CivicJourney" alt="CivicJourney Logo" width="120" height="120" />

  <h1>🗳️ CivicJourney</h1>
  
  <p>
    <strong>A Gamified, Intent-Driven Election Education Platform</strong><br>
    Built autonomously for the <strong>Google PromptWars Hackathon</strong>
  </p>

  <p>
    <a href="https://civic-journey-102848677466.us-central1.run.app"><strong>View Live Demo</strong></a> ·
    <a href="#features">Features</a> ·
    <a href="#tech-stack">Tech Stack</a> ·
    <a href="#architecture">Architecture</a>
  </p>
</div>

<hr />

## 🌟 Overview

**CivicJourney** is a production-ready, interactive web application designed to demystify the election process for first-time voters. Engineered using **Google Antigravity** and **Gemini 3.1 Pro**, the platform embraces the paradigm of *intent-driven development* ("vibe coding").

By adhering to an "Art Gallery Airy" design philosophy, CivicJourney aggressively reduces cognitive load while providing an engaging, interactive learning experience.

## ✨ Key Features

- **📜 Scroll-Triggered Timeline**: A Framer Motion-powered vertical tracker that visually guides users through the election lifecycle.
- **📚 Bite, Snack, Meal Architecture**: Information is delivered progressively. Users can scan the "Bites" and expand the "Meals" (interactive accordions) only when they desire deep-dive legal data.
- **✅ Interactive Mock Ballot**: A fully accessible, stateful simulation allowing users to securely select candidates and cast a simulated vote with dynamic success animations.
- **🏆 Gamification Engine**: A global `CivicRewardsContext` powering digital achievement badges (e.g., "Civic Duty") that persist and celebrate the user's progress.
- **🎨 Semantic Design System**: Built with strict constraints for high-contrast accessibility (WCAG AAA), using a deep Democratic Blue (`#005A9C`) and Off-White (`#F8F9FA`).

## 🛠️ Tech Stack

- **Framework**: Next.js 16.2.4 (App Router)
- **Styling**: Tailwind CSS, utilizing a strict semantic palette defined in `DESIGN.md`
- **Animations**: Framer Motion (Spring physics, AnimatePresence)
- **Icons**: Lucide React
- **Deployment**: Google Cloud Run (Serverless)

## 🚀 Getting Started

To run the application locally:

```bash
# Clone the repository
git clone https://github.com/bajpaishivanshu67-sudo/VoteCast.git

# Navigate to the application
cd civic-journey

# Install dependencies
npm install

# Start the development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## 🏗️ Architecture & AI Governance

CivicJourney was engineered using **Google Antigravity's** intent-driven capabilities. The AI agent logic was governed by `.agents/skills/civic-builder/SKILL.md`, ensuring all generated components strictly adhered to the "Bite, Snack, Meal" hierarchy and avoided banned UX clichés (like infinite scrolling).

---
*Developed for Google PromptWars 2026.*
