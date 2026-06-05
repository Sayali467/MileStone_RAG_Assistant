# Centralized configuration and settings for the Mutual Fund FAQ Assistant
import os

# Project Path settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "db")
CORPUS_DIR = os.path.join(BASE_DIR, "corpus")
PARSED_DIR = os.path.join(BASE_DIR, "data", "parsed")

# Embeddings model name (BGE Small — local CPU, no API cost)
MODEL_NAME = "BAAI/bge-small-en-v1.5"

# LLM — Groq inference (llama-3.3-70b-versatile, free tier)
GROQ_MODEL_NAME = "llama-3.3-70b-versatile"

# Scoped Mutual Fund Schemes
SCHEME_URLS = {
    "nippon_india_large_cap": "https://groww.in/mutual-funds/nippon-india-large-cap-fund-direct-growth",
    "nippon_india_flexi_cap": "https://groww.in/mutual-funds/nippon-india-flexi-cap-fund-direct-growth",
    "nippon_india_growth_mid_cap": "https://groww.in/mutual-funds/nippon-india-growth-mid-cap-fund-direct-growth",
    "nippon_india_small_cap": "https://groww.in/mutual-funds/nippon-india-small-cap-fund-direct-growth",
    "nippon_india_silver_etf_fof": "https://groww.in/mutual-funds/nippon-india-silver-etf-fof-direct-growth",
    "nippon_india_statements": "https://nipponindiaim.com/"
}

# Refusal and Redirect Messages (Compliance & Safety)
PII_REFUSAL_MESSAGE = (
    "For security and compliance reasons, we cannot accept queries containing personal identifiers "
    "(such as PAN, Aadhaar, folio numbers, bank accounts, emails, or phone numbers). "
    "Please rephrase your query without any personal details."
)

ADVISORY_REFUSAL_MESSAGE = (
    "I cannot provide investment advice, opinions, or recommendations. "
    "For educational resources on mutual funds, please visit the official AMFI Investor Education portal."
)

PERFORMANCE_REDIRECT_MESSAGE_TEMPLATE = (
    "I am not permitted to perform or present return/performance calculations. "
    "You can view the live performance metrics, CAGR, and historical returns directly on the official factsheet."
)

OUT_OF_SCOPE_REFUSAL_MESSAGE = (
    "I can only answer factual queries about the 5 scoped Nippon India Mutual Fund schemes "
    "(Large Cap, Flexi Cap, Growth/Mid Cap, Small Cap, and Silver ETF FoF) and statement download guides. "
    "Your query appears to be outside this scope."
)

# LLM Constrained System Prompt
SYSTEM_PROMPT = (
    "You are a compliance-first, facts-only Mutual Fund FAQ Assistant. "
    "Your goal is to answer factual, objective questions about specific mutual fund schemes using ONLY the provided retrieved context.\n\n"
    "You must strictly adhere to the following rules:\n"
    "1. Base your answer ONLY on the provided information. If the information does not contain the answer, "
    "state that you couldn't find the details in the official sources and suggest visiting the official Nippon India Mutual Fund website. "
    "Do not make assumptions or extrapolate.\n"
    "2. NEVER recommend buying, selling, holding, or investing in any fund. Do not provide opinions, advice, or comparisons.\n"
    "3. Keep your response brief and direct. Do not write more than 3 sentences.\n"
    "4. Do not include any performance calculations, CAGR, or return projections. If asked for performance, politely redirect the user.\n"
    "5. Format your response using bullet points wherever necessary (e.g. if listing multiple fund managers or conditions). Start bullet lines with '- '.\n"
    "6. Use markdown bold to highlight any numbers, percentages, or monetary values (e.g. **0.22%**, **Rs. 100**, **15 days**).\n"
    "7. NEVER use the words 'provided context', 'retrieved context', 'knowledge base', 'chunk', or 'database' in your response. Instead, refer to 'official sources' (e.g., 'I couldn't find detailed steps in the official sources currently available.').\n"
)
