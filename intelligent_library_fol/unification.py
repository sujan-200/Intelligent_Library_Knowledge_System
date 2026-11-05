"""First-order term unification with recursive substitution and occurs check."""
import re

class UnificationError(ValueError):
    pass

def is_variable(term: str) -> bool:
    # Variables begin with lowercase letters; constants begin uppercase or contain quoted text.
    return bool(re.fullmatch(r"[a-z][A-Za-z0-9_]*", term.strip()))

def apply_substitution(term, substitution):
    seen = set()
    while term in substitution:
        if term in seen:
            raise UnificationError("Cyclic substitution detected.")
        seen.add(term)
        term = substitution[term]
    return term

def occurs(variable, term, substitution):
    term = apply_substitution(term, substitution)
    return variable == term

def unify_terms(left, right, substitution=None, steps=None):
    substitution = dict(substitution or {})
    steps = steps if steps is not None else []
    left = apply_substitution(left, substitution)
    right = apply_substitution(right, substitution)
    steps.append(f"Compare {left} with {right}")
    if left == right:
        steps.append("Terms are identical; no new substitution.")
        return substitution
    if is_variable(left):
        if occurs(left, right, substitution):
            raise UnificationError(f"Occurs check failed: {left} occurs in {right}.")
        substitution[left] = right
        steps.append(f"Bind {left} = {right}")
        return substitution
    if is_variable(right):
        if occurs(right, left, substitution):
            raise UnificationError(f"Occurs check failed: {right} occurs in {left}.")
        substitution[right] = left
        steps.append(f"Bind {right} = {left}")
        return substitution
    raise UnificationError(f"Constant mismatch: {left} != {right}")

def unify_predicates(left, right, steps=None):
    """Unify (predicate, tuple(args)) pairs."""
    steps = steps if steps is not None else []
    lp, la = left
    rp, ra = right
    steps.append(f"Compare predicate names: {lp} and {rp}")
    if lp != rp:
        raise UnificationError(f"Predicate mismatch: {lp} != {rp}")
    if len(la) != len(ra):
        raise UnificationError(f"Argument count mismatch: {len(la)} != {len(ra)}")
    subst = {}
    for a, b in zip(la, ra):
        subst = unify_terms(a, b, subst, steps)
    # Fully normalize every mapping.
    return {k: apply_substitution(v, subst) for k, v in subst.items()}, steps

def parse_predicate(text):
    """Parse Predicate(term, term). Constants may be quoted or bare identifiers."""
    text = text.strip()
    match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_]*)\s*\((.*)\)", text)
    if not match:
        raise ValueError("Use the format Predicate(argument, argument).")
    name, body = match.groups()
    args, current, quote, depth = [], "", None, 0
    for ch in body:
        if quote:
            current += ch
            if ch == quote: quote = None
        elif ch in ("'", '"'):
            quote = ch; current += ch
        elif ch == "(":
            depth += 1; current += ch
        elif ch == ")":
            depth -= 1; current += ch
        elif ch == "," and depth == 0:
            args.append(current.strip()); current = ""
        else:
            current += ch
    if current.strip() or body.strip():
        args.append(current.strip())
    cleaned = []
    for arg in args:
        arg = arg.strip()
        if len(arg) >= 2 and arg[0] == arg[-1] and arg[0] in ("'", '"'):
            arg = arg[1:-1]
        if not arg:
            raise ValueError("Empty arguments are not allowed.")
        cleaned.append(arg)
    if not cleaned and body.strip():
        raise ValueError("Invalid argument list.")
    return name, tuple(cleaned)
