"""Pluggable file storage. LocalStorageBackend (default, free) writes to disk;
MinIOStorageBackend (free, self-hosted, S3-compatible) uses boto3 — the same
client also works with Backblaze B2 and Cloudflare R2 free tiers.

Switching backends is a config change (STORAGE_BACKEND env var), never a code
change: all callers use the module-level `storage` proxy.
"""
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from flask import current_app
from werkzeug.utils import secure_filename


def _unique_name(filename):
    safe = secure_filename(filename) or "file"
    return f"{uuid.uuid4().hex}_{safe}"


class StorageBackend(ABC):
    @abstractmethod
    def save(self, file_storage, folder):
        """Persist a Werkzeug FileStorage; return a backend-relative path."""

    @abstractmethod
    def url(self, path):
        """Return a URL/route that serves the stored file."""

    @abstractmethod
    def open(self, path):
        """Return raw bytes for the stored file."""

    @abstractmethod
    def delete(self, path):
        ...


class LocalStorageBackend(StorageBackend):
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)

    def _abs(self, folder, name):
        target_dir = self.base_dir / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir / name

    def save(self, file_storage, folder):
        name = _unique_name(file_storage.filename)
        dest = self._abs(folder, name)
        file_storage.save(dest)
        return f"{folder}/{name}"

    def save_bytes(self, data, folder, filename):
        name = _unique_name(filename)
        dest = self._abs(folder, name)
        dest.write_bytes(data)
        return f"{folder}/{name}"

    def url(self, path):
        # Served by the media route (see app/routes/members.py media endpoint)
        return f"/media/{path}"

    def open(self, path):
        return (self.base_dir / path).read_bytes()

    def delete(self, path):
        target = self.base_dir / path
        if target.exists():
            target.unlink()

    def abspath(self, path):
        return self.base_dir / path


class MinIOStorageBackend(StorageBackend):
    """S3-compatible object storage via boto3. Works with MinIO, Backblaze B2,
    Cloudflare R2 — all free/self-hosted or free-tier options."""

    def __init__(self, *, endpoint, access_key, secret_key, bucket, region):
        import boto3

        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except Exception:
            self.client.create_bucket(Bucket=self.bucket)

    def save(self, file_storage, folder):
        name = _unique_name(file_storage.filename)
        key = f"{folder}/{name}"
        self.client.upload_fileobj(file_storage.stream, self.bucket, key)
        return key

    def save_bytes(self, data, folder, filename):
        name = _unique_name(filename)
        key = f"{folder}/{name}"
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data)
        return key

    def url(self, path):
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": path},
            ExpiresIn=3600,
        )

    def open(self, path):
        obj = self.client.get_object(Bucket=self.bucket, Key=path)
        return obj["Body"].read()

    def delete(self, path):
        self.client.delete_object(Bucket=self.bucket, Key=path)


class _StorageProxy:
    """Lazily builds the configured backend on first use within an app context."""

    _backend = None

    def _get(self):
        if self._backend is None:
            cfg = current_app.config
            if cfg["STORAGE_BACKEND"] == "minio":
                self._backend = MinIOStorageBackend(
                    endpoint=cfg["MINIO_ENDPOINT"],
                    access_key=cfg["MINIO_ACCESS_KEY"],
                    secret_key=cfg["MINIO_SECRET_KEY"],
                    bucket=cfg["MINIO_BUCKET"],
                    region=cfg["MINIO_REGION"],
                )
            else:
                self._backend = LocalStorageBackend(cfg["UPLOAD_DIR"])
        return self._backend

    def __getattr__(self, item):
        return getattr(self._get(), item)


storage = _StorageProxy()
