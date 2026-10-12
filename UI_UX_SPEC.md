# UI/UX Specification

## Overall direction

A credible engineering inspection workspace: precision instrument, not a generic AI chatbot or neon SaaS dashboard. Use restrained contrast, generous spacing, technical labels, clear image evidence and purposeful animation.

## Art direction

- Dark-first, neutral graphite/navy canvas so annotations over construction images are easy to inspect.
- High-contrast text, subdued borders and surfaces, restrained teal/cyan as the primary action color.
- Amber for caution/uncertain; red only for confirmed potential out-of-tolerance findings or errors; green only for a valid, supported check—not as a blanket claim that the rebar is safe.
- No giant glowing gradients, constant motion, fake real-time counters, random stock dashboards or decorative charts without data.
- Use a construction photograph or a clean rebar-grid SVG only where it helps users understand the product. Do not use image mockups in place of live outputs.

## Starting tokens (adjust after using Realtime Colors)

These are initial design tokens, not a final brand constraint:

```css
:root {
  color-scheme: dark;
  --background: #0b1116;
  --surface: #111a21;
  --surface-raised: #19242c;
  --border: #2a3943;
  --text: #edf3f5;
  --muted: #a0afb8;
  --primary: #65d9c1;
  --primary-foreground: #071310;
  --info: #81b9ff;
  --warning: #f3bf69;
  --danger: #ff7777;
  --success: #68d6a3;
  --focus: #b3e9ff;
}
```

Verify contrast rather than assuming colors pass. Include a clear light/dark strategy only if time permits; do not let theme work delay the vision workflow.

## Typography and layout

- Use a modern neutral sans such as Inter or the system UI stack; use a monospaced face for coordinates, units, IDs and performance values.
- Numeric measurements use tabular numerals and always show units.
- Desktop inspection layout: navigation/heading, image work area, parameter/result side panel, then trace/detail section. Keep the image as the primary focus.
- Mobile layout: stack controls before results, keep upload/retake action reachable, make result table scroll or reflow appropriately.
- Consistent radii and spacing tokens. Avoid nested card-in-card-in-card layouts.

## MVP screens

### 1. Overview (`/`)

- Product name and a concrete value proposition.
- Primary action: “Start inspection”.
- Three compact steps: calibrate, measure, review evidence.
- A real or clearly labelled sample only; do not present fabricated benchmark values as real outcomes.
- Small limitations statement: calibrated, visible, planar reinforcement only; engineer retains decision authority.

### 2. Inspection workspace (`/inspect`)

- Upload/drop area supporting listed formats and showing size/dimension limits.
- Parameter form: marker size, nominal center-to-center spacing, tolerance, units.
- Original image preview plus a clearly separated annotated/rectified preview.
- Image quality/calibration status with specific reason codes and next action.
- “Analyze” button disabled until mandatory fields are valid.
- Loading states describe actual stages; no fake percentage progress unless progress is measured.

### 3. Results (`/inspections/:id` or a returned result view)

- Status banner must be `Complete`, `Complete with flags`, `Retake image`, `Needs human review`, or `Failed`—do not use `PASS: SAFE`.
- Measurement table with ID, direction, measured spacing, unit, deviation from user-entered nominal spacing, quality/status and evidence link.
- Overlay legend for detected centerlines, calibration marker, measured gaps and candidates requiring review.
- Agent trace/timeline showing tool, evidence/reason, output summary and selected next action.
- Export raw JSON report; PDF report is optional.

### 4. Evaluation (`/evaluation`, optional after MVP)

- Dataset name/version, number of total/accepted/rejected cases and failure count.
- Actual error statistics, precision/recall for the defined detection task, abstention rate and agentic retry comparison.
- Latency per stage and benchmark environment.
- Clear distinction between controlled fixtures and field photographs.
- If values are unavailable, show an empty state explaining how to run evaluation; do not create sample values that look real.

## Interaction details

- Upload progress only when real bytes/progress are available.
- Every warning says what failed and the next useful action.
- Keep the original image accessible when the result is annotated.
- Tool trace is inspectable and copyable; don't use vague “AI is thinking” animations to replace actual event logging.
- Confirm before clearing an in-progress inspection if it would discard user input.
- Respect reduced-motion settings. Motion should be limited to route/panel entrances, upload feedback and small state changes.

## Icons, charts and animations

- `lucide-react` icons only for consistency.
- Motion from `motion/react` for restrained interactions. No animated detection overlay that shifts the measured evidence.
- Bklit or other chart component only after real evaluation metrics are present; prioritize labels, scales and provenance over visual spectacle.
- 21st.dev/React Bits/Watermelon/Skiper components must be adapted to these tokens; never paste a component that creates a second unrelated visual system.

## Accessibility checklist

- Keyboard-accessible upload button, forms, dialogs and navigation.
- Explicit labels, inline error messages and status announcements for upload/results.
- Visible focus and meaningful alt text for original/annotated images.
- Text labels accompany color-coded statuses.
- No essential instruction is communicated by color alone.
- Respect `prefers-reduced-motion`.
