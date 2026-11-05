from knowledge_base import KnowledgeBase, Fact
from data import sample_facts
from inference_engine import run_forward_chaining
from query_engine import answer_query
from unification import unify_predicates

kb = KnowledgeBase(sample_facts())
run_forward_chaining(kb)
assert answer_query("LibraryUser(Ravi)", kb)["truth"]
# Dedicated clean R2 test
kb2 = KnowledgeBase(sample_facts() + [
    Fact("Book",("Demo_Book",)), Fact("WrittenBy",("Demo_Book","Russell"))
])
run_forward_chaining(kb2)
assert answer_query("BelongsTo(Demo_Book, Artificial_Intelligence)",kb2)["truth"]
assert any(x.get("x")=="AI_A_Modern_Approach" for x in answer_query("Borrowed(Ravi, x)",kb)["matches"])
assert answer_query("Available(x)",kb)["truth"]
subst,_ = unify_predicates(("Borrowed",("x","AI_Book")),("Borrowed",("Ravi","AI_Book")))
assert subst == {"x":"Ravi"}
print("All five demonstration scenarios passed.")
