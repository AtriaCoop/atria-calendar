# Generated by Django 2.0.9 on 2019-01-10 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atriacalendar', '0004_atriaorganization'),
    ]

    operations = [
        migrations.AddField(
            model_name='atriaorganization',
            name='org_name_en',
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='atriaorganization',
            name='org_name_es',
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='atriaorganization',
            name='org_name_fr',
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='atriaorganization',
            name='org_name_zh',
            field=models.CharField(max_length=40, null=True),
        ),
    ]