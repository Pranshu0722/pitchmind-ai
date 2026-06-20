from pathlib import Path
from typing import Any

import boto3

from pitchmind.config import settings


def _s3() -> Any:
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
    )


def download_file_sync(key: str, dest: Path) -> None:
    _s3().download_file(settings.s3_bucket_name, key, str(dest))


def upload_file_sync(src: Path, key: str, content_type: str) -> None:
    _s3().upload_file(
        str(src),
        settings.s3_bucket_name,
        key,
        ExtraArgs={"ContentType": content_type},
    )
