---
name: contextual-writing
description: Route standalone German and English writing, editing, research, and audience-facing prose. Not routine README, API-doc, or code-comment updates within coding tasks.
---

# Contextual writing router

Select one focused workflow. Do not flatten all writing into one generic style.

## Scope

Use this router when writing, editing, or research is the requested deliverable, or when explicitly invoked. For routine README, API-documentation, or code-comment updates accompanying a code change, work directly from the implementation and repository conventions; do not load this router's workflows.

## Core sequence

1. Read [context gate](references/context-gate.md), [evidence and preservation](references/evidence-and-preservation.md), and [language and register](references/language-and-register.md).
2. Identify the deliverable, audience, purpose, language or locale, evidence status, risk, format, and requested mode.
3. Reuse context already supplied in the conversation, files, templates, or optional profile. Do not ask for it again.
4. If a missing fact would materially change content, claims, tone, structure, or compliance, ask one compact fill-in form containing only the missing fields. Do not draft through a material gap.
5. Read the selected focused skill in full, then load only its relevant references and assets.
6. Produce the requested artifact. Do not replace a complete brief with another outline.
7. Apply a semantic preservation review. For recipient-visible, submitted, posted, or hard-limit text, also read [submission readiness](references/submission-readiness.md) and enforce the controlling instructions before calling the artifact final. Use scripts only as review aids.

## Route by primary outcome

- CV, resume, cover letter, application answer, proactive internship or job outreach, biography, or professional profile: [career documents](../write-career-documents/SKILL.md)
- Email, professional message, memo, meeting follow-up, report, technical, administrative, or legal-context communication: [professional communication](../write-professional-communication/SKILL.md)
- Sales, customer, partner, outreach, marketing, website conversion, or competitive content: [commercial content](../write-commercial-content/SKILL.md). When `$sales:index` is available, it owns real seller, customer, prospect, partner, account, opportunity, or other commercial-intent workflows first; use commercial content as the fallback when Sales is unavailable and as the reader-fit editing layer after the specialist workflow.
- Academic paragraph, abstract, introduction, literature synthesis, method, results, discussion, conclusion, thesis section, or scholarly revision from supplied material: [academic content](../write-academic-content/SKILL.md)
- Academic-light, legal-light, company, product, source, or fact-check research: [research content](../write-research-content/SKILL.md)
- Consulting, strategy, startup, investor, sales, case, or decision slide narrative: [slides and strategy](../write-slides-and-strategy/SKILL.md)
- Article, essay, blog, post, website, personal, or other general prose: [general content](../write-general-content/SKILL.md)
- Audit, rewrite, humanize, compress, expand, localize, translate-review, or voice-match existing text: [edit and humanize](../edit-and-humanize/SKILL.md)
- Explanation, tutoring, exam support, active recall, or accessible learning material: [teach and explain](../teach-and-explain/SKILL.md)

If several apply, choose the workflow that owns the final deliverable. Load editing as a review layer and research as an evidence layer rather than letting them replace the owner.

Applicant-to-employer, founder, investor, accelerator, or hiring-team outreach belongs to career documents even when the channel is email. Commercial content owns outreach that sells an offer to a customer, buyer, or partner. Professional communication owns ordinary relationship-based messages whose primary purpose is neither an application nor a commercial action.

The Sales handoff takes precedence over the generic commercial route whenever its installed index applies, even when the user already supplied evidence. General marketing, website, product, or brand copy without a seller, customer, prospect, partner, account, opportunity, or commercial-motion workflow can remain with commercial content. If Sales is unavailable, commercial content provides the evidence-led, draft-only fallback and must disclose any material missing live account context.

Domain ownership always outranks the generic editor. Route CVs to career, scholarly deliverables to academic content, academic or legal research to research, sales copy to commercial, slides to slides, and operative legal, contractual, regulatory, policy, specification, or compliance text to professional communication before loading editing. Never route protected operative wording to the editor alone.

## Precedence

Apply this order:

1. Latest explicit user instruction and authorization.
2. Supplied facts, sources, quotations, templates, rubrics, and hard limits.
3. Safety, law, academic integrity, and professional obligations that actually apply.
4. Deliverable, audience, organization, discipline, and language conventions.
5. User-approved profile and representative writing samples.
6. Generic writing heuristics.

Never impose academic, legal, sales, casual, or minimalist conventions outside their context. A good legal clause may be dense. A strong sales message may be persuasive. A personal essay may use fragments. Diagnose before changing.

## Optional personalization

Read [style calibration](references/style-calibration.md) when the user supplies past writing or requests a reusable profile. Use [the blank profile template](assets/user-context-profile.template.yaml) only with user authorization. Never infer sensitive traits. Never disclose age, disability, health, nationality, religion, family status, or other protected information in an output unless the user explicitly requests it and the context supports disclosure.

## Editing safeguards

Read [humanizing and QA](references/humanizing-and-qa.md) for any revision. For important factual rewrites, run the scripts using paths resolved from this skill directory:

```bash
python3 scripts/claim_guard.py --before-file <original> --after-file <revision>
python3 scripts/style_guard.py --file <revision> --language <en|de> --register <neutral|formal|casual|academic|legal|commercial>
```

`claim_guard.py` is a fail-closed mechanical review gate, not semantic verification. Every changed text still requires semantic comparison with the original. Do not optimize for AI detector scores or claim that surface patterns prove authorship.

For operative legal, contractual, regulatory, policy, specification, or compliance wording, do not produce replacement text unless an authorized domain owner supplies or approves it. Preserve the original and offer only a separately labeled plain-language explanation.
