"""
Test file uploads API endpoint for users in impress's core app.
"""

import re
import uuid

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile

import pytest
from rest_framework.test import APIClient

from core import factories
from core.tests.conftest import TEAM, USER, VIA

pytestmark = pytest.mark.django_db


def test_api_documents_attachment_upload_anonymous():
    """Anonymous users can't upload attachments to a document."""
    document = factories.DocumentFactory()
    file = SimpleUploadedFile("test_file.jpg", b"Dummy content")

    url = f"/api/v1.0/documents/{document.id!s}/attachment-upload/"
    response = APIClient().post(url, {"file": file}, format="multipart")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_documents_attachment_upload_authenticated_public():
    """
    Users who are not related to a public document should not be allowed to upload an attachment.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    document = factories.DocumentFactory(is_public=True)
    file = SimpleUploadedFile("test_file.jpg", b"Dummy content")

    url = f"/api/v1.0/documents/{document.id!s}/attachment-upload/"
    response = client.post(url, {"file": file}, format="multipart")

    assert response.status_code == 403
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }


def test_api_documents_attachment_upload_authenticated_private():
    """
    Users who are not related to a private document should not be able to upload an attachment.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    document = factories.DocumentFactory(is_public=False)
    file = SimpleUploadedFile("test_file.jpg", b"Dummy content")

    url = f"/api/v1.0/documents/{document.id!s}/attachment-upload/"
    response = client.post(url, {"file": file}, format="multipart")

    assert response.status_code == 404
    assert response.json() == {"detail": "No Document matches the given query."}


@pytest.mark.parametrize("via", VIA)
def test_api_documents_attachment_upload_reader(via, mock_user_get_teams):
    """
    Users who are simple readers on a document should not be allowed to upload an attachment.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    document = factories.DocumentFactory()
    if via == USER:
        factories.UserDocumentAccessFactory(document=document, user=user, role="reader")
    elif via == TEAM:
        mock_user_get_teams.return_value = ["lasuite", "unknown"]
        factories.TeamDocumentAccessFactory(
            document=document, team="lasuite", role="reader"
        )

    file = SimpleUploadedFile("test_file.jpg", b"Dummy content")

    url = f"/api/v1.0/documents/{document.id!s}/attachment-upload/"
    response = client.post(url, {"file": file}, format="multipart")

    assert response.status_code == 403
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }


@pytest.mark.parametrize("role", ["editor", "administrator", "owner"])
@pytest.mark.parametrize("via", VIA)
def test_api_documents_attachment_upload_success(
    via, role, mock_user_get_teams, settings
):
    """
    Editors, administrators and owners of a document should be able to upload an attachment.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    document = factories.DocumentFactory()
    if via == USER:
        factories.UserDocumentAccessFactory(document=document, user=user, role=role)
    elif via == TEAM:
        mock_user_get_teams.return_value = ["lasuite", "unknown"]
        factories.TeamDocumentAccessFactory(
            document=document, team="lasuite", role=role
        )

    file = SimpleUploadedFile("test_file.jpg", b"Dummy content")

    url = f"/api/v1.0/documents/{document.id!s}/attachment-upload/"
    response = client.post(url, {"file": file}, format="multipart")

    assert response.status_code == 201

    pattern = re.compile(rf"^{settings.MEDIA_URL}{document.id!s}/attachments/(.*)\.jpg")
    match = pattern.search(response.json()["file"])
    file_id = match.group(1)

    # Validate that file_id is a valid UUID
    uuid.UUID(file_id)


def test_api_documents_attachment_upload_invalid(client):
    """Attempt to upload without a file should return an explicit error."""
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    document = factories.DocumentFactory(users=[(user, "owner")])
    url = f"/api/v1.0/documents/{document.id!s}/attachment-upload/"

    response = client.post(url, {}, format="multipart")

    assert response.status_code == 400
    assert response.json() == {"file": ["No file was submitted."]}


def test_api_documents_attachment_upload_size_limit_exceeded(settings):
    """The uploaded file should not exceeed the maximum size in settings."""
    settings.DOCUMENT_IMAGE_MAX_SIZE = 1048576  # 1 MB for test

    user = factories.UserFactory()
    client = APIClient()
    client.force_login(user)

    document = factories.DocumentFactory(users=[(user, "owner")])
    url = f"/api/v1.0/documents/{document.id!s}/attachment-upload/"

    # Create a temporary file larger than the allowed size
    content = b"a" * (1048576 + 1)
    file = ContentFile(content, name="test.jpg")

    response = client.post(url, {"file": file}, format="multipart")

    assert response.status_code == 400
    assert response.json() == {"file": ["File size exceeds the maximum limit of 1 MB."]}


def test_api_documents_attachment_upload_type_not_allowed(settings):
    """The uploaded file should be of a whitelisted type."""
    settings.DOCUMENT_IMAGE_ALLOWED_MIME_TYPES = ["image/jpeg", "image/png"]

    user = factories.UserFactory()
    client = APIClient()
    client.force_login(user)

    document = factories.DocumentFactory(users=[(user, "owner")])
    url = f"/api/v1.0/documents/{document.id!s}/attachment-upload/"

    # Create a temporary file with a not allowed type (e.g., text file)
    file = ContentFile(b"a" * 1048576, name="test.txt")

    response = client.post(url, {"file": file}, format="multipart")

    assert response.status_code == 400
    assert response.json() == {
        "file": [
            "File type 'text/plain' is not allowed. Allowed types are: image/jpeg, image/png"
        ]
    }
