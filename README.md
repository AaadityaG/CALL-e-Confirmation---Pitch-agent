# CommercePilot

A CALL-E-powered conversational commerce agent that turns post-purchase phone conversations into real Shopify actions. Customers confirm orders, accept merchant-defined offers, and the AI genuinely updates the Shopify order.

## Prerequisites

- [Python 3.12+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- Git

---

## Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
```

Edit `.env`:
- `DATABASE_URL` — your Neon Postgres connection string
- `JWT_SECRET` — `python -c "import secrets; print(secrets.token_hex(32))"`
- `GOOGLE_CLIENT_ID` — from Google Cloud Console (optional; email/password works without it)
- `SHOPIFY_*` / `CALLE_API_KEY` — integrations (fill in when wiring the flows)

### Frontend

```bash
cd frontend
npm install
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
```

Edit `.env` and set `VITE_GOOGLE_CLIENT_ID` if you want Google sign-in.

---

## Run

**Backend (one line, PowerShell):**
```powershell
cd backend; .\.venv\Scripts\Activate.ps1; uvicorn main:app --reload --port 8008
```

Or open two terminals:

**Terminal 1 — Backend**
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --port 8008
```

**Terminal 2 — Frontend**
```bash
cd frontend
npm run dev
```

Frontend: [http://localhost:5173](http://localhost:5173)
Backend API: [http://localhost:8008](http://localhost:8008)
API docs: [http://localhost:8008/docs](http://localhost:8008/docs)

> Note: `npm run dev` / `npm run build` may misbehave if the project path contains `&` (this folder does). Workarounds: invoke `node node_modules/oxlint/bin/oxlint src` and `node node_modules/typescript/bin/tsc -b` directly, or run from a copy of the repo in a path without `&`.

---

## Project Structure

```
CommercePilot/
├── backend/          # FastAPI server
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/         # React + TypeScript + Tailwind + RTK
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── store/
│   │   └── services/
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   ├── BUILD_PLAN.md  # Hackathon build plan & milestones
│   └── AUTH_PLAN.md   # Auth design & build plan
└── README.md
```