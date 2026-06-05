# Groww Genie — Mutual Fund FAQ Assistant

Groww Genie is a facts-only, compliance-first RAG (Retrieval-Augmented Generation) chatbot designed to answer objective queries about specific mutual fund schemes available on Groww.

## Scope
The knowledge base is strictly limited to **5 Nippon India Mutual Fund schemes**:
1. Nippon India Large Cap Fund (Direct - Growth)
2. Nippon India Flexi Cap Fund (Direct - Growth)
3. Nippon India Growth Mid Cap Fund (Direct - Growth)
4. Nippon India Small Cap Fund (Direct - Growth)
5. Nippon India Silver ETF FoF (Direct - Growth)

Additionally, it can guide users on how to download capital gains statements and account statements.

## Key Features
- **Factual Answers Only:** Answers are limited to 3 sentences, extracted strictly from verified AMC factsheets and Groww scheme pages.
- **Strict Citations:** Every valid answer provides a direct citation link to the source document and a "Last updated" date to ensure data provenance.
- **PII Guardrails:** Actively blocks queries containing PAN, Aadhaar, email addresses, phone numbers, or folio details to protect user privacy.
- **Anti-Advisory Controls:** Gracefully refuses subjective questions ("should I invest?", "which is better?"), referring users to AMFI Investor Education.
- **Performance Restrictions:** Prevents the LLM from generating return calculations, instead directing users to the official scheme page to view performance metrics safely.

## 8. Execution Commands (Quick Start)

You can use the provided `quick_start.bat` script to automate these steps on Windows, or run them manually:

```bash
# 1. Configure API key
copy .env.example .env
# Edit .env -> set GROQ_API_KEY=gsk_...

# 2. Install dependencies
pip install -r requirements.txt

# 3. Build vector database from corpus
python ingest.py

# 4. Run automated compliance tests
python verify_rag.py

# 5. Launch the backend API
uvicorn api:app --port 8000

# 6. Launch the Angular frontend
cd frontend
npm start
```

## 9. Known Limitations & Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Corpus limited to 5 Groww pages | Cannot answer queries about other schemes/AMCs | Clear out-of-scope refusal with explanation |
| Groww is a secondary source (not AMC primary) | Data may lag AMC factsheet updates | Daily scheduler refresh; `last_updated` footer for transparency |
| No disambiguation loop | Ambiguous queries (e.g. *"exit load?"* without scheme name) may return wrong scheme | Keyword-based scheme detection + top-K retrieval fallback |
| LLM hallucination on edge cases | May fabricate facts not in context | `temperature=0.0`, output validator cross-checks chunks, grounding evaluation |
| Groq API dependency | Outages block LLM generation | Fallback: return direct corpus URL link if API fails; Groq has 99.9% SLA |
