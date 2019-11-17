# pylint: disable=missing-docstring, invalid-name
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('helcim', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='helcimtoken',
            name='cc_name',
            field=models.CharField(
                blank=True,
                help_text='The cardholder name',
                max_length=256,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='helcimtoken',
            name='cc_expiry',
            field=models.DateField(
                blank=True,
                help_text='The credit card expiry date',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='helcimtoken',
            name='django_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='helcim_tokens',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
