# Forward testing

`forward_cases.json` is a versioned qualitative scenario pack. It is intended to test actual model behavior after the deterministic package tests pass.

## What the pack tests

Each case specifies a route, a prompt, required properties, forbidden properties, and scoring dimensions. The pack currently covers every installed writing workflow, including the separate academic-content workflow. The validator discovers workflow directories under `skills/*/SKILL.md` and fails if an installed route is not represented in the pack.

The cases are evaluated manually with a fresh model context for every case. A fresh context means that the evaluator provides the case prompt and the relevant plugin only, without relying on a previous case's answer or hidden state. The evaluator checks the required and forbidden properties and scores each dimension from 0 to 2:

- `0`: absent, contradicted, or materially unsafe;
- `1`: partially present or usable with a material defect;
- `2`: clearly present and fit for the stated context.

This is a repeatable qualitative review protocol, not a benchmark. It does not contain model scores, comparative claims, or a pass rate. Deterministic tests validate only the pack's schema, IDs, route coverage, and non-empty properties. They cannot certify the quality of a generated answer.

## Release record format

Create one dated record outside the runtime package for a forward-test run. Do not fill this template with invented results.

```yaml
pack_version: "<evaluated pack version>"
run_date: "YYYY-MM-DD"
model_and_build: ""
fresh_context_per_case: true
case_ids:
  - ""
deterministic_validation: "passed | failed"
manual_evaluation:
  evaluator: ""
  scores:
    # One entry per evaluated case. Use 0, 1, or 2 for each named dimension.
    - case_id: ""
      required_properties_observed: []
      forbidden_properties_observed: []
      dimension_scores: {}
      notes: ""
      disposition: "pass | revise | blocked"
limitations:
  - ""
release_decision: "not assessed | ready for review | revise before release"
```

Keep manual evaluation evidence, model metadata, and limitations with the dated record. Never represent a deterministic schema check as an output-quality score.
