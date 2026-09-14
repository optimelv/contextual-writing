# Contextual Writing

Contextual Writing is a shareable German and English writing plugin. It creates, researches, edits, and reviews content according to the real audience, purpose, language, evidence, risk, and output format. It does not impose one personality or one universal style.

## Codex and Claude compatibility

This repository is the single source of truth for both runtimes. Codex reads `.codex-plugin/plugin.json`; Claude Code and Claude Cowork read `.claude-plugin/plugin.json`. The skills, references, templates, guards, and tests are shared so the Claude version is kept current with the Codex version instead of becoming a separate fork.

For a one-session Claude Code test, clone the repository and load it directly:

```bash
git clone https://github.com/optimelv/contextual-writing.git
claude --plugin-dir ./contextual-writing
```

Claude Code can also load the packaged plugin from a release asset. The current release is available at [v0.1.0](https://github.com/optimelv/contextual-writing/releases/tag/v0.1.0).

## Components

| Skill | Primary scope |
| --- | --- |
| `contextual-writing` | Automatic router, context gate, evidence rules, language selection, and optional profile use |
| `write-career-documents` | CVs, resumes, cover letters, proactive internship or job outreach, application fields, biographies, and professional profiles |
| `write-professional-communication` | Emails, messages, memos, meeting follow-ups, reports, technical, administrative, and legal-context communication |
| `write-commercial-content` | Evidence-led sales outreach, customer, buyer, partner, marketing, web, and competitive content |
| `write-academic-content` | Academic paragraphs, abstracts, paper sections, literature syntheses, and scholarly revisions from supplied material |
| `write-research-content` | Lightweight academic, legal, company, product, and fact-check research |
| `write-slides-and-strategy` | Consulting, strategy, startup, investor, sales, and decision-led slide narratives |
| `write-general-content` | Articles, essays, posts, website copy, personal prose, and other general writing |
| `edit-and-humanize` | Context-aware audits, minimal edits, voice calibration, translation review, and null edits |
| `teach-and-explain` | Explanations, tutoring, exam support, and accessible learning material |

Only the router is implicitly invoked. It selects one focused workflow and loads shared references. This prevents several broad writing skills from competing for the same request.

## Context and privacy

The plugin contains no personal biography, private writing samples, chat export, or user profile. Optional profile and intake templates contain blank fields only. Users decide whether to provide or save personal context. Sensitive traits are never inferred, required by default, or inserted into a document without explicit authorization.

Career-document assets include anonymized native Word templates for a dense consulting-style CV, a sparse early-career CV, and a formal cover letter. Their content is fictional and must be replaced. Layout is content-driven: spacing, typography and margins are adjusted incrementally and verified through rendering instead of being fixed globally.

## Product boundary

The plugin improves reader fit, truthfulness, clarity, register, and voice. It does not optimize for AI detector scores or promise to conceal authorship. Academic Content owns scholarly drafting and revision from supplied evidence; Research Content owns lightweight evidence gathering; deep academic research remains owned by specialist workflows. Legal advice, CRM-grounded sales workflows, and editable slide production remain owned by specialist plugins or qualified professionals. Contextual Writing prepares inputs, provides a safe lightweight path, and hands off when depth or risk requires it.

Recipient-visible and hard-limit artifacts use a shared submission-readiness gate for exact instructions, word or character limits, internal-note separation, semantic one-action checks, target specificity, and claim strength. A deterministic helper checks surface constraints but does not replace semantic review or the destination's own counter.

## Source method

The rules combine independently formulated writing principles, anonymized lessons from repeated editing work, and selected concepts from the sources listed in `NOTICE.md`. No personal examples or third-party pattern catalogues are copied into the runtime instructions.

## Validation

Run every deterministic package, routing, privacy, guard, and contract test with:

```bash
python3 scripts/run_tests.py
```

Use `tests/forward_cases.json` together with `tests/FORWARD_TESTING.md` for versioned fresh-model forward tests that evaluate actual writing behavior. The deterministic test command validates the pack protocol, but it does not score generated outputs or claim benchmark performance.
