# Generated by Django 4.2.7 on 2024-10-06 15:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0035_singleform'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='singleform',
            name='is_active',
        ),
    ]
