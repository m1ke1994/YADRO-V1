from rest_framework import serializers

from .models import MediaFile


class MediaFileSerializer(serializers.ModelSerializer):
    site = serializers.IntegerField(source="site_id", read_only=True)
    uploaded_by = serializers.IntegerField(source="uploaded_by_id", read_only=True)
    alt = serializers.CharField(source="alt_text", required=False, allow_blank=True)
    created_at = serializers.DateTimeField(source="uploaded_at", read_only=True)
    url = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()
    filename = serializers.SerializerMethodField()

    class Meta:
        model = MediaFile
        fields = (
            "id",
            "site",
            "section_key",
            "field_key",
            "original_name",
            "title",
            "alt_text",
            "alt",
            "description",
            "file",
            "url",
            "path",
            "filename",
            "file_type",
            "mime_type",
            "size",
            "checksum_sha256",
            "uploaded_by",
            "uploaded_at",
            "created_at",
        )
        read_only_fields = (
            "id",
            "file_type",
            "mime_type",
            "size",
            "checksum_sha256",
            "uploaded_by",
            "uploaded_at",
            "created_at",
            "url",
            "path",
            "filename",
        )

    def get_url(self, obj):
        return obj.get_absolute_url()

    def get_path(self, obj):
        return obj.get_relative_media_path()

    def get_filename(self, obj):
        return obj.get_filename()

    def update(self, instance, validated_data):
        if "file" in validated_data:
            instance.checksum_sha256 = ""
        return super().update(instance, validated_data)
