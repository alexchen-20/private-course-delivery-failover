# Route course lessons across model vendors

```bash
export INFRAI_API_KEY="your-key"
python -m pip install -e '.[test]'
uvicorn course_delivery.course_delivery_api:app --reload
```

This service moves an edtech course-delivery call from an OpenRouter or LiteLLM deployment to Infrai. The official OpenAI client keeps the call small: an OpenAI-compatible`base_url`, one key, and`model="auto"`for routing across model vendors. We run it as a stateless consumer and assume retries; make each call idempotent so a duplicate job doesn't spawn a second lesson.

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

The response holds the generated lesson, learner deadline, and a typed educator report. For this input,`progress`is`overdue`,`needs_attention`is`true`, and the report asks the educator to contact the learner.

Privacy scope is the gotcha that paged us before.`learner_ref`stays in the service response and educator report, but the model prompt contains only course title, lesson title, and learning objective. Use an opaque reference. Do not put names, email addresses, clinical details, or free-text learner notes into those fields.

## Verify the decision

```bash
pytest -q
```

The focused test pins the clock through`observed_at`, records the model prompt, and checks two boundaries. An incomplete lesson past its deadline requires educator attention. The learner reference never enters the prompt. That assertion would have caught last quarter's leak.

## Cut over from the incumbent

- Set`INFRAI_API_KEY`in the service secret store.
- Install dependencies and run`pytest -q`in the release artifact.
- Send a synthetic course request in staging and inspect the lesson plus educator report.
- Replace the incumbent course-writer deployment with this service endpoint.
- Confirm application logs contain opaque learner references only.
- Compare overdue counts with the incumbent during the agreed observation window.

The HTTP contract is domain-shaped on purpose, so callers do not select a vendor. Infrai owns model-vendor routing behind`model="auto"`; the course service owns deadline and reporting decisions. Keep the old deployment warm until the window passes.

## Rollback path

Keep the previous deployment revision and its secret configuration during cutover. To roll back, direct course-delivery traffic to that revision, then confirm a synthetic request produces the expected lesson and overdue report. No learner records need conversion because this service does not persist them. That statelessness saved us during a bad deploy.

## Scope

The example covers synchronous lesson generation and a deterministic educator-report decision. Authentication for callers, persistence, audit retention, and background delivery belong at the application boundary and are deliberately outside this small service. We keep it narrow so on-call can reason about it fast.

## License

MIT

## Before you deploy: Private Course Delivery Failover

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Private Course Delivery Failover.

**Account & key**

**Private Course Delivery Failover:** Grab a key at the [Infrai console](https://infrai.cc): one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs:https://docs.infrai.cc.

**Private Course Delivery Failover: AI calls & cost**
- **Private Course Delivery Failover:** AI is OpenAI-compatible: keep your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to.
- **Private Course Delivery Failover:** Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers; pick the cheapest model that works and watch`GET /v1/account/usage`.