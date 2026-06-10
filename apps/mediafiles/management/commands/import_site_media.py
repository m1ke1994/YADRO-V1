import hashlib
import os
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from apps.mediafiles.models import MediaFile
from apps.sites.models import Site

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".svg", ".gif", ".avif"}
EXCLUDED_DIRECTORIES = {
    ".git",
    "__pycache__",
    "backups",
    "dist",
    "env",
    "node_modules",
    "staticfiles",
    "venv",
}


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class Command(BaseCommand):
    help = "Import repository images into the Django MediaFile library without creating duplicates."

    def add_arguments(self, parser):
        parser.add_argument("--site", help="Default target site id or slug.")
        parser.add_argument("--root", help="Repository root to scan. Defaults to BASE_DIR.")
        parser.add_argument("--report", help="Markdown report path.")
        parser.add_argument("--dry-run", action="store_true", help="Scan and report without changing files or DB.")

    def handle(self, *args, **options):
        root = Path(options["root"] or settings.BASE_DIR).resolve()
        if not root.exists() or not root.is_dir():
            raise CommandError(f"Scan root does not exist: {root}")

        default_site = self._resolve_default_site(options.get("site"))
        dry_run = bool(options["dry_run"])
        report_path = self._resolve_report_path(root, options.get("report"))
        sources = list(self._find_images(root))
        existing_by_hash = self._index_existing_media(dry_run=dry_run)

        rows = []
        imported = 0
        skipped = 0
        duplicates = 0
        total_bytes = sum(path.stat().st_size for path in sources)

        for source in sources:
            relative_source = source.relative_to(root).as_posix()
            checksum = file_sha256(source)
            site = self._site_for_source(source, default_site)
            existing = existing_by_hash.get((site.id, checksum))

            if existing is not None:
                duplicates += 1
                rows.append(
                    {
                        "source": relative_source,
                        "target": existing.get_relative_media_path(),
                        "status": "duplicate",
                        "size": source.stat().st_size,
                        "checksum": checksum,
                    }
                )
                continue

            section_key = self._section_for_source(source)
            target = self._expected_target(site, section_key, source.name)

            if dry_run:
                skipped += 1
                rows.append(
                    {
                        "source": relative_source,
                        "target": target,
                        "status": "dry-run",
                        "size": source.stat().st_size,
                        "checksum": checksum,
                    }
                )
                existing_by_hash[(site.id, checksum)] = self._dry_run_media(target)
                continue

            media = self._import_source(
                source=source,
                root=root,
                site=site,
                section_key=section_key,
                checksum=checksum,
            )
            existing_by_hash[(site.id, checksum)] = media
            imported += 1
            rows.append(
                {
                    "source": relative_source,
                    "target": media.get_relative_media_path(),
                    "status": "imported",
                    "size": source.stat().st_size,
                    "checksum": checksum,
                }
            )

        self._write_report(
            report_path=report_path,
            root=root,
            site=default_site,
            dry_run=dry_run,
            rows=rows,
            imported=imported,
            skipped=skipped,
            duplicates=duplicates,
            total_bytes=total_bytes,
        )

        self.stdout.write(f"found={len(sources)}")
        self.stdout.write(f"imported={imported}")
        self.stdout.write(f"skipped={skipped}")
        self.stdout.write(f"duplicates={duplicates}")
        self.stdout.write(f"total_bytes={total_bytes}")
        self.stdout.write(self.style.SUCCESS(f"report={report_path}"))

    def _resolve_default_site(self, requested):
        queryset = Site.objects.filter(is_active=True)
        value = requested or os.getenv("DEMO_SITE_SLUG", "").strip()
        site = None

        if value:
            if str(value).isdigit():
                site = queryset.filter(id=int(value)).first()
            if site is None:
                site = queryset.filter(slug=str(value)).first()
        elif queryset.count() == 1:
            site = queryset.first()

        if site is None:
            raise CommandError("Specify an active target site with --site <id-or-slug>.")
        return site

    def _resolve_report_path(self, root, configured):
        if configured:
            path = Path(configured)
            if not path.is_absolute():
                path = root / path
        else:
            stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            path = root / "docs" / f"media_import_report_{stamp}.md"
        return path.resolve()

    def _find_images(self, root):
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            relative_parts = path.relative_to(root).parts
            if any(part.lower() in EXCLUDED_DIRECTORIES for part in relative_parts):
                continue
            yield path

    def _index_existing_media(self, *, dry_run):
        indexed = {}
        for media in MediaFile.objects.select_related("site").exclude(file="").order_by("id"):
            try:
                source_path = Path(media.file.path)
            except (NotImplementedError, ValueError):
                continue
            if not source_path.exists():
                continue

            checksum = media.checksum_sha256 or file_sha256(source_path)
            if not dry_run and not media.checksum_sha256:
                MediaFile.objects.filter(pk=media.pk).update(checksum_sha256=checksum)
                media.checksum_sha256 = checksum
            indexed.setdefault((media.site_id, checksum), media)
        return indexed

    def _site_for_source(self, source, default_site):
        try:
            relative_media = source.resolve().relative_to(Path(settings.MEDIA_ROOT).resolve())
        except ValueError:
            return default_site

        parts = relative_media.parts
        if len(parts) >= 2 and parts[0] == "sites":
            site = Site.objects.filter(slug=parts[1], is_active=True).first()
            if site is not None:
                return site
        return default_site

    def _section_for_source(self, source):
        try:
            relative_media = source.resolve().relative_to(Path(settings.MEDIA_ROOT).resolve())
        except ValueError:
            relative_media = None

        if relative_media is not None and len(relative_media.parts) >= 3 and relative_media.parts[0] == "sites":
            return slugify(relative_media.parts[2]) or "imported"

        parts = {part.lower() for part in source.parts}
        if "vue-admin" in parts:
            return "frontend-assets"
        if "demo_public" in parts:
            return "demo-assets"
        return "imported"

    def _expected_target(self, site, section_key, filename):
        stem = slugify(Path(filename).stem) or "file"
        normalized = f"{stem}{Path(filename).suffix.lower()}"
        return f"{settings.MEDIA_URL.rstrip('/')}/sites/{site.slug}/{section_key}/{normalized}"

    def _dry_run_media(self, target):
        class DryRunMedia:
            def get_relative_media_path(self):
                return target

        return DryRunMedia()

    def _import_source(self, *, source, root, site, section_key, checksum):
        media_root = Path(settings.MEDIA_ROOT).resolve()
        source_resolved = source.resolve()
        relative_source = source.relative_to(root).as_posix()
        media = MediaFile(
            site=site,
            section_key=section_key,
            field_key=f"import:{relative_source}"[:255],
            original_name=source.name,
            title=source.stem,
            alt_text=source.stem,
            description=f"Imported from {relative_source}",
            checksum_sha256=checksum,
        )

        try:
            existing_media_name = source_resolved.relative_to(media_root).as_posix()
        except ValueError:
            existing_media_name = ""

        if existing_media_name:
            media.file.name = existing_media_name
            media.save()
            return media

        with source.open("rb") as handle:
            media.file.save(source.name, File(handle), save=False)
            media.save()
        return media

    def _write_report(
        self,
        *,
        report_path,
        root,
        site,
        dry_run,
        rows,
        imported,
        skipped,
        duplicates,
        total_bytes,
    ):
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Media import report",
            "",
            f"- Root: `{root}`",
            f"- Default site: `{site.slug}`",
            f"- Mode: `{'dry-run' if dry_run else 'import'}`",
            f"- Found: **{len(rows)}**",
            f"- Imported: **{imported}**",
            f"- Skipped: **{skipped}**",
            f"- Duplicates: **{duplicates}**",
            f"- Total bytes: **{total_bytes}**",
            "",
            "| Source | Target media URL | Status | Size | SHA-256 |",
            "| --- | --- | --- | ---: | --- |",
        ]
        for row in rows:
            lines.append(
                f"| `{row['source']}` | `{row['target']}` | {row['status']} | "
                f"{row['size']} | `{row['checksum']}` |"
            )
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
