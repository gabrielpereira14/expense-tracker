# Generated by Django 5.0.6 on 2024-06-20 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_rename_name_expense_establishment'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='products',
            field=models.ManyToManyField(related_name='products', through='home.CartItem', to='home.product'),
        ),
    ]
