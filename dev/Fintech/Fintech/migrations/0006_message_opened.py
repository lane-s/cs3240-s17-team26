# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-21 21:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Fintech', '0005_auto_20170417_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='opened',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
