#source .venv/bin/activate
#uvicorn main:app --reload
from routes.auth import router as auth_router
from routes.clients import router as client_router
from routes.tasks import router as task_router
from routes.comments import router as comment_router
from routes.admin import router as admin_router
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles



app = FastAPI()

app.include_router(auth_router)

app.include_router(client_router)

app.include_router(task_router)

app.include_router(comment_router)

app.include_router(admin_router)

app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")