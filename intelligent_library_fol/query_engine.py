"""Query answering by unification against the knowledge base."""
from unification import parse_predicate, unify_predicates, UnificationError, is_variable, apply_substitution

PREDICATES = {
    "Book":1,"Author":1,"Student":1,"Faculty":1,"LibraryUser":1,"Subject":1,
    "Department":1,"WrittenBy":2,"BelongsTo":2,"SpecializesIn":2,
    "Borrowed":2,"HasBorrowed":2,"Available":1,"MemberOf":2
}

def answer_query(query, kb):
    name, args = parse_predicate(query)
    if name not in PREDICATES:
        raise ValueError(f"Unknown predicate '{name}'. Known predicates: {', '.join(PREDICATES)}")
    if len(args) != PREDICATES[name]:
        raise ValueError(f"{name} expects {PREDICATES[name]} argument(s), received {len(args)}.")
    matches, supports = [], []
    for fact in kb.by_predicate(name):
        try:
            subst, _ = unify_predicates((name,args),(fact.predicate,fact.args))
            # Only expose query variables, not implementation details.
            visible = {k:v for k,v in subst.items() if is_variable(k)}
            matches.append(visible)
            supports.append({"fact":str(fact),"provenance":kb.provenance.get(fact,{})})
        except UnificationError:
            continue
    return {"query":query,"truth":bool(matches),"matches":matches,
            "supporting_facts":supports,
            "explanation":"Matched against stored and inferred facts using predicate unification." if matches
                         else "No fact in the current knowledge base unifies with this query."}
