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
| **Backend API** | **Railway** | Supports Docker/Python, offers persistent volumes for ChromaDB. |
| **Scheduler** | **Railway (Integrated)** | Runs inside the API container to share the persistent volume. |

---

## 3. Deployment Steps

### Phase 1: Frontend Deployment (Vercel)

The Angular frontend is stateless and can be hosted statically. It has been configured with an `environment.ts` system to handle API routing automatically.

1. **Environment Setup**:
   - The production API URL is already configured in `src/environments/environment.prod.ts` (currently pointing to a placeholder URL `https://your-railway-app.up.railway.app/api/chat`). Ensure this URL exactly matches your live Railway deployment URL.
2. **Vercel Configuration**:
   - Connect the GitHub repository to Vercel.
   - Set the Framework Preset to **Angular**.
   - Build Command: `npm run build --prod` (This flag automatically swaps `environment.ts` with `environment.prod.ts`).
   - Output Directory: `dist/frontend` (or matching `angular.json` output path).
3. **Deployment**:
   - Click "Deploy". Vercel will automatically provide a secure HTTPS URL.

### Phase 2: Backend API Deployment (Railway)

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
2. **Railway Configuration**:
   - Connect the repo to Railway (`railway.app`).
   - Create a new project and deploy from your GitHub repo. Railway will automatically detect the `Dockerfile`.
   - Add a **Volume** to the service via the Railway dashboard or CLI (`railway volume add --mount-path /app/db`) to ensure vector embeddings survive re-deployments.
3. **Environment Variables**:
   - Set `GROQ_API_KEY=gsk_...`
   - Set `CORS_ORIGINS=https://your-vercel-frontend.vercel.app`
4. **Deploy**:
   - Generate a domain in Railway (under Service Settings -> Networking). Note the provided URL and update the frontend if needed.

### Phase 3: Scheduler Deployment (Vector DB Updates)

The scheduler ensures the vector DB is updated daily with the latest mutual fund data. 

Because cloud platforms like Railway enforce one persistent volume per service (and do not support attaching volumes to separate ephemeral Cron jobs), the scheduler must run within the same container as the FastAPI web service to update the local ChromaDB database.

- **Integrated APScheduler**: The `api.py` has been updated to automatically launch a `BackgroundScheduler` on startup. 
- It triggers the ingestion script (`scheduler.py`) daily at 10:00 AM IST. 
- Since it runs within the main Web Service container, it has full read/write access to the `/app/db` persistent disk mount.

---

## 4. Pre-Deployment Checklist

- [x] **CORS Configuration**: Ensure `api.py` CORS middleware explicitly allows the production frontend URL.
- [ ] **Initial DB Ingestion**: Run `python ingest.py` once on the production server to seed the `db/` folder before accepting API traffic.
- [x] **Security Review**: Verify that `.env` files are in `.gitignore` and API keys are strictly loaded via provider secrets management.
- [x] **Health Check**: Implement a simple `GET /` or `GET /health` endpoint in `api.py` for Railway to verify service uptime.
- [ ] **Compliance Validation**: Run `verify_rag.py` in the CI/CD pipeline before deploying any backend code changes.

---

## 5. Monitoring & Maintenance

- **Logs**: Monitor backend logs via Railway dashboard for failed LLM generations or ingestion errors.
- **Data Freshness**: The frontend will automatically display the `Last updated from sources: <date>` footer, making it easy to verify that the daily scheduler is working.
- **Groq Rate Limits**: Monitor Groq API usage. If rate limits are hit, implement an exponential backoff in `query_engine.py` or upgrade the tier.
