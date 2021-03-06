# Generated by Django 2.0.9 on 2019-01-20 17:02

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        #('swingtime', '0003_auto_20181019_1411'),
        ('swingtime', '0001_initial'),
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=30)),
                ('last_name', models.CharField(blank=True, max_length=150)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AtriaEvent',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='swingtime.Event')),
                ('program', models.CharField(blank=True, max_length=32)),
                ('program_en', models.CharField(blank=True, max_length=32, null=True)),
                ('program_es', models.CharField(blank=True, max_length=32, null=True)),
                ('program_zh', models.CharField(blank=True, max_length=32, null=True)),
                ('program_fr', models.CharField(blank=True, max_length=32, null=True)),
                ('location', models.CharField(blank=True, max_length=100)),
            ],
            bases=('swingtime.event',),
        ),
        migrations.CreateModel(
            name='AtriaEventProgram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abbr', models.CharField(max_length=4, unique=True)),
                ('label', models.CharField(max_length=50)),
                ('label_en', models.CharField(max_length=50, null=True)),
                ('label_es', models.CharField(max_length=50, null=True)),
                ('label_zh', models.CharField(max_length=50, null=True)),
                ('label_fr', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='atriaevent',
            name='event_program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='atriacalendar.AtriaEventProgram', verbose_name='event program'),
        ),
        migrations.CreateModel(
            name='AtriaNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note_ptr', models.CharField(blank=True, max_length=32, null=True)),
            ],
        ),
    ]
