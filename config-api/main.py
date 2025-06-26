from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os, json

app = FastAPI(
    root_path="/api/settings",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",

)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
CONFIG_PATH = "/shared_data/configs"

@app.get("/configs")
def list_configs():
    return [f for f in os.listdir(CONFIG_PATH) if f.endswith(".json")]

@app.get("/configs/{filename}")
def get_config(filename: str):
    path = os.path.join(CONFIG_PATH, filename)
    if not os.path.exists(path):
        raise HTTPException(404)
    with open(path, encoding="utf-8") as f:
        return json.load(f)

@app.post("/configs/{filename}")
async def save_config(filename: str, request: Request):
    data = await request.json()
    path = os.path.join(CONFIG_PATH, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {"status": "ok"}