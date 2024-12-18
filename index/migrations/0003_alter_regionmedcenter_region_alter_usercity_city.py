# Generated by Django 4.2.7 on 2024-11-03 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0002_alter_regionmedcenter_region_alter_usercity_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regionmedcenter',
            name='region',
            field=models.CharField(choices=[('Астана', 'Астана'), ('ALMATY', 'Алматы'), ('AKTOBE', 'Актюбинская область'), ('ATYRAUSKAYA', 'Атырауская область'), ('ZAPADNO', 'Западно-Казахстанская область'), ('Кызылординская область', 'Кызылординская область'), ('MANGISTAU', 'Мангистауская область'), ('PAVLODAR', 'Павлодарская область'), ('TURKESTAN', 'Южно-Казахстанская область')], max_length=50),
        ),
        migrations.AlterField(
            model_name='usercity',
            name='city',
            field=models.CharField(blank=True, choices=[('Астана', 'Астана'), ('ALMATY', 'Алматы'), ('AKTOBE', 'Актюбинская область'), ('ATYRAUSKAYA', 'Атырауская область'), ('ZAPADNO', 'Западно-Казахстанская область'), ('Кызылординская область', 'Кызылординская область'), ('MANGISTAU', 'Мангистауская область'), ('PAVLODAR', 'Павлодарская область'), ('TURKESTAN', 'Южно-Казахстанская область')], max_length=50, null=True),
        ),
    ]
