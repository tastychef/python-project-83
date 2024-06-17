"""Url validation and normalization logic."""
from urllib.parse import urlparse

from validators import url as url_validator

MAX_URL_LENGTH = 255


def validate(url: str) -> list:
    """Validate url.

    Parameters:
        url: url address.

    Returns:
        Validation error message/-s if not passed.
    """
    errors = []
    if not url_validator(url):
        errors.append('Некорректный URL')
    if len(url) > MAX_URL_LENGTH:
        errors.append('URL превышает 255 символов')
    elif not url:
        errors.append('URL обязателен')
    return errors


def normalize(url: str) -> str:
    """Normalize url.

    Parameters:
        url: url address.

    Returns:
        Normalized url address.
    """
    parsed_url = urlparse(url)
    return '{scheme}://{netloc}'.format(
        scheme=parsed_url.scheme,
        netloc=parsed_url.netloc,
    )
