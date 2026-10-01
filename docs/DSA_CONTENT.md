# DSA content and API contract

DSA content lives in `content/dsa/catalog.json` and `content/dsa/lessons/{id}.json`.
The FastAPI router is registered by `app.include_router(build_dsa_router())` before
static-file routing. It adds no database tables: learner state uses the existing
account-scoped `/api/state` sync mechanism. Completion and mastery are distinct
fields in the DSA state document.

## Publishing content

Catalog `topics` define stable IDs, prerequisites, aliases, category and readiness.
`resources` and `paths` are reusable catalog collections. Detailed lessons carry
sections, language implementations, quizzes, problems, resource IDs and trace
metadata. Lesson JSON filenames must match their IDs and each ID must name a topic.
Only mark a topic `published` when its corresponding lesson is available. Aliases name
one canonical topic; Fenwick Tree and Binary Indexed Tree must not become separate
learning records. Preserve ambiguous terminology as pending curation.

The API validates the entire revision on first request and caches it until restart.
Publish catalog and lesson files together, validate them in tests, then restart the
server. Invalid IDs, duplicate IDs/aliases, missing prerequisites, cycles and broken
lesson resource references return a redacted HTTP 503. Missing lessons return 404.
Failed validation is not cached, so corrected files can be retried. Content files
are trusted authored data, not uploads or a runtime code-execution mechanism.

## Endpoints

- `GET /api/dsa/catalog`: topic/navigation metadata and resource/path catalogs.
- `GET /api/dsa/lessons/{id}`: a detailed lesson, loaded by route when needed.
- `GET /api/dsa/resources`: `q`, `topic`, `type`, `difficulty`, `language`, `limit`, `offset`.
- `GET /api/dsa/problems`: `topic`, `lesson`, `limit`, `offset`; includes problems embedded in lessons.
- `POST /api/dsa/tutor`: explicit learner request for a context-aware tutor response.

Pagination returns `{items, total, limit, offset}`. Limits range from 1 to 100
(default 20), offsets are nonnegative. Filter values match authored metadata.
Resource search is case-insensitive. Topic matching uses canonical IDs.

Tutor requests use `{lessonId, question, mode, context}`. Modes are `explain`,
`socratic`, `hint`, `exam`. Context accepts `frame` (snapshot object or index),
`code`, `error`, `problem` (ID), `attempts` (count), `hints` (already used count),
`mastery` (dimension-to-percentage map), and `selectedObject`. Unknown fields and
oversized context are rejected. The server never executes learner code. Responses
include `answer`, `provider`, `mode`, `lessonId` and a provider disclosure `notice`.

Without configuration, `provider: guided` is a deterministic lesson guide. It
retrieves relevant lesson prose, offers authored progressive hints, and asks
reflection questions. It must not be presented as a language model or code debugger.

## Optional model tutor

Configure an administrator-controlled chat-completions-compatible endpoint:

- `ACADEMY_TUTOR_URL`: full HTTPS endpoint URL (loopback HTTP also allowed).
- `ACADEMY_TUTOR_MODEL`: provider's model identifier.
- `ACADEMY_TUTOR_KEY`: optional bearer credential, stored server-side only.

Both URL and model must be present. Lesson loading and navigation never contact
the provider. Only a learner's explicit tutor POST sends question, mode, selected
lesson excerpt and bounded execution/code context. Disclose that transfer beside
the Ask button. Exam/hint requests omit lesson excerpts to avoid sending solution
material; the system instruction asks for questions or progressive hints. Like any
model instruction, it cannot guarantee the provider never reveals an answer.

Provider requests have a 20-second timeout and a 128KB response limit. Redirects
are rejected to protect credentials. Upstream failures return a redacted 502;
there is no silent fallback that could disguise a failed model call. The app requires a signed-in account for configured model calls and applies a per-IP request limit. Deployments exposing a paid provider should also configure provider spending caps or per-account quotas. Never commit API keys to the catalog.

## Testing

Run `.venv/bin/pytest -q tests/test_dsa_api.py`. Tests use temporary content and
mock provider calls; they need neither a model credential nor outbound access.

## Hierarchy, comparisons and publication validation

Categories can declare `parent` to form a hierarchy. Each topic has one primary
`category` and optional additional `categories` for cross-listing. Both placements
link to the same topic ID and the same learner state. Gomory–Hu, for example,
appears in Graph Algorithms and Advanced Graph Structures. A category parent must
exist and category ancestry must be acyclic.

`comparisons` entries have `id`, `title`, exactly two distinct `topics`, `rows`
(`label` plus two `values` in topic order), and `guidance` explaining how to choose.
The `#compare/{id}` route renders this data as a semantic table. Lesson pages link
to applicable comparisons automatically. Related topics, cross-listings, paths,
resource associations, patterns and practice attachments are validated references.

Published lessons must have objectives, nonempty sections, Python/C++ code,
complexity reasoning, configured trace input, assessments and runnable practice.
This checks the reader contract, not pedagogical quality. Editorial review,
algorithm tests and browser verification are still required. Legacy `ready`
fixtures remain compatible; authors should publish using `published`.

Quiz `type` is `single` (one zero-based integer `answer`) or `multiple` (a nonempty
array of distinct option indices). Multiple-answer grading requires the exact set:
selecting only some correct options or including a distractor fails. Both use the
same independent mastery evidence and review scheduling. Question IDs must be
unique within a lesson. Starter languages must have matching test harnesses;
C++ harnesses contain their own `int main()` and use the existing `__check` protocol.

New trace kinds:

- `linear-search`: `values`, `target`; at most 128 bounded finite values.
- `operation-count`: integer `n` from 0 to 48 and `mode` of `linear`, `triangular`
  or `doubling`. Counts body executions, not every machine instruction.
- `dynamic-array`: `values` (at most 48), initial `capacity` from 0 to 64.
  Starts empty, appends all values, and exposes live size, capacity, copies,
  element writes and simultaneous old/new buffers. Allocation initialization
  is not counted as an element write.

The lab reads `lesson.trace.kind` instead of assuming the topic ID is an adapter
name. All adapters emit the existing immutable frame protocol. The array renderer
accepts optional interval/outside labels so spare capacity is not presented as an
excluded search candidate. Actual edited code still runs separately from traces.

Upgraded `complexity` and `arrays` topics retain their original completion IDs
(`dsa-1-1`, `dsa-1-2`). Reading and writing completion both use that mapping;
mastery, notes and trace evidence use canonical topic IDs. No completion is
converted into mastery. Path recommendations visit prerequisite ancestors before
ranking available topics in the chosen path, and still exclude unmet prerequisites.

Validate content without starting the web application or touching its database:

```sh
.venv/bin/python tools/validate_dsa.py
.venv/bin/python tools/validate_dsa.py --content-dir /path/to/candidate/dsa
```

The command exits nonzero on invalid revisions and distinguishes published,
legacy, planned and unresolved counts. Restart the service after publishing a
validated revision; an already cached server revision is intentionally immutable.
