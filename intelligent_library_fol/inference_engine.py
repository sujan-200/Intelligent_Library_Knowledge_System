"""Semi-naive-style fixed-point forward chaining for the project's Horn rules."""
from knowledge_base import Fact

def _join(patterns, kb):
    """Return substitutions satisfying all positive body patterns."""
    substitutions = [{}]
    for predicate, terms in patterns:
        next_subs = []
        for subst in substitutions:
            for fact in kb.by_predicate(predicate):
                if len(terms) != len(fact.args): continue
                candidate = dict(subst)
                ok = True
                for term, value in zip(terms, fact.args):
                    if term[0].islower():
                        if term in candidate and candidate[term] != value:
                            ok = False; break
                        candidate[term] = value
                    elif term != value:
                        ok = False; break
                if ok: next_subs.append(candidate)
        substitutions = next_subs
        if not substitutions: break
    return substitutions

def run_forward_chaining(kb):
    log = []
    initial = len(kb.facts)
    # Positive Horn rules are iterated to a fixed point.
    changed = True
    while changed:
        changed = False
        # R1
        for s in _join([("Borrowed",("x","y"))], kb):
            f = Fact("LibraryUser",(s["x"],))
            if kb.add_fact(f,"inferred","R1",s):
                changed = True; log.append({"rule":"R1","substitution":s,"derived":str(f)})
        # R2
        for s in _join([("WrittenBy",("b","a")),("SpecializesIn",("a","s"))], kb):
            f = Fact("BelongsTo",(s["b"],s["s"]))
            if kb.add_fact(f,"inferred","R2",s):
                changed = True; log.append({"rule":"R2","substitution":s,"derived":str(f)})
        # R3
        for s in _join([("Borrowed",("p","b"))], kb):
            f = Fact("HasBorrowed",(s["p"],s["b"]))
            if kb.add_fact(f,"inferred","R3",s):
                changed = True; log.append({"rule":"R3","substitution":s,"derived":str(f)})
    # R4 is a closed-world/negation-as-failure check, recalculated after positive closure.
    borrowed_books = {f.args[1] for f in kb.by_predicate("Borrowed") if len(f.args)==2}
    for book_fact in kb.by_predicate("Book"):
        book = book_fact.args[0]
        if book not in borrowed_books:
            f = Fact("Available",(book,))
            if kb.add_fact(f,"inferred","R4",{"b":book}):
                log.append({"rule":"R4","substitution":{"b":book},"derived":str(f)})
    return {"initial_count":initial,"final_count":len(kb.facts),
            "derived_count":len(kb.facts)-initial,"steps":log}
