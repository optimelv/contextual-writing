#!/usr/bin/env python3
"""Ensure critical behavior contracts remain present in runtime instructions."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class BehavioralContractTests(unittest.TestCase):
    def test_incomplete_cv_does_not_force_page_count(self) -> None:
        text = read("skills/write-career-documents/SKILL.md") + read(
            "skills/write-career-documents/references/career-documents.md"
        )
        self.assertIn("Do not promise a page count", text)
        self.assertIn("not a universal rule", text)

    def test_native_documents_use_adaptive_layout_and_render_gate(self) -> None:
        skill = read("skills/write-career-documents/SKILL.md")
        layout = read(
            "skills/write-career-documents/references/adaptive-document-layout.md"
        )
        self.assertIn("use it to create the file", skill)
        self.assertIn("Change one layout variable at a time", layout)
        self.assertIn("do not go below 9 pt", layout)
        self.assertIn("render every page", layout)
        self.assertIn("scrub source metadata", layout)
        self.assertIn("MM/YYYY – MM/YYYY", layout)
        self.assertIn("MM/YYYY – MM/YYYY (voraussichtlich)", layout)
        self.assertIn("Do not mix this with `bis`", layout)

    def test_career_native_file_capability_gate_is_explicit(self) -> None:
        skill = read("skills/write-career-documents/SKILL.md")
        self.assertIn("For Word or PDF deliverables", skill)
        self.assertIn("$documents:documents", skill)
        self.assertIn("$pdf:pdf", skill)
        self.assertIn("If the required capability is available", skill)
        self.assertIn("If it is unavailable", skill)
        self.assertIn(
            "Never claim that a file was created or visually verified",
            skill,
        )

    def test_locale_and_style_profile_application_checks_are_explicit(self) -> None:
        router = read("skills/contextual-writing/SKILL.md")
        language = read("skills/contextual-writing/references/language-and-register.md")
        profile = read("skills/contextual-writing/references/style-calibration.md")
        self.assertIn("language or locale", router)
        self.assertIn("selected English locale", language)
        self.assertIn("Before drafting with a profile", profile)
        self.assertIn("applied", profile)
        self.assertIn("not applicable", profile)
        self.assertIn("conflicts with a higher-priority convention", profile)

    def test_sparse_early_career_cv_uses_a_distinct_layout_contract(self) -> None:
        skill = read("skills/write-career-documents/SKILL.md")
        layout = read(
            "skills/write-career-documents/references/adaptive-document-layout.md"
        )
        self.assertIn("evidence density", skill)
        self.assertIn("generic-cv-template-early-career.docx", layout)
        self.assertIn("Put education first for Bachelor students", layout)
        self.assertIn("two or three evidence-rich bullets per internship", layout)
        self.assertIn("Do not invent metrics", layout)
        self.assertIn("Accept deliberate lower-page whitespace", layout)

    def test_complete_briefs_do_not_trigger_questionnaires(self) -> None:
        text = read("skills/contextual-writing/references/context-gate.md")
        self.assertIn("Do not force a questionnaire on a complete brief", text)
        self.assertIn("Ask only when", text)

    def test_operative_text_requires_original_and_separate_explanation(self) -> None:
        text = read("skills/write-professional-communication/SKILL.md") + read(
            "skills/write-professional-communication/references/professional-communication.md"
        )
        self.assertIn("technical specification", text)
        self.assertIn("compliance wording as protected text", text)
        self.assertIn("Original operative wording", text)
        self.assertIn("Plain-language explanation", text)
        self.assertIn("retain `material` rather than replacing it with `significant`", text)

    def test_academic_uncertainty_is_protected(self) -> None:
        text = read("skills/contextual-writing/references/evidence-and-preservation.md") + read(
            "skills/write-research-content/references/lightweight-research.md"
        )
        self.assertIn("uncertainty", text)
        self.assertIn("Preserve hedging", text)

    def test_academic_writing_has_a_direct_owner(self) -> None:
        router = read("skills/contextual-writing/SKILL.md")
        academic = read("skills/write-academic-content/SKILL.md")
        self.assertIn("scholarly deliverables to academic content", router)
        self.assertIn("draft or revise directly", academic)
        self.assertIn("Do not require a research intake", academic)
        self.assertIn("Never invent citations", academic)
        self.assertIn("$academic-research-suite", academic)
        self.assertIn("subject-verb agreement", academic)
        self.assertIn("a single cited author takes a singular verb", academic)
        self.assertIn("categorical meaning across languages", academic)
        self.assertIn("a comparative final sentence alone does not repair", academic)

    def test_sales_persuasion_is_not_neutralized(self) -> None:
        text = read("skills/write-commercial-content/SKILL.md") + read(
            "skills/contextual-writing/references/language-and-register.md"
        )
        self.assertIn("Preserve useful persuasion", text)
        self.assertIn("Remove unsupported hype, not persuasion itself", text)

    def test_submission_readiness_is_a_cross_route_gate(self) -> None:
        router = read("skills/contextual-writing/SKILL.md")
        readiness = read(
            "skills/contextual-writing/references/submission-readiness.md"
        )
        career = read("skills/write-career-documents/SKILL.md")
        commercial = read("skills/write-commercial-content/SKILL.md")
        academic = read("skills/write-academic-content/SKILL.md")
        general = read("skills/write-general-content/SKILL.md")
        editing = read("skills/edit-and-humanize/SKILL.md")
        research = read("skills/write-research-content/SKILL.md")
        self.assertIn("submission readiness", router)
        self.assertIn("recipient-visible artifact", readiness)
        self.assertIn("destination's own counter as authoritative", readiness)
        self.assertIn("distinct items", readiness)
        self.assertIn("every named claim category", readiness)
        self.assertIn("revenue` is not necessarily `recurring revenue", readiness)
        self.assertIn("Recount after every final edit", readiness)
        self.assertIn("Judge the requested action semantically", readiness)
        self.assertIn("name-swap test", readiness)
        self.assertIn("keep internal uncertainty notes outside", career)
        self.assertIn("keep internal uncertainty notes outside", commercial)
        self.assertIn("Recount hard limits after the final edit", academic)
        for direct_skill in (general, editing, research):
            self.assertIn("submission-readiness gate", direct_skill)
            self.assertIn("recipient-visible or hard-limited", direct_skill)
            self.assertIn("destination's own counter", direct_skill)

    def test_sales_outreach_separates_trigger_from_hypotheses(self) -> None:
        router = read("skills/contextual-writing/SKILL.md")
        skill = read("skills/write-commercial-content/SKILL.md")
        outreach = read(
            "skills/write-commercial-content/references/sales-outreach.md"
        )
        commercial = read(
            "skills/write-commercial-content/references/commercial-content.md"
        )
        intake = read(
            "skills/write-commercial-content/assets/commercial-intake.md"
        )
        self.assertIn("sales outreach", skill)
        self.assertIn("Sales handoff takes precedence", router)
        self.assertIn("use it first for every real seller", skill)
        self.assertIn("fallback when Sales is unavailable", skill)
        self.assertIn("Relevance trigger", outreach)
        self.assertIn("Implication hypothesis", outreach)
        self.assertIn("Problem hypothesis", outreach)
        self.assertIn("one central problem or outcome", outreach)
        self.assertIn("one proportionate next step", outreach)
        self.assertIn("do not invent personalization", outreach)
        self.assertIn("as a universal rule", outreach)
        self.assertIn("draft-only", outreach)
        self.assertIn("public trigger into a private customer need", commercial)
        self.assertIn("Verified reason for contact, source, and date", intake)

    def test_claim_ladder_blocks_investor_overreach(self) -> None:
        commercial = read(
            "skills/write-commercial-content/references/commercial-content.md"
        )
        slides = read(
            "skills/write-slides-and-strategy/references/slides-and-strategy.md"
        )
        self.assertIn("Access does not establish trust", commercial)
        self.assertIn("does not establish recurring revenue", commercial)
        self.assertIn("not proof of switching cost", slides)
        self.assertIn("uncertainty note outside the slide or script", slides)
        self.assertIn("recurring revenue as a distinct claim", slides)
        self.assertIn("repeat payment, renewal, usage, or contract recurrence", slides)

    def test_academic_importance_language_requires_analysis(self) -> None:
        academic = read(
            "skills/write-academic-content/references/academic-writing.md"
        )
        self.assertIn("Generic importance language is not analysis", academic)
        self.assertIn("bounded implication of the evidence", academic)

    def test_cover_letter_specificity_and_close_are_explicit(self) -> None:
        career = read(
            "skills/write-career-documents/references/career-documents.md"
        )
        self.assertIn("replacing the organization or role", career)
        self.assertIn("target-specific reasoning do real work", career)
        self.assertIn("final list of generic virtues", career)
        self.assertIn("Do not infer retrospective learning", career)
        self.assertIn("taught me", career)
        self.assertIn("strengthened my ability", career)
        self.assertIn("keep drafting notes outside the submitted field", career)

    def test_proactive_career_outreach_has_context_dependent_rules(self) -> None:
        router = read("skills/contextual-writing/SKILL.md")
        career = read("skills/write-career-documents/SKILL.md")
        outreach = read(
            "skills/write-career-documents/references/proactive-career-outreach.md"
        )
        intake = read(
            "skills/write-career-documents/assets/proactive-career-outreach-intake.md"
        )
        commercial = read(
            "skills/write-commercial-content/references/commercial-content.md"
        )
        self.assertIn("proactive internship or job outreach", router)
        self.assertIn("belongs to career documents", router)
        self.assertIn("proactive career outreach", career)
        self.assertIn("Exploratory cold outreach", outreach)
        self.assertIn("Speculative application", outreach)
        self.assertIn("Formal or referred application email", outreach)
        self.assertIn("keep the mode open and ask for it", outreach)
        self.assertIn("Do not label an exploratory inquiry as a speculative application", outreach)
        self.assertIn("source and date for volatile claims", outreach)
        self.assertIn("sourced observation", outreach)
        self.assertIn("one or two verified applicant experiences", outreach)
        self.assertIn("one proportionate next step", outreach)
        self.assertIn("Never claim that an attachment will or will not trigger spam", outreach)
        self.assertIn("Current sourced observation, source, and date", intake)
        self.assertIn("belongs to career documents", commercial)

    def test_null_edit_is_required(self) -> None:
        text = read("skills/contextual-writing/references/humanizing-and-qa.md")
        self.assertIn("Null edit", text)
        self.assertIn("fit for purpose", text)

    def test_specialist_handoffs_are_availability_conditional(self) -> None:
        research = read("skills/write-research-content/SKILL.md")
        slides = read("skills/write-slides-and-strategy/SKILL.md")
        self.assertIn("check whether `$academic-research-suite` is available", research)
        self.assertIn("If unavailable", research)
        self.assertIn("check whether a presentation-authoring skill is available", slides)
        self.assertIn("If unavailable", slides)


if __name__ == "__main__":
    unittest.main()
