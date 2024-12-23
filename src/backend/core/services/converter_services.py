"""Converter services."""

from django.conf import settings

import requests


class ConversionError(Exception):
    """Base exception for conversion-related errors."""


class ValidationError(ConversionError):
    """Raised when the input validation fails."""


class ServiceUnavailableError(ConversionError):
    """Raised when the conversion service is unavailable."""


class InvalidResponseError(ConversionError):
    """Raised when the conversion service returns an invalid response."""


class MissingContentError(ConversionError):
    """Raised when the response is missing required content."""


class YdocConverter:
    """Service class for conversion-related operations."""

    @property
    def auth_header(self):
        """Build microservice authentication header."""
        return f"Bearer {settings.CONVERSION_API_KEY}"

    def convert_markdown(self, text):
        """Convert a Markdown text into our internal format using an external microservice."""

        if not text:
            raise ValidationError("Input text cannot be empty")

        try:
            response = requests.post(
                settings.CONVERSION_API_URL,
                json={
                    "content": text,
                },
                headers={
                    "Authorization": self.auth_header,
                    "Content-Type": "application/json",
                },
                timeout=settings.CONVERSION_API_TIMEOUT,
            )
            response.raise_for_status()
            conversion_response = response.json()

        except requests.RequestException as err:
            raise ServiceUnavailableError(
                "Failed to connect to conversion service",
            ) from err

        except ValueError as err:
            raise InvalidResponseError(
                "Could not parse conversion service response"
            ) from err

        try:
            document_content = conversion_response[
                settings.CONVERSION_API_CONTENT_FIELD
            ]
        except KeyError as err:
            raise MissingContentError(
                f"Response missing required field: {settings.CONVERSION_API_CONTENT_FIELD}"
            ) from err

        return document_content
