# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-02 03:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Fintech', '0009_message_static_encrypt'),
    ]

    operations = [
        migrations.AddField(
            model_name='companydetails',
            name='company_ceo',
            field=models.CharField(default='ceo', max_length=30),
            preserve_default=False,
        ),
    ]
