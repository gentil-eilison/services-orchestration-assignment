# Generated by Django 5.1 on 2024-08-28 03:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_payment_value'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='status',
        ),
    ]
