# Intelligent Library Knowledge and Query System

A modular Streamlit application demonstrating symbolic AI with First-Order Logic (FOL), a fact-based knowledge base, forward chaining, unification, and query answering.

## Features
- 15 books, 10 authors, 8 subjects, 10 students, 5 faculty, 20 borrowing facts and 4 departments.
- Unary and binary predicates with validation.
- Custom forward-chaining rules R1–R3.
- Availability rule R4 implemented as a separate closed-world/negation check.
- Genuine predicate unification, recursive substitutions and occurs check.
- Variable-based queries and supporting-fact provenance.
- Ontology graph, rule explorer, dashboard and library explorer.

## Folder structure
```text
intelligent_library_fol/
├── app.py
├── knowledge_base.py
├── rules.py
├── unification.py
├── inference_engine.py
├── query_engine.py
├── data.py
├── utils.py
├── requirements.txt
└── README.md
```

## Run on Windows
1. Install Python 3.10 or newer.
2. Open Command Prompt or PowerShell in this folder.
3. Create a virtual environment:
   ```powershell
   py -m venv .venv
   .venv\\Scripts\\activate
   ```
4. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Start the application:
   ```powershell
   streamlit run app.py
   ```
6. Streamlit prints a local URL, normally `http://localhost:8501`.

## Predicate signatures
| Predicate | Arity | Meaning |
|---|---:|---|
| Book(x) | 1 | x is a book |
| Author(x) | 1 | x is an author |
| Student(x) | 1 | x is a student |
| Faculty(x) | 1 | x is faculty |
| LibraryUser(x) | 1 | x is a library user |
| Subject(x) | 1 | x is a subject |
| Department(x) | 1 | x is a department |
| WrittenBy(book, author) | 2 | authorship |
| BelongsTo(book, subject) | 2 | book classification |
| SpecializesIn(author, subject) | 2 | author specialization |
| Borrowed(person, book) | 2 | current borrowing |
| HasBorrowed(person, book) | 2 | inferred borrowing association |
| Available(book) | 1 | no current borrowing record |
| MemberOf(person, department) | 2 | department membership |

## Inference rules
- R1: `Borrowed(x,y) -> LibraryUser(x)`
- R2: `WrittenBy(b,a) AND SpecializesIn(a,s) -> BelongsTo(b,s)`
- R3: `Borrowed(p,b) -> HasBorrowed(p,b)`
- R4: `Book(b) AND NOT EXISTS p Borrowed(p,b) -> Available(b)`

R4 is deliberately not treated as ordinary monotonic Horn inference. The application checks the complete current `Borrowed` relation after positive closure. If borrowing records are edited in a long-running session, rerun inference to refresh availability. This sample has no return transaction UI; add/remove facts in the knowledge base or restart the app to reset its in-memory sample state.

## Demonstration scenarios
Run the app, then use **Inference Engine → Run forward chaining**.

1. `LibraryUser(Ravi)` — true; R1 derives it from `Borrowed(Ravi, ...)`.
2. `BelongsTo(AI_A_Modern_Approach, Artificial_Intelligence)` — true; present as sample data and also derivable through R2.
3. `Borrowed(Ravi, x)` — returns matching borrowed books, including `AI_A_Modern_Approach`.
4. `Available(x)` — returns books with no current borrowing record after running inference.
5. Unification of `Borrowed(x, AI_Book)` with `Borrowed(Ravi, AI_Book)` — returns `{x: Ravi}`.

For a clean demonstration of R2, add `WrittenBy(Demo_Book, Russell)` and `Book(Demo_Book)` as facts, then run inference. The author specialization fact already exists, so `BelongsTo(Demo_Book, Artificial_Intelligence)` is derived.

## Design notes and limitations
- Facts are in memory for the current Streamlit process; the app includes JSON export. JSON import/persistent database storage is not enabled.
- The query engine answers atomic predicate queries, not arbitrary nested formulas or user-authored quantified formulas.
- Variables follow the convention that a term beginning with a lowercase letter is a variable; constants use uppercase-leading names or quoted names.
- `Available` uses a closed-world assumption for current loans. A real library system would model returns, dates, renewals and loan status explicitly.
- The ontology graph uses Graphviz through Streamlit. If Graphviz system binaries are not installed, the Python graphviz package may require installing Graphviz for your OS.

## Academic concepts in plain language
FOL describes objects and relationships using predicates, constants and variables. A knowledge base stores facts and rules. Forward chaining repeatedly applies rules to known facts. Unification finds substitutions that make two expressions match. Query processing uses unification to find facts that satisfy a question and returns the evidence used.
