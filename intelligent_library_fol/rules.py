"""Declarative descriptions and executable rule identifiers."""
RULES = [
    {"id": "R1", "name": "Borrower is a library user",
     "fol": "∀x,y Borrowed(x,y) → LibraryUser(x)",
     "english": "Anyone who borrows a book is a library user.",
     "premises": ["Borrowed(x, y)"], "conclusion": "LibraryUser(x)"},
    {"id": "R2", "name": "Author specialization determines book subject",
     "fol": "∀b,a,s (WrittenBy(b,a) ∧ SpecializesIn(a,s)) → BelongsTo(b,s)",
     "english": "A book inherits a subject associated with its author's specialization.",
     "premises": ["WrittenBy(b, a)", "SpecializesIn(a, s)"], "conclusion": "BelongsTo(b, s)"},
    {"id": "R3", "name": "Borrowing relationship alias",
     "fol": "∀p,b Borrowed(p,b) → HasBorrowed(p,b)",
     "english": "Every borrowing record also establishes HasBorrowed.",
     "premises": ["Borrowed(p, b)"], "conclusion": "HasBorrowed(p, b)"},
    {"id": "R4", "name": "Availability under negation",
     "fol": "∀b (Book(b) ∧ ¬∃p Borrowed(p,b)) → Available(b)",
     "english": "A known book is available when no current borrowing record exists for it.",
     "premises": ["Book(b)", "No Borrowed(p, b)"], "conclusion": "Available(b)",
     "note": "Non-monotonic check: recomputed from the complete current Borrowed relation."}
]
