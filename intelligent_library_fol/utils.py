"""Shared validation and presentation helpers."""
from unification import parse_predicate
from query_engine import PREDICATES

def validate_fact(text):
    name,args = parse_predicate(text)
    if name not in PREDICATES:
        raise ValueError(f"Unknown predicate: {name}")
    if len(args) != PREDICATES[name]:
        raise ValueError(f"{name} requires {PREDICATES[name]} argument(s).")
    if any(a[0].islower() for a in args):
        raise ValueError("Facts must contain constants, not lowercase variables.")
    return name,args

def predicate_reference():
    return [
        ("Book(x)","x is a known book"),("Author(x)","x is an author"),
        ("Student(x)","x is a student"),("Faculty(x)","x is a faculty member"),
        ("LibraryUser(x)","x is a library user"),
        ("Subject(x)","x is an academic subject"),("Department(x)","x is a department"),
        ("WrittenBy(book, author)","book was written by author"),
        ("BelongsTo(book, subject)","book is classified under subject"),
        ("SpecializesIn(author, subject)","author specializes in subject"),
        ("Borrowed(person, book)","person currently has book borrowed"),
        ("HasBorrowed(person, book)","derived borrowing association"),
        ("Available(book)","book has no current borrowing record"),
        ("MemberOf(person, department)","person belongs to department")
    ]
