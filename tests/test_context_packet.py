from __future__ import annotations

import re
import unittest

from tools import emit_context


class ContextPacketBoundsTests(unittest.TestCase):
    """The portable packet is a projection with a bounded decision section."""

    @classmethod
    def setUpClass(cls):
        cls.accepted = [
            item for item in emit_context.parse_decisions() if item["status"] == "accepted"
        ]
        cls.ids = [item["id"] for item in cls.accepted]
        cls.full = emit_context.adrs_rendered_in_full(cls.ids)
        cls.packet = emit_context.generated_outputs()[emit_context.CONTEXT_OUTPUT]
        cls.section = cls.packet.split("## 3. Settled architectural decisions", 1)[1].split(
            "## 4.", 1
        )[0]

    def _entries(self) -> list[str]:
        return [line for line in self.section.splitlines() if line.startswith("- `ADR-")]

    def test_every_accepted_adr_appears_once_in_order(self):
        found = [re.match(r"- `(ADR-\d{4})`", line).group(1) for line in self._entries()]
        self.assertEqual(found, self.ids)

    def test_newest_four_adrs_render_full_decision_text(self):
        newest = self.ids[-emit_context.NEWEST_ADR_FULL_TEXT:]
        for identifier in newest:
            self.assertIn(identifier, self.full)
        rendered = {
            re.match(r"- `(ADR-\d{4})`", line).group(1): line for line in self._entries()
        }
        for identifier in newest:
            decision = next(
                item["decision"] for item in self.accepted if item["id"] == identifier
            )
            self.assertIn(decision, rendered[identifier])

    def test_cited_older_adrs_render_full_and_the_rest_are_index_entries(self):
        cited = emit_context.adrs_rendered_in_full(self.ids) - set(
            self.ids[-emit_context.NEWEST_ADR_FULL_TEXT:]
        )
        rendered = {
            re.match(r"- `(ADR-\d{4})`", line).group(1): line for line in self._entries()
        }
        for identifier in cited:
            decision = next(
                item["decision"] for item in self.accepted if item["id"] == identifier
            )
            self.assertIn(decision, rendered[identifier])
        indexed = [item for item in self.ids if item not in self.full]
        self.assertTrue(indexed, "expected some historical decisions to be indexed")
        for identifier in indexed:
            title = next(
                item["title"] for item in self.accepted if item["id"] == identifier
            )
            self.assertEqual(rendered[identifier], f"- `{identifier}` — {title}")

    def test_pointer_to_the_decision_ledger_is_present(self):
        self.assertIn(emit_context.ADR_HISTORY_POINTER, self.section)
        self.assertIn("DECISIONS.md", self.section)

    def test_packet_stays_inside_the_word_guardrail(self):
        words = len(re.findall(r"\b[\w'-]+\b", self.packet))
        self.assertGreaterEqual(words, 1200)
        self.assertLessEqual(words, 4000)
        self.assertLess(words, 3900, "keep headroom for the next decisions")

    def test_packet_matches_the_renderer(self):
        self.assertEqual(
            emit_context.CONTEXT_OUTPUT.read_text(encoding="utf-8"), self.packet
        )


if __name__ == "__main__":
    unittest.main()
