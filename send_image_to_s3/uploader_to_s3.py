import boto3
import random
import os
from datetime import datetime
from pathlib import Path

AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""
AWS_REGION     = ""
BUCKET_NAME    = ""
IMAGES_FOLDER  = ""          



def pick_random_image() -> Path:
    extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    images = [
        p for p in Path(IMAGES_FOLDER).iterdir()
        if p.suffix.lower() in extensions
    ]
    if not images:
        raise FileNotFoundError(f"Không tìm thấy ảnh trong '{IMAGES_FOLDER}'")
    return random.choice(images)


def build_s3_key(local_path: Path) -> str:
    ext = local_path.suffix.lower()
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M")
    return f"camera_{timestamp}{ext}"


def upload_to_s3(local_path: Path) -> str:
    s3_key = build_s3_key(local_path)

    s3 = boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
    )
    s3.upload_file(str(local_path), BUCKET_NAME, s3_key)
    return s3_key
