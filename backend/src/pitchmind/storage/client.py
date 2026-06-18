from __future__ import annotations

from typing import Any

import aioboto3
import structlog
from botocore.exceptions import ClientError

from pitchmind.config import settings

log = structlog.get_logger(__name__)

_session = aioboto3.Session()


def _client_kwargs() -> dict[str, Any]:
    return {
        "endpoint_url": settings.s3_endpoint_url,
        "aws_access_key_id": settings.s3_access_key,
        "aws_secret_access_key": settings.s3_secret_key.get_secret_value(),
        "region_name": settings.s3_region,
    }


async def ensure_bucket() -> None:
    async with _session.client("s3", **_client_kwargs()) as s3:
        try:
            await s3.head_bucket(Bucket=settings.s3_bucket_name)
        except ClientError:
            await s3.create_bucket(Bucket=settings.s3_bucket_name)
            log.info("storage.bucket_created", bucket=settings.s3_bucket_name)


async def upload_file(key: str, data: bytes, content_type: str) -> str:
    async with _session.client("s3", **_client_kwargs()) as s3:
        await s3.put_object(
            Bucket=settings.s3_bucket_name,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
    log.info("storage.uploaded", key=key, size=len(data))
    return key


async def get_presigned_url(key: str, expires: int = 3600) -> str:
    async with _session.client("s3", **_client_kwargs()) as s3:
        url = await s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.s3_bucket_name, "Key": key},
            ExpiresIn=expires,
        )
    return str(url)


async def delete_file(key: str) -> None:
    async with _session.client("s3", **_client_kwargs()) as s3:
        await s3.delete_object(Bucket=settings.s3_bucket_name, Key=key)
    log.info("storage.deleted", key=key)


async def file_exists(key: str) -> bool:
    async with _session.client("s3", **_client_kwargs()) as s3:
        try:
            await s3.head_object(Bucket=settings.s3_bucket_name, Key=key)
            return True
        except ClientError:
            return False
