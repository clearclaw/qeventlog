# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-05 03:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qeventlog', '0003_auto_20160503_0352'),
    ]

    operations = [
        migrations.CreateModel(
            name='QTaskType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, db_index=True, max_length=128, null=True, unique=True)),
            ],
            options={
                'ordering': ['type'],
            },
        ),
        migrations.AlterIndexTogether(
            name='qtaskstate',
            index_together=set([]),
        ),
        migrations.RemoveField(
            model_name='qtaskstate',
            name='name',
        ),
        migrations.DeleteModel(
            name='QTaskName',
        ),
        migrations.DeleteModel(
            name='QTaskState',
        ),
        migrations.AddField(
            model_name='qevent',
            name='type',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='qeventlog.QTaskType'),
            preserve_default=False,
        ),
    ]
