# Generated by Django 4.1.6 on 2023-02-10 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gui', '0004_alter_trope_genre'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trope',
            old_name='genre',
            new_name='genres',
        ),
    ]
