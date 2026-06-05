# Deployment Plan — Mutual Fund FAQ Assistant

This document outlines the end-to-end deployment strategy for the Mutual Fund FAQ Assistant (Groww Genie), considering its specific architecture: a FastAPI backend, an Angular frontend, a local persistent ChromaDB vector store, and scheduled tasks.

---

## 1. Architecture Overview for Deployment

The application consists of three main deployable components:
1. **Frontend**: An Angular SPA (Single Page Application) built with Tailwind CSS.
2. **Backend**: A FastAPI Python server serving the RAG API endpoints.
3. **Background Scheduler**: A Python process (`scheduler.py`) to trigger `ingest.py` daily for corpus updates.

*Key Constraint:* The backend uses a local, file-based **ChromaDB** (`db/` directory). Therefore, the backend environment requires a **persistent file system** (ephemeral serverless environments like AWS Lambda or Vercel serverless functions are not recommended for the backend unless the vector DB is externalized or rebuilt dynamically).

---

## 2. Target Hosting Platforms

Based on the requirements, here is the recommended hosting stack:

| Component | Recommended Platform | Why? |
|-----------|----------------------|------|
| **Frontend** | **Vercel** or **Netlify** | Free, zero-config CI/CD for Angular, global CDN. |
| **Backend API** | **Render (Web Service)** | Supports Docker/Python, offers persistent disks for ChromaDB. |
| **Scheduler** | **Render (Background Worker)** | Can share the persistent disk with the API to update the database. |

---

## 3. Deployment Steps

### Phase 1: Frontend Deployment (Vercel)

The Angular frontend is stateless and can be hosted statically. It has been configured with an `environment.ts` system to handle API routing automatically.

1. **Environment Setup**:
   - The production API URL is already configured in `src/environments/environment.prod.ts` (currently pointing to a placeholder Render URL `https://groww-genie-backend.onrender.com/api/chat`). Ensure this URL exactly matches your live Render deployment URL.
2. **Vercel Configuration**:
   - Connect the GitHub repository to Vercel.
   - Set the Framework Preset to **Angular**.
   - Build Command: `npm run build --prod` (This flag automatically swaps `environment.ts` with `environment.prod.ts`).
   - Output Directory: `dist/frontend` (or matching `angular.json` output path).
3. **Deployment**:
   - Click "Deploy". Vercel will automatically provide a secure HTTPS URL.

### Phase 2: Backend API Deployment (Render)

Since ChromaDB writes data to the `db/` folder locally, we need a VPS or a PaaS with a persistent disk.

1. **Dockerization (Recommended)**:
   - Create a `Dockerfile` for the FastAPI backend:
     ```dockerfile
     FROM python:3.10-slim
     WORKDIR /app
     COPY requirements.txt .
     RUN pip install --no-cache-dir -r requirements.txt
     COPY . .
     CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
     ```
2. **Render Web Service Configuration**:
   - Connect the repo to Render.
   - Create a new **Web Service**.
   - Environment: `Docker` (or `Python 3`).
   - Add a **Persistent Disk** mounted at `/app/db` to ensure vector embeddings survive re-deployments.
3. **Environment Variables**:
   - Set `GROQ_API_KEY=gsk_...`
   - Set `CORS_ORIGINS=https://your-vercel-frontend.vercel.app`
4. **Deploy**:
   - Start the service. Note the provided `.onrender.com` URL and update the frontend if needed.

### Phase 3: Scheduler Deployment (Vector DB Updates)

The scheduler ensures the vector DB is updated daily with the latest mutual fund data.

1. **Option A: Render Cron Job (Simplest)**
   - Create a Render Cron Job mapped to the same codebase.
   - Command: `python ingest.py`
   - Schedule: `0 10 * * *` (10:00 AM daily).
   - *Requirement*: Needs to mount the exact same Persistent Disk used by the Web Service.
2. **Option B: Integrated APScheduler**
   - Run the existing `scheduler.py` alongside the FastAPI app (using threading or Render Background Worker).

---

## 4. Pre-Deployment Checklist

- [x] **CORS Configuration**: Ensure `api.py` CORS middleware explicitly allows the production frontend URL.
- [ ] **Initial DB Ingestion**: Run `python ingest.py` once on the production server to seed the `db/` folder before accepting API traffic.
- [x] **Security Review**: Verify that `.env` files are in `.gitignore` and API keys are strictly loaded via provider secrets management.
- [x] **Health Check**: Implement a simple `GET /` or `GET /health` endpoint in `api.py` for Render to verify service uptime.
- [ ] **Compliance Validation**: Run `verify_rag.py` in the CI/CD pipeline before deploying any backend code changes.

---

## 5. Monitoring & Maintenance

- **Logs**: Monitor backend logs via Render dashboard for failed LLM generations or ingestion errors.
- **Data Freshness**: The frontend will automatically display the `Last updated from sources: <date>` footer, making it easy to verify that the daily scheduler is working.
- **Groq Rate Limits**: Monitor Groq API usage. If rate limits are hit, implement an exponential backoff in `query_engine.py` or upgrade the tier.
