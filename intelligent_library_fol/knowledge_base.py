"""Fact storage for the Intelligent Library Knowledge and Query System."""
from dataclasses import dataclass, asdict
from typing import Iterable

@dataclass(frozen=True)
class Fact:
    predicate: str
    args: tuple[str, ...]

    def __str__(self):
        return f"{self.predicate}({', '.join(self.args)})"

    def to_dict(self):
        return {"Predicate": self.predicate, "Arguments": ", ".join(self.args), "Fact": str(self)}

class KnowledgeBase:
    def __init__(self, facts: Iterable[Fact] = ()):
        self.facts: list[Fact] = []
        self._set = set()
        self.provenance: dict[Fact, dict] = {}
        for fact in facts:
            self.add_fact(fact)

    def add_fact(self, fact: Fact, source="original", rule=None, substitution=None):
        if fact in self._set:
            return False
        self._set.add(fact)
        self.facts.append(fact)
        self.provenance[fact] = {
            "source": source, "rule": rule,
            "substitution": substitution or {}
        }
        return True

    def contains(self, fact: Fact) -> bool:
        return fact in self._set

    def by_predicate(self, predicate: str):
        return [f for f in self.facts if f.predicate == predicate]

    def count(self, predicate: str) -> int:
        return len(self.by_predicate(predicate))

    def original_facts(self):
        return [f for f in self.facts if self.provenance[f]["source"] == "original"]

    def inferred_facts(self):
        return [f for f in self.facts if self.provenance[f]["source"] == "inferred"]

    def to_rows(self):
        return [f.to_dict() | {"Type": self.provenance[f]["source"],
                              "Rule": self.provenance[f]["rule"] or "-"}
                for f in self.facts]

    def clear_inferred(self):
        keep = self.original_facts()
        self.facts, self._set, self.provenance = [], set(), {}
        for fact in keep:
            self.add_fact(fact)
