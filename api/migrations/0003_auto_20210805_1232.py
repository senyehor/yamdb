# Generated by Django 3.0.5 on 2021-08-05 09:32

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_review_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 8, 5, 9, 32, 26, 310979, tzinfo=utc)),
        ),
    ]