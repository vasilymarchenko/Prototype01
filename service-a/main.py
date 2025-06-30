from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/call-b")
async def call_b():
    async with httpx.AsyncClient() as client:
        r = await client.get("http://service-b:8000/ping")
        return {"from-b": r.json()}
