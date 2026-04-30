CivicJourney DESIGN.md - Semantic Design System

Visual Atmosphere
Mood: Trustworthy, highly accessible, strictly non-partisan, and empowering.
Density: "Art Gallery Airy" - Prioritize expansive negative space to aggressively reduce cognitive load for first-time voters.

Color Calibration (WCAG AAA Accessible Contrast)
Primary Action (Hex): #005A9C (Deep Democratic Blue - used for primary navigation and successful states).
Secondary Action (Hex): #E31937 (Civic Red - used extremely sparingly, only for critical registration deadlines).
Background (Hex): #F8F9FA (Off-white to drastically reduce digital eye strain).
Text Primary (Hex): #212529 (High contrast dark grey for maximum legibility).

Typographic Architecture
Font Stack: 'Inter', system-ui, sans-serif (Clearview ADA alternative).
Scale Hierarchy:
H1 (Bite): 2.5rem, font-weight 700, tight tracking.
P1 (Snack): 1.125rem, font-weight 400, 1.6 line-height for readability.
Detail (Meal): 0.875rem, font-weight 500.

Component Behaviors & Strict Anti-Patterns
Cards: Must utilize subtle glassmorphism or ultra-soft 4px drop shadows. Hard borders are strictly forbidden.
Buttons: Minimum touch target of 48x48px to meet accessibility compliance. Hover states must introduce a smooth 1.05x scale transform.
Anti-Patterns: BANNED: Infinite scrolling mechanics, low-contrast grey text elements, dense text paragraphs exceeding four continuous sentences, and generic AI "slop" rasterized illustrations.
