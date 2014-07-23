# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deploy', '0002_deploy'),
    ]

    operations = [
        migrations.AddField(
            model_name='deploy',
            name='output',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
