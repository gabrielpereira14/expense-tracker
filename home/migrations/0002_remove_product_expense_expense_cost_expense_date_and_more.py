# Generated by Django 5.0.6 on 2024-06-20 19:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='expense',
        ),
        migrations.AddField(
            model_name='expense',
            name='cost',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='expense',
            name='date',
            field=models.DateField(default="2011-01-01"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='expense',
            name='name',
            field=models.TextField(default='a'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='name',
            field=models.TextField(default='a'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='unit',
            field=models.TextField(default='a', max_length=2),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='productcode',
            name='code',
            field=models.BigIntegerField(unique=True),
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField()),
                ('unit_price', models.FloatField()),
                ('expense', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.expense')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.product')),
            ],
        ),
    ]
