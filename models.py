"""Structured representation of analysis results."""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any


@dataclass
class Commitment:
    person: str
    task: str
    deadline: str
    status: str
    source: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ClarificationItem:
    issue: str
    source: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisResult:
    commitments: List[Commitment] = field(default_factory=list)
    needs_clarification: List[ClarificationItem] = field(default_factory=list)
    model_used: str = ""

    @property
    def has_commitments(self) -> bool:
        return len(self.commitments) > 0

    @property
    def has_clarifications(self) -> bool:
        return len(self.needs_clarification) > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "commitments": [c.to_dict() for c in self.commitments],
            "needs_clarification": [item.to_dict() for item in self.needs_clarification],
            "model_used": self.model_used,
        }

    def to_markdown(self) -> str:
        """Format results as a clean, ready-to-share summary for WhatsApp/Discord."""
        lines = ["📋 *College Coordination Copilot — Action Items*\n"]
        if self.commitments:
            lines.append("*Commitments:*")
            for c in self.commitments:
                deadline_str = f"Due: {c.deadline}" if c.deadline != "unclear" else "No deadline"
                status_icon = "⏳" if c.status == "pending" else "✅" if c.status == "completed" else "❓"
                lines.append(f"• {status_icon} *{c.person}*: {c.task} ({deadline_str}) [{c.status}]")
                if c.source:
                    lines.append(f"  > \"{c.source}\"")
            lines.append("")
        else:
            lines.append("No commitments found.\n")

        if self.needs_clarification:
            lines.append("⚠️ *Needs Clarification:*")
            for item in self.needs_clarification:
                lines.append(f"• {item.issue}")
                if item.source:
                    lines.append(f"  > \"{item.source}\"")
            lines.append("")

        return "\n".join(lines).strip()


VALID_STATUSES = {"pending", "completed", "unclear"}
