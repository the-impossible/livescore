# Generated by Django 4.2.1 on 2023-07-08 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0001_initial'),
        ('scores_fixtures', '0015_matchstat'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MatchStat',
            new_name='Card',
        ),
        migrations.CreateModel(
            name='MatchStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('home_corner', models.IntegerField(default=0)),
                ('away_corner', models.IntegerField(default=0)),
                ('home_fouls', models.IntegerField(default=0)),
                ('away_fouls', models.IntegerField(default=0)),
                ('home_ball_possession', models.IntegerField(default=0)),
                ('away_ball_possession', models.IntegerField(default=0)),
                ('home_offside', models.IntegerField(default=0)),
                ('away_offside', models.IntegerField(default=0)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scores_fixtures.match')),
            ],
        ),
    ]
