# Generated by Django 4.2.1 on 2023-06-04 11:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0001_initial'),
        ('scores_fixtures', '0007_goalscorers_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goalscorers',
            name='team',
            field=models.ForeignKey(default='8bd1e805-08e4-470c-9a31-200788fbf4d9', on_delete=django.db.models.deletion.CASCADE, to='tournament.team'),
        ),
    ]
