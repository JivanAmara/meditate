# Generated by Django 2.0 on 2018-04-20 00:01

from django.db import migrations, models
import meditate.models


class Migration(migrations.Migration):

    dependencies = [
        ('meditate', '0018_auto_20180417_2102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saleitem',
            name='downloadable',
            field=models.FileField(blank=True, default='', storage=meditate.models.OverwriteStorage(), upload_to=''),
        ),
    ]