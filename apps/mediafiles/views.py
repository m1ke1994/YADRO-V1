from django.db.models import QuerySet
from django.db.models import Q
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from apps.sites.models import Site

from .models import MediaFile
from .serializers import MediaFileSerializer


class ClientMediaAccessMixin:
    permission_classes = [IsAuthenticated]

    def get_accessible_sites(self) -> QuerySet[Site]:
        queryset = Site.objects.filter(is_active=True)
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(owner=self.request.user)

    def resolve_site(self, requested=None) -> Site:
        queryset = self.get_accessible_sites()
        if requested not in (None, ""):
            lookup = Q(slug=str(requested))
            if str(requested).isdigit():
                lookup |= Q(id=int(requested))
            site = queryset.filter(lookup).first()
        else:
            site = queryset.order_by("id").first()

        if site is None:
            raise NotFound(detail="Active site for current user was not found.")
        return site

    def get_client_site(self) -> Site:
        return self.resolve_site()

    def get_queryset(self) -> QuerySet[MediaFile]:
        return MediaFile.objects.filter(site__in=self.get_accessible_sites()).select_related("site", "uploaded_by")


class ClientMediaListView(ClientMediaAccessMixin, generics.ListAPIView):
    serializer_class = MediaFileSerializer

    def get_queryset(self) -> QuerySet[MediaFile]:
        queryset = super().get_queryset()
        site = self.request.query_params.get("site")
        file_type = self.request.query_params.get("file_type")
        search = self.request.query_params.get("search")

        if site:
            queryset = queryset.filter(site=self.resolve_site(site))
        if file_type:
            queryset = queryset.filter(file_type=file_type)
        if search:
            queryset = queryset.filter(
                Q(original_name__icontains=search)
                | Q(title__icontains=search)
                | Q(alt_text__icontains=search)
                | Q(description__icontains=search)
            )

        return queryset.order_by("-uploaded_at")


class ClientMediaUploadView(ClientMediaAccessMixin, generics.CreateAPIView):
    serializer_class = MediaFileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def _resolve_site(self):
        return self.resolve_site(self.request.data.get("site"))

    def perform_create(self, serializer):
        site = self._resolve_site()
        section_key = str(self.request.data.get("section") or "uploads")
        field_key = str(self.request.data.get("field") or "")
        original_name = getattr(self.request.data.get("file"), "name", "")

        existing = MediaFile.objects.filter(
            site=site,
            section_key=section_key,
            field_key=field_key,
            original_name=original_name,
        ).first()
        if existing is not None:
            storage = existing.file.storage
            file_name = existing.file.name
            existing.delete()
            if file_name:
                storage.delete(file_name)

        serializer.save(
            site=site,
            section_key=section_key,
            field_key=field_key,
            original_name=original_name,
            uploaded_by=self.request.user,
        )


class ClientMediaDetailView(ClientMediaAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MediaFileSerializer
    lookup_field = "id"
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def perform_destroy(self, instance):
        storage = instance.file.storage
        file_name = instance.file.name

        instance.delete()

        if file_name:
            storage.delete(file_name)


class UploadFileView(ClientMediaUploadView):
    """
    Alias endpoint for uploader integrations.
    POST /api/uploads/
    """
