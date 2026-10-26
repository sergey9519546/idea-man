# Worked examples and local receipts

Run `python eval/worked_examples.py`, then `python eval/worked_examples.py --check`.

These are **authored responses to synthetic tasks**, not captured plugin conversations,
customer results or baseline comparisons. The generator uses three tasks from
`eval/cases.json`, calculates the displayed facts, and executes the packaged
candidate helper twice. Its readiness inputs are authored judgments.

`results.json` contains complete source conversations, responses, calculations,
helper inputs/outputs and SHA-256 bindings to the source cases, generator and helper.
A pinned casebook hash stops generation if the task source changes; review the
narratives and arithmetic before deliberately updating that pin.

The web build rejects stale source bindings before replacing its output directory.
It never upgrades these records into paired model evidence. The paired-output
harness in ../README.md is separate: genuine fresh captures and independent reviews
are still required. Do not import these worked responses as observed captures.

Coverage: diagnosis, decision sensitivity and pilot interpretation. These examples
do not establish ideation originality, superiority over an ordinary assistant,
native host activation or customer usefulness. No model calls are made.

Source hashes use UTF-8 text with CRLF normalized to LF (sha256-utf8-lf), so a Git checkout on another operating system can reproduce the same source bindings.
