from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Json
import hashlib
import os
from dotenv import load_dotenv
import hmac
import json

load_dotenv() 

key = os.getenv("SHARED_KEY")
app = FastAPI()

secrets = {}

class Secret(BaseModel):
    name: str
    value: str

class AuthToken(BaseModel):
    token: str


def load_secrets() -> None:
    try:
        global secrets
        with open('secrets.json', 'r') as file:
            secrets = json.load(file)
    except FileNotFoundError:
        with open('secrets.json', 'w') as file:
            file.write("{}")

load_secrets()

def get_secret(name: str) -> str | None:
    """Retrieves a secret by name."""
    return secrets.get(name)

def hash_secret(value: str, encodingType: str) -> str:
    """Hashes a secret using SHA256."""
    if encodingType.lower() == "sha256":
        return hashlib.sha256(value.encode()).hexdigest()

    if encodingType.lower() == "blake2b":
        return hashlib.blake2b(value.encode()).hexdigest()

    if encodingType.lower() == "blake2s":
        return hashlib.blake2s(value.encode()).hexdigest()


    if encodingType.lower() == "md5":
        return hashlib.md5(value.encode()).hexdigest()
    
    else:
        raise ValueError("Invalid encoding chosen")


@app.post("/secrets/")
async def create_secret(secret: Secret):
    """Creates a new secret."""
    if secret.name in secrets:
        raise HTTPException(status_code=400, detail="Secret name already exists")
    secrets[secret.name] = secret.value
    json_secrets = json.dumps(secrets, indent=4)
    with open("secrets.json", "r+") as f:
        f.write(json_secrets)
        secrets = json.load(file)
    return {"message": "Secret created successfully"}

@app.get("/secrets/{name}")
async def get_secret_by_name(name: str):
    """Retrieves a secret by name, outputting its SHA256 hash."""
    secret_value = get_secret(name)
    if secret_value is None:
        raise HTTPException(status_code=404, detail="Secret not found")
    return {"sha256_hash": hash_secret(secret_value)}



@app.post("/auth/", status_code=200)
async def authenticate(token: AuthToken):
    shared_key = os.getenv("SHARED_KEY")
    if not hmac.compare_digest(token.token,shared_key or ""):
            raise HTTPException(status_code=401, detail="Authentication failed")
    return {"message": "Authentication successful"}
         


