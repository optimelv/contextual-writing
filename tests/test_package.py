#!/usr/bin/env python3
"""Package-level privacy, link, placeholder, and routing tests."""

from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".py"}
PRIVATE_PATTERNS = {
    "absolute_user_path": re.compile("/" + r"(?:Users|home)/[^/\s]+/"),
    "email_address": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "chat_export_identifier": re.compile(
        r"\b(?:"
        + "|".join(
            (
                "conversation" + "_id",
                "message" + "_id",
                "chatgpt" + "-export-index",
            )
        )
        + r")\b",
        re.IGNORECASE,
    ),
}
EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b"
)
DOCX_NS = {
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}
CAREER_TEMPLATE_NAMES = (
    "generic-cv-template.docx",
    "generic-cv-template-early-career.docx",
    "generic-cover-letter-template.docx",
)


def text_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and path.suffix in TEXT_SUFFIXES
    ]


class PackageTests(unittest.TestCase):
    def test_no_placeholders_remain(self) -> None:
        hits = []
        for path in text_files():
            text = path.read_text(encoding="utf-8")
            if "[" + "TODO:" in text:
                hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [])

    def test_no_generated_bytecode_is_packaged(self) -> None:
        generated = [
            str(path.relative_to(ROOT))
            for path in ROOT.rglob("*")
            if path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}
        ]
        self.assertEqual(generated, [])

    def test_no_personal_source_data_is_packaged(self) -> None:
        hits = []
        for path in text_files():
            text = path.read_text(encoding="utf-8")
            for label, pattern in PRIVATE_PATTERNS.items():
                if pattern.search(text):
                    hits.append(f"{path.relative_to(ROOT)}: {label}")
        self.assertEqual(hits, [])

    def test_native_career_templates_exist_and_are_anonymized(self) -> None:
        assets = ROOT / "skills/write-career-documents/assets"
        templates = [assets / name for name in CAREER_TEMPLATE_NAMES]
        forbidden = [
            "melvin",
            "friedrichsen",
            "icloud.com",
            "horváth",
            "klixbüll",
        ]
        for template in templates:
            self.assertTrue(template.is_file(), template)
            with ZipFile(template) as archive:
                xml = "\n".join(
                    archive.read(name).decode("utf-8", errors="ignore")
                    for name in archive.namelist()
                    if name.endswith(".xml")
                ).lower()
            for value in forbidden:
                self.assertNotIn(value, xml, f"{template.name}: {value}")

    def test_all_native_career_templates_have_safe_a4_package_structure(self) -> None:
        """Check the three shipped Word assets, not only the sparse CV."""
        assets = ROOT / "skills/write-career-documents/assets"
        for name in CAREER_TEMPLATE_NAMES:
            template = assets / name
            with self.subTest(template=name):
                with ZipFile(template) as archive:
                    names = archive.namelist()
                    document = ET.fromstring(archive.read("word/document.xml"))
                    core = ET.fromstring(archive.read("docProps/core.xml"))
                    all_xml = "\n".join(
                        archive.read(member).decode("utf-8", errors="ignore")
                        for member in names
                        if member.endswith(".xml")
                    )

                    # A macro-enabled extension or vbaProject is not allowed in
                    # a shareable template package.
                    macro_members = [
                        member
                        for member in names
                        if "vbaproject" in member.lower()
                        or "macroenabled" in member.lower()
                    ]
                    self.assertEqual(macro_members, [])
                    content_types = archive.read("[Content_Types].xml").lower()
                    self.assertNotIn(b"macroenabled", content_types)

                    # Every section must be A4. Use explicit dimensions rather
                    # than relying on a locale-dependent page-size label.
                    page_sizes = document.findall(".//w:sectPr/w:pgSz", DOCX_NS)
                    self.assertTrue(page_sizes)
                    for page_size in page_sizes:
                        self.assertEqual(
                            page_size.get(f"{{{DOCX_NS['w']}}}w"), "11906"
                        )
                        self.assertEqual(
                            page_size.get(f"{{{DOCX_NS['w']}}}h"), "16838"
                        )

                    # Personal metadata must be blank in every shipped asset.
                    self.assertFalse(
                        core.findtext(
                            "dc:creator", default="", namespaces=DOCX_NS
                        ).strip()
                    )
                    self.assertFalse(
                        core.findtext(
                            "cp:lastModifiedBy", default="", namespaces=DOCX_NS
                        ).strip()
                    )

                    # Relationships must stay package-local. This catches
                    # external hyperlinks, images, and template dependencies.
                    external = []
                    for member in names:
                        if not member.endswith(".rels"):
                            continue
                        rel_root = ET.fromstring(archive.read(member))
                        external.extend(
                            relationship
                            for relationship in rel_root.findall(
                                "pr:Relationship", DOCX_NS
                            )
                            if relationship.get("TargetMode", "").lower()
                            == "external"
                        )
                    self.assertEqual(external, [])

                    # Do not ship local absolute paths. Only fictional example.com
                    # addresses are permitted if a template contains an email.
                    self.assertNotRegex(
                        all_xml,
                        r"(?i)(?:file://|/(?:Users|home)/|(?<![A-Za-z0-9])[A-Za-z]:[\\/])",
                    )
                    for match in EMAIL_PATTERN.finditer(all_xml):
                        self.assertEqual(
                            match.group(1).lower(),
                            "example.com",
                            f"{name}: non-example.com email address",
                        )

    def test_repaired_native_templates_keep_the_new_contract(self) -> None:
        assets = ROOT / "skills/write-career-documents/assets"
        with ZipFile(assets / "generic-cv-template.docx") as archive:
            cv_xml = archive.read("word/document.xml").decode(
                "utf-8", errors="ignore"
            )
        self.assertIn("10/2024 – 09/2026 (voraussichtlich)", cv_xml)
        self.assertNotIn("10/2024 – voraussichtlich 09/2026", cv_xml)

        with ZipFile(assets / "generic-cover-letter-template.docx") as archive:
            letter_xml = archive.read("word/document.xml").decode("utf-8", errors="ignore")
            letter_document = ET.fromstring(letter_xml)
        self.assertNotIn("An Consulting reizt mich", letter_xml)
        justified_text_paragraphs = []
        for paragraph in letter_document.findall(".//w:body/w:p", DOCX_NS):
            text = "".join(paragraph.itertext()).strip()
            alignment = paragraph.find("./w:pPr/w:jc", DOCX_NS)
            if (
                text
                and alignment is not None
                and alignment.get(f"{{{DOCX_NS['w']}}}val") == "both"
            ):
                justified_text_paragraphs.append(text)
        self.assertEqual(justified_text_paragraphs, [])

    def test_relative_markdown_links_resolve(self) -> None:
        broken = []
        pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for path in ROOT.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            for raw_target in pattern.findall(text):
                target = raw_target.split("#", 1)[0]
                if not target or "://" in target or target.startswith("plugin:"):
                    continue
                resolved = (path.parent / target).resolve()
                if not resolved.exists():
                    broken.append(f"{path.relative_to(ROOT)} -> {raw_target}")
        self.assertEqual(broken, [])

    def test_only_router_is_implicitly_invokable(self) -> None:
        agent_files = list(ROOT.glob("skills/*/agents/openai.yaml"))
        true_count = 0
        false_count = 0
        for path in agent_files:
            text = path.read_text(encoding="utf-8")
            true_count += text.count("allow_implicit_invocation: true")
            false_count += text.count("allow_implicit_invocation: false")
        self.assertEqual(true_count, 1)
        self.assertEqual(false_count, len(agent_files) - 1)


if __name__ == "__main__":
    unittest.main()
