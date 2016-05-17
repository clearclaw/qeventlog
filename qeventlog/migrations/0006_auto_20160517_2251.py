# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-17 22:51
from __future__ import unicode_literals

import decimal
import django.core.serializers.json
from django.db import migrations
import django_pgjsonb.fields


class Migration(migrations.Migration):

    dependencies = [
        ('qeventlog', '0005_auto_20160509_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qevent',
            name='data',
            field=django_pgjsonb.fields.JSONField(blank=True, db_index=True, db_index_options=[{}], decode_kwargs={'parse_float': decimal.Decimal}, encode_kwargs={'cls': django.core.serializers.json.DjangoJSONEncoder}, null=True),
        ),
    ]
