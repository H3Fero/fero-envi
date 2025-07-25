from fastapi import FastAPI, HTTPException
from minio import Minio
from datetime import timedelta
import os
import urllib3

app = FastAPI()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID", "admin")
MINIO_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "admin1234")
PUBLIC_ENDPOINT = os.environ.get("PUBLIC_ENDPOINT", "minio.localhost")
PUBLIC_USE_SSL = os.environ.get("PUBLIC_USE_SSL", "false").lower() == "true"
BUCKET = "films"

internal_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)
public_client = Minio(
    PUBLIC_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=PUBLIC_USE_SSL,
    http_client=urllib3.PoolManager(cert_reqs='CERT_NONE')
)

@app.get("/contenu/{film_name}")
def get_film_url(film_name: str):
    try:
        internal_client.stat_object(BUCKET, film_name)
        url = public_client.presigned_get_object(BUCKET, film_name, expires=timedelta(minutes=60))
        return {"stream_url": url}
    except Exception as e:
        raise HTTPException(404, f"film not found: {str(e)}")