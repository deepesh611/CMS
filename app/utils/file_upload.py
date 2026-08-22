"""Secure file upload handling: validation, image resizing, storage."""
import io

from PIL import Image

from app.utils.storage import storage

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "bmp"}
DOCUMENT_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "docx"}
MAX_IMAGE_DIM = (800, 800)
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


def _ext(filename):
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def is_allowed_image(filename):
    return _ext(filename) in IMAGE_EXTENSIONS


def is_allowed_document(filename):
    return _ext(filename) in DOCUMENT_EXTENSIONS


def save_photo(file_storage, folder="photos"):
    """Validate, resize, and store an uploaded image. Returns stored path.

    - Allowed formats: JPG, JPEG, PNG, BMP.
    - Maximum file size: 5 MB.
    - BMP files are automatically converted to JPEG on save.
    """
    if not file_storage or not file_storage.filename:
        return None
    if not is_allowed_image(file_storage.filename):
        raise ValueError(
            "Unsupported image format. Use JPG, JPEG, PNG, or BMP."
        )

    # --- Size check (max 5 MB) -------------------------------------------
    file_storage.stream.seek(0, 2)  # seek to end
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)     # reset
    if size > MAX_IMAGE_SIZE:
        raise ValueError(
            f"Image too large ({size / (1024 * 1024):.1f} MB). "
            f"Maximum allowed size is {MAX_IMAGE_SIZE // (1024 * 1024)} MB."
        )

    image = Image.open(file_storage.stream)
    image = image.convert("RGB") if image.mode in ("RGBA", "P") else image
    image.thumbnail(MAX_IMAGE_DIM)

    buf = io.BytesIO()

    # BMP is converted to JPEG for storage efficiency
    ext = _ext(file_storage.filename)
    if ext == "bmp":
        fmt = "JPEG"
        # Rewrite the filename extension so the stored file is .jpg
        save_filename = file_storage.filename.rsplit(".", 1)[0] + ".jpg"
    elif ext == "png":
        fmt = "PNG"
        save_filename = file_storage.filename
    else:
        fmt = "JPEG"
        save_filename = file_storage.filename

    image.save(buf, format=fmt)
    buf.seek(0)

    return storage.save_bytes(buf.getvalue(), folder, save_filename)


def save_document(file_storage, folder="documents"):
    """Validate and store an uploaded document. Returns stored path."""
    if not file_storage or not file_storage.filename:
        return None
    if not is_allowed_document(file_storage.filename):
        raise ValueError("Unsupported document format. Use PDF, JPG, PNG, or DOCX.")
    return storage.save(file_storage, folder)
