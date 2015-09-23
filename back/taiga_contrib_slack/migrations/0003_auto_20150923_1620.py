# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taiga_contrib_slack', '0002_slackhook_channel'),
    ]

    operations = [
        migrations.AddField(
            model_name='slackhook',
            name='notify_issue_change',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='slackhook',
            name='notify_issue_create',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='slackhook',
            name='notify_issue_delete',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='slackhook',
            name='notify_task_change',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='slackhook',
            name='notify_task_create',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='slackhook',
            name='notify_task_delete',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='slackhook',
            name='notify_userstory_change',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='slackhook',
            name='notify_userstory_create',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='slackhook',
            name='notify_userstory_delete',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='slackhook',
            name='notify_wikipage_change',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='slackhook',
            name='notify_wikipage_create',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='slackhook',
            name='notify_wikipage_delete',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
