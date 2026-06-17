from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .router import post, user, auth, vote

origins = ["*"]
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)
@app.get("/")
def default():
    return {'message': 'hello world'}


