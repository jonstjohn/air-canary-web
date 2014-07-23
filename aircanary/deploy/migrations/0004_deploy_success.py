# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deploy', '0003_deploy_output'),
    ]

    operations = [
        migrations.AddField(
            model_name='deploy',
            name='success',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
