# APIs, Credentials and External Services

## The key decision

**No external AI API key is required for Milestone 0 or the first vision prototype.** Start with local OpenCV 5, Python, and test images. Do not configure Gemini, AWS storage, authentication, a database, or an agent framework before the local vision spike passes.

The frontend later calls our own FastAPI service. That is an API we build; it is not a vendor key.

## Service plan by phase

| Phase | Service or API | Required? | Credentials |
|---|---|---:|---|
| 0–1: local vision spike | OpenCV 5 + Python | Yes | None for local processing |
| 2: tests and evaluation | Local test fixtures and evaluation scripts | Yes | None |
| 3: perception/decision/action loop | Internal Python functions and deterministic controller | Yes | None |
| 4: web UI | Our FastAPI endpoints + React fetch client | Yes, once UI is connected | None for localhost |
| 5: cloud deployment | AWS EC2 or another eligible AWS compute service | Yes, for meaningful cloud delivery | AWS account and scoped permissions |
| 5: optional artifacts | Amazon S3 | Only if persistence is required | IAM role / scoped permissions |
| 5: observability | Amazon CloudWatch | Recommended for deployed measurements | IAM role / scoped permissions |
| optional LLM planner | Gemini API or another supported model provider | No | Provider API key, kept server-side only |
| COOL award path | COOL on compatible AWS Graviton deployment | Optional special-award path | AWS account, Marketplace access/subscription and correct deployment permissions |

## Credentials that may be needed later

### AWS

1. Have an AWS account ready; do not use root credentials for application execution.
2. Set a budget/usage alert before launching compute. A budget alert is not a hard spending cap.
3. For local deployment work, use AWS CLI with a named profile or an approved federation/SSO setup. Do not paste access keys into prompts.
4. For an EC2-hosted app, prefer an instance IAM role with least-privilege permissions over long-lived credentials on the instance.
5. Create a dedicated bucket only if the product actually needs persistent artifacts. Keep it private and define a retention/deletion policy.
6. Before COOL: verify the exact Marketplace product, supported instance families/regions, Python version, license, usage fee, and how to terminate resources. Never start an instance without confirming the intended hourly cost and shutdown procedure.

Official security references:
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html
- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html
- https://github.com/opencv/COOL-Benchmark
- https://aws.amazon.com/marketplace/pp/prodview-igdweaoo6prb6

### Optional LLM API

Do not obtain a key yet. First ship a deterministic controller where measured OpenCV outputs determine the allowed next action. If later evaluation shows that an LLM improves tool selection or user-facing explanation, add one provider behind a backend adapter and compare it with the deterministic baseline.

If using Gemini, create the key via Google AI Studio and set `GEMINI_API_KEY` only in the local untracked `.env` or a deployment secret manager. Never put it in React/Vite `VITE_*` variables, source code, browser requests, screenshots, commits, or logs. The browser must call our backend; only the backend may call the LLM provider.

Official references:
- https://ai.google.dev/gemini-api/docs/billing
- https://ai.google.dev/gemini-api/docs/rate-limits

Guardrails if an LLM is added:
- The LLM may select only from an allow-list such as `REPROCESS_CROP`, `REQUEST_RECAPTURE`, `REVIEW_MEASUREMENT`, `HUMAN_REVIEW`.
- Validate model output against a schema and deterministic policy checks.
- The LLM may not write or alter numeric measurements, thresholds or ground truth.
- Persist a redacted action trace and handle timeout, quota exhaustion, malformed output and provider errors.
- Don't transmit real construction-site photos to a third-party model without an explicit product/privacy decision.

## Local environment variables

Copy `.env.example` to `.env` only when the app needs it. All values in `.env.example` are placeholders. `.env` must remain untracked.

- `APP_ENV`: `development` locally.
- `API_BASE_URL`: the local FastAPI base URL.
- `ENABLE_LLM_PLANNER`: false until the LLM is approved and tested.
- `GEMINI_API_KEY`: blank until an LLM is intentionally added.
- `AWS_REGION`, `AWS_PROFILE`, `S3_BUCKET`: blank until AWS is needed and configured.

Do **not** add `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` to the committed sample file. Use the AWS CLI profile/role mechanism instead.

## Do not configure all integrations up front

The correct sequence is: local OpenCV works → measured evaluation works → deterministic agent loop works → local API/UI works → AWS deployment works → optional COOL benchmark → optional LLM. This order keeps debugging local and limits surprise costs.
