# pylint: disable=missing-docstring, line-too-long, invalid-name

from __future__ import unicode_literals
from uuid import uuid4

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HelcimTransaction',
            fields=[
                ('id', models.UUIDField(default=uuid4, editable=False, primary_key=True, verbose_name='ID')),
                ('raw_request', models.CharField(blank=True, help_text='The raw request used for this transaction', max_length=1024, null=True)),
                ('raw_response', models.CharField(blank=True, help_text='The raw response returned for this transaction', max_length=1024, null=True)),
                ('transaction_success', models.BooleanField(help_text='Whether the transaction was successful or not')),
                ('response_message', models.CharField(blank=True, help_text='The response message with the API call', max_length=256, null=True)),
                ('notice', models.CharField(blank=True, help_text='Any error or warning messages from Helcim', max_length=128, null=True)),
                ('date_response', models.DateTimeField(help_text='The date and time of the API response')),
                ('date_created', models.DateTimeField(auto_now_add=True, help_text='Date and time this transaction was recorded in database')),
                ('transaction_type', models.CharField(choices=[('s', 'purchase (sale)'), ('p', 'pre-authorization'), ('c', 'capture'), ('r', 'refund')], help_text='The type of transaction', max_length=1)),
                ('transaction_id', models.PositiveIntegerField(blank=True, help_text='The Helcim Commerce transaction ID', null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, help_text='The transaction amount', max_digits=12, null=True)),
                ('currency', models.CharField(blank=True, help_text='The transaction currency', max_length=8, null=True)),
                ('cc_name', models.CharField(blank=True, help_text='The cardholder name', max_length=256, null=True)),
                ('cc_number', models.CharField(blank=True, help_text='The first four and last 4 digits of the credit card number', max_length=16, null=True)),
                ('cc_expiry', models.DateField(blank=True, help_text='The credit card expiry date', null=True)),
                ('cc_type', models.CharField(blank=True, help_text='The credit card type', max_length=32, null=True)),
                ('token', models.CharField(blank=True, help_text='The Helcim generated and stored credit card token', max_length=23, null=True)),
                ('token_f4l4', models.CharField(blank=True, help_text='The first and last 4 digits of the credit card number', max_length=8, null=True)),
                ('avs_response', models.CharField(blank=True, help_text='The address verification response', max_length=1, null=True)),
                ('cvv_response', models.CharField(blank=True, help_text='The CVV verification response', max_length=1, null=True)),
                ('approval_code', models.CharField(blank=True, help_text='The transaction approval code', max_length=16, null=True)),
                ('order_number', models.CharField(blank=True, help_text='The Helcim order number', max_length=16, null=True)),
                ('customer_code', models.CharField(blank=True, help_text='The Helcim customer code', max_length=16, null=True)),
            ],
            options={
                'ordering': ('-date_response',),
                'permissions': (('helcim_transactions', 'Can view and interact with Helcim transactions.'),),
            },
        ),
        migrations.CreateModel(
            name='HelcimToken',
            fields=[
                ('id', models.UUIDField(default=uuid4, editable=False, primary_key=True, verbose_name='ID')),
                ('token', models.CharField(help_text='The Helcim card token number', max_length=23)),
                ('token_f4l4', models.CharField(help_text='The first & last four digits of the credit card number', max_length=8)),
                ('date_added', models.DateTimeField(auto_now_add=True, help_text='Date and time this token was added to database')),
                ('customer_code', models.CharField(blank=True, help_text='The Helcim customer code', max_length=16, null=True)),
                ('django_user', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='tokens', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('helcim_tokens', 'Can view and interact with Helcim tokens.'),),
                'unique_together': {('token', 'token_f4l4', 'customer_code', 'django_user')},
            },
        )
    ]
