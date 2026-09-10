# Agent OTG frontend

This React/Vite interface talks to the existing FastAPI backend without changing backend code.

## Run locally

Start the existing backend from `../backend`:

```powershell
py -m uvicorn main:app --reload --port 8000
```

Then start the frontend:

```powershell
npm run dev
```

Vite proxies `/api/*` to `http://127.0.0.1:8000/*`, so no browser CORS setup is required. For a separately deployed frontend, copy `.env.example` to `.env` and set `VITE_API_URL` to the FastAPI origin.

## Connected behavior

- **Agent mode** is the default. It streams `/ask/stream`, preserving backend routing to the coder, 7B, vision, RAG and document-agent paths.
- **Chief mode** explicitly prefixes the prompt with `/complex`, the backend's existing switch for Qwen 14B. It is never selected automatically.
- Selecting PDF, Excel or Word turns a short topic such as `sun` into an explicit artifact request before sending it to the existing document agent.
- Generated artifacts use the backend's `/files/{filename}` download URL. Responses expose progress stages and copy controls; fenced code is rendered in a dedicated code panel.
- The sidebar reads `/sessions` and `/sessions/{name}`, derives a title from the prompt's most frequent meaningful term, supports a local title override, search, and incremental “Show more”.

## Existing backend limitations surfaced by the UI

The API currently receives RAG ingestion as a list of local filesystem paths (`POST /knowledge-base/ingest`); it has no multipart upload endpoint. Normal web browsers intentionally do not reveal a selected file's absolute path, so PDFs/Office/text files can be selected in the UI but cannot be indexed from a browser until the backend adds an upload endpoint. A single image is still sent to the existing `/ask/image` vision endpoint as base64.

Similarly, the backend exposes session listing and retrieval but no public rename or delete endpoint. The frontend keeps history title edits and cleared-history visibility locally while calling `/reset` to clear the active server memory.
