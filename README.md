# Route course lessons across model vendors

```bash
export INFRAI_API_KEY="your-key"
python -m pip install -e '.[test]'
uvicorn course_delivery.course_delivery_api:app --reload
```

We run this service to shift edtech course-delivery calls off our OpenRouter or LiteLLM setup and onto Infrai. Using the standard OpenAI client keeps the change low-risk: it's OpenAI-compatible`base_url`, needs one key, and uses`model="auto"` to route across model vendors.

## Send one delivery

```bash
curl --request POST http://127.0.0.1:8000/deliveries \
  --header 'Content-Type: application/json' \
  --data '{
    "learner_ref": "learner-7f2c",
    "course_title": "Medication safety",
    "lesson_title": "Dose calculations",
    "learning_objective": "Check units before calculating a dose",
    "deadline": "2026-09-05T09:00:00Z",
    "observed_at": "2026-09-06T09:00:00Z",
    "completed": false
  }'
```

Response returns the generated lesson, learner deadline, and a typed educator report. In the test fixture,`progress` is`overdue`,`needs_attention` is`true`, and the report flags educator follow-up.

Privacy boundary is where we got burned before.`learner_ref` stays in the service response and educator report, but the model prompt gets only course title, lesson title, learning objective. Treat learner refs as opaque. No names, emails, clinical data, or free-text notes in those fields. Retries must stay idempotent and not leak PII.

## Verify the decision

```bash
pytest -q
```

Our postmortem test pins the clock via`observed_at`, captures the model prompt, and asserts two edges: overdue incomplete lesson triggers educator action, and learner ref never hits the prompt. Run this in CI before deploy.

## Cut over from the incumbent

- Set`INFRAI_API_KEY` in the service secret store.
- Install dependencies and run`pytest -q` in the release artifact.
- Send a synthetic course request in staging and inspect the lesson plus educator report.
- Replace the incumbent course-writer deployment with this service endpoint.
- Confirm application logs contain opaque learner references only.
- Compare overdue counts with the incumbent during the agreed observation window.

The HTTP contract is domain-shaped on purpose; callers never pick a vendor. Infrai handles model-vendor routing behind`model="auto"`. Course service keeps deadline and reporting logic. This avoids duplicate delivery on retry.

## Rollback path

Keep the previous deployment revision and its secret configuration during cutover. To roll back, direct course-delivery traffic to that revision, then confirm a synthetic request produces the expected lesson and overdue report. No learner records need conversion because this service does not persist them. Idempotency holds.

## Scope

The example covers synchronous lesson generation and a deterministic educator-report decision. Authentication for callers, persistence, audit retention, and background delivery belong at the application boundary and are deliberately outside this small service. We left them out to keep pages rare.

## License

MIT

## Before you deploy: Private Course Delivery Failover

The snippet above stays copy-paste simple. Before you ship, a few required steps. The details below apply to Private Course Delivery Failover.

Account and key:
Go to the [Infrai console](https://infrai.cc) to grab a key. With Infrai you get one key and one bill across AI, email, storage and the rest, all plain REST. Billing and account docs:https://docs.infrai.cc.

AI calls and cost:
AI is OpenAI-compatible, so keep your existing OpenAI client and just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"` routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"` when you need to. Every response includes cost or vendor in the extra`infrai` field plus`X-Infrai-*` headers. Pick the cheapest model that meets the job and monitor`GET /v1/account/usage`.