"""Comprehensive unit tests for College Coordination Copilot.

Tests parsing, validation, edge cases, model data structures,
and markdown generation without consuming API quota.
"""

import unittest
from models import Commitment, ClarificationItem, AnalysisResult, VALID_STATUSES
from ai_service import _strip_code_fences, _extract_json, _validate_structure


class TestModels(unittest.TestCase):
    def test_commitment_creation_and_dict(self):
        c = Commitment(
            person="Rahul",
            task="Finish PPT",
            deadline="tomorrow morning",
            status="pending",
            source="I will do it tomorrow morning",
        )
        self.assertEqual(c.person, "Rahul")
        self.assertEqual(c.task, "Finish PPT")
        self.assertEqual(c.deadline, "tomorrow morning")
        self.assertEqual(c.status, "pending")
        d = c.to_dict()
        self.assertEqual(d["person"], "Rahul")

    def test_clarification_creation_and_dict(self):
        item = ClarificationItem(
            issue="Who has HDMI cable?",
            source="Does anyone have an HDMI cable?",
        )
        self.assertEqual(item.issue, "Who has HDMI cable?")
        d = item.to_dict()
        self.assertEqual(d["issue"], "Who has HDMI cable?")

    def test_analysis_result_properties(self):
        res = AnalysisResult()
        self.assertFalse(res.has_commitments)
        self.assertFalse(res.has_clarifications)

        res.commitments.append(
            Commitment("A", "B", "C", "pending", "D")
        )
        self.assertTrue(res.has_commitments)

        res.needs_clarification.append(
            ClarificationItem("E", "F")
        )
        self.assertTrue(res.has_clarifications)

    def test_to_markdown_formatting(self):
        res = AnalysisResult(
            commitments=[
                Commitment("Rahul", "Make PPT", "tomorrow", "pending", "I'll make PPT tonight"),
                Commitment("Priya", "Bring cable", "unclear", "completed", "Done with cable"),
            ],
            needs_clarification=[
                ClarificationItem("Missing diagram", "Who has the diagram?"),
            ],
            model_used="gemma-4-26b-a4b-it",
        )
        md = res.to_markdown()
        self.assertIn("Action Items", md)
        self.assertIn("Rahul", md)
        self.assertIn("Due: tomorrow", md)
        self.assertIn("No deadline", md)
        self.assertIn("Missing diagram", md)


class TestParsing(unittest.TestCase):
    def test_strip_code_fences_plain(self):
        text = '{"commitments": []}'
        self.assertEqual(_strip_code_fences(text), text)

    def test_strip_code_fences_markdown(self):
        text = '```json\n{"commitments": []}\n```'
        self.assertEqual(_strip_code_fences(text), '{"commitments": []}')

    def test_strip_code_fences_with_surrounding_text(self):
        text = 'Here is the JSON:\n```json\n{"commitments": []}\n```\nHope this helps!'
        self.assertEqual(_strip_code_fences(text), '{"commitments": []}')

    def test_extract_json_clean(self):
        raw = '{"commitments": [{"person": "Rahul", "task": "PPT", "deadline": "tomorrow", "status": "pending", "source": "s"}]}'
        data = _extract_json(raw)
        self.assertEqual(len(data["commitments"]), 1)
        self.assertEqual(data["commitments"][0]["person"], "Rahul")

    def test_extract_json_with_trailing_commas(self):
        raw = '{"commitments": [{"person": "Rahul", "task": "PPT", "deadline": "tomorrow", "status": "pending", "source": "s",},],}'
        data = _extract_json(raw)
        self.assertEqual(len(data["commitments"]), 1)

    def test_extract_json_embedded(self):
        raw = 'Some explanation before\n{"commitments": []}\nSome text after'
        data = _extract_json(raw)
        self.assertIn("commitments", data)

    def test_extract_json_empty_raises(self):
        with self.assertRaises(ValueError):
            _extract_json("")

    def test_extract_json_invalid_raises(self):
        with self.assertRaises(ValueError):
            _extract_json("not valid json at all")


class TestValidation(unittest.TestCase):
    def test_validate_structure_standard(self):
        raw = {
            "commitments": [
                {
                    "person": "Rahul",
                    "task": "Build presentation",
                    "deadline": "tomorrow 10 AM",
                    "status": "pending",
                    "source": "Rahul: I'll finish it",
                }
            ],
            "needs_clarification": [
                {
                    "issue": "Which projector room?",
                    "source": "Aman: Which room?",
                }
            ],
        }
        res = _validate_structure(raw)
        self.assertEqual(len(res.commitments), 1)
        self.assertEqual(res.commitments[0].person, "Rahul")
        self.assertEqual(res.commitments[0].status, "pending")
        self.assertEqual(len(res.needs_clarification), 1)
        self.assertEqual(res.needs_clarification[0].issue, "Which projector room?")

    def test_validate_structure_status_normalization(self):
        raw = {
            "commitments": [
                {"person": "A", "task": "B", "deadline": "C", "status": "COMPLETED", "source": "D"},
                {"person": "E", "task": "F", "deadline": "G", "status": "unknown_value", "source": "H"},
            ]
        }
        res = _validate_structure(raw)
        self.assertEqual(res.commitments[0].status, "completed")
        self.assertEqual(res.commitments[1].status, "unclear")

    def test_validate_structure_synonyms(self):
        raw = {
            "tasks": [
                {"assignee": "Neha", "action": "Submit report", "due": "Friday", "status": "pending", "source": "s"}
            ],
            "clarifications": [
                {"question": "Has Sir signed?", "source": "Who checked?"}
            ]
        }
        res = _validate_structure(raw)
        self.assertEqual(len(res.commitments), 1)
        self.assertEqual(res.commitments[0].person, "Neha")
        self.assertEqual(res.commitments[0].task, "Submit report")
        self.assertEqual(res.commitments[0].deadline, "Friday")
        self.assertEqual(len(res.needs_clarification), 1)
        self.assertEqual(res.needs_clarification[0].issue, "Has Sir signed?")


if __name__ == "__main__":
    unittest.main()
