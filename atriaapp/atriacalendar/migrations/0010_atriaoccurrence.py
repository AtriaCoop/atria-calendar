# Generated by Django 2.0.10 on 2019-03-04 23:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        #('swingtime', '0002_auto_20190210_1236'),
        ('swingtime', '0001_initial'),
        ('atriacalendar', '0009_auto_20190215_1744'),
    ]

    operations = [
        migrations.CreateModel(
            name='AtriaOccurrence',
            fields=[
                ('occurrence_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='swingtime.Occurrence')),
            ],
            bases=('swingtime.occurrence',),
        ),
    ]
