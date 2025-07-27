from minio import Minio
import os

# Configuration MinIO depuis ton Docker Compose
client = Minio(
    "127.0.0.1:43293",            # ou "minio:9000" si lancé depuis un conteneur
    access_key="admin",          # adapte selon ta conf
    secret_key="admin1234",      # adapte selon ta conf
    secure=False                 # True si tu utilises HTTPS
)

bucket = "films"
source_dir = "./data"  # Ton dossier local où sont les vidéos

# Crée le bucket si nécessaire
if not client.bucket_exists(bucket):
    client.make_bucket(bucket)

# Upload tous les .mp4 du dossier data/
for fname in os.listdir(source_dir):
    if fname.endswith(".mp4"):
        src_path = os.path.join(source_dir, fname)
        print(f"Uploading {fname}...")
        client.fput_object(bucket, fname, src_path)
print("Import terminé !")