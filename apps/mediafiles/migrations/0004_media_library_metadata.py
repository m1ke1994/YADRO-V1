from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("mediafiles", "0003_mediafile_field_key_mediafile_original_name_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name="mediafile",
            old_name="alt",
            new_name="alt_text",
        ),
        migrations.RenameField(
            model_name="mediafile",
            old_name="created_at",
            new_name="uploaded_at",
        ),
        migrations.AlterField(
            model_name="mediafile",
            name="uploaded_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Загружено"),
        ),
        migrations.AddField(
            model_name="mediafile",
            name="checksum_sha256",
            field=models.CharField(blank=True, db_index=True, max_length=64, verbose_name="SHA-256"),
        ),
        migrations.AddField(
            model_name="mediafile",
            name="uploaded_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="uploaded_media_files",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Загрузил",
            ),
        ),
        migrations.AlterModelOptions(
            name="mediafile",
            options={
                "ordering": ["-uploaded_at"],
                "verbose_name": "Медиафайл",
                "verbose_name_plural": "Медиафайлы",
            },
        ),
    ]
