import tempfile

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from io import StringIO
from pathlib import Path

from apps.sites.models import Site

from .models import MediaFile


class MediaUploadTests(APITestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.settings_override.enable()

        self.user = get_user_model().objects.create_user(
            username="media-owner",
            email="media@example.com",
            password="test-test",
        )
        self.site = Site.objects.create(
            name="A Meditation",
            slug="a-meditation",
            domain="localhost:5173",
            owner=self.user,
        )
        self.client.force_authenticate(self.user)

    def tearDown(self):
        self.settings_override.disable()
        self.media_dir.cleanup()

    def test_reupload_same_file_replaces_media_record(self):
        url = reverse("upload-file")
        payload = {
            "site": str(self.site.id),
            "section": "hero",
            "field": "image",
            "file": SimpleUploadedFile("cover.png", b"first", content_type="image/png"),
        }
        first = self.client.post(url, payload, format="multipart")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        payload["file"] = SimpleUploadedFile("cover.png", b"second", content_type="image/png")
        second = self.client.post(url, payload, format="multipart")

        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MediaFile.objects.count(), 1)
        self.assertTrue(second.data["path"].startswith("/media/sites/a-meditation/hero/"))
        media = MediaFile.objects.get()
        self.assertEqual(media.uploaded_by, self.user)
        self.assertEqual(len(media.checksum_sha256), 64)

    def test_media_library_supports_list_patch_and_delete(self):
        upload = self.client.post(
            reverse("upload-file"),
            {
                "site": str(self.site.id),
                "section": "hero",
                "field": "image",
                "file": SimpleUploadedFile("cover.svg", b"<svg></svg>", content_type="image/svg+xml"),
            },
            format="multipart",
        )
        self.assertEqual(upload.status_code, status.HTTP_201_CREATED)
        media_id = upload.data["id"]

        listing = self.client.get(reverse("client-media-list"), {"site": self.site.id, "file_type": "image"})
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(len(listing.data), 1)

        detail_url = reverse("client-media-detail", kwargs={"id": media_id})
        patched = self.client.patch(
            detail_url,
            {"title": "Hero cover", "alt_text": "Meditation hero"},
            format="json",
        )
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.assertEqual(patched.data["title"], "Hero cover")
        self.assertEqual(patched.data["alt_text"], "Meditation hero")
        self.assertEqual(patched.data["alt"], "Meditation hero")

        deleted = self.client.delete(detail_url)
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MediaFile.objects.filter(id=media_id).exists())

    def test_media_library_does_not_expose_another_users_site(self):
        other_user = get_user_model().objects.create_user(
            username="other-media-owner",
            email="other-media@example.com",
            password="test-test",
        )
        other_site = Site.objects.create(
            name="Other",
            slug="other",
            domain="other.test",
            owner=other_user,
        )
        MediaFile.objects.create(
            site=other_site,
            file=SimpleUploadedFile("private.png", b"private", content_type="image/png"),
        )

        response = self.client.get(reverse("client-media-list"), {"site": other_site.id})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ImportSiteMediaTests(APITestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.media_dir = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.settings_override.enable()

        user = get_user_model().objects.create_user(
            username="import-owner",
            email="import@example.com",
            password="test-test",
        )
        self.site = Site.objects.create(
            name="Imported site",
            slug="imported-site",
            domain="example.test",
            owner=user,
        )

        images = Path(self.workspace.name) / "assets"
        images.mkdir()
        (images / "one.png").write_bytes(b"same-image")
        (images / "duplicate.png").write_bytes(b"same-image")

    def tearDown(self):
        self.settings_override.disable()
        self.media_dir.cleanup()
        self.workspace.cleanup()

    def test_import_command_is_idempotent_and_reports_duplicates(self):
        report = Path(self.workspace.name) / "report.md"
        stdout = StringIO()

        call_command(
            "import_site_media",
            root=self.workspace.name,
            site=self.site.slug,
            report=str(report),
            stdout=stdout,
        )

        self.assertEqual(MediaFile.objects.count(), 1)
        self.assertIn("imported=1", stdout.getvalue())
        self.assertIn("duplicates=1", stdout.getvalue())
        self.assertTrue(report.exists())

        call_command(
            "import_site_media",
            root=self.workspace.name,
            site=self.site.slug,
            report=str(report),
            stdout=StringIO(),
        )
        self.assertEqual(MediaFile.objects.count(), 1)
