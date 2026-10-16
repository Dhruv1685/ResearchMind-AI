# Deploying ResearchMind AI

Two services:

| Part | Where | URL pattern |
| :--- | :--- | :--- |
| FastAPI backend (`server.py`) | Render | `https://<name>.onrender.com` |
| Next.js dashboard (`frontend/`) | Vercel | `https://<name>.vercel.app` |

The 410 MB arXiv CSV is git-ignored and is NOT deployed. Search automatically
falls back to the live arXiv API, so everything still works.

---

## PART A - DEPLOY THE API ON RENDER

### A1. Push the repo to GitHub

```bash
git push origin dataset-version
```

`render.yaml` at the repo root is a Render Blueprint, so Render reads it
automatically.

### A2. Create the service

1. Go to https://dashboard.render.com and sign in with GitHub.
2. Click **New +** > **Blueprint**.
3. Pick the repo `Dhruv1685/ResearchMind-AI`.
4. Render detects `render.yaml` and proposes the service `researchmind-api`.
5. Click **Apply**.

Manual alternative: **New +** > **Web Service** > connect repo, then set

```
Runtime:          Python
Build Command:    pip install torch --index-url https://download.pytorch.org/whl/cpu && pip install -r requirements.txt
Start Command:    uvicorn server:app --host 0.0.0.0 --port $PORT
```

### A3. Set environment variables

In the Render dashboard, **Environment** > **Add Environment Variable**:

| Key | Value |
| :--- | :--- |
| `GEMINI_API_KEY` | your key from https://aistudio.google.com/app/apikey |

`ALLOWED_ORIGINS` can stay empty. Empty means any origin may call the API,
which is what you want for a first deploy.

### A4. Wait for the deploy

The first build takes 5-15 minutes (PyTorch CPU wheel + sentence-transformers).

Check it is up:

```
https://<your-name>.onrender.com/api/status
```

Expected JSON:

```json
{"apiKeyConfigured": true, "datasetAvailable": false, "modules": [...]}
```

`datasetAvailable: false` is expected and correct.

---

## PART B - DEPLOY THE DASHBOARD ON VERCEL

### B1. Import the project

1. Go to https://vercel.com/new and sign in with GitHub.
2. Pick the repo `Dhruv1685/ResearchMind-AI`.
3. **Important:** set **Root Directory** to `frontend`
   (click **Edit** next to the detected framework). Vercel must build from
   `frontend/`, not the repo root.
4. Framework preset: **Next.js** (auto-detected).
5. Build Command / Output: leave the defaults.

### B2. Set the API URL before building

`NEXT_PUBLIC_API_URL` is inlined into the JavaScript at build time, so it must
exist **before** the first build.

Under **Environment Variables** add:

| Name | Value |
| :--- | :--- |
| `NEXT_PUBLIC_API_URL` | `https://<your-name>.onrender.com` |

Use your real Render URL, no trailing slash.

### B3. Deploy

Click **Deploy**. When it finishes, Vercel shows a URL like
`researchmind-ai-xxxx.vercel.app`. Open it.

---

## PART C - VERIFY BOTH LIVE

Open the Vercel URL and run all four modules:

1. **Search** - pick a source, type a topic, press **Search papers**.
   You should see the note "CSV dataset not found in this environment"
   and papers from the live arXiv API.
2. **Recommendation** - select a primary paper, press **Find similar papers**.
   The first call after a cold start loads the Sentence-BERT model and can
   take 10-30 seconds. Later calls are fast.
3. **Summarization** - press **Generate summary**.
4. **Research gaps** - tick 2+ papers, press **Analyze research gaps**.

Also confirm directly:

```
https://<your-name>.onrender.com/api/status
```

---

## OPTIONAL - LOCK DOWN CORS

Leaving `ALLOWED_ORIGINS` empty allows any website to call your API. Fine for a
demo, not fine if you care. To allow only your dashboard, set in Render:

```
ALLOWED_ORIGINS=https://<your-name>.vercel.app
```

Then restart the service and redeploy Vercel.

If you add a custom domain, list it too, comma separated:

```
ALLOWED_ORIGINS=https://myapp.vercel.app,https://myapp.com
```

---

## TROUBLESHOOTING

**Render build fails installing torch**
The CPU index line in the build command is required. A plain
`pip install torch` pulls the CUDA build (~3 GB) and exceeds the free tier
disk. Keep `--index-url https://download.pytorch.org/whl/cpu`.

**Render deploy fails with out of memory**
Set `WARM_MODELS=0` in Render to skip pre-loading the model, or move to a
paid instance type (Standard, 2 GB) under **Instance Type**.

**Dashboard shows "API server is not reachable"**
`NEXT_PUBLIC_API_URL` is wrong or missing. Fix it in Vercel under
**Settings > Environment Variables**, then **Redeploy**. It does not apply
without a rebuild.

**CORS error in the browser console**
The API is up but rejecting the origin. Either clear `ALLOWED_ORIGINS` in
Render, or set it to your exact Vercel URL.

**First search is slow / times out**
Render free instances sleep after inactivity. The first request after a
cold start re-runs the startup warm-up. Upgrade the instance or send a
keep-alive ping to `/api/status` every 10 minutes.

**Sentence-BERT download slow on first recommendation**
The model is fetched from Hugging Face on first use. It is cached in the
instance for the lifetime of that instance, not permanently.
