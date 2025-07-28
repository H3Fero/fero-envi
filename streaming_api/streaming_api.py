from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from minio import Minio
from minio.error import S3Error
from datetime import timedelta
import json
import os
import urllib3

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "minio")
MINIO_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID", "admin")
MINIO_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "admin1234")
PUBLIC_ENDPOINT = os.environ.get("PUBLIC_ENDPOINT", "minio.localhost:9000")
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

@app.on_event("startup")
def startup_event():
    if not internal_client.bucket_exists(BUCKET):
        internal_client.make_bucket(BUCKET)
        policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Action": ["s3:GetObject"],
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Resource": [f"arn:aws:s3:::{BUCKET}/*"],
                "Sid": ""
            }]
        }
        policy_json = json.dumps(policy)
        internal_client.set_bucket_policy(BUCKET, policy_json)

@app.get("/contenu/{film_name}")
def get_film_url(film_name: str):
    try:
        internal_client.stat_object(BUCKET, film_name)
        url = public_client.presigned_get_object(BUCKET, film_name, expires=timedelta(minutes=60))
        return {"stream_url": url}
    except Exception as e:
        raise HTTPException(404, f"film not found: {str(e)}")