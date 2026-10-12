# Developer Setup Checklist

Use this checklist manually and ask Antigravity to report each check. Do not share secrets in chat.

## Before running the first prompt

- [ ] Extract the starter-pack folder into the intended repository.
- [ ] Open that exact folder as Antigravity's workspace.
- [ ] Check whether the folder already contains code or an existing Git repository. Do not overwrite existing work.
- [ ] Install a supported Python runtime and Node.js LTS on the development machine if they are missing.
- [ ] Check `python --version`, `node --version`, `npm --version`, and `git --version`.
- [ ] Do not create AWS resources or obtain an LLM API key yet.

## First coding-agent response must provide

- [ ] Current working directory and Git status.
- [ ] Runtime and package-manager versions.
- [ ] OpenCV import path, actual `cv2.__version__`, and whether the runtime is OpenCV 5.
- [ ] Small installation/import smoke-test output.
- [ ] Files created or modified and why.
- [ ] Any unresolved compatibility blocker.
- [ ] A clear pass/fail decision for the current milestone.

## Before frontend/backend integration

- [ ] Vision module can be called from a command-line test without FastAPI or React.
- [ ] Test fixture includes known physical spacing and its provenance.
- [ ] Measurements are compared against ground truth and errors are reported.
- [ ] Low-quality/uncalibrated inputs are rejected or escalated.
- [ ] The local API's OpenAPI schema and health endpoint match the implementation.
- [ ] `.env` and test/site images are ignored by Git.

## Before any AWS deployment

- [ ] AWS account sign-in, region and permissions are verified.
- [ ] Set a budget or billing alert and understand that alerts are not hard caps.
- [ ] Use an IAM role or named profile with least privilege; do not use root credentials for app access.
- [ ] Confirm eligible instance region/type, COOL Marketplace terms and actual estimated/posted price.
- [ ] Have a written create / test / terminate sequence and verify resources are gone after testing.
- [ ] Remove secrets from logs, repository, screenshots and demo recordings.

## Before submission

- [ ] Confirm the live endpoint or judge-accessible demonstration works from a clean session.
- [ ] Run unit, integration, build and held-out evaluation checks.
- [ ] Capture the actual OpenCV version and AWS instance/deployment configuration.
- [ ] Report real accuracy, failure cases, latency and cost results; do not use invented benchmark values.
- [ ] Confirm all used libraries, datasets, photos, model weights and visual assets have appropriate rights.
- [ ] Review official Devpost rules and exact deadline in the live competition page.
