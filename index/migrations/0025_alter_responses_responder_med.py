# Generated by Django 4.2.7 on 2024-09-09 13:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0024_responses_responder_med'),
    ]

    operations = [
        migrations.AlterField(
            model_name='responses',
            name='responder_med',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='index.usermed'),
        ),
    ]
