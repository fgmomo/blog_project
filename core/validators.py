from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]
MAX_IMAGE_SIZE_MB = 5

validate_image_extension = FileExtensionValidator(
    allowed_extensions=ALLOWED_IMAGE_EXTENSIONS
)


def validate_image_size(file):
    max_size = MAX_IMAGE_SIZE_MB * 1024 * 1024

    if file.size > max_size:
        raise ValidationError(
            f"L'image ne doit pas dépasser {MAX_IMAGE_SIZE_MB} Mo."
        )
