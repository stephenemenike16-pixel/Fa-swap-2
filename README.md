# FluxSwap Backend Starter

This is a small FastAPI backend starter for the FluxSwap front end.

## Deploy from an Android phone
1. Create a new GitHub repository named `fluxswap-backend`.
2. Upload `main.py`, `requirements.txt`, and `render.yaml` to the repository root.
3. Open Render's dashboard and create a **New Web Service**.
4. Connect the `fluxswap-backend` GitHub repository.
5. Use:
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Deploy. Open your service URL followed by `/health`; it should return `{"ok":true}`.
7. Open `/docs` on your service URL to try the endpoints.

## Current limitation
`POST /api/morph-preview` checks that the two uploaded images are valid and returns their dimensions. It does NOT generate a face swap yet. You must integrate a suitable model or authorized AI provider before the endpoint can return an actual generated result.

## Connect the website
Your browser JavaScript will need to send `FormData` with:
- `source_face`: source face image
- `target_image`: target image
to `https://YOUR-SERVICE.onrender.com/api/morph-preview`.

After deploying, set `ALLOWED_ORIGINS` in the service environment to your exact GitHub Pages origin, for example `https://YOUR-USERNAME.github.io`. Do not include a path. For a quick prototype, the default is `*`; restrict it before public production use.

Do not store private API keys in GitHub Pages HTML/JavaScript. Store secrets in the backend host's environment settings. Use only images you have permission to edit and disclose edited media.
