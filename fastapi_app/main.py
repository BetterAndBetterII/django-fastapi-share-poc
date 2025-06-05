import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from django.conf import settings
from django.contrib.sessions.backends.cache import SessionStore
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/whoami")
async def whoami(request: Request):
    session_key = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not session_key:
        return {"username": None}
    store = SessionStore(session_key=session_key)
    try:
        session = store.load()
    except Exception:
        return {"username": None}
    user_id = session.get("_auth_user_id")
    if not user_id:
        return {"username": None}
    user_model = get_user_model()
    user = await sync_to_async(user_model.objects.get)(pk=user_id)
    return {"username": user.username}
