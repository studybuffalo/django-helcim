# pylint: disable=missing-docstring, invalid-name
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('helcim', '0002_token_update_v2'),
    ]

    operations = [
        migrations.AddField(
            model_name='helcimtransaction',
            name='django_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='helcim_transactions',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
