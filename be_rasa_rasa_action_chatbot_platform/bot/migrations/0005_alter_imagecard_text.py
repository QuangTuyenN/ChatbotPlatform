# Generated by Django 4.2.8 on 2024-07-17 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0004_alter_actioncard_action_alter_imagecard_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagecard',
            name='text',
            field=models.TextField(blank=True, max_length=500),
        ),
    ]