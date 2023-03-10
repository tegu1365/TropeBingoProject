# Generated by Django 4.1.6 on 2023-02-16 01:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gui', '0012_bingosheet_type_personaltrope_types_trope_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='bingosheet',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bingosheet',
            name='last_update',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
