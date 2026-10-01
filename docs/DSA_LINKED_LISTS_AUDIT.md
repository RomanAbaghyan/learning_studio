# Linked Lists continuation — 2026-10-01

## A. Existing system

The current FastAPI/static JavaScript application already publishes seven DSA
lesson documents through ContentStore. SQLite identity and versioned account
state persist completion, independent mastery, notes, bookmarks and resources.
The shared reader loads lesson JSON and integrates Runner practice, quizzes,
tutor context and DSATimeline. Immutable teaching frames already support arrays,
trees, graphs and tables. The legacy combined lists/stacks/queues reader remains
available as `linear-structures` / `dsa-1-3`.

## B. Gap analysis

`linked-lists` has a canonical topic and prerequisite but is still planned.
There is no pointer-reassignment teaching trace. The graph renderer assumes
shortest-path distances and heap state, so presenting a linked list as a graph
would produce misleading labels. Advanced list prerequisites currently depend
on the combined legacy introduction rather than this deeper unit.

## C. Architecture changes

Publish the existing `linked-lists` ID. Add a bounded linked-list adapter to
DSATraces and a semantic node/link view in the existing timeline renderer.
Use the same controller, frame protocol, inspectors, predictions and bookmarks;
create no separate animation framework. Trace reverse, indexed insert, indexed
erase, first-match find and stable sorted merge, retaining detached nodes in
intermediate snapshots.

## D. Database changes

None. All new learning state uses the existing canonical topic ID and sync.
Keep the combined legacy completion separate: completing it does not prove this
lesson's mastery and must not complete this new unit automatically.

## E. API changes

No new endpoints. The existing lesson endpoint exposes the new JSON, the problem
API indexes its practice, the resource API includes verified OpenDSA metadata,
and tutor requests receive the existing lesson/frame/code context contract.

## F. Frontend changes

Existing `#topic/linked-lists` and `#lab` routes discover published content.
Extend `DSATimeline.renderView` with directed successor arrows and a node/link
table using existing canvas primitives, styles, text labels and active-state
markers. All transient pointers are visible without relying on color; diagrams
and tables scroll inside the visualization on mobile. The lab's pattern and size
controls generate input chains rather than showing unrelated graph/DP guidance.

## G. Content architecture

One declarative lesson teaches the sequence ADT, singly/doubly/circular lists,
sentinels, traversal, find, insertion, deletion, reversal, sorted merge,
ownership, invariants, proofs, memory costs and alternatives. Python, C++, Java,
TypeScript and JavaScript implementations demonstrate actual node operations.
Runnable reverse practice tests preservation of node identity and links, beyond
checking output values. Additional reasoning exercises build toward advanced
lists. External sources supply metadata and study guidance, never copied prose.

## H. Migration plan

Keep all IDs, existing documents and learner data. Mark only this topic
published when content, traces and executable examples pass validation. Update
advanced list prerequisite edges to the new unit without creating duplicate
topics or remapping previous completion. No database migration or server-side
publishing action is needed for this working-tree change.

## I. Implementation phases

1. Record this audit before implementation.
2. Implement bounded immutable traces and shared semantic pointer rendering.
3. Author and publish the full lesson and verified resource associations.
4. Validate implementations against independent list/identity oracles; execute
   all language examples and practice harnesses.
5. Exercise lesson, lab, pointer inspections and mobile behavior in browser;
   run existing regression tests and update delivery documentation.

The remaining core and advanced topics remain outstanding. Fibonacci Tree is
skipped at the learner's explicit request and remains unpublished.
