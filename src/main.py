from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import post, user, auth, vote

origins = ["*"]
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(post.route)
app.include_router(user.route)
app.include_router(auth.route)
app.include_router(vote.route)
@app.get("/")
def root():
    return {'message': 'hello world'}