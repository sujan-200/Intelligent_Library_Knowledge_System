import streamlit as st
import pandas as pd
import json
from knowledge_base import KnowledgeBase, Fact
from data import sample_facts
from inference_engine import run_forward_chaining
from query_engine import answer_query, PREDICATES
from unification import parse_predicate, unify_predicates, UnificationError
from utils import validate_fact, predicate_reference
from rules import RULES

# --- Page Configuration ---
st.set_page_config(
    page_title="Intelligent Library FOL",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Minimal CSS (enhances theme without breaking native components) ---
st.markdown("""
<style>
/* Subtle gradient backgrounds & card accents */
.hero-card {
    background: linear-gradient(135deg, rgba(19, 35, 56, 0.85) 0%, rgba(11, 20, 34, 0.95) 100%);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 14px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.3);
    color: #38bdf8;
    border-radius: 9999px;
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}

.hero-title {
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 0.5rem 0;
    color: #f1f7fe;
    letter-spacing: -0.02em;
    line-height: 1.2;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 0.95rem;
    margin: 0;
    line-height: 1.5;
    max-width: 900px;
}

.stat-chip {
    display: inline-block;
    background: rgba(30, 58, 95, 0.6);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 8px;
    padding: 0.35rem 0.65rem;
    font-size: 0.82rem;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
}

.rule-box {
    background: rgba(15, 29, 48, 0.7);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 0.75rem;
}
</style>
""", unsafe_allow_html=True)


# --- Knowledge Base State Management ---
@st.cache_resource
def get_kb():
    return KnowledgeBase(sample_facts())

kb = get_kb()


def render_hero(title: str, subtitle: str, badge: str = "Symbolic AI Engine", icon: str = "📚"):
    st.markdown(f"""
    <div class="hero-card">
        <div class="hero-pill">{icon} {badge}</div>
        <h1 class="hero-title">{title}</h1>
        <p class="hero-subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def show_fact_table(facts=None):
    fact_list = facts if facts is not None else kb.facts
    rows = []
    for f in fact_list:
        meta = kb.provenance.get(f, {"source": "original", "rule": None, "substitution": {}})
        rows.append({
            "Predicate": f.predicate,
            "Arguments": ", ".join(f.args),
            "Type": "Inferred" if meta.get("source") == "inferred" else "Original",
            "Rule": meta.get("rule") or "—",
            "Formula": str(f)
        })
    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        column_config={
            "Predicate": st.column_config.TextColumn("Predicate", width="small"),
            "Arguments": st.column_config.TextColumn("Arguments", width="medium"),
            "Type": st.column_config.TextColumn("Type", width="small"),
            "Rule": st.column_config.TextColumn("Rule", width="small"),
            "Formula": st.column_config.TextColumn("Logical Fact", width="large"),
        },
        width="stretch",
        hide_index=True
    )


# ==========================================
# PAGE 1: DASHBOARD
# ==========================================
def page_dashboard():
    render_hero(
        title="Intelligent Library Knowledge & Reasoning System",
        subtitle="A modular First-Order Logic (FOL) reasoning engine demonstrating explicit knowledge representation, forward-chaining deduction, and explainable unification query answering.",
        badge="Executive Overview",
        icon="📊"
    )

    # Primary Metric Row
    with st.container():
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Books", kb.count("Book"), border=True)
        c2.metric("Authors", kb.count("Author"), border=True)
        c3.metric("Students", kb.count("Student"), border=True)
        c4.metric("Faculty", kb.count("Faculty"), border=True)

    with st.container():
        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Active Loans", kb.count("Borrowed"), border=True)
        avail = kb.count("Available")
        c6.metric("Available Books", avail if avail > 0 else "Run Inference", border=True)
        c7.metric("Known Facts", len(kb.facts), border=True)
        c8.metric("Inferred Facts", len(kb.inferred_facts()), border=True)

    st.markdown("###")

    # Middle Content: Distribution Chart & System Highlights
    col_chart, col_highlights = st.columns([1.6, 1], gap="large")

    with col_chart:
        with st.container(border=True):
            st.subheader("Knowledge Base Distribution", divider="blue")
            chart_predicates = ["Book", "Author", "Student", "Faculty", "Borrowed", "Department", "Subject", "Available"]
            data = []
            for p in chart_predicates:
                count = kb.count(p)
                if count > 0 or p == "Available":
                    data.append({"Predicate": p, "Count": count})
            df_chart = pd.DataFrame(data).set_index("Predicate")
            st.bar_chart(df_chart, y="Count", color="#38bdf8", height=280)

    with col_highlights:
        with st.container(border=True):
            st.subheader("Reasoning Engine Status", divider="blue")
            if len(kb.inferred_facts()) > 0:
                st.badge("Inference Active", icon=":material/check_circle:", color="green")
                st.write(f"The forward chaining engine has derived **{len(kb.inferred_facts())}** additional facts from Horn rules and closed-world loan checks.")
            else:
                st.badge("Baseline State", icon=":material/pending:", color="orange")
                st.write("Forward chaining has not been executed yet. Inferred relations (such as `LibraryUser` and `Available`) await deduction.")
            
            st.markdown("---")
            if st.button("⚡ Run Forward Chaining Now", width="stretch", type="primary"):
                result = run_forward_chaining(kb)
                st.session_state["last_inference"] = result
                st.toast(f"Derived {result['derived_count']} facts!", icon="🎉")
                st.rerun()

    st.markdown("###")

    # Recent Facts Preview
    with st.container(border=True):
        st.subheader("Knowledge Base Snapshot", divider="blue")
        st.caption("Inspect the most recently added or inferred ground atomic facts.")
        show_fact_table(kb.facts[-12:])


# ==========================================
# PAGE 2: KNOWLEDGE BASE
# ==========================================
def page_knowledge_base():
    render_hero(
        title="Knowledge Base Explorer",
        subtitle="The repository of ground atomic formulas representing the library domain. Each fact consists of an n-ary predicate over constant symbols.",
        badge="Data Layer",
        icon="🗄️"
    )

    col_search, col_filter, col_type = st.columns([2, 1.2, 1], gap="medium")
    with col_search:
        search = st.text_input("Search facts", placeholder="Search by name, book, or keyword...", label_visibility="visible")
    with col_filter:
        pred = st.selectbox("Filter by predicate", ["All Predicates"] + sorted(PREDICATES))
    with col_type:
        fact_type = st.selectbox("Origin", ["All Facts", "Original Only", "Inferred Only"])

    # Filtering logic
    filtered = kb.facts
    if pred != "All Predicates":
        filtered = [f for f in filtered if f.predicate == pred]
    if fact_type == "Original Only":
        filtered = [f for f in filtered if kb.provenance.get(f, {}).get("source") != "inferred"]
    elif fact_type == "Inferred Only":
        filtered = [f for f in filtered if kb.provenance.get(f, {}).get("source") == "inferred"]
    if search:
        s = search.strip().lower()
        filtered = [f for f in filtered if s in str(f).lower()]

    st.info(f"Displaying **{len(filtered)}** of **{len(kb.facts)}** total facts.", icon=":material/filter_list:")
    show_fact_table(filtered)

    st.markdown("###")

    # Add Fact & Export in side-by-side cards
    c_add, c_export = st.columns([1.6, 1], gap="large")

    with c_add:
        with st.container(border=True):
            st.subheader("Add a New Fact", divider="blue")
            st.caption("Enter a ground predicate expression. Example: `Book(Quantum_Computing)` or `WrittenBy(Quantum_Computing, Nielsen)`")
            
            preset = st.pills(
                "Quick templates",
                ["Book(Title)", "Author(Name)", "Borrowed(Person, Book)", "WrittenBy(Book, Author)"],
                label_visibility="collapsed"
            )
            default_val = preset if preset else ""
            fact_input = st.text_input("Expression", value=default_val, placeholder="Predicate(arg1, arg2...)")
            
            if st.button("➕ Insert Fact into KB", type="primary", width="stretch"):
                if not fact_input.strip():
                    st.warning("Please enter a fact expression.", icon=":material/warning:")
                else:
                    try:
                        p, args = validate_fact(fact_input)
                        new_fact = Fact(p, args)
                        if kb.add_fact(new_fact, source="original"):
                            st.success(f"Successfully added fact: `{new_fact}`", icon=":material/check_circle:")
                            st.rerun()
                        else:
                            st.info("That fact already exists in the knowledge base.", icon=":material/info:")
                    except Exception as e:
                        st.error(f"Validation error: {e}", icon=":material/error:")

    with c_export:
        with st.container(border=True):
            st.subheader("Export Knowledge", divider="blue")
            st.caption("Download the complete state of original and derived facts as structured JSON.")
            payload = [
                {
                    "predicate": f.predicate,
                    "args": list(f.args),
                    "source": kb.provenance.get(f, {}).get("source", "original"),
                    "rule": kb.provenance.get(f, {}).get("rule")
                }
                for f in kb.facts
            ]
            json_str = json.dumps(payload, indent=2)
            st.download_button(
                "📥 Download Knowledge Base (JSON)",
                data=json_str,
                file_name="library_knowledge_base.json",
                mime="application/json",
                width="stretch"
            )


# ==========================================
# PAGE 3: ONTOLOGY GRAPH
# ==========================================
def page_ontology():
    render_hero(
        title="Library Domain Ontology",
        subtitle="Formal conceptualization of entities and semantic relations in the academic library universe.",
        badge="Semantic Model",
        icon="🕸️"
    )

    with st.container(border=True):
        st.subheader("Entity-Relationship Graph", divider="blue")
        st.graphviz_chart("""
        digraph LibraryOntology {
          graph [bgcolor="transparent", rankdir=LR, splines=spline, nodesep=0.6, ranksep=1.0];
          node [shape=box, style="rounded,filled", fillcolor="#102338", color="#38bdf8", fontcolor="#f1f7fe", fontname="Inter", fontsize=12, penwidth=1.5];
          edge [color="#60a5fa", fontcolor="#93c5fd", fontname="Inter", fontsize=10, penwidth=1.3, arrowsize=0.8];
          
          Book [label="Book (b)"];
          Author [label="Author (a)"];
          Subject [label="Subject (s)"];
          Student [label="Student (p)"];
          Faculty [label="Faculty (p)"];
          LibraryUser [label="LibraryUser (x)\n[Inferred R1]", fillcolor="#0d3b66", color="#34d399"];
          Department [label="Department (d)"];
          
          Author -> Book [label="WrittenBy(b, a)"];
          Book -> Subject [label="BelongsTo(b, s)"];
          Author -> Subject [label="SpecializesIn(a, s)"];
          Student -> Department [label="MemberOf(p, d)"];
          Faculty -> Department [label="MemberOf(p, d)"];
          Student -> Book [label="Borrowed(p, b)"];
          Faculty -> Book [label="Borrowed(p, b)"];
          Book -> Book [label="Available(b) [R4 / CWA]", color="#34d399", fontcolor="#34d399"];
        }
        """)

    st.markdown("###")

    with st.container(border=True):
        st.subheader("Predicate Signatures & Semantics", divider="blue")
        t1, t2 = st.tabs(["Unary Predicates (Entity Types)", "Binary Predicates (Relationships)"])
        
        with t1:
            unary = [
                ("Book(x)", "x is a recognized library book item", "Book(AI_A_Modern_Approach)"),
                ("Author(x)", "x is an academic author or textbook writer", "Author(Russell)"),
                ("Student(x)", "x is an enrolled student member", "Student(Ravi)"),
                ("Faculty(x)", "x is an academic faculty member", "Faculty(Dr_Smith)"),
                ("LibraryUser(x)", "x is authorized/active borrower (derived via R1)", "LibraryUser(Ravi)"),
                ("Subject(x)", "x is an academic study discipline", "Subject(Artificial_Intelligence)"),
                ("Department(x)", "x is an institutional department", "Department(Computer_Science)"),
                ("Available(x)", "Book x is not currently on loan (derived via R4)", "Available(Clean_Code)")
            ]
            df_unary = pd.DataFrame(unary, columns=["Predicate", "Semantics", "Example Fact"])
            st.dataframe(df_unary, width="stretch", hide_index=True)
            
        with t2:
            binary = [
                ("WrittenBy(b, a)", "Book b is authored by author a", "WrittenBy(AI_A_Modern_Approach, Russell)"),
                ("BelongsTo(b, s)", "Book b is categorized under subject s", "BelongsTo(AI_A_Modern_Approach, Artificial_Intelligence)"),
                ("SpecializesIn(a, s)", "Author a has core domain expertise in subject s", "SpecializesIn(Russell, Artificial_Intelligence)"),
                ("Borrowed(p, b)", "Person p currently holds book b on active loan", "Borrowed(Ravi, AI_A_Modern_Approach)"),
                ("HasBorrowed(p, b)", "Denotes active or historical loan relationship (derived via R3)", "HasBorrowed(Ravi, AI_A_Modern_Approach)"),
                ("MemberOf(p, d)", "Person p belongs to academic department d", "MemberOf(Ravi, Computer_Science)")
            ]
            df_binary = pd.DataFrame(binary, columns=["Predicate", "Semantics", "Example Fact"])
            st.dataframe(df_binary, width="stretch", hide_index=True)


# ==========================================
# PAGE 4: LOGICAL RULES
# ==========================================
def page_logical_rules():
    render_hero(
        title="Executable Logical Rules",
        subtitle="Declarative inference rules that drive the forward-chaining deduction engine. R1–R3 are definite Horn clauses; R4 implements negation-as-failure.",
        badge="Rule Base",
        icon="📜"
    )

    for r in RULES:
        with st.container(border=True):
            r_col1, r_col2 = st.columns([3, 1])
            with r_col1:
                st.markdown(f"#### {r['id']}: {r['name']}")
            with r_col2:
                if r['id'] == 'R4':
                    st.badge("Closed-World Negation", icon=":material/shield_lock:", color="orange")
                else:
                    st.badge("Definite Horn Clause", icon=":material/done_all:", color="blue")

            fol_latex = r["fol"].replace("∀", r"\forall ").replace("∧", r"\land ").replace("¬", r"\neg ").replace("→", r"\rightarrow ")
            st.latex(fol_latex)

            p_col, c_col = st.columns(2)
            with p_col:
                st.markdown(f"**Premises:** `{', '.join(r['premises'])}`")
            with c_col:
                st.markdown(f"**Conclusion:** `{r['conclusion']}`")

            st.markdown(f"**Plain Language:** {r['english']}")

            if r.get("note"):
                st.warning(f"**Modeling Note:** {r['note']}", icon=":material/info:")


# ==========================================
# PAGE 5: INFERENCE ENGINE
# ==========================================
def page_inference_engine():
    render_hero(
        title="Forward-Chaining Inference Engine",
        subtitle="Repeatedly joins rule antecedents against the knowledge base until reaching a fixed point. Applies closed-world negation to compute book availability.",
        badge="Deductive Reasoning",
        icon="⚙️"
    )

    btn_col, info_col = st.columns([1, 2], gap="large")
    with btn_col:
        run_btn = st.button("▶ Run Forward Chaining", type="primary", width="stretch")
    with info_col:
        st.caption("Executes semi-naive forward chaining across R1, R2, R3, followed by R4 availability deduction.")

    if run_btn:
        with st.spinner("Executing forward-chaining closure..."):
            result = run_forward_chaining(kb)
            st.session_state["last_inference"] = result
            st.success(f"Inference completed: **{result['derived_count']}** new facts derived!", icon=":material/check_circle:")

    result = st.session_state.get("last_inference")
    if result:
        st.markdown("###")
        m1, m2, m3 = st.columns(3)
        m1.metric("Initial Ground Facts", result["initial_count"], border=True)
        m2.metric("Facts Derived", f"+{result['derived_count']}", border=True)
        m3.metric("Final Knowledge Base", result["final_count"], border=True)

        st.markdown("###")
        with st.container(border=True):
            st.subheader("Step-by-Step Execution Trace", divider="blue")
            if result["steps"]:
                trace_rows = []
                for i, step in enumerate(result["steps"], start=1):
                    trace_rows.append({
                        "Step": f"#{i}",
                        "Rule": step["rule"],
                        "Substitution Binding": str(step["substitution"]),
                        "Derived Fact": step["derived"]
                    })
                st.dataframe(pd.DataFrame(trace_rows), width="stretch", hide_index=True)
            else:
                st.info("The knowledge base has already reached a fixed point; no new facts were derived.", icon=":material/info:")

    st.markdown("###")
    with st.container(border=True):
        st.subheader("Knowledge State Breakdown", divider="blue")
        tab_inf, tab_orig, tab_all = st.tabs(["Derived Inferred Facts", "Base Original Facts", "Complete Knowledge Base"])
        with tab_inf:
            inferred = kb.inferred_facts()
            if inferred:
                show_fact_table(inferred)
            else:
                st.info("No inferred facts present yet. Click 'Run Forward Chaining' above.", icon=":material/info:")
        with tab_orig:
            show_fact_table(kb.original_facts())
        with tab_all:
            show_fact_table(kb.facts)


# ==========================================
# PAGE 6: UNIFICATION DEMO
# ==========================================
def page_unification_demo():
    render_hero(
        title="First-Order Logic Unification Lab",
        subtitle="Finds the Most General Unifier (MGU) — the minimal set of variable substitutions that makes two predicate expressions syntactically identical.",
        badge="Pattern Matching",
        icon="🔄"
    )

    preset = st.selectbox(
        "Choose an educational preset or type custom expressions below:",
        [
            "Custom Predicates",
            "Example 1: Single Variable Binding [Borrowed(x, AI_Book) vs Borrowed(Ravi, AI_Book)]",
            "Example 2: Cross Variables [WrittenBy(b, Russell) vs WrittenBy(AI_Book, a)]",
            "Example 3: Dual Argument Matching [BelongsTo(b, Artificial_Intelligence) vs BelongsTo(AI_Book, s)]",
            "Example 4: Conflict Failure [Borrowed(Ravi, AI_Book) vs Borrowed(Priya, AI_Book)]",
            "Example 5: Arity Mismatch Failure [Book(x) vs WrittenBy(x, y)]"
        ]
    )

    if preset.startswith("Example 1"):
        d1, d2 = "Borrowed(x, AI_Book)", "Borrowed(Ravi, AI_Book)"
    elif preset.startswith("Example 2"):
        d1, d2 = "WrittenBy(b, Russell)", "WrittenBy(AI_Book, a)"
    elif preset.startswith("Example 3"):
        d1, d2 = "BelongsTo(b, Artificial_Intelligence)", "BelongsTo(AI_Book, s)"
    elif preset.startswith("Example 4"):
        d1, d2 = "Borrowed(Ravi, AI_Book)", "Borrowed(Priya, AI_Book)"
    elif preset.startswith("Example 5"):
        d1, d2 = "Book(x)", "WrittenBy(x, y)"
    else:
        d1, d2 = "Borrowed(x, AI_Book)", "Borrowed(Ravi, AI_Book)"

    c_left, c_right = st.columns(2, gap="medium")
    with c_left:
        left = st.text_input("Expression 1 (Predicate A)", value=d1)
    with c_right:
        right = st.text_input("Expression 2 (Predicate B)", value=d2)

    st.caption("Note: Lowercase identifiers (`x`, `y`, `b`, `a`) are treated as variables; capitalized identifiers (`Ravi`, `AI_Book`) are constants.")

    if st.button("⚡ Compute Most General Unifier (MGU)", type="primary", width="stretch"):
        try:
            lp, la = parse_predicate(left)
            rp, ra = parse_predicate(right)
            steps = []
            subst, steps = unify_predicates((lp, la), (rp, ra), steps)

            with st.container(border=True):
                st.subheader("Unification Result: SUCCESS", divider="green")
                st.badge("Unifier Found", icon=":material/check:", color="green")
                
                res_col, steps_col = st.columns([1, 1.5], gap="large")
                with res_col:
                    st.markdown("#### Most General Unifier (θ)")
                    if subst:
                        formatted = {k: v for k, v in subst.items()}
                        st.json(formatted)
                    else:
                        st.info("Empty substitution `{}` (expressions are already identical).", icon=":material/info:")
                
                with steps_col:
                    st.markdown("#### Unification Steps")
                    for i, step_desc in enumerate(steps, start=1):
                        st.markdown(f"**Step {i}:** {step_desc}")

        except Exception as e:
            with st.container(border=True):
                st.subheader("Unification Result: FAILED", divider="red")
                st.badge("Cannot Unify", icon=":material/close:", color="red")
                st.error(f"Unification error: {e}", icon=":material/error:")


# ==========================================
# PAGE 7: INTELLIGENT QUERY
# ==========================================
def page_query_system():
    render_hero(
        title="Intelligent FOL Query Engine",
        subtitle="Pose logical queries to the library knowledge base. Supports ground truth checks, variable-binding discovery, and full deduction provenance.",
        badge="Query Solver",
        icon="🔍"
    )

    sample_queries = [
        "LibraryUser(Ravi)",
        "Borrowed(Ravi, x)",
        "Available(x)",
        "WrittenBy(x, Russell)",
        "BelongsTo(x, Artificial_Intelligence)",
        "MemberOf(x, Computer_Science)",
        "HasBorrowed(x, AI_A_Modern_Approach)",
        "Book(AI_A_Modern_Approach)"
    ]

    selected_sample = st.selectbox("Select a sample query or compose a custom query below:", sample_queries)
    query_text = st.text_input("Enter Query Expression", value=selected_sample)

    st.caption("Tip: Use variables (`x`, `y`, `book`) to search for matching entities, or constants (`Ravi`, `Russell`) to verify specific assertions.")

    if st.button("🔎 Execute Query", type="primary", width="stretch"):
        try:
            result = answer_query(query_text, kb)
            with st.container(border=True):
                if result["truth"]:
                    st.subheader("Query Evaluation: TRUE", divider="green")
                    st.badge("Satisfiable", icon=":material/check_circle:", color="green")
                    st.write(f"**Explanation:** {result['explanation']}")

                    if result["matches"]:
                        st.markdown("#### Variable Bindings (Solutions)")
                        st.dataframe(pd.DataFrame(result["matches"]), width="stretch", hide_index=True)

                    if result["supporting_facts"]:
                        st.markdown("#### Supporting Evidence & Provenance")
                        rows = []
                        for sf in result["supporting_facts"]:
                            p_info = sf.get("provenance", {})
                            rows.append({
                                "Fact": str(sf.get("fact")),
                                "Source": p_info.get("source", "original").capitalize(),
                                "Rule Applied": p_info.get("rule") or "Direct Assertion",
                                "Bindings": str(p_info.get("substitution", {}))
                            })
                        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
                else:
                    st.subheader("Query Evaluation: FALSE", divider="red")
                    st.badge("No Models / No Matching Facts", icon=":material/cancel:", color="red")
                    st.write(f"**Explanation:** {result['explanation']}")
                    st.warning("If this query references inferred relationships (like `LibraryUser` or `Available`), ensure you have run the **Inference Engine** first.", icon=":material/help:")

        except Exception as e:
            st.error(f"Query processing error: {e}", icon=":material/error:")


# ==========================================
# PAGE 8: LIBRARY EXPLORER
# ==========================================
def page_library_explorer():
    render_hero(
        title="Library Catalog & Entity Explorer",
        subtitle="Browse books, patrons, faculty, and departments through connected relational views.",
        badge="Catalog View",
        icon="📖"
    )

    kind = st.segmented_control(
        "Domain Category",
        ["Books", "Authors", "Subjects", "Students", "Faculty", "Departments", "Borrowing Records"],
        default="Books"
    )

    mapping = {
        "Books": "Book",
        "Authors": "Author",
        "Subjects": "Subject",
        "Students": "Student",
        "Faculty": "Faculty",
        "Departments": "Department",
        "Borrowing Records": "Borrowed"
    }

    facts = kb.by_predicate(mapping[kind])
    st.info(f"Total **{len(facts)}** {kind.lower()} records cataloged in the knowledge base.", icon=":material/info:")

    if kind == "Books":
        book_names = [f.args[0] for f in facts]
        selected_book = st.selectbox("Inspect Book Details", book_names)

        with st.container(border=True):
            st.subheader(f"📘 {selected_book.replace('_', ' ')}", divider="blue")
            
            # Look up authorship
            authors = [f.args[1] for f in kb.by_predicate("WrittenBy") if f.args[0] == selected_book]
            # Look up subject
            subjects = [f.args[1] for f in kb.by_predicate("BelongsTo") if f.args[0] == selected_book]
            # Look up borrowing
            borrowers = [f.args[0] for f in kb.by_predicate("Borrowed") if f.args[1] == selected_book]

            b1, b2, b3 = st.columns(3)
            with b1:
                st.markdown("**Author(s)**")
                if authors:
                    for a in authors: st.markdown(f"- `{a}`")
                else: st.caption("Unknown author")

            with b2:
                st.markdown("**Subject Classification**")
                if subjects:
                    for s in subjects: st.markdown(f"- `{s.replace('_', ' ')}`")
                else: st.caption("Unclassified")

            with b3:
                st.markdown("**Availability Status**")
                if borrowers:
                    st.badge("Checked Out", icon=":material/schedule:", color="orange")
                    st.markdown(f"Borrowed by: `{borrowers[0]}`")
                else:
                    st.badge("Available", icon=":material/check_circle:", color="green")
                    st.markdown("On library shelves.")

    elif kind in ("Students", "Faculty"):
        person_names = [f.args[0] for f in facts]
        selected_person = st.selectbox(f"Inspect {kind[:-1]} Details", person_names)

        with st.container(border=True):
            st.subheader(f"👤 {selected_person.replace('_', ' ')}", divider="blue")
            depts = [f.args[1] for f in kb.by_predicate("MemberOf") if f.args[0] == selected_person]
            loans = [f.args[1] for f in kb.by_predicate("Borrowed") if f.args[0] == selected_person]

            p1, p2 = st.columns(2)
            with p1:
                st.markdown("**Department Membership**")
                if depts:
                    st.markdown(f"`{depts[0].replace('_', ' ')}`")
                else:
                    st.caption("No department fact recorded")

            with p2:
                st.markdown("**Currently Borrowed Books**")
                if loans:
                    for b in loans: st.markdown(f"- `{b.replace('_', ' ')}`")
                else:
                    st.caption("No active loans")
    else:
        # Generic table view for other entities
        df_entities = pd.DataFrame([{"Predicate": str(f.predicate), "Arguments": ", ".join(f.args)} for f in facts])
        st.dataframe(df_entities, width="stretch", hide_index=True)


# ==========================================
# PAGE 9: DOCUMENTATION
# ==========================================
def page_documentation():
    render_hero(
        title="Theoretical & Architectural Documentation",
        subtitle="Comprehensive guide to the symbolic AI foundations, First-Order Logic semantics, and implementation principles powering this system.",
        badge="Reference Manual",
        icon="📚"
    )

    docs = [
        ("1. First-Order Logic (FOL) Foundations", 
         "First-Order Logic is a formal language expressive enough to describe objects, properties, and relationships. "
         "Unlike Propositional Logic which operates on monolithic true/false statements, FOL decomposes assertions into:\n"
         "- **Objects / Constants**: Specific domain entities such as `Ravi` or `AI_A_Modern_Approach`.\n"
         "- **Predicates**: Relations or properties holding over objects, such as `Book(x)` or `Borrowed(person, book)`.\n"
         "- **Variables**: Placeholders representing any member of the domain, denoted by leading lowercase letters (`x`, `y`, `book`).\n"
         "- **Quantifiers**: Universal (∀) and Existential (∃) quantification."),

        ("2. Knowledge Base Structure",
         "A Knowledge Base (KB) stores known truths about the universe of discourse. In this project:\n"
         "- All stored facts are **ground atomic formulas** (tuples of constants under an n-ary predicate).\n"
         "- Provenance metadata tracks whether each fact was originally asserted or inferred by a rule, recording the exact rule and substitution used."),

        ("3. Definite Horn Clauses and Forward Chaining",
         "Rules R1, R2, and R3 are definite Horn clauses of the form:\n"
         "$$\\bigwedge_i P_i \\rightarrow C$$\n"
         "Forward chaining begins with known premises and iteratively matches them against antecedent patterns. "
         "When all premises of a rule are satisfied by a substitution $\\theta$, the conclusion instance $C\\theta$ is derived and added to the knowledge base. "
         "This continues until reaching a **fixed point** where no further facts can be generated."),

        ("4. Robinson's Unification Algorithm",
         "Unification finds the Most General Unifier (MGU) $\\theta$ such that $P_1\\theta = P_2\\theta$. "
         "Our unification engine implements:\n"
         "- Recursive substitution across term arguments.\n"
         "- **Occurs Check**: Prevents circular unification (e.g., binding variable $x$ to a term containing $x$).\n"
         "- Predicate symbol and arity consistency checks."),

        ("5. Negation as Failure & Closed-World Assumption (Rule R4)",
         "Pure First-Order Logic does not provide negation-as-failure. In a real library, a book is 'available' if there is no active loan record. "
         "Rule R4 implements this via the Closed-World Assumption (CWA):\n"
         "$$\\forall b \\; (\\text{Book}(b) \\land \\neg \\exists p \\; \\text{Borrowed}(p, b)) \\rightarrow \\text{Available}(b)$$\n"
         "This rule is evaluated after positive Horn closure across the current set of `Borrowed` facts.")
    ]

    for title, content in docs:
        with st.container(border=True):
            st.subheader(title, divider="blue")
            st.markdown(content)


# ==========================================
# MULTI-PAGE NAVIGATION SETUP
# ==========================================
pages = {
    "Overview": [
        st.Page(page_dashboard, title="Dashboard", icon=":material/dashboard:"),
        st.Page(page_ontology, title="Ontology Graph", icon=":material/hub:"),
    ],
    "Knowledge & Rules": [
        st.Page(page_knowledge_base, title="Knowledge Base", icon=":material/database:"),
        st.Page(page_logical_rules, title="Logical Rules", icon=":material/rule:"),
        st.Page(page_unification_demo, title="Unification Lab", icon=":material/compare_arrows:"),
    ],
    "Reasoning & Query": [
        st.Page(page_inference_engine, title="Inference Engine", icon=":material/psychology:"),
        st.Page(page_query_system, title="Intelligent Query", icon=":material/search:"),
    ],
    "Library Domain": [
        st.Page(page_library_explorer, title="Library Explorer", icon=":material/menu_book:"),
        st.Page(page_documentation, title="Documentation", icon=":material/article:"),
    ],
}

nav = st.navigation(pages, position="sidebar")

# Sidebar Branding Header
st.sidebar.markdown("""
<div style="display:flex; align-items:center; gap:12px; padding: 0.5rem 0.2rem 1rem 0.2rem;">
    <div style="font-size:32px;">📚</div>
    <div>
        <div style="font-weight:700; font-size:17px; color:#f1f7fe; line-height:1.2;">LibraryFOL</div>
        <div style="font-size:11px; color:#38bdf8; font-weight:600; letter-spacing:0.06em; text-transform:uppercase;">Knowledge & Inference</div>
    </div>
</div>
""", unsafe_allow_html=True)

nav.run()
