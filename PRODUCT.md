# Product Brief — PourProof

## One-line description

PourProof is an evidence-driven visual assistant that measures visible reinforcement-bar spacing from a calibrated, approximately planar photograph and requests better evidence when a trustworthy measurement cannot be made.

## Problem

Before a concrete pour, construction teams inspect a reinforcement mat against engineer-specified spacing. Manual checks take time, and photographs can be hard to interpret because of perspective, glare, poor lighting, overlapping bars or incomplete calibration. A computer-vision result without calibration and uncertainty handling risks giving false confidence.

## Target user

A site engineer, QA/QC engineer or inspector who can place a known-size calibration marker in the same plane as the visible rebar mat, knows the design spacing/tolerance, and remains responsible for the construction decision.

## Primary job to be done

"Help me measure the visible spacing in this rebar mat, show the evidence behind each measurement, and tell me when the photo is not good enough to support a result."

## Product promise

- Display visible measurements and how they were derived.
- Compare measurements only against specifications entered by the user.
- Explain when calibration or visual quality is inadequate.
- Reinspect or ask for a new photograph when image evidence indicates that the next step is needed.
- Preserve a trace of image quality checks, detection/measurement attempts and agent decisions.

## MVP workflow

1. User uploads one image showing a single visible rebar mat and a known-size fiducial/calibration marker in the same plane.
2. User enters marker dimension, nominal rebar center-to-center spacing and allowed tolerance. Units are explicit.
3. The API validates the image and runs quality checks.
4. OpenCV 5 detects/validates the marker, rectifies the plane when possible, detects the two grid directions and estimates centerlines.
5. The measurement module computes candidate center-to-center gaps in millimetres and attaches evidence/quality metadata.
6. A controller decides whether to accept the evidence, retry a permitted processing path, request a new image or escalate to human review.
7. The UI presents an annotated image, measurement table, specification comparison, limitations and an inspectable action trace.
8. A benchmark mode evaluates an image set with recorded ground truth; it must not mix results from evaluation with invented demo values.

## MVP boundary

### In scope

- One approximately planar exposed reinforcement grid per image.
- A clear fiducial/calibration marker or another documented known-size reference coplanar with the mat.
- Visible bar centerline and adjacent spacing estimation.
- Image-quality/marker checks, abstention and recapture requests.
- Annotation, result trace, small repeatable evaluation set.
- A modest React web client and Python API.
- A meaningful OpenCV 5 workload running locally first, then on AWS.

### Out of scope for the deadline

- Certified code-compliance decisions or structural safety assessment.
- Automatic approval of a concrete pour.
- Estimating hidden reinforcement or steel grade.
- Reliable diameter, lap-length, anchorage, cover-depth or multi-layer detection.
- General-purpose BIM/digital-twin integration.
- Mobile native application, user accounts, enterprise roles or elaborate collaboration.
- Unbounded autonomous LLM behavior.
- Claims of industry-standard measurement accuracy without a verified evaluation protocol.

## User stories

- As an inspector, I can state the marker size, design spacing, tolerance and unit before analysis.
- As an inspector, I can see the original and annotated/rectified evidence side by side.
- As an inspector, I can inspect each gap estimate and understand whether it is supported by sufficient image quality.
- As an inspector, I can see why a measurement was withheld or why a new image was requested.
- As a reviewer/judge, I can replay an inspection trace and reproduce results using the supplied environment and fixtures.
- As a competition judge, I can see the running OpenCV 5 implementation and the workload running on AWS.

## Product principles

1. Evidence before explanation.
2. Refuse to guess when calibration or detection fails.
3. Human authority for any real construction decision.
4. Make failure modes visible, not hidden behind a polished score.
5. Keep the MVP narrow enough to test honestly before adding more features.

## Success measures

The project succeeds as a prototype when it can reproducibly measure a clearly defined controlled test set, report its actual error and failure rate, request better evidence in relevant cases, and prove that OpenCV 5 executes on AWS. Numeric targets are specified in `TEST_AND_EVALUATION.md` as goals to test, not pre-existing achievements.
