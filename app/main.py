from fastapi import FastAPI
from .routers import oauth,user,research_session,source
from . import models
from app.db.database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(oauth.router)
app.include_router(user.router)
app.include_router(research_session.router)
app.include_router(source.router)