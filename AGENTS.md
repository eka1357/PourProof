# PourProof — Agent Operating Rules

These rules apply to every coding agent working in this repository, including Antigravity.

## 1. Read the source of truth first

Before editing code, read `PRODUCT.md`, `REQUIREMENTS.md`, `ARCHITECTURE.md`, `STACK_DECISIONS.md`, `UI_UX_SPEC.md`, `TEST_AND_EVALUATION.md`, and `IMPLEMENTATION_PLAN.md`. Follow the current milestone only. Do not jump ahead to later phases.

## 2. Build one verifiable slice at a time

- Start by inspecting the existing workspace, runtimes and Git status.
- Propose a short plan and identify files to create/change before significant edits.
- Implement only the active milestone, not the entire product.
- Run the relevant tests and smoke checks after changes.
- Report commands run, actual results, files changed, unresolved failures and the next gate.
- Never say something works unless you ran it or clearly label it as unverified.

## 3. Computer-vision integrity is non-negotiable

- The required image/video analysis must use **OpenCV 5** substantively. Verify the installed `cv2` version and binary/path at runtime. Do not silently fall back to OpenCV 4.
- Before choosing an API, confirm it exists in the installed OpenCV 5 version. Do not invent APIs or cite untested code as working.
- Never fabricate measurements, confidence, calibration, benchmark results, ground truth, or evaluation outputs.
- A confidence score is not automatically a calibrated probability. Document exactly how any score is calculated.
- The application must abstain or request human review when calibration or visual evidence is insufficient.
- The algorithm must distinguish detected values from nominal/specification values entered by a human.
- Synthetic images can be used for unit tests, but cannot be represented as field validation.

## 4. Genuine Agentic Vision

- The running application—not the coding assistant—must perform a multi-step perception/decision/action loop.
- OpenCV outputs must influence a later tool call, plan, recapture request, reprocessing step or request for human approval.
- Log the inputs, outputs, decisions, selected tool/action, rationale codes, retries and final disposition of each run.
- Do not use a language model to invent or alter numerical measurements.
- Start with a deterministic, testable controller and allow-listed tools. Introduce an LLM planner only if it improves tool selection and can be constrained, tested and observed.
- Never allow autonomous project code to approve a real concrete pour.

## 5. UI and dependency discipline

- Follow `STACK_DECISIONS.md` and `UI_UX_SPEC.md`.
- Do not add every recommended UI library. Use one core component foundation, `motion` for React animation, and copy-paste registries sparingly.
- Before adding a component from an external registry, inspect its source, dependency changes, license/attribution terms, accessibility and mobile behavior.
- Avoid adding both Motion and GSAP for the same job. Do not use Barba.js for navigation in this React SPA.
- No decorative animation may block upload, inspection or reading results. Respect reduced-motion preferences.
- Do not hardcode visual styles repeatedly; use shared tokens and reusable components.

## 6. Security and privacy

- Never put API keys, AWS credentials, access tokens, private endpoints or personal information in source code, screenshots, logs, `.env` files committed to Git, or the demo video.
- Use `.env.example` with placeholders only. Ensure `.env`, private keys, uploaded site photos and local result data are ignored by Git by default.
- Validate file type, decoded file size and image dimensions. Do not trust the filename or browser MIME type alone.
- Do not persist inspection images remotely without clear user disclosure. For the prototype, store only what is required and make retention easy to explain.
- Add request limits and safe error messages. Never expose stack traces, secrets or server filesystem paths to the browser.

## 7. Engineering standards

- TypeScript for the web client; Python type hints for API and vision modules.
- Keep vision logic independent from FastAPI routes and UI components.
- Keep API schemas explicit and versioned.
- Use deterministic tests and fixtures. Test normal cases, invalid inputs, boundary cases and failures.
- Pin tested dependencies for final submission. Do not fabricate version pins before confirming installation and compatibility.
- Prefer small functions, clear types, meaningful logs and focused modules over one very large file.
- Add comments for engineering decisions, not obvious syntax.
- Do not disable tests, lint rules, type checks or security validation merely to make a build pass.

## 8. Change control

- Do not delete working code or rewrite a project from scratch without explaining the reason and obtaining an explicit approval in chat.
- Do not overwrite user-edited configuration without reading it first.
- Do not introduce databases, authentication, Docker, queues, cloud storage or paid services before the active milestone requires them.
- If a requirement conflicts with feasibility, explain the trade-off and propose the smallest safe scope change.
- At the end of every milestone, update `IMPLEMENTATION_PLAN.md` with status and record any measured results in `TEST_AND_EVALUATION.md` or `docs/evidence/`.
