# Generated by Django 5.1 on 2024-12-01 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_rename_item_name_userentry2_substock_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='userentry2',
            name='stock_main',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
