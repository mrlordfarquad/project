# Generated by Django 4.2.7 on 2024-10-06 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0034_answer_is_skipped_questions_is_skip'),
    ]

    operations = [
        migrations.CreateModel(
            name='SingleForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('form', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='single_form', to='index.form')),
            ],
            options={
                'verbose_name': 'Single Form',
                'verbose_name_plural': 'Single Forms',
            },
        ),
    ]
