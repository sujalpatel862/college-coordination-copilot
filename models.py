"""Structured representation of analysis results."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Commitment:
    person: str
    task: str
    deadline: str
    status: str
    source: str


@dataclass
class ClarificationItem:
    issue: str
    source: str


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


VALID_STATUSES = {"pending", "completed", "unclear"}
