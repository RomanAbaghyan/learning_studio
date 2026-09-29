# DSA extension architecture

## Existing system and gaps
The existing FastAPI service serves a dependency-free static frontend. SQLite holds users, sessions, password-reset tokens, and versioned localStorage state. Eight legacy DSA lessons use stable dsa-* IDs. Progress, XP, Review, CodeEditor and Runner are reusable. LabViz renders canvas data but has no public reversible timeline protocol. There is no existing AI provider, content API, resource library or mastery model.

## Changes and persistence
Keep the existing pages, legacy lesson IDs, database tables and authentication. Extend tracks/dsa.html with hash routes for the DSA workspace. Existing dsa-* hashes continue to open the original reader. Add validated catalog/lesson JSON documents under content/dsa, read APIs under /api/dsa, and a versioned 1991_academy:dsa:v1 state key that travels through existing authenticated sync. Completion remains in Progress; evidence-based mastery is independent. No destructive migration or second identity/progress system.

## Content and API
The catalog owns topic hierarchy, prerequisites, aliases, paths, relationships, patterns and structured resources. Lesson JSON owns original explanations, implementations, problems, hints and assessments. Published topics have real lesson documents; planned topics are visibly labelled and are excluded from next-lesson recommendations. Catalog, lesson, resource and problem APIs expose the same source of truth. The tutor endpoint receives bounded lesson, code, problem, timeline, attempts and mastery context. Deterministic guidance is labelled distinctly from an optionally configured model provider.

## Frontend and visualization
Use existing CSS tokens, auth navigation, code editor and workers. Lazy-load lesson documents and the trace module. One trace frame protocol covers arrays, tree nodes, graphs and DP tables. A shared timeline controller supports play/pause, previous/next, seeking, speed, frame bookmarks, variables, conceptual memory, counters and explanatory pseudocode highlighting. These are teaching traces, not an instrumentation debugger for arbitrary edited code. Edited code runs separately through Runner.

## Safe delivery sequence
1. Audit and architecture (this document).
2. Catalog, APIs and content validation.
3. Binary Search vertical slice.
4. AVL, Dijkstra and 0/1 Knapsack through the same components.
5. Resources/My Library, paths/knowledge graph, practice, mastery/review, notes/bookmarks and tutor context.
6. Content, API, state, trace and browser regression validation.
7. Expand advanced topics into complete lessons individually; do not present roadmap entries as completed teaching material.

## Scope of advanced expansion
Every requested advanced structure receives a canonical curriculum identity and prerequisites. Fenwick Tree and Binary Indexed Tree are aliases, as are KD-Tree and K-Dimensional Tree. Gomory-Hu spans graph algorithms and advanced structures. Fibonacci Tree requires its course definition; it must not silently become Fibonacci Heap. The four reference lessons establish the publishing standard; the full advanced catalog is a continuing curriculum, not a claim that a short introduction satisfies the requirements.
