# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_transaction_bank_transaction_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbankaccount',
            name='is_simulation',
            field=models.BooleanField(default=False, verbose_name='시뮬레이션 계좌 여부'),
        ),
    ]

