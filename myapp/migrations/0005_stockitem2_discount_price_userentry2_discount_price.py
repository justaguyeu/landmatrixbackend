# Generated by Django 5.1 on 2024-11-01 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_rename_discount_price_stockitem2_percentage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockitem2',
            name='discount_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='userentry2',
            name='discount_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]