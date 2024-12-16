# Generated by Django 5.1 on 2024-12-16 14:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_userentry2_stock_main'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='substock_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.stockitem2'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='stock_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.stockitem'),
        ),
        migrations.AlterField(
            model_name='userentry2',
            name='total_price',
            field=models.DecimalField(decimal_places=2, max_digits=1000),
        ),
    ]