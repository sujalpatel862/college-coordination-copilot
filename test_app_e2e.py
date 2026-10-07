"""End-to-End Programmatic Test for College Coordination Copilot Streamlit App.

Tests interactive behavior using Streamlit's official AppTest framework:
1. Initial page load & element validation
2. Sample scenario button click
3. Analysis execution with mock result rendering
4. Interactive local status changing via dropdown
5. Status filtering
6. Markdown copy block rendering
7. Clear button behavior
"""

import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from models import AnalysisResult, Commitment, ClarificationItem


class TestStreamlitAppE2E(unittest.TestCase):
    def test_initial_load(self):
        """Verify the app loads with expected header and inputs."""
        at = AppTest.from_file("app.py", default_timeout=30)
        at.run()
        self.assertEqual(len(at.exception), 0)
        
        # Verify text area exists
        self.assertTrue(len(at.text_area) >= 1)
        self.assertEqual(at.text_area[0].value, "")

        # Verify buttons exist
        button_labels = [b.label for b in at.button]
        self.assertTrue(any("Hackathon" in label for label in button_labels))
        self.assertTrue(any("Analyze" in label for label in button_labels))
        self.assertTrue(any("Clear" in label for label in button_labels))

    def test_sample_scenario_loading(self):
        """Clicking a sample button populates the chat text area."""
        at = AppTest.from_file("app.py", default_timeout=30)
        at.run()
        
        # Click the first sample button (Hackathon Rush)
        sample_btn = [b for b in at.button if "Hackathon" in b.label][0]
        sample_btn.click().run()
        
        self.assertEqual(len(at.exception), 0)
        self.assertIn("Rahul:", at.text_area[0].value)
        self.assertIn("PPT", at.text_area[0].value)

    def test_analysis_rendering_and_interaction(self):
        """Simulate analysis output and verify interactive UI elements."""
        mock_result = AnalysisResult(
            commitments=[
                Commitment(
                    person="Rahul",
                    task="make the PPT",
                    deadline="tomorrow morning",
                    status="pending",
                    source="I will do it tomorrow morning",
                ),
                Commitment(
                    person="Priya",
                    task="bring HDMI cable",
                    deadline="unclear",
                    status="pending",
                    source="I'll bring the HDMI cable",
                ),
            ],
            needs_clarification=[
                ClarificationItem(
                    issue="Does anyone have the circuit diagram?",
                    source="Aman: Does anyone have the circuit diagram?",
                )
            ],
            model_used="gemma-4-26b-a4b-it",
        )

        with patch("ai_service.analyze_conversation", return_value=(mock_result, "")), \
             patch("app.analyze_conversation", return_value=(mock_result, "")):
            at = AppTest.from_file("app.py", default_timeout=30)
            at.run()

            # Set text and click analyze
            at.text_area[0].input("Rahul: I will do PPT tomorrow morning.\nPriya: I'll bring HDMI cable.\nAman: Diagram?").run()
            analyze_btn = [b for b in at.button if "Analyze" in b.label][0]
            analyze_btn.click().run()

            self.assertEqual(len(at.exception), 0)

            # Check that selectboxes for updating status are rendered
            status_boxes = [s for s in at.selectbox if s.key and s.key.startswith("status_select_")]
            self.assertEqual(len(status_boxes), 2)
            self.assertEqual(status_boxes[0].value, "pending")

            # INTERACTIVE TEST: Change Rahul's status from "pending" to "completed"
            status_boxes[0].select("completed").run()
            self.assertEqual(len(at.exception), 0)

            # Verify that commitments remain visible after rerun
            status_boxes_after = [s for s in at.selectbox if s.key and s.key.startswith("status_select_")]
            self.assertEqual(len(status_boxes_after), 2)
            self.assertEqual(status_boxes_after[0].value, "completed")

            # Test filter: filter by "completed"
            filter_box = [s for s in at.selectbox if s.key == "status_filter"][0]
            filter_box.select("completed").run()
            self.assertEqual(len(at.exception), 0)
            
            # Now only 1 commitment selectbox is visible (the completed one)
            filtered_boxes = [s for s in at.selectbox if s.key and s.key.startswith("status_select_")]
            self.assertEqual(len(filtered_boxes), 1)

            # Reset filter to "All"
            filter_box_fresh = [s for s in at.selectbox if s.key == "status_filter"][0]
            filter_box_fresh.select("All").run()
            self.assertEqual(len(at.exception), 0)

            # Test Clear button
            clear_btn = [b for b in at.button if "Clear" in b.label][0]
            clear_btn.click().run()
            self.assertEqual(len(at.exception), 0)
            self.assertEqual(at.text_area[0].value, "")


if __name__ == "__main__":
    unittest.main()
