"""Secure file upload handling: validation, image resizing, storage."""
import io

from PIL import Image

from app.utils.storage import storage

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
DOCUMENT_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "docx"}
MAX_IMAGE_DIM = (800, 800)


def _ext(filename):
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def is_allowed_image(filename):
    return _ext(filename) in IMAGE_EXTENSIONS


def is_allowed_document(filename):
    return _ext(filename) in DOCUMENT_EXTENSIONS


def save_photo(file_storage, folder="photos"):
    """Validate, resize, and store an uploaded image. Returns stored path."""
    if not file_storage or not file_storage.filename:
        return None
    if not is_allowed_image(file_storage.filename):
        raise ValueError("Unsupported image format. Use JPG, JPEG, or PNG.")

    image = Image.open(file_storage.stream)
    image = image.convert("RGB") if image.mode in ("RGBA", "P") else image
    image.thumbnail(MAX_IMAGE_DIM)

    buf = io.BytesIO()
    fmt = "PNG" if _ext(file_storage.filename) == "png" else "JPEG"
    image.save(buf, format=fmt)
    buf.seek(0)

    return storage.save_bytes(buf.getvalue(), folder, file_storage.filename)


def save_document(file_storage, folder="documents"):
    """Validate and store an uploaded document. Returns stored path."""
    if not file_storage or not file_storage.filename:
        return None
    if not is_allowed_document(file_storage.filename):
        raise ValueError("Unsupported document format. Use PDF, JPG, PNG, or DOCX.")
    return storage.save(file_storage, folder)
