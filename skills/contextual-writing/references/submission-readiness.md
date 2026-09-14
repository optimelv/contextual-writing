# Submission readiness

Use this gate for text that will be submitted, sent, posted, uploaded, or placed in a field with hard instructions. It is not required for exploratory notes or internal analysis unless the user asks for a final-ready version.

## Build the submission artifact first

Separate the artifact the recipient will see from drafting commentary. Do not append unmistakably internal labels such as `Material uncertainty`, `Confidence and gaps`, `Internal note`, `Draft note`, or editing commentary inside a submit-ready field, email, letter, essay, or slide unless the destination explicitly requires them. Put useful caveats outside the copy under a clearly separate review note, or state them before drafting when they block a defensible artifact.

Recipient-facing labels such as `Assumption`, `Open question`, `Limitation`, or `Source` can be necessary in research, consulting, investor, legal, and decision material. Preserve them when the genre or brief requires them. The `--forbid-internal-notes` guard targets drafting-process residue, not legitimate evidence labels.

## Enforce exact instructions

Create a checklist from the controlling prompt, portal, posting, rubric, template, or house style. Verify every required field, attachment, subject line, filename, section, language, and prohibited element against that checklist.

When the controlling instruction enumerates distinct items, keep them as separate checklist entries through final review. Do not compress several requirements into one broader phrase and accidentally omit an item. Verify every named claim category, question, attachment, criterion, and deliverable element individually before returning the artifact.

Preserve category specificity when checking compliance. A broader term does not satisfy a narrower named requirement when the distinction matters: `revenue` is not necessarily `recurring revenue`, access is not trust, and a file is not the same as the requested file format.

For a hard word or character limit:

1. Count only the recipient-visible artifact, not headings or internal notes added for the user.
2. Treat the destination's own counter as authoritative when its counting convention is known.
3. If the destination convention is unknown, use the local guard as a reproducible approximation and leave a small margin instead of targeting the last permitted unit.
4. Recount after every final edit. Never describe an over-limit draft as submission-ready.

When a local text file is available, use the guard from the router skill directory:

```bash
python3 scripts/submission_guard.py --file <draft> --max-words <limit>
python3 scripts/submission_guard.py --file <draft> --max-characters <limit>
```

Add `--forbid-internal-notes` for recipient-visible copy. It recognizes unmistakable drafting labels in common Markdown headings, blockquotes, ordered, unordered, and task-list items, emphasis, and colon or dash forms. It ignores fenced and four-space-indented code because quoted examples are not recipient instructions. It is a conservative label check, not a complete Markdown or semantic classifier. Add `--max-questions 1` only when the brief explicitly limits the number of questions. The question counter is a surface check and does not replace the semantic ask review below.

## One-action review

When the brief requests one call to action or next step, identify the actual decisions or actions requested from the recipient. Keep one. A sentence can contain two asks even if it has one question mark; two sentences can express the same single action. Judge the requested action semantically, not by punctuation alone.

Make the action proportionate to the relationship, channel, and stage. A low-friction interest question can fit an early cold touch. A meeting request can fit a warm, referred, formal, or already active process. Do not force one CTA type across all contexts.

## Specificity and claim review

- For target-specific applications or outreach, apply a name-swap test to the target-dependent lines. If another organization can replace the name without changing the reasoning, add verified relevance or remove the generic claim.
- Check that every proof point supports the exact proposition attached to it. Access is not trust; interest is not demand; a possible partner is not recurring revenue; workflow integration is not automatically defensibility.
- Keep hypotheses visibly tentative. Do not let a caveat outside the artifact excuse an overconfident statement inside it.
- Remove generic closing virtue lists when the body already demonstrates the relevant qualities.

## Final pass

Verify facts, ownership, claim strength, exact instructions, hard limits, one-action requirements, recipient-only content, grammar, and rendering where applicable. Return `ready` only when all controlling checks pass. Otherwise return the draft as provisional and name the exact remaining issue.
