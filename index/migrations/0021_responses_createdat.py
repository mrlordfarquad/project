# Generated by Django 4.2.7 on 2024-08-15 10:09

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0020_remove_responses_createdat_delete_avgvalue'),
    ]

    operations = [
        migrations.AddField(
            model_name='responses',
            name='createdAt',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
