# DSA expansion audit — 2026-10-01

## A. Existing system

FastAPI (`app.py`) serves static pages and the DSA router (`dsa_api.py`). SQLite
stores users, sessions, password resets and a per-user versioned state document.
Authentication, optimistic revision checks, XP, completion, drafts and account
sync already work across tracks. No separate DSA identity database is needed.

`tracks/dsa.html` uses hash routes and `js/dsa-page.js`. The original eight lessons
remain in `dsa-legacy.html` and `js/data/dsa.js`. CSS tokens and shared navigation
are reused. `content/dsa/catalog.json` owns topics, aliases, prerequisites, paths,
resources and patterns. Four lazy-loaded lesson documents cover binary search,
AVL, Dijkstra and knapsack. Each includes implementations, practice, assessments
and original explanatory text.

`DSATraces` emits immutable frames; `DSATimeline` renders arrays, trees, graphs and
tables using existing LabViz primitives. Stepping, replay, seeking, predictions,
bookmarks and conceptual memory are implemented. This is reference execution,
not an arbitrary-code debugger. Runner separately executes Python/JS/C++ practice.
Java and TypeScript are reference implementations. Tutor context and an optional
external provider already exist, with an explicitly labelled local guide.

## B. Gaps

Most advanced topics are planned entries, not complete lessons. Foundational
content still uses the original reader; algorithmic thinking has no lesson.
The data structure hierarchy is too coarse, related edges are mostly empty, and
curriculum validation does not check many cross-references. The algorithm lab
assumes a topic ID is its trace adapter ID. That prevents normal reuse of one
adapter by several lessons. There is no dedicated comparison workspace. A path
selection does not affect recommendations. Comprehensive advanced lessons,
multiple assessment types, full-text search and an in-app content editor remain
larger follow-on work; existing features must not be relabelled as new work.

## C. Architecture changes

Extend the declarative catalog with nested categories, optional cross-listing,
and structured comparisons. Keep canonical topic IDs and aliases. Add deep
foundation lessons and reusable bounded teaching traces through the existing
frame protocol. Resolve algorithm adapters from lesson metadata in the lab.
Add a comparison route using catalog data, and make path recommendations honor
prerequisite closure. Validate references before serving an atomic revision.

## D. Database changes

No tables or destructive migrations. Continue using `state(user_id, data,
updated)` and `martinium:dsa:v1`. Existing completion IDs remain valid, including
`legacyId` mappings for upgraded topics. Historical completion never creates
mastery evidence. New topic evidence and notes use their stable topic IDs.

## E. API changes

Preserve `/api/dsa/catalog`, `/lessons/{id}`, `/resources`, `/problems` and `/tutor`.
The catalog gains optional `categories[].parent`, `topics[].categories` and
`comparisons[]`. Comparisons contain two topic IDs and labelled rows with two
values plus decision guidance. Validate these references, paths, related topics,
resource topics/prerequisites, patterns and problem attachments. Invalid revisions
continue returning redacted 503 responses. No client-originated publishing API.

## F. Frontend changes

Keep existing routes and components. Curriculum renders nested category headings
and cross-listed topics without duplicating learning records. `#compare` offers
semantic comparison tables and links to lessons/labs. The shared lesson reader
continues handling implementations, quizzes, notes, tutor and progress. The lab
loads selected lesson metadata and uses its declared trace kind/input. Path
selection reorders prerequisite-ready recommendations; it never skips prerequisites.

## G. Content architecture

Author substantial algorithmic-thinking, complexity and array units first, with
worked derivations, proofs, memory assumptions, runnable practice and assessments.
Reuse existing lesson JSON fields. Additional traces cover first-match scanning,
operation counting and dynamic-array growth. Source links are added only after
verification, with original summaries and study guidance. Advanced categories
remain honest about publication readiness. Fibonacci Tree stays unresolved.

## H. Migration

Publish upgraded topics under the same canonical IDs; preserve `legacyId` and
original pages. Keep user state unchanged. Categories may move topics without
changing their identity. Validate catalog and lesson files together, run regression
checks against temporary data, then restart the service to load the revision.

## I. Execution order

1. This audit and reviewable architecture contract, before implementation.
2. Category hierarchy, references and comparison model with API regressions.
3. Foundational lessons, verified resources and executable examples.
4. Shared traces and lab integration, with independent result/counter oracles.
5. Curriculum/comparison navigation and prerequisite-aware path recommendations.
6. Full existing test suite and desktop/mobile browser checks.
7. Continue advanced publication topic by topic; catalog coverage is not lesson
   completion and must never be reported as such.
