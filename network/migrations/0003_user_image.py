# Generated by Django 3.1 on 2020-10-17 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_auto_20201017_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(default='site/default.jpg', upload_to='users/'),
        ),
    ]
