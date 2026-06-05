import os
import re
import dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
import config

# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

dotenv.load_dotenv()

# Phase 4 — load the same embedding model used at ingest time so query
# vectors live in the same vector space as the stored chunk vectors.
embeddings = HuggingFaceEmbeddings(
    model_name=config.MODEL_NAME,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

db = None
if os.path.exists(config.DB_DIR):
    db = Chroma(
        persist_directory=config.DB_DIR,
        embedding_function=embeddings,
    )

# ---------------------------------------------------------------------------
# Phase 5 — Guardrail Patterns & Keywords
# ---------------------------------------------------------------------------

PII_PATTERNS = [
    r"[A-Z]{5}[0-9]{4}[A-Z]",               # PAN card
    r"\d{4}[ -]?\d{4}[ -]?\d{4}",            # Aadhaar
    r"[\w.-]+@[\w.-]+\.\w+",                  # Email
    r"(?:\+91|0)?[6-9]\d{9}",                 # Indian mobile
    r"folio\s*(?:no|number)?\s*[:.-]?\s*\d+", # Folio number
    r"account\s*(?:no|number)?\s*[:.-]?\s*\d+" # Account number
]

ADVISORY_KEYWORDS = [
    "should i buy", "should i invest", "which is better", "recommend",
    "best fund", "suggest", "buy or sell", "portfolio advice",
    "is it good to buy", "should i hold", "investment tips", "give advice",
    "should i switch", "switch from", "switch to"
]

PERFORMANCE_KEYWORDS = [
    "return", "cagr", "past performance", "annualized", "yield",
    "growth rate", "returns", "percentage growth", "profit percentage"
]

GREETING_KEYWORDS = [
    "hi", "hey", "hello", "greetings", "morning", "afternoon", "evening"
]

CAPITAL_GAINS_KEYWORDS = [
    "capital gains statement", "download capital gains", "get capital gains"
]

# ---------------------------------------------------------------------------
# Phase 5 — Guardrail scanner functions
# ---------------------------------------------------------------------------

def scan_pii(query: str) -> bool:
    """Returns True if the query contains a PII pattern."""
    for pattern in PII_PATTERNS:
        if re.search(pattern, query, re.IGNORECASE):
            return True
    return False


def scan_advisory(query: str) -> bool:
    """Returns True if the query contains an advisory intent keyword."""
    q = query.lower()
    return any(kw in q for kw in ADVISORY_KEYWORDS)


def scan_performance(query: str) -> bool:
    """Returns True if the query is asking about performance/returns."""
    q = query.lower()
    return any(kw in q for kw in PERFORMANCE_KEYWORDS)

def scan_greeting(query: str) -> bool:
    """Returns True if the query is purely a greeting."""
    import string
    q = query.lower().translate(str.maketrans('', '', string.punctuation)).strip()
    words = q.split()
    if not words: return False
    if len(words) <= 3 and any(kw in words for kw in GREETING_KEYWORDS):
        return True
    return False

def scan_capital_gains(query: str) -> bool:
    """Returns True if the query asks about downloading capital gains statement."""
    q = query.lower()
    return any(kw in q for kw in CAPITAL_GAINS_KEYWORDS)

# ---------------------------------------------------------------------------
# Phase 4 — Scheme & Section Detection
# ---------------------------------------------------------------------------

def detect_scheme(query: str) -> str | None:
    """
    Maps query keywords to a source_file stem used as a ChromaDB metadata filter.

    Fix (Phase 4.2): "growth" alone is no longer mapped to mid-cap because it
    appears in natural-language queries unrelated to the Growth Fund.  We now
    require "mid cap", "mid-cap", or the explicit product name "growth fund".
    """
    q = query.lower()
    if "large cap" in q or "large-cap" in q or ("large" in q and "nippon" in q):
        return "nippon_india_large_cap"
    if "flexi cap" in q or "flexi-cap" in q or "flexi" in q:
        return "nippon_india_flexi_cap"
    if "mid cap" in q or "mid-cap" in q or "growth fund" in q or "midcap" in q:
        return "nippon_india_growth_mid_cap"
    if "small cap" in q or "small-cap" in q or "smallcap" in q:
        return "nippon_india_small_cap"
    if "silver" in q or "etf fof" in q or "silver etf" in q:
        return "nippon_india_silver_etf_fof"
    if "statement" in q or "download" in q or "account statement" in q or "capital gain" in q:
        return "nippon_india_statements"
    return None


def detect_section(query: str) -> str | None:
    """
    Phase 4.1 — Maps natural-language query intent to a ChromaDB section
    metadata value.  Returns None when no clear section intent is detected,
    allowing the retrieval cascade to fall back to scheme-only or pure-vector
    search.

    IMPORTANT: statement/download queries must be checked FIRST so that
    "capital gain statement" does not get routed to the 'tax' section.
    """
    q = query.lower()

    # Statement/download queries: no section filter — let scheme routing
    # (nippon_india_statements.json) pick the best chunk via vector search.
    if any(k in q for k in ["statement", "download", "account statement",
                              "how do i get", "how to get statement"]):
        return None

    if any(k in q for k in ["expense ratio", "ter", " expense", "management fee"]):
        return "expense_ratio"
    if any(k in q for k in ["exit load", "redemption charge", "exit fee", "exit charges"]):
        return "exit_load"
    if any(k in q for k in ["sip", "minimum sip", "lumpsum", "min investment",
                              "minimum investment", "minimum amount"]):
        return "minimum_investment"
    if any(k in q for k in ["benchmark", "index", "nifty", "bse", "tri"]):
        return "benchmark"
    if any(k in q for k in ["tax", "stcg", "ltcg", "capital gain", "taxation"]):
        return "tax"
    if any(k in q for k in ["fund manager", "who manages", "manager name",
                              "fund management", "managed by"]):
        return "fund_management"
    if any(k in q for k in ["objective", "investment objective", "goal",
                              "invest in what", "what does it invest"]):
        return "investment_objective"
    if any(k in q for k in ["fund house", "amc", "asset management", "nippon india mutual"]):
        return "fund_house"
    if any(k in q for k in ["overview", "about the fund", "category", "riskometer"]):
        return "overview"
    if any(k in q for k in ["nav", "net asset value"]):
        return "nav"
    if any(k in q for k in ["aum", "assets under management", "fund size", "corpus"]):
        return "aum"
    if any(k in q for k in ["pe ratio", "p/e ratio", "pb ratio", "p/b ratio", "price to earnings", "price to book", "pe and pb", "valuation"]):
        return "pe_pb_ratio"
    if any(k in q for k in ["rating", "stars", "star rating"]):
        return "rating"
    if any(k in q for k in ["returns", "performance", "cagr", "past performance", "yield", "growth rate"]):
        return "returns"
    return None

# ---------------------------------------------------------------------------
# Phase 4 — Core Retrieval Layer
# ---------------------------------------------------------------------------

def retrieve(query: str) -> dict:
    """
    Phase 4.3 — Three-stage cascading metadata-filtered retrieval.

    Stage 1: source_file + section  (k=2) — most precise
    Stage 2: source_file only       (k=3) — scheme-scoped
    Stage 3: section only           (k=3) — cross-scheme, same topic
    Stage 4: pure vector search     (k=3) — last resort

    Returns a dict with:
      context      — labelled context blocks "[Scheme — Section]\n<text>"
      source_url   — citation URL from the best-matching chunk
      last_updated — date string from the best-matching chunk
      chunks       — raw list[Document]
    """
    global db

    if db is None:
        if os.path.exists(config.DB_DIR):
            db = Chroma(persist_directory=config.DB_DIR, embedding_function=embeddings)
        else:
            return {
                "context": "",
                "source_url": "",
                "last_updated": "",
                "chunks": [],
            }

    scheme_key = detect_scheme(query)
    section    = detect_section(query)
    docs       = []

    # Stage 1: scheme + section (most precise, k=2)
    # ChromaDB requires $and operator for multi-field filtering.
    if scheme_key and section:
        docs = db.similarity_search(
            query,
            k=2,
            filter={"$and": [
                {"source_file": {"$eq": f"{scheme_key}.json"}},
                {"section":      {"$eq": section}},
            ]},
        )

    # Stage 2: scheme only (k=3)
    if not docs and scheme_key:
        docs = db.similarity_search(
            query,
            k=3,
            filter={"source_file": {"$eq": f"{scheme_key}.json"}},
        )

    # Stage 3: section only, any scheme (k=3)
    if not docs and section:
        docs = db.similarity_search(
            query,
            k=3,
            filter={"section": {"$eq": section}},
        )

    # Stage 4: pure vector search (k=3)
    if not docs:
        docs = db.similarity_search(query, k=3)

    if not docs:
        return {
            "context": "",
            "source_url": config.SCHEME_URLS.get("nippon_india_statements", ""),
            "last_updated": "",
            "chunks": [],
        }

    # Phase 4.4 — Structured context assembly with provenance labels.
    # Each block is headed by "[Scheme Name — Section]" so the LLM knows
    # exactly where each fact originates, reducing hallucination risk.
    context_parts = []
    for doc in docs:
        sec    = doc.metadata.get("section", "").replace("_", " ").title()
        scheme = doc.metadata.get("scheme_name", "")
        context_parts.append(f"[{scheme} -- {sec}]\n{doc.page_content}")
    context_str = "\n\n".join(context_parts)

    best_meta = docs[0].metadata
    source_url   = best_meta.get("source_url", "")
    last_updated = best_meta.get("last_updated", "")
    citation_title = best_meta.get("scheme_name", "Source Factsheet")
    if "T" in last_updated:
        last_updated = last_updated.split("T")[0]

    return {
        "context":      context_str,
        "source_url":   source_url,
        "citation_title": citation_title,
        "last_updated": last_updated,
        "chunks":       docs,
    }

# ---------------------------------------------------------------------------
# Phase 5 — Query Engine: Guardrails + LLM Generation + Output Validator
# ---------------------------------------------------------------------------

def query_rag_engine(query: str) -> dict:
    """
    Full query pipeline matching the Query Routing Matrix:

    PII Scan → Advisory Scan → Performance Scan
        → Phase 4 retrieve() → LLM Generation → Output Validation
    """

    # 5.1 PII Safety Guardrail (NFR-01)
    if scan_pii(query):
        return {
            "answer":      config.PII_REFUSAL_MESSAGE,
            "citation_url": "",
            "citation_title": "",
            "last_updated": "",
            "is_refusal":   True,
        }

    # 5.1.5 Greeting Handler
    if scan_greeting(query):
        return {
            "answer": "Hello! I'm Genie. How can I assist you with Nippon India Mutual Funds today?",
            "citation_url": "",
            "citation_title": "",
            "last_updated": "",
            "is_refusal": True,
        }

    # 5.1.6 Capital Gains Statement Guide
    if scan_capital_gains(query):
        return {
            "answer": "You can download your capital gains statement from CAMS (camsonline.com) or KFintech (kfintech.com) — the two RTAs (Registrar & Transfer Agents) for Nippon India Mutual Fund — using your PAN and registered email. Alternatively, if you invested via Groww, you can access it under Account → Statements → Capital Gains in the Groww app.",
            "citation_url": "https://mf.nipponindiaim.com/investoreducation/types-of-mutual-fund-statements",
            "citation_title": "Types of Mutual Fund Statements | nipponindiaim.com",
            "last_updated": "June 2026",
            "is_refusal": False,
        }

    # 5.2 Advisory Intent Classifier (FR-03)
    if scan_advisory(query):
        return {
            "answer":      config.ADVISORY_REFUSAL_MESSAGE,
            "citation_url": "https://www.amfiindia.com/investor-corner/education/interest.html",
            "citation_title": "AMFI Investor Education",
            "last_updated": "",
            "is_refusal":   True,
        }

    # 5.3 Performance Redirect Handler (NFR-02)
    if scan_performance(query):
        scheme_key   = detect_scheme(query) or "nippon_india_large_cap"
        factsheet_url = config.SCHEME_URLS.get(scheme_key, config.SCHEME_URLS["nippon_india_large_cap"])
        return {
            "answer":      config.PERFORMANCE_REDIRECT_MESSAGE_TEMPLATE.format(factsheet_url=factsheet_url),
            "citation_url": factsheet_url,
            "citation_title": "Groww Factsheet",
            "last_updated": "",
            "is_refusal":   True,
        }

    # 5.4 RAG Retrieval (Phase 4)
    retrieval = retrieve(query)
    context_str  = retrieval["context"]
    source_url   = retrieval["source_url"]
    citation_title = retrieval.get("citation_title", "Source Factsheet")
    last_updated = retrieval["last_updated"]
    chunks       = retrieval["chunks"]

    if not context_str or not chunks:
        return {
            "answer":      config.OUT_OF_SCOPE_REFUSAL_MESSAGE,
            "citation_url": config.SCHEME_URLS.get("nippon_india_statements", ""),
            "citation_title": "Nippon India",
            "last_updated": "",
            "is_refusal":   True,
        }

    # 5.5 LLM Constrained Generation (temperature=0.0)
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key in ("your_groq_api_key_here", "your_key_here"):
        best_chunk = chunks[0].page_content
        return {
            "answer":      f"Groq API key is not configured. Sourced fact: {best_chunk[:300]}...",
            "citation_url": source_url,
            "citation_title": citation_title,
            "last_updated": last_updated,
            "is_refusal":   False,
        }

    try:
        llm = ChatGroq(
            model=config.GROQ_MODEL_NAME,
            temperature=0.0,
            groq_api_key=api_key,
        )

        prompt = (
            f"{config.SYSTEM_PROMPT}\n"
            f"Context:\n{context_str}\n\n"
            f"User Query: {query}\n"
            f"Answer:"
        )

        response    = llm.invoke(prompt)
        raw_answer  = response.content.strip()

        # 5.6 Output Validator & Formatter (FR-02, FR-05, FR-06)

        # (Naive sentence truncation removed to allow bullet points and newlines)

        return {
            "answer":      raw_answer,
            "citation_url": source_url,
            "citation_title": citation_title,
            "last_updated": last_updated,
            "is_refusal":   False,
        }

    except Exception as e:
        fallback = (
            f"Factual details are available on the official scheme factsheet."
        )
        return {
            "answer":      fallback,
            "citation_url": source_url,
            "citation_title": citation_title,
            "last_updated": last_updated,
            "is_refusal":   False,
        }


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_queries = [
        "What is the expense ratio of Nippon India Large Cap Fund?",
        "What is the exit load for Nippon India Flexi Cap Fund?",
        "Who is the fund manager of Nippon India Small Cap Fund?",
        "What is the benchmark for Nippon India Silver ETF FoF?",
        "How can I download my capital gains statement?",
        "Should I invest in Nippon India Large Cap Fund?",
        "My PAN is BKDPD8829C. Show my portfolio.",
        "What returns has Nippon India Flexi Cap given?",
    ]
    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"Query : {q}")
        res = query_rag_engine(q)
        print(f"Answer: {res['answer'][:300]}")
        print(f"URL   : {res['citation_url']}")
        print(f"Refusal: {res['is_refusal']}")
