# 🛠️ Two-Container Prototype Specification (Updated for GHCR)

## 🎯 Goal
Create a minimal system of **two containerized services**:
- **Service A (caller)** exposes a public HTTP endpoint.
- **Service B (callee)** responds to internal HTTP requests from Service A.
- Deploy both to Azure using **Azure Container Apps**.
- Set up **CI/CD**, enable **scaling to 0**, and verify **container-to-container communication**.

---

## 🧩 Stage 1: Local Development — Code + Docker + Compose

### Structure
```
/project-root
  /service-a
    main.py
    Dockerfile
  /service-b
    main.py
    Dockerfile
  docker-compose.yml
```

### Service A (caller)
/service-a/main.py
```python
from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/call-b")
async def call_b():
    async with httpx.AsyncClient() as client:
        r = await client.get("http://service-b:8000/ping")
        return {"from-b": r.json()}
```

### Service B (callee)
/service-b/main.py
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/ping")
async def ping():
    return {"message": "Hello from B"}
```

### Dockerfiles

/service-a/Dockerfile
```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn httpx
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

/service-b/Dockerfile (same, omit httpx)
```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  service-a:
    build: ./service-a
    ports:
      - "8080:8000"
    depends_on:
      - service-b

  service-b:
    build: ./service-b
    ports:
      - "8081:8000"
```

Run locally:
```bash
docker-compose up --build
```

Test: http://localhost:8080/call-b → `{"from-b": {"message": "Hello from B"}}`

---

## 🧷 Stage 2: Azure Manual Preparation

### Create resources
```bash
az group create --name prototype01-rg --location westeurope

az containerapp env create   --name prototype-env   --resource-group prototype01-rg   --location westeurope
```

---

## 🔁 Stage 3: CI/CD with GitHub Actions and GHCR

### Prerequisites
- Create a GitHub PAT with `write:packages`, `read:packages` and add it as a secret: `GHCR_TOKEN`
- Set your GitHub username as a secret: `GHCR_USERNAME`

### .github/workflows/deploy.yml
```yaml
name: Deploy Two-Container App

on:
  push:
    branches:
      - main

env:
  RESOURCE_GROUP: prototype01-rg
  CONTAINER_ENV: prototype-env
  LOCATION: westeurope
  GHCR_REGISTRY: ghcr.io
  GHCR_USER: ${{ secrets.GHCR_USERNAME }}
  GHCR_TOKEN: ${{ secrets.GHCR_TOKEN }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Log in to GHCR
      run: echo "${{ env.GHCR_TOKEN }}" | docker login ghcr.io -u ${{ env.GHCR_USER }} --password-stdin

    - name: Build and push service-a
      run: |
        docker build -t ghcr.io/${{ env.GHCR_USER }}/service-a:latest ./service-a
        docker push ghcr.io/${{ env.GHCR_USER }}/service-a:latest

    - name: Build and push service-b
      run: |
        docker build -t ghcr.io/${{ env.GHCR_USER }}/service-b:latest ./service-b
        docker push ghcr.io/${{ env.GHCR_USER }}/service-b:latest

    - name: Azure login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}

    - name: Deploy Service B
      run: |
        az containerapp create           --name service-b           --resource-group $RESOURCE_GROUP           --environment $CONTAINER_ENV           --image ghcr.io/${{ env.GHCR_USER }}/service-b:latest           --target-port 8000           --ingress internal           --registry-server ghcr.io           --registry-username $GHCR_USER           --registry-password $GHCR_TOKEN

    - name: Deploy Service A
      run: |
        az containerapp create           --name service-a           --resource-group $RESOURCE_GROUP           --environment $CONTAINER_ENV           --image ghcr.io/${{ env.GHCR_USER }}/service-a:latest           --target-port 8000           --ingress external           --env-vars SERVICE_B_URL=http://service-b:8000           --registry-server ghcr.io           --registry-username $GHCR_USER           --registry-password $GHCR_TOKEN
```

---

## ⚙️ Stage 4: Azure Configuration

### Scaling
```bash
az containerapp revision set-mode --name service-a --resource-group prototype01-rg --mode single

az containerapp update --name service-a --resource-group prototype01-rg   --min-replicas 0 --max-replicas 1
```

### Internal Networking
- Same Container App Environment → internal DNS
- service-a can call `http://service-b:8000`

---

## ✅ Summary Checklist

| Task | Status |
|------|--------|
| Two APIs working locally via Compose | ✅ |
| Containers can talk internally | ✅ |
| Azure setup: ACA + shared environment | ✅ |
| Scale to zero for unused services | ✅ |
| CI/CD via GitHub Actions with GHCR | ✅ |
| Secure environment variables/config | ✅ |
| Observability (logs, scaling) | Optional extra |