# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-24 16:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('age', models.CharField(max_length=1)),
                ('category', models.CharField(max_length=1)),
            ],
        ),
    ]
