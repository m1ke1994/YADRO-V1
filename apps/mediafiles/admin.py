from django.contrib import admin
from django.utils.html import format_html

from .models import MediaFile


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = (
        "site",
        "section_key",
        "field_key",
        "title",
        "preview",
        "filename",
        "file_type",
        "mime_type",
        "size",
        "uploaded_by",
        "uploaded_at",
    )
    list_filter = ("site", "section_key", "field_key", "file_type", "mime_type", "uploaded_at")
    search_fields = (
        "title",
        "alt_text",
        "description",
        "file",
        "original_name",
        "site__name",
        "section_key",
        "field_key",
        "checksum_sha256",
    )
    readonly_fields = ("preview", "size", "mime_type", "file_type", "checksum_sha256", "uploaded_at")

    @admin.display(description="Preview")
    def preview(self, obj):
        if not obj.file:
            return "-"
        if obj.file_type == "image":
            return format_html('<img src="{}" style="height:48px;border-radius:6px;" />', obj.file.url)
        if obj.file_type == "video":
            return format_html('<a href="{}" target="_blank">Видео</a>', obj.file.url)
        return format_html('<a href="{}" target="_blank">Файл</a>', obj.file.url)

    @admin.display(description="Filename")
    def filename(self, obj):
        return obj.get_filename()
