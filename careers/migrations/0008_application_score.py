# Generated by Django 3.0.7 on 2020-07-17 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careers', '0007_applicantanalysis'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='score',
            field=models.IntegerField(default=0, verbose_name='Applicant Score'),
        ),
    ]