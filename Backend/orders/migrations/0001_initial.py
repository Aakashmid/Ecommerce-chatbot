# Generated by Django 5.2.2 on 2025-06-07 13:34

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(editable=False, max_length=20, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], db_index=True, default='pending', max_length=20)),
                ('payment_method', models.CharField(choices=[('cod', 'Cash On Delivery'), ('card', 'Credit/Debit Card'), ('paypal', 'PayPal'), ('bank_transfer', 'Bank Transfer')], default='cod', max_length=20)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('shipping_cost', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('tax', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('notes', models.TextField(blank=True, null=True)),
                ('tracking_number', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('shipped_at', models.DateTimeField(blank=True, null=True)),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
