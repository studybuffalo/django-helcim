from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='HelcimTransaction',
            fields=[
                # TODO: Ensure UUID built correctly
                ('uuid', models.UUIDField(primary_key=True, serialize=False, verbose_name='ID')),
                # TODO: Figure out good length for response and notice messages
                ('raw_response', models.TextField(max_length=1024)),
                ('response', models.IntegerField(max_length=1)),
                ('response_message', models.CharField(blank=True, max_length=32, null=True)),
                ('notice_message', models.CharField(blank=True, max_length=128, null=True)),
                ('date_response', models.DateTimeField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('transaction_type', models.CharField(max_length=8)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('currency', models.CharField(blank=True, max_length=8, null=True)),
                ('card_number', models.CharField(help_text='The first four and last 4 digits of the credit card number', max_length=16)),
                ('card_type', models.CharField(blank=True, max_length=32, null=True)),
                ('card_token', models.CharField(help_text='The Helcim generated and stored credit card token', max_length=23)),
                ('avs_response', models.CharField(blank=True, max_length=1, null=True)),
                ('cvv_response', models.CharField(blank=True, max_length=1, null=True)),
                ('approval_code', models.CharField(blank=True, max_length=16, null=True)),
                ('order_number', models.CharField(blank=True, max_length=16, null=True)),
                ('customer_code', models.CharField(blank=True, max_length=16, null=True)),
            ],
            options={
                'ordering': ('-date_created',),
            },
        ),
    ]