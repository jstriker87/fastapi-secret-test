from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Json
import hashlib
import os
from dotenv import load_dotenv
import hmac
import json
from fastapi.middleware.cors import CORSMiddleware
load_dotenv() 

app = FastAPI()
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

secrets = {}

class Secret(BaseModel):
    name: str
    value: str

class AuthToken(BaseModel):
    token: str


shared_key = os.getenv("SHARED_KEY")
secrets_path = "/var/lib/backend/persistence/secrets.json"
def load_secrets() -> None:
    try:
        global secrets

        with open(secrets_path, "r") as file:
            secrets = json.load(file)
    except FileNotFoundError:
        with open(secrets_path, "w") as file:
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
    global secrets
    """Creates a new secret."""
    if secret.name in secrets:
        raise HTTPException(status_code=400, detail="Secret name already exists")
    secrets[secret.name] = secret.value
    with open(secrets_path, "w") as file:
        json.dump(secrets, file, indent=4)
        print("secrets",secrets)
    return {"message": "Secret created successfully"}


@app.get("/secrets/")
async def get_secrets_by_name(encoding_method: str | None = None):
    """Retrieves a secret by name, outputting its SHA256 hash."""
    if encoding_method is None:
        encoding_method = "sha256"

    all_secrets = list(map(lambda secret: { "name": secret[0], "value": hash_secret(secret[1], encoding_method)}, zip(secrets.keys(), secrets.values())))
    return all_secrets




@app.get("/secrets/{name}")
async def get_secret_by_name(name: str, encoding_method: str):
    print("Yes")
    """Retrieves a secret by name, outputting its SHA256 hash."""
    secret_value = get_secret(name)
    if secret_value is None:
        raise HTTPException(status_code=404, detail="Secret not found")
    return {"hash": hash_secret(secret_value,encoding_method)}


@app.post("/auth/", status_code=200)
async def authenticate(token: AuthToken):
    global shared_key
    print("sk",shared_key)
    if not hmac.compare_digest(token.token,shared_key or ""):
            raise HTTPException(status_code=401, detail="Authentication failed")
    else:
        return {"message": "Authentication successful"}
         


