# Generated by Django 2.2.1 on 2019-05-03 16:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_jobbundle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestedscene',
            name='imagery_request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requested_scenes', to='api.ImageryRequest'),
        ),
    ]