from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import post_router, user_router, auth_router, comment_router, vote_router

origins = ["*"]
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(post_router.router)
app.include_router(comment_router.router)
app.include_router(vote_router.router)
app.include_router(auth_router.router)
app.include_router(user_router.router)