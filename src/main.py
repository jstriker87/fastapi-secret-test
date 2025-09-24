from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import hashlib
import os

app = FastAPI()

# In-memory secret store (for demonstration only - DO NOT use in production!)
secrets = {}

class Secret(BaseModel):
    name: str
    value: str

class AuthToken(BaseModel):
    token: str


def get_secret(name: str) -> str | None:
    """Retrieves a secret by name."""
    return secrets.get(name)

def hash_secret(value: str) -> str:
    """Hashes a secret using SHA256."""
    return hashlib.sha256(value.encode()).hexdigest()

@app.post("/secrets/")
async def create_secret(secret: Secret):
    """Creates a new secret."""
    if secret.name in secrets:
        raise HTTPException(status_code=400, detail="Secret name already exists")
    secrets[secret.name] = secret.value
    return {"message": "Secret created successfully"}

@app.get("/secrets/{name}")
async def get_secret_by_name(name: str):
    """Retrieves a secret by name, outputting its SHA256 hash."""
    secret_value = get_secret(name)
    if secret_value is None:
        raise HTTPException(status_code=404, detail="Secret not found")
    return {"sha256_hash": hash_secret(secret_value)}

@app.post("/auth/")
async def authenticate(token: AuthToken):
    """Authentication endpoint (HMAC token - placeholder)."""
    # In a real application, you would verify the HMAC token here.
    # This is just a placeholder to demonstrate the endpoint exists.
    return {"message": "Authentication successful"}


