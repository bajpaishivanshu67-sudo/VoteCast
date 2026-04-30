name: civic-builder
description: Ironclad constraints for generating the Election Process React UI components.

Execution Protocol
You MUST follow this 4-step processing loop without any deviation:
Analyze: Read DESIGN.md prior to generating any component to verify exact hex code and typography alignment.
Fetch: Query the Stitch MCP server to pull down the requisite UI component tokens for the current task.
Animate: All state transitions, layout changes, and scroll events MUST be wrapped in framer-motion <motion.div> components. Utilize React's IntersectionObserver logic for scroll-triggered timeline reveals to ensure ultra-smooth performance.
Structure: You must implement the "Bite, Snack, Meal" information hierarchy for all civic text blocks, ensuring complex legal data is hidden behind expandable, animated accordions.
