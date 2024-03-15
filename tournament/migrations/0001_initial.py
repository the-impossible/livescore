# Generated by Django 4.2.1 on 2023-05-30 16:54

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deptName', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('rector_cup', 'rector_cup'), ('departmental', 'departmental')], max_length=15, unique=True)),
                ('session', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('team_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('coach', models.CharField(max_length=30)),
                ('deptName', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tournament.department')),
                ('tournaments', models.ManyToManyField(blank=True, related_name='tournaments', to='tournament.tournament')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('image', models.ImageField(blank=True, null=True, upload_to='upload/')),
                ('age', models.IntegerField()),
                ('jersey_number', models.IntegerField()),
                ('position', models.CharField(max_length=20)),
                ('goals', models.IntegerField()),
                ('assists', models.IntegerField()),
                ('is_captain', models.BooleanField()),
                ('team_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournament.team')),
            ],
        ),
    ]