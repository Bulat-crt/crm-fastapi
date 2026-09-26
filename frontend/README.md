# CRM Frontend

A niche dark editorial frontend for the existing FastAPI CRM backend.

## Backend serving mode (recommended)

Because the frontend is designed to be served by the same FastAPI app, no CORS configuration is required for local development.

Add this to `main.py` after all API routers are included:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")
```

Then run:

```bash
uvicorn main:app --reload
```

Open:

`http://127.0.0.1:8000/app/`

or

`http://127.0.0.1:8000/app/login.html`

## Notes

- JWT is stored in `localStorage` under `crm_access_token`.
- Login uses the backend OAuth2 password flow: email is sent as `username`.
- Protected requests automatically attach `Authorization: Bearer <token>`.
- The frontend hides admin-only navigation for managers, but the backend remains the real security boundary.
- Client list assumes `ClientSort` supports `created_at` and `name` based on the current API design. If your enum uses different names, change the select options in `clients.html` and `clients.js` to match `/openapi.json`.
