# FluxSwap AI backend (starter)

This version adds a real model-provider integration to `/api/morph-preview` using the Replicate `codeplugtech/face-swap` model. The provider charges according to its current account/pricing terms; this is not guaranteed to be free. Get adult/guardian permission before creating an account, adding billing, or using paid services.

## Deploy update

Upload `main.py` and `requirements.txt` to the root of your existing GitHub repository `Fa-swap-2`, replacing the current versions. Commit the changes; Render should redeploy automatically.

## Configure on Render

In your Render service, open **Environment** and add:

- Key: `REPLICATE_API_TOKEN`
- Value: your provider API token (keep it secret; never put it in `index.html` or commit it to GitHub)

Also set `ALLOWED_ORIGINS` to the exact origin of your GitHub Pages site, such as `https://YOUR-USERNAME.github.io` or `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY` depending on the published site URL. Do not leave `*` for a public production site.

## API

`POST /api/morph-preview` expects multipart form data:
- `source_face`: the face image to use
- `target_image`: the image to edit
- `consent_confirmed`: `true`

Successful responses are image bytes (`image/jpeg`), not JSON. Update the frontend to send the three fields and display the returned image blob.

## Important

Only process images you own or have clear permission to edit. Do not use face swaps to impersonate someone or mislead people. Do not submit intimate images. This backend starter does not provide authentication, quotas, or abuse prevention; add these before making the service public.
