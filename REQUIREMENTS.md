# Requirements — PourProof MVP

Every requirement must be mapped to an implementation location and a test. The labels below are stable identifiers for issue/task tracking.

## Functional requirements

### Inputs and validation

- **FR-001 — Image upload:** User can submit one JPEG, PNG or WebP image supported by the installed image decoder.
- **FR-002 — Image validation:** API validates the decoded format, byte size, pixel dimensions and image readability; invalid files receive a useful safe error.
- **FR-003 — Inspection parameters:** User enters marker/reference dimension, nominal spacing, tolerance and units. Units must not be implicit.
- **FR-004 — No hidden assumptions:** API records input parameters and calibration assumptions with each result.

### Vision pipeline

- **FR-010 — OpenCV 5 verification:** Runtime diagnostics report OpenCV version and binary/module path. If OpenCV 5 is not active, mark the service unhealthy for competition use instead of silently falling back.
- **FR-011 — Image quality:** Evaluate blur, exposure/contrast and relevant calibration-marker visibility. Thresholds must be documented and tested; they are not universal physical guarantees.
- **FR-012 — Calibration:** Detect a known-size calibration reference and estimate a pixel-to-mm mapping only when the reference is usable and sufficiently coplanar with the bars.
- **FR-013 — Plane rectification:** Use perspective correction when the image/reference geometry supports it; report failure or unsupported conditions rather than pretending an oblique photo is rectified correctly.
- **FR-014 — Grid detection:** Detect candidate rebar centerlines in two grid directions for the supported single-mat case.
- **FR-015 — Gap computation:** Estimate adjacent center-to-center gaps in physical units and preserve the underlying pixel measurements, transformation/calibration details and quality metadata.
- **FR-016 — Specification comparison:** Compare measured values against only the user-entered nominal spacing/tolerance. Do not infer a design requirement.
- **FR-017 — Annotation:** Return an annotated image overlay showing detected centerlines, gap labels and review flags. Avoid hiding uncertainty under green status colors.
- **FR-018 — Abstention:** If calibration or grid detection is insufficient, do not return a definitive pass/fail result. Return a structured status explaining why.

### Agent loop

- **FR-020 — Tool allowlist:** Controller can call only explicit image-quality, calibration, rectification, detection, measurement, comparison and permitted reinspection tools.
- **FR-021 — Evidence-dependent action:** Actual vision output determines whether the controller retries processing, requests recapture, measures, completes or escalates to human review.
- **FR-022 — Bounded retries:** Set a documented maximum number of processing attempts; terminate loops safely.
- **FR-023 — Trace:** Record ordered tool calls, essential inputs/outputs, rationale codes, status changes and final disposition.
- **FR-024 — No invented measurements:** A language model, if eventually added, may not write numeric measurement outputs except by returning IDs/references produced by measurement tools.
- **FR-025 — Human decision:** UI makes clear that the tool is advisory and does not approve construction work.

### Report and evaluation

- **FR-030 — Result view:** Display original image, annotated image, parameters, measurements, quality/uncertainty status and the agent trace.
- **FR-031 — Export:** Provide a reproducible JSON report at minimum; PDF export is optional after the core works.
- **FR-032 — Evaluation command:** Provide a command that runs the evaluation set and saves a machine-readable metrics file.
- **FR-033 — Failure reporting:** Report false detections, failed calibrations and withheld outputs; don't count only successful cases.
- **FR-034 — Benchmark support:** Where COOL is available, run the same workload on documented baselines and record environment/configuration.

## Non-functional requirements

- **NFR-001 — Reproducibility:** Document environment setup, versions, data manifest, commands and how to reproduce recorded metrics.
- **NFR-002 — Separation of concerns:** Vision functions are independent of API routes, UI and orchestration.
- **NFR-003 — Type safety:** TypeScript types for the frontend/API contract; Python type hints and validation for the backend.
- **NFR-004 — Error handling:** Unsupported/poor-quality images return explicit machine-readable errors, not unhandled stack traces.
- **NFR-005 — Performance observability:** Record total latency and per-stage latency, at least during evaluation.
- **NFR-006 — Accessibility:** Keyboard navigation, visible focus, clear labels, readable contrast and reduced-motion support.
- **NFR-007 — Responsive layout:** Desktop-first detailed inspection screen, with upload and results usable on narrower screens.
- **NFR-008 — Privacy:** Don't upload or retain images remotely unless the user is informed; don't log image payloads or secrets.
- **NFR-009 — Safe file handling:** Enforce file size/dimension limits and use generated safe filenames if storing files.
- **NFR-010 — Pin tested dependencies:** Final environment must use exact versions verified to install and pass the test suite.
- **NFR-011 — OpenCV 5 compliance:** The substantive analysis path uses the actual OpenCV 5 distribution; compatibility claims require a smoke test on the target environment.
- **NFR-012 — Maintainability:** No single giant source file; errors, schemas and state transitions are explicit and documented.

## Definition of done for MVP

- [ ] The app starts from documented commands on a clean environment.
- [ ] OpenCV 5 version/path verification passes in the intended execution environment.
- [ ] One calibrated controlled fixture produces a measured result compared with known ground truth.
- [ ] Invalid/unusable images produce abstention or a recapture/review path.
- [ ] The agent trace proves a vision result changed a later action/tool call.
- [ ] Tests cover normal, boundary and failure cases.
- [ ] A small evaluation dataset is documented and its metrics are reproducible.
- [ ] UI does not overstate accuracy or construction safety.
- [ ] AWS execution and logs are verified before making claims about deployment.
