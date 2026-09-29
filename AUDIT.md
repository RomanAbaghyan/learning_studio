# Project review

This is a small, local-first learning application: static HTML/JavaScript, one FastAPI service, SQLite, and a separate Docker C++ runner. That deployment is coherent for a personal learning site. Splitting it into microservices or replacing SQLite would add complexity without evidence of a scaling requirement.

## Fixed

- API handlers assumed JSON objects and accepted coerced credential types. Arrays, scalars, deeply nested JSON and invalid Unicode now return validation errors.
- Streamed requests could bypass the Content-Length limit. Actual request bytes are bounded before dispatch; cross-origin browser mutations are rejected.
- Reset tokens could be used by concurrent requests. Reset, password change, login/session creation and account deletion now serialize their critical database operations. Password changes revoke outstanding reset links, and password verification endpoints have rate limits.
- Production without SMTP logged usable reset links. Only debug mode logs those links now.
- State writes silently overwrote concurrent edits, and startup could mix accounts. The frontend sends account ownership and a revision; the database checks and writes atomically. Uploads are serialized in each tab. Startup checks ownership, tracks the last synced copy, and asks the learner to choose on the Account page when both copies changed. Equal XP no longer determines which edits survive. Failed local replacement rolls back to the previous values.
- Upload sizing counted UTF-16 characters instead of UTF-8 bytes. Armenian drafts now obey the actual upload cap. Draft shedding retains the device's local draft.
- JavaScript fell back to executing learner code on the main thread if workers failed. Execution now reports a capability error instead of risking an unrecoverable UI freeze.
- Direct startup exposed host C++ execution on the LAN by default. It now binds to localhost and requires explicit opt-in for host C++ execution. Docker retains its isolated runner.
- Runner connections could allocate unbounded handler threads; temporary-directory allocation could leak slots. Connections are bounded, reads time out, allocation failures return slots, and failed cleanup quarantines a slot.
- Rate-limit buckets had no hard bound while all entries were recent. New buckets are rejected when capacity is exhausted.
- Restore overwrote the live database before checking whether its contents were a valid Academy database. The new restore utility stages, validates and fsyncs a backup before replacement, checkpoints the old database first, and retains the pre-restore backup workflow.
- Compose now waits for the runner's health check before starting the app.

## Remaining boundaries and design decisions

These changes do not establish that every bug has been found.

1. **Leaderboard integrity:** XP and grading are still client-reported. The leaderboard is suitable for an honor-system learning site, not prizes, certification or adversarial competition. Trusted grading would require server-owned exercise definitions and server-validated completion events.
2. **Browser execution isolation:** workers protect responsiveness, but they are not a separate security origin. Treat pasted JavaScript/Python as code the learner trusts. Running arbitrary third-party code safely requires a separate-origin execution service/frame and a constrained message protocol.
3. **Legacy sync clients:** the API accepts writes without revision metadata for compatibility. Reload existing tabs after deploying. Requiring revision metadata is a future breaking API change.
4. **Scale and availability:** rate limits are process-local, SQLite has one writer, reset email delivery is an in-process task, and backups share the server unless copied elsewhere. Multiple app replicas or stronger recovery/delivery guarantees require explicit deployment targets and additional shared infrastructure.
5. **Sync semantics:** conflicts use an explicit whole-copy choice, not automatic field-level merging. Large drafts may stay on one device; a page being killed can still prevent its last queued upload. Local storage remains the recovery copy.
6. **Schema evolution:** startup migrations are still embedded in app.py. A versioned migration layer and separate auth/state/runner modules are reasonable follow-ups as the schema and team grow; a wholesale rewrite was not necessary for these fixes.

## Verification

The full Python/content suite passed with 268 tests, including reference solutions and starters in JavaScript, Python and C++. The final targeted run passed 159 checks; one Unicode test failed in the HTTP client before reaching the app. After correcting its escaped JSON payload, that remaining test passed on rerun. These 160 checks cover the subsequent runner-resource and request-validation changes. The frontend suite runs through pytest and directly through `node tests/frontend.test.cjs`.

JavaScript syntax and Compose configuration were checked. This review did not run a real-browser end-to-end session, rebuild the Docker images, or rerun the hostile-program container suite. The existing CI exercises Docker deployment and the sandbox; those checks remain necessary before production rollout. No live database was restored or changed.
