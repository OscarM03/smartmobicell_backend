# Generated by Django 5.0.7 on 2024-08-25 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartmobicell', '0004_orderitems_shippingoption'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitems',
            name='shippingoption',
        ),
        migrations.AddField(
            model_name='order',
            name='shippingoption',
            field=models.CharField(default='CBD', max_length=100),
            preserve_default=False,
        ),
    ]
