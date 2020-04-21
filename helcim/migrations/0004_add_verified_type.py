# pylint: disable=missing-docstring, invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('helcim', '0003_add_user_to_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helcimtransaction',
            name='transaction_type',
            field=models.CharField(
                choices=[
                    ('s', 'purchase (sale)'),
                    ('p', 'pre-authorization'),
                    ('c', 'capture'),
                    ('r', 'refund'),
                    ('v', 'verify')
                ],
                help_text='The type of transaction',
                max_length=1,
            ),
        ),
    ]
