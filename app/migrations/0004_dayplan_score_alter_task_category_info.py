# Generated by Django 5.1.3 on 2024-11-23 03:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_dayplan_task_delete_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='dayplan',
            name='score',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='task',
            name='category',
            field=models.CharField(choices=[('Compulsory', 'Compulsory'), ('Optional', 'Optional')], max_length=20),
        ),
        migrations.CreateModel(
            name='info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('streak', models.IntegerField(default=0)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='static/images/photos/')),
                ('discipline_score', models.IntegerField(default=0)),
                ('freeze_available', models.IntegerField(default=3)),
                ('last_freeze_used', models.DateField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]