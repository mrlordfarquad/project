# Generated by Django 4.2.7 on 2024-06-26 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0005_remove_questions_max_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='max_value',
            field=models.IntegerField(blank=True, default=100),
        ),
    ]
