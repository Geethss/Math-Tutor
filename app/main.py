from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import grading

app = FastAPI(title="Auto Math Grader System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(grading.router, prefix="/api")

@app.get("/")
def home():
    return {"message": "Auto Math Grader System API is running!"}
