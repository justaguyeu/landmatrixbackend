# Generated by Django 5.1 on 2024-11-17 09:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stockitem2',
            options={'verbose_name': 'Stock Item', 'verbose_name_plural': 'Stock Items'},
        ),
        migrations.AlterUniqueTogether(
            name='stockitem2',
            unique_together={('stock_name', 'stock_main')},
        ),
    ]
