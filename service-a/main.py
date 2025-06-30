from fastapi import FastAPI
import httpx
import os

app = FastAPI()

@app.get("/call-b")
async def call_b():
    service_b_url = os.environ.get("SERVICE_B_URL")
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{service_b_url}/ping")
        return {"from-b": r.json()}
