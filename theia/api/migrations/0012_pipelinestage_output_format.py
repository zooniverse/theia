# Generated by Django 2.2.2 on 2019-06-14 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20190515_0156'),
    ]

    operations = [
        migrations.AddField(
            model_name='pipelinestage',
            name='output_format',
            field=models.CharField(max_length=8, null=True),
        ),
    ]