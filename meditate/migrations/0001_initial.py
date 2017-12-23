# Generated by Django 2.0 on 2017-12-23 01:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=80)),
                ('dollarsOff', models.DecimalField(decimal_places=4, max_digits=10)),
                ('percentOff', models.DecimalField(decimal_places=4, max_digits=7)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=80)),
                ('desc', models.CharField(max_length=500)),
                ('img', models.FileField(upload_to='')),
                ('price', models.DecimalField(decimal_places=2, max_digits=3)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sessionid', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='coupon',
            name='items',
            field=models.ManyToManyField(to='meditate.Item'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='coupons',
            field=models.ManyToManyField(to='meditate.Coupon'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='meditate.Item'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='order',
            field=models.ForeignKey(on_delete='cascade', to='meditate.Order'),
        ),
    ]
